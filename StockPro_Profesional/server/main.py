"""StockPro licensing API starter. Configure secrets and deploy behind HTTPS before production use."""
import os, sqlite3, secrets, hashlib, time, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, PublicFormat

DB = os.getenv('STOCKPRO_DB', 'stockpro.db')
OWNER_TOKEN = os.getenv('STOCKPRO_OWNER_TOKEN', '')
TRIAL_DAYS = int(os.getenv('STOCKPRO_TRIAL_DAYS', '30'))
app = FastAPI(title='StockPro License API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('STOCKPRO_CORS_ORIGINS','').split(',') if os.getenv('STOCKPRO_CORS_ORIGINS') else [], allow_credentials=False, allow_methods=['GET','POST'], allow_headers=['Authorization','Content-Type'])

def db():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON'); con.execute('PRAGMA journal_mode=WAL')
    con.execute('''CREATE TABLE IF NOT EXISTS licenses(id TEXT PRIMARY KEY, customer TEXT NOT NULL, device_hash TEXT NOT NULL, plan TEXT NOT NULL, expires_at TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, revoked_at TEXT)''')
    con.execute('''CREATE TABLE IF NOT EXISTS trials(device_hash TEXT PRIMARY KEY, started_at TEXT NOT NULL, expires_at TEXT NOT NULL)''')
    con.execute('''CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, license_id TEXT, at TEXT NOT NULL, detail TEXT)''')
    return con

def utcnow(): return datetime.now(timezone.utc)
def iso(dt): return dt.astimezone(timezone.utc).isoformat()
def owner_auth(authorization: str | None = Header(default=None)):
    if not OWNER_TOKEN or not authorization or not secrets.compare_digest(authorization, 'Bearer '+OWNER_TOKEN):
        raise HTTPException(401, 'Autenticación de propietario requerida')
    return True
class TrialRequest(BaseModel): device_id: str = Field(min_length=8, max_length=256)
class IssueRequest(BaseModel): customer: str = Field(min_length=1,max_length=160); device_id: str = Field(min_length=8,max_length=256); days: int = Field(ge=1,le=3650); plan: str = Field(min_length=1,max_length=60)
class RenewRequest(BaseModel): days: int = Field(ge=1,le=3650)

def dhash(device): return hashlib.sha256(device.encode()).hexdigest()
def audit(con, action, lid=None, detail=''):
    con.execute('INSERT INTO audit(action,license_id,at,detail) VALUES(?,?,?,?)',(action,lid,iso(utcnow()),detail))
@app.get('/health')
def health(): return {'ok':True,'service':'StockPro License API'}
@app.post('/v1/trial')
def trial(req: TrialRequest):
    h=dhash(req.device_id); con=db(); row=con.execute('SELECT * FROM trials WHERE device_hash=?',(h,)).fetchone()
    if row: con.close(); return {'trial_started_at':row['started_at'],'expires_at':row['expires_at'],'status':'active' if datetime.fromisoformat(row['expires_at'])>utcnow() else 'expired'}
    now=utcnow(); end=now+timedelta(days=TRIAL_DAYS); con.execute('INSERT INTO trials VALUES(?,?,?)',(h,iso(now),iso(end))); con.commit(); con.close()
    return {'trial_started_at':iso(now),'expires_at':iso(end),'status':'active'}
@app.post('/v1/license/validate')
def validate(req: TrialRequest):
    con=db(); row=con.execute("SELECT * FROM licenses WHERE device_hash=? AND status='active' ORDER BY expires_at DESC LIMIT 1",(dhash(req.device_id),)).fetchone()
    if row and datetime.fromisoformat(row['expires_at'])>utcnow(): out={'status':'licensed','expires_at':row['expires_at'],'plan':row['plan']}
    else:
        t=con.execute('SELECT * FROM trials WHERE device_hash=?',(dhash(req.device_id),)).fetchone()
        out={'status':'trial_required'} if not t else {'status':'trial' if datetime.fromisoformat(t['expires_at'])>utcnow() else 'expired','expires_at':t['expires_at']}
    con.close(); return out
@app.get('/v1/owner/licenses', dependencies=[Depends(owner_auth)])
def list_licenses():
    con=db(); rows=[dict(r) for r in con.execute('SELECT id,customer,device_hash,plan,expires_at,status,created_at,revoked_at FROM licenses ORDER BY created_at DESC')]; con.close(); return {'licenses':rows}
@app.post('/v1/owner/licenses', dependencies=[Depends(owner_auth)])
def issue(req: IssueRequest):
    con=db(); lid='SP-'+secrets.token_hex(6).upper(); now=utcnow(); exp=now+timedelta(days=req.days)
    con.execute('INSERT INTO licenses VALUES(?,?,?,?,?,?,?,NULL)',(lid,req.customer,dhash(req.device_id),req.plan,iso(exp),'active',iso(now))); audit(con,'issued',lid,f'{req.plan}; days={req.days}'); con.commit(); con.close()
    return {'id':lid,'customer':req.customer,'plan':req.plan,'expires_at':iso(exp),'status':'active'}
@app.post('/v1/owner/licenses/{license_id}/renew', dependencies=[Depends(owner_auth)])
def renew(license_id: str, req: RenewRequest):
    con=db(); row=con.execute('SELECT * FROM licenses WHERE id=?',(license_id,)).fetchone()
    if not row: con.close(); raise HTTPException(404,'Licencia no encontrada')
    if row['status']!='active': con.close(); raise HTTPException(409,'No se puede renovar una licencia revocada')
    current=datetime.fromisoformat(row['expires_at']); base=max(current,utcnow()); exp=base+timedelta(days=req.days)
    con.execute('UPDATE licenses SET expires_at=? WHERE id=?',(iso(exp),license_id)); audit(con,'renewed',license_id,f'days={req.days}'); con.commit(); con.close(); return {'id':license_id,'expires_at':iso(exp)}
@app.post('/v1/owner/licenses/{license_id}/revoke', dependencies=[Depends(owner_auth)])
def revoke(license_id: str):
    con=db(); row=con.execute('SELECT id FROM licenses WHERE id=?',(license_id,)).fetchone()
    if not row: con.close(); raise HTTPException(404,'Licencia no encontrada')
    now=iso(utcnow()); con.execute("UPDATE licenses SET status='revoked',revoked_at=? WHERE id=?",(now,license_id)); audit(con,'revoked',license_id); con.commit(); con.close(); return {'id':license_id,'status':'revoked'}
@app.get('/v1/owner/audit', dependencies=[Depends(owner_auth)])
def audit_log():
    con=db(); rows=[dict(r) for r in con.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 500')]; con.close(); return {'events':rows}
