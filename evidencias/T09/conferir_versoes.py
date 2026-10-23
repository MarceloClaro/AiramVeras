"""Confronta saídas T09 sem publicar linhas individuais."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    'publico_01': ('estatistica/t09/versoes/analise01.json', '569d394e91bd5c99fecee1ed35dc32ddaf7c38c28f50868036eede3217689e9d'),
    'publico_02': ('estatistica/t09/checkpoint.json', '150592d325fde9c80bfd98717a974b3a53e816987601b1b3968168e558f14339'),
    'restrito_01': ('restrito/t09/versoes/analise01.json', '55d7e80d38dcbea5f0ebe32f51faf10e161b3ce6da671a9592cd1464fd310651'),
    'restrito_02': ('restrito/t09/checkpoint.json', '0e8359f648e3a4a01dce2a817d2fb7fb5397b31752a83c04ca2082f37cbc0901'),
}


def read_checked(name):
    relative, expected = FILES[name]
    raw = (ROOT / relative).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Hash de versao divergente: ' + name)
    return json.loads(raw)


def main():
    earlier_public, final_public = read_checked('publico_01'), read_checked('publico_02')
    earlier_private, final_private = read_checked('restrito_01'), read_checked('restrito_02')
    public_fields = ('cenarios', 'sensibilidade_meta_A', 'outros_instrumentos')
    private_fields = ('cenarios_individuais', 'outros_instrumentos')
    results = {key: earlier_public[key] == final_public[key] for key in public_fields}
    results.update({key + '_restrito': earlier_private[key] == final_private[key] for key in private_fields})
    results['gate_temporal_mudou'] = earlier_public['gate_temporal'] != final_public['gate_temporal']
    print(json.dumps(results, sort_keys=True))
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
