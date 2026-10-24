"""Identidade local provisória; nenhum erro ou log inclui chaves pessoais."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import unicodedata

QUALIDADE = 'local_provisorio_sem_id_institucional'
_ORIGEM = {'fonte_id', 'sha256', 'caminho', 'linha_fonte', 'exportacao',
           'sha256_exportacao', 'manifesto', 'sha256_manifesto', 'avaliacao_id',
           'ano_avaliacao', 'ciclo', 'ano_escolar', 'componente', 'origem_metadados',
           'coluna_turma_original', 'turma_bruto'}


def _normal(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Chave local incompleta')
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD', text)
                           if not unicodedata.combining(c)).upper().split())


def _validar_sem_nominais(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            label = _normal(str(key))
            if 'NOME' in label or 'ESTUDANTE' in label or label == 'MATRICULA_LOCAL_ID':
                raise ValueError('Campo nominal inesperado em saida pseudonimizada')
            _validar_sem_nominais(nested)
    elif isinstance(value, list):
        for nested in value:
            _validar_sem_nominais(nested)


def carregar_ou_criar_segredo(path: Path) -> bytes:
    """Cria uma única chave local de 32 bytes. Chamador mantém o caminho fora do Git.

    Arquivo inválido nunca é substituído. A execução real usa diretório fora do
    repositório; mode 0600 é aplicado onde suportado pelo sistema de arquivos.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError('Arquivo de segredo invalido')
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        secret = path.read_bytes()
    else:
        with os.fdopen(descriptor, 'wb') as stream:
            secret = secrets.token_bytes(32)
            stream.write(secret)
            stream.flush()
            os.fsync(stream.fileno())
    if len(secret) != 32:
        raise ValueError('Arquivo de segredo invalido')
    return secret


def vincular_localmente(matriculas: list[dict], secret: bytes) -> tuple[list[dict], list[dict]]:
    """HMAC-SHA256 de [domínio, escola, ano escolar, turma, nome normalizado].

    Retorna cadastro minimizado e mapa nominal restrito, na ordem de entrada.
    A referência transitória antiga só existe no segundo retorno. Nomes informados
    como normalizados são recalculados a partir do bruto para evitar divergência.
    """
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError('Segredo deve conter ao menos 32 bytes')
    public, private, keys, refs, pseudonyms = [], [], set(), set(), set()
    for row in matriculas:
        ref = row.get('matricula_local_id')
        if not isinstance(ref, str) or not ref.strip() or type(row.get('ano_escolar')) is not int:
            raise ValueError('Chave local incompleta')
        key = (_normal(row.get('escola_codigo')), row['ano_escolar'],
               _normal(row.get('turma')), _normal(row.get('nome_bruto')))
        if key in keys or ref in refs:
            raise ValueError('Duplicata de chave local ou referencia')
        keys.add(key)
        refs.add(ref)
        message = json.dumps(['airam-local-v1', *key], ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        identifier = hmac.new(secret, message, hashlib.sha256).hexdigest()
        if identifier in pseudonyms:
            raise ValueError('Colisao de pseudonimo local')
        pseudonyms.add(identifier)
        origins = [{k: deepcopy(v) for k, v in origin.items() if k in _ORIGEM}
                   for origin in row.get('origens', [])]
        public.append(dict(aluno_local_id=identifier, escola_codigo=key[0], ano_escolar=key[1],
                           turma=key[2], qualidade_vinculo=QUALIDADE, origens=origins))
        private.append(dict(**deepcopy(row), aluno_local_id=identifier))
    _validar_sem_nominais(public)
    return public, private


def pseudonimizar_tabelas(tabelas: dict[str, list[dict]], secret: bytes) -> tuple[dict, list[dict]]:
    """Substitui referências de matrícula; valida integridade matrícula/aplicação.

    Preserva integralmente valores, máscaras e proveniência das observações.
    Retorno pseudonimizado ainda é dado pessoal e deve permanecer restrito.
    """
    public, mapping = vincular_localmente(tabelas['matriculas'], secret)
    lookup = {r['matricula_local_id']: r['aluno_local_id'] for r in mapping}
    applications = {}
    for row in tabelas['avaliacoes']:
        app = row.get('avaliacao_local_id')
        if not app or app in applications or row.get('matricula_local_id') not in lookup:
            raise ValueError('Vinculo de aplicacao invalido')
        applications[app] = row['matricula_local_id']
    result = deepcopy(tabelas)
    result['matriculas'] = public
    for table in ['avaliacoes', 'habilidades', 'escrita', 'fluencia']:
        for row in result[table]:
            ref = row.pop('matricula_local_id', None)
            if ref not in lookup or applications.get(row.get('avaliacao_local_id')) != ref:
                raise ValueError('Vinculo de medida ou matricula invalido')
            row['aluno_local_id'] = lookup[ref]
            row['qualidade_vinculo'] = QUALIDADE
    _validar_sem_nominais(result)
    return result, mapping
