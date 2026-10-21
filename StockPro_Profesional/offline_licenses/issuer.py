"""StockPro offline Ed25519 license issuer.
Private key is encrypted with a passphrase. Send only the generated license JSON,
never the private key. This utility is not yet wired into the web/Android app.
"""
import argparse, base64, getpass, hashlib, json, secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (Encoding, PrivateFormat,
    PublicFormat, BestAvailableEncryption, load_pem_private_key)
ROOT=Path(__file__).resolve().parent
PRIV=ROOT/'owner_private_key.pem'; PUB=ROOT/'app_public_key.pem'
PLANS={'Mensual': {'days':30,'price_usd':10.0}, 'Trimestral': {'days':90,'price_usd':27.0}, 'Anual': {'days':365,'price_usd':99.0}}
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def init_keys():
    if PRIV.exists() or PUB.exists(): raise SystemExit('Ya existen claves; no se sobrescriben. Haz copia segura antes de cualquier rotación.')
    password=getpass.getpass('Contraseña fuerte para cifrar la clave privada (mín. 16 caracteres): ')
    if len(password)<16: raise SystemExit('Usa al menos 16 caracteres.')
    confirm=getpass.getpass('Repite la contraseña: ')
    if password!=confirm: raise SystemExit('Las contraseñas no coinciden.')
    k=Ed25519PrivateKey.generate()
    PRIV.write_bytes(k.private_bytes(Encoding.PEM,PrivateFormat.PKCS8,BestAvailableEncryption(password.encode())))
    PUB.write_bytes(k.public_key().public_bytes(Encoding.PEM,PublicFormat.SubjectPublicKeyInfo))
    try: PRIV.chmod(0o600); PUB.chmod(0o644)
    except OSError: pass
    print('Claves creadas. Mantén owner_private_key.pem cifrada y fuera del dispositivo del cliente. Distribuye solo la clave pública a la app.')
def show_plans(): print(json.dumps(PLANS,ensure_ascii=False,indent=2))
def issue(a):
    if not PRIV.exists(): raise SystemExit('Primero ejecuta init-keys.')
    customer=a.customer.strip(); device=a.device_id.strip(); plan=a.plan.strip()
    if not customer or len(customer)>160: raise SystemExit('Cliente debe tener entre 1 y 160 caracteres.')
    if len(device)<8 or len(device)>256: raise SystemExit('ID de dispositivo inválido (8–256 caracteres).')
    if not 1<=a.days<=3650: raise SystemExit('days debe estar entre 1 y 3650.')
    if not 0<=a.price<=1000000: raise SystemExit('price debe estar entre 0 y 1.000.000 USD.')
    password=getpass.getpass('Contraseña de la clave privada: ')
    try: key=load_pem_private_key(PRIV.read_bytes(),password=password.encode())
    except (ValueError, TypeError): raise SystemExit('No se pudo abrir la clave: contraseña incorrecta o archivo dañado.')
    if not isinstance(key,Ed25519PrivateKey): raise SystemExit('La clave privada no es Ed25519.')
    now=datetime.now(timezone.utc); payload={'license_id':'SP-'+secrets.token_hex(8).upper(),'customer':customer,'device_hash':hashlib.sha256(device.encode()).hexdigest(),'plan':plan,'price':{'amount':round(a.price,2),'currency':'USD'},'issued_at':now.isoformat(),'expires_at':(now+timedelta(days=a.days)).isoformat(),'schema':2}
    out={'payload':payload,'signature':base64.b64encode(key.sign(canonical(payload))).decode(),'algorithm':'Ed25519'}
    target=Path(a.out).resolve()
    if target.exists() and not a.force: raise SystemExit(f'El archivo ya existe: {target}; usa --force para reemplazarlo.')
    target.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    try: target.chmod(0o600)
    except OSError: pass
    print(f"Licencia creada: {payload['license_id']} — vence {payload['expires_at']} — {a.days} días")
    print('Envía únicamente el archivo de licencia como adjunto por email/WhatsApp. Nunca envíes la clave privada ni su contraseña.')
def main():
    p=argparse.ArgumentParser(description='Emisor local de licencias StockPro firmadas')
    sub=p.add_subparsers(dest='cmd',required=True); sub.add_parser('init-keys'); sub.add_parser('plans')
    q=sub.add_parser('issue'); q.add_argument('--customer',required=True); q.add_argument('--device-id',required=True); q.add_argument('--days',required=True,type=int); q.add_argument('--plan',required=True); q.add_argument('--price',required=True,type=float,help='Precio acordado en USD'); q.add_argument('--out',default='license.json'); q.add_argument('--force',action='store_true')
    a=p.parse_args()
    if a.cmd=='init-keys': init_keys()
    elif a.cmd=='plans': show_plans()
    else: issue(a)
if __name__=='__main__': main()
