"""Preserva recibos minimizados existentes; não chama inferência nem muda Core."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source=ROOT.parent/'datamining/.superpowers/sdd/implementation-plan/core-2026-10-23-recibos.json'
    target=ROOT/'evidencias/bootstrap/core-2026-10-23-recibos.json'
    raw=source.read_bytes(); before=sha(source); target.write_bytes(raw)
    if not before==sha(source)==sha(target):raise ValueError('Recibo divergiu na copia')
    contract={'versao_schema':'airam-agentes-v1','primario':'marceloclaro',
        'perfis':[{'id':'plugin-data','configurado':True,'validado':True,'ativado':True,
            'recibo':{'caminho':'evidencias/bootstrap/core-execucao-minimizada.json',
                'sha256':sha(ROOT/'evidencias/bootstrap/core-execucao-minimizada.json')}},
            {'id':'caed-spaece-educacao-ceara','configurado':True,'validado':True,'ativado':True,
                'recibo':{'caminho':target.relative_to(ROOT).as_posix(),'sha256':sha(target)}}],
        'eventos_sessao':{'configurado':True,'estado':'contract_only'},
        'papeis':{'curadoria_fontes':'Codex local/T01-T04','estatistica_principal':'Codex local/T05-T09',
            'contraprova':'rotas independentes registradas T05-T09/T11',
            'vinculo_curricular':'Codex local/T04','revisao_entrega':'controlador; revisao independente T11 pendente'},
        'perfis_previstos_sem_inferencia_comprovada':['scientific-profile','scientific-review','red-history-final-audit'],
        'politica_dados':'Nenhum dado individual, inclusive pseudonimo, enviado ao Core/LLM externo.',
        'limites':['Inventario, validacao e ativacao A2A nao comprovam inferencia.',
            'Sondas TSPEC-4272ac13 e TSPEC-a6e24d1b bloqueadas com zero passos; nao repetidas.',
            'Hooks preflight/release da CLI sao processos locais; eventos globais permanecem contract_only.']}
    path=ROOT/'agents/contratos.json'; path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    cfgpath=ROOT/'config/analise.json'; cfg=json.loads(cfgpath.read_text(encoding='utf-8'))
    cfg['agentes']={'caminho':'agents/contratos.json','sha256':sha(path)}
    cfgpath.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'recibo_copiado_sha256':sha(target),'contratos_sha256':sha(path),'nova_inferencia':False}))


if __name__=='__main__': main()
