"""Preserva resultado intermediario anterior a correcao aditiva de altura."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    source=ROOT/'evidencias/T10/layout-resultado.json'
    target=ROOT/'evidencias/T10/layout01-resultado.json'
    assert source.exists() and not target.exists()
    data=source.read_bytes();target.write_bytes(data)
    print(hashlib.sha256(data).hexdigest())
if __name__=='__main__':main()
