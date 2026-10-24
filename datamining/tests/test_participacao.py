import pytest

from test_ingestao import api, fonte


def test_t12_t13_nao_avaliado_preserva_cadastro_sem_total(tmp_path, monkeypatch):
    rows = [{'Turma': 'T1', 'Estudante': f'PESSOA SINTETICA {i}', 'Avaliado': 'Sim' if i < 53 else 'Não',
             'H 01': '0/2' if i < 53 else ''} for i in range(54)]
    catalogo, _ = fonte(tmp_path, monkeypatch, rows=rows, year=5)
    result = api('ingestao', 'ler_exportacoes')(catalogo)
    assert len(result['matriculas']) == 54
    assert sum(a['participacao'] is True for a in result['avaliacoes']) == 53
    absent = next(a for a in result['avaliacoes'] if a['participacao'] is False)
    assert absent['acertos'] is None and absent['oportunidades'] is None
    h = next(h for h in result['habilidades'] if h['participacao'] is False)
    assert h['numerador'] is None and h['motivo_ausencia'] == 'nao_participacao'


def test_t14_zero_legitimo_disponivel():
    result = api('esquemas', 'medida')('0/2', 'acertos_itens', True)
    assert result['numerador'] == 0
    assert result['denominador'] == 2
    assert result['disponibilidade'] is True
    assert result['motivo_ausencia'] is None


@pytest.mark.parametrize('raw', ['', '-', '  - ', 'sem resultado'])
def test_t19_hifen_nao_vira_zero_nem_imputa_motivo(raw):
    result = api('esquemas', 'medida')(raw, 'nota_escrita', True)
    assert result['valor'] is None and result['numerador'] is None
    assert result['motivo_ausencia'] == 'resultado_ausente'
    assert result['participacao'] is True and result['disponibilidade'] is False
    assert result['bruto'] == raw


def test_tarefa_nao_aplicavel_e_distinta_de_resultado_ausente():
    result = api('esquemas', 'medida')(None, 'nota_escrita', True, aplicavel=False)
    assert result['motivo_ausencia'] == 'nao_aplicavel'
    assert result['aplicavel'] is False


def test_t18_contagens_fluencia_preservam_unidades():
    count = api('esquemas', 'medida')(' 17 de 60', 'palavras_total', True)
    assert (count['numerador'], count['denominador'], count['unidade']) == (17, 60, 'palavras_total')
    words = api('esquemas', 'medida')(' 87 - 95%', 'palavras_corretas', True)
    assert words['valor'] == 87 and words['percentual'] == 95
    assert words['denominador'] is None and words['unidade'] == 'palavras'
    assert words['duracao_segundos'] is None


@pytest.mark.parametrize('raw', ['3 de 2', '87 - 101%', '-1 - 50%', '87 - lixo'])
def test_fluencia_valor_invalido_rejeitado(raw):
    unit = 'palavras_total' if 'de' in raw else 'palavras_corretas'
    with pytest.raises(ValueError):
        api('esquemas', 'medida')(raw, unit, True)


def test_bom_turmma_escrita_e_ausencia_parcial(tmp_path, monkeypatch):
    row = {'Turmma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Participação': 'Sim',
           'Nota': '7.5', 'Categoria de escrita': 'Alto', 'Questão 1 - Aspecto 1': '-'}
    catalogo, _ = fonte(tmp_path, monkeypatch, component='ESCRITA', rows=[row], year=2)
    result = api('ingestao', 'ler_exportacoes')(catalogo)
    assert result['matriculas'][0]['turma'] == 'T1'
    assert result['matriculas'][0]['origens'][0]['coluna_turma_original'] == 'Turmma'
    assert result['escrita'][0]['valor'] == 7.5
    assert result['escrita'][1]['valor'] is None
    assert result['avaliacoes'][0]['participacao'] is True


def test_agregado_contagem_nao_pode_divergir_da_participacao(tmp_path, monkeypatch):
    rows = [{'Turmma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Participação': 'Não',
             'Nota': '-', 'Categoria de escrita': '-', 'Questão 1 - Aspecto 1': '-'}]
    catalogo, target = fonte(tmp_path, monkeypatch, component='ESCRITA', rows=rows, year=2)
    # Mantém o hash do catálogo atualizado para testar a reconciliação, não a guarda de hash.
    import hashlib
    path = target / 'ESCOLA.csv'
    raw = path.read_text(encoding='utf-8-sig').replace(';1;0;', ';1;1;')
    path.write_text(raw, encoding='utf-8-sig')
    next(c for c in catalogo if c['caminho'].endswith('ESCOLA.csv'))['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError):
        api('ingestao', 'ler_exportacoes')(catalogo)
