"""Create an encrypted backup of a local StockPro data export using Fernet.
Requires: pip install cryptography
Keep the key in a password manager or separate encrypted storage, never alongside backups.
"""
import argparse, os
from pathlib import Path
from cryptography.fernet import Fernet
p=argparse.ArgumentParser(); p.add_argument('input',help='JSON export from StockPro'); p.add_argument('output',help='Destination .spbackup'); p.add_argument('--key-file',required=True,help='Fernet key file kept separately'); a=p.parse_args()
key=Path(a.key_file)
if not key.exists():
    key.write_bytes(Fernet.generate_key()); os.chmod(key,0o600); print('Se creó una clave nueva. Guárdala por separado; sin ella no podrás recuperar la copia.')
f=Fernet(key.read_bytes()); data=Path(a.input).read_bytes(); Path(a.output).write_bytes(f.encrypt(data)); os.chmod(a.output,0o600); print('Copia cifrada creada:',a.output)
