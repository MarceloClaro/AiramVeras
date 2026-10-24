/** Único autor XLSX T10. Dados pessoais entram e saem somente por arquivos locais. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const runtime=process.env.AIRAM_ARTIFACT_RUNTIME || path.join(root,'.superpowers/sdd/implementation-plan/runtime-probe');
// Resolução da entrada pública pelo node_modules oficial já ligado ao scratch.
const requireOfficial=createRequire(pathToFileURL(path.join(runtime,'entry.mjs')));
const {Workbook,SpreadsheetFile,FileBlob}=await import(pathToFileURL(requireOfficial.resolve('@oai/artifact-tool')).href);
const names=['Metas','Intervenção nominal','Habilidades','Grupos','Cálculos','Fontes e Auditoria'];
const START=8;
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const json=x=>JSON.stringify(x,null,2)+'\n';
const own=c=>['ESCRITA','FLUENCIA'].includes(c);
const safe=v=>typeof v==='string' && /^[=+@]/.test(v) ? "'"+v : v;
const plain=v=>v===null || v===undefined ? '' : typeof v==='object' ? JSON.stringify(v) : v;
const col=i=>{let x=i+1,s='';while(x){x--;s=String.fromCharCode(65+x%26)+s;x=Math.floor(x/26);}return s;};
const instrument=r=>r.instrumento || `${r.ano_escolar}|${r.componente}`;
let stage='validar';const started=performance.now();
function progress(value) {stage=value;console.log(JSON.stringify({etapa:value,segundos:Math.round((performance.now()-started)/1000),rss_mb:Math.round(process.memoryUsage().rss/1048576)}));}

function validate(data) {
  if(data.versao_schema!=='airam-workbook-t10-v1' || !data.intervencao.length) throw new Error('contrato');
  for(const c of ['A','B']) if(typeof data.metas[c]!=='number' || data.metas[c]<0 || data.metas[c]>1) throw new Error('meta');
  const keys=new Set();
  for(const r of data.intervencao) {
    if(!r.chave || keys.has(r.chave)) throw new Error('chave duplicada');keys.add(r.chave);
    if(!['LEITURA','MATEMATICA','ESCRITA','FLUENCIA'].includes(r.componente)) throw new Error('componente');
    if(!own(r.componente) && r.disponivel && (!Number.isInteger(r.acertos) || !Number.isInteger(r.oportunidades) || r.oportunidades<=0 || r.acertos<0 || r.acertos>r.oportunidades)) throw new Error('contagens');
    if(!r.participacao && r.disponivel) throw new Error('mascara');
  }
  const opportunities=new Set(data.intervencao.filter(r=>!own(r.componente)&&r.disponivel).map(r=>r.oportunidades));
  if(opportunities.size>1)throw new Error('Contrato T10 exige total de oportunidades comum autenticado; novo instrumento requer revisar contrato');
}

function writeTable(sheet,headers,rows,name,{width=18}={}) {
  const last=START+rows.length-1, end=col(headers.length-1);
  sheet.getRange(`A7:${end}7`).values=[headers];
  if(rows.length) sheet.getRange(`A${START}:${end}${last}`).values=rows.map(r=>r.map(x=>safe(plain(x))));
  const area=sheet.getRange(`A7:${end}${Math.max(7,last)}`);
  area.format.font={name:'Arial',size:10,color:'#243342'};
  area.format.rowHeight=24;area.format.columnWidth=width;area.format.verticalAlignment='center';
  sheet.getRange(`A7:${end}7`).format={fill:'#294F73',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:40};
  if(rows.length) {
    const table=sheet.tables.add(`A7:${end}${last}`,true,name);
    table.showFilterButton=true;table.showBandedColumns=false;
  }
  sheet.freezePanes.freezeRows(7);
  return last;
}

function fitRows(sheet,first,last,widths,matrix,uniform=false,padding=0) {
  // autofitRows encerra nativamente este runtime Windows (recibos diagnóstico01/02).
  // Alturas explícitas mantêm a fonte: estimativa conservadora por caracteres e quebras.
  if(last<first)return;
  const heights=matrix.map(row=>{
    let lines=1;
    row.forEach((v,c)=>{
      if(typeof v!=='string')return;
      const capacity=Math.max(8,Math.floor((widths[c]||18)*.8));
      lines=Math.max(lines,v.split('\n').reduce((total,line)=>total+Math.max(1,Math.ceil(line.length/capacity)),0));
    });
    if(lines*13+8+padding>409)throw new Error('conteudo requer celula mais larga');
    return Math.max(24,lines*13+8+padding);
  });
  if(uniform)sheet.getRange(`A${first}:${col(widths.length-1)}${last}`).format.rowHeight=Math.max(...heights);
  else heights.forEach((height,i)=>sheet.getRange(`A${first+i}:${col(widths.length-1)}${first+i}`).format.rowHeight=height);
}

function scaffold(wb) {
  for(const name of names) {
    const s=wb.worksheets.add(name);s.showGridLines=false;
    s.getRange('A2').values=[[name]];s.getRange('A2').format.font={name:'Arial',size:14,bold:true,color:'#243342'};
    s.getRange('A3:K3').format.borders={bottom:{style:'thin',color:'#B7C5D2'}};
    s.getRange('A4:K5').format.font={name:'Arial',size:10,color:'#52616E'};
  }
  wb.worksheets.getItem('Metas').tabColor='#294F73';
  wb.worksheets.getItem('Intervenção nominal').tabColor='#426D91';
}

function textPriorities(r) {
  return (r.habilidades_prioritarias||[]).map(h=>`${h.posicao}: ${h.acertos}/${h.oportunidades}`).join('; ');
}
function textLinks(r) {
  return (r.habilidades_prioritarias||[]).flatMap(h=>(h.vinculos||[]).map(v=>`${h.posicao}: ${v.codigo_caed} → ${v.codigo_bncc}; MEC p.${v.pagina_matriz}; ${v.status_contextual}; ${v.status_semantico}`)).join('\n');
}

function baseMatrix(rows,ties) {
  return rows.map(r=>[r.chave,r.nome,r.ano_escolar,r.turma,r.componente,r.participacao?1:0,r.categoria??'',
    r.acertos??'',r.oportunidades??'',r.disponivel?1:0,ties.get(r.chave),'','','','','',
    r.notas_docentes||'',r.revisao_docente||'pendente','','',textPriorities(r),textLinks(r),
    [...new Set((r.habilidades_prioritarias||[]).map(h=>h.atividade).filter(Boolean))].join('\n') || (own(r.componente)?'Revisar tarefas originais, registrar estratégia/apoio e nova medida comparável.':'Sondar estratégias e rever evidências individuais com o docente.'),
    own(r.componente)?(r.medidas||[]).map(m=>`${m.campo_original}: ${m.disponibilidade?m.valor:'ausente'} (${m.unidade})`).join('; '):'itens (acertos/oportunidades)',
    r.apoio_sugerido,r.fonte||r.caminho||r.fonte_id||'',r.linha_fonte??'',
    (r.grupos||[]).map(g=>`${g.grupo_id} (${g.tipo||'regra'}, ${g.versao})`).join('; '),
    'Identidade local provisória. Sem corte oficial de acertos para adequação. H agregada não identifica itens errados. BNCC documental não comprova domínio.',
    own(r.componente)?0:1,own(r.componente)?'unidade própria; metas não aplicáveis':r.disponivel?'itens observados':'prova ausente',
    '',instrument(r),'','','','']);
}

function baseFormulas(calc,n) {
  const last=START+n-1;
  const rng=c=>`$${c}$${START}:$${c}$${last}`;
  const formulas=[];
  for(let r=START;r<=last;r++) formulas.push([
    `=IF('Metas'!$B$8<>"válido","controle inválido",IF(AND(J${r}=1,AD${r}=1),CEILING(I${r}*'Metas'!$B$6,1),"n.a."))`,
    `=IF('Metas'!$B$8<>"válido","controle inválido",IF(AND(J${r}=1,AD${r}=1),MAX(0,L${r}-H${r}),"n.a."))`,
    `=IF('Metas'!$B$8<>"válido",9,IF(J${r}=0,0,IF(AD${r}=0,2,IF(M${r}>0,1,3))))`,
    `=IF(N${r}=1,IF('Metas'!$B$7=1,-M${r},M${r}),0)`,
    `=IF('Metas'!$B$8<>"válido",K${r},1+AI${r}+AJ${r}+AK${r})`
  ]);
  calc.getRange(`L${START}:P${last}`).formulas=formulas;
  const prior=[];
  for(let r=START;r<=last;r++)prior.push([
    `=IF(N${r}=0,0,COUNTIFS(${rng('J')},0)+IF(N${r}>=2,COUNTIFS(${rng('J')},1,${rng('AD')},1,${rng('H')},"<"&'Metas'!$D$6),0)+IF(N${r}=3,COUNTIFS(${rng('J')},1,${rng('AD')},0),0))`,
    `=IF(N${r}=1,IF('Metas'!$B$7=1,COUNTIFS(${rng('J')},1,${rng('AD')},1,${rng('H')},"<"&H${r}),COUNTIFS(${rng('J')},1,${rng('AD')},1,${rng('H')},">"&H${r},${rng('H')},"<"&'Metas'!$D$6)),0)`,
    `=IF(N${r}=0,COUNTIFS(${rng('J')},0,${rng('K')},"<"&K${r}),IF(N${r}=1,COUNTIFS(${rng('J')},1,${rng('AD')},1,${rng('H')},H${r},${rng('K')},"<"&K${r}),IF(N${r}=2,COUNTIFS(${rng('J')},1,${rng('AD')},0,${rng('K')},"<"&K${r}),COUNTIFS(${rng('J')},1,${rng('AD')},1,${rng('H')},">="&'Metas'!$D$6,${rng('K')},"<"&K${r}))))`
  ]);
  calc.getRange(`AI${START}:AK${last}`).formulas=prior;
  calc.getRange(`AF${START}:AF${last}`).formulas=Array.from({length:n},(_,i)=>[`=IF(AND(J${START+i}=1,AD${START+i}=1),H${START+i}/I${START+i},"n.a.")`]);
  calc.getRange(`AH${START}:AH${last}`).formulas=Array.from({length:n},(_,i)=>{
    const r=START+i;
    return [`=IF(R${r}<>"revisado","Revisão docente pendente",IF(S${r}="","Registrar apoio acordado",IF(T${r}="","Definir data de reavaliação","Acompanhar na data registrada")))`];
  });
}

function writeBase(wb,rows,ties) {
  const calc=wb.worksheets.getItem('Cálculos');const last=START+rows.length-1;
  const matrix=baseMatrix(rows,ties).map(r=>r.map(safe));
  // Permutação só dos inputs: os blocos calculados conservam fórmulas por linha.
  calc.getRange(`A${START}:K${last}`).values=matrix.map(r=>r.slice(0,11));
  calc.getRange(`Q${START}:AE${last}`).values=matrix.map(r=>r.slice(16,31));
  calc.getRange(`AG${START}:AG${last}`).values=matrix.map(r=>r.slice(32,33));
}

function displayNumber(value,rate=false) {
  if(value===null||value===undefined||typeof value!=='number'||!Number.isFinite(value))return 'não disponível';
  return new Intl.NumberFormat('pt-BR',{maximumFractionDigits:rate?2:3,useGrouping:false}).format(rate?value*100:value)+(rate?'%':'');
}
function distributionText(d,rate=false) {
  if(!d)return 'não disponível';
  return `N ${displayNumber(d.n)}; média ${displayNumber(d.media,rate)}; mediana ${displayNumber(d.mediana,rate)}; mínimo ${displayNumber(d.minimo,rate)}; máximo ${displayNumber(d.maximo,rate)}; p10 ${displayNumber(d.p10,rate)}`;
}
function groupSummary(g) {
  if(g.status_publicacao==='suprimido_n_menor_5')return 'Suprimido: N<5; estatísticas não publicadas. Atendimento individual não depende desse mínimo.';
  if(g.observado) {
    const o=g.observado;
    return `Somas observadas: ${displayNumber(o.acertos)} acertos / ${displayNumber(o.oportunidades)} oportunidades (itens). C/D ponderado: ${displayNumber(o.taxa,true)}.\n`+
      `Distribuição individual de acertos (itens): ${distributionText(o.distribuicao_acertos)}.\n`+
      `Distribuição individual de oportunidades (itens): ${distributionText(o.distribuicao_oportunidades)}.\n`+
      `Taxas individuais C/D: ${distributionText(o.distribuicao_taxas_individuais,true)}. Média individual e C/D ponderado são indicadores distintos. Ausências: ver Cobertura.`;
  }
  const measures=Array.isArray(g.medidas_proprias)?g.medidas_proprias:[];
  if(measures.length)return measures.slice(0,3).map(m=>`${m.campo_original} [${String(m.unidade||'unidade original').replaceAll('_',' ')}]: disponíveis ${displayNumber(m.disponiveis)}; ausentes ${displayNumber(m.ausentes)}; ${distributionText(m.distribuicao)}.`).join('\n')+
    (measures.length>3?`\nDemais ${measures.length-3} medidas: distribuições completas no relatório agregado, nas unidades originais e sem imputação.`:'');
  return 'Estatística não disponível; ausência preservada. Consultar Cobertura e relatório agregado.';
}

function applyPresentation(wb,data) {
  const last=START+data.intervencao.length-1;
  const meta=wb.worksheets.getItem('Metas'),calc=wb.worksheets.getItem('Cálculos'),queue=wb.worksheets.getItem('Intervenção nominal');
  meta.getRange('C5:C7').format.columnWidth=30;meta.getRange('C5:C7').format.wrapText=true;
  meta.getRange('C5:D7').format.rowHeight=36;
  meta.getRange('A9').values=[['As metas são independentes. Referência de 80% no instrumento: 18/22. O alvo do controle editado aparece em D6. Sem corte oficial em acertos para a Meta A.']];
  queue.getRange(`I7:I${last}`).format.columnWidth=36;queue.getRange(`I7:I${last}`).format.wrapText=true;
  // Este exportador nao produz hidden=true com largura zero. O formato Excel
  // padrao ;;; retira somente a exibicao, preservando valores/formulas auditaveis.
  queue.getRange(`Z7:Z${last}`).format.columnWidth=0;
  queue.getRange('Z7').values=[['']];
  queue.getRange(`Z${START}:Z${last}`).setNumberFormat(';;;');
  calc.getRange(`V7:V${last}`).format.columnWidth=70;calc.getRange(`V7:V${last}`).format.wrapText=true;
  queue.getRange(`O7:O${last}`).format.columnWidth=70;queue.getRange(`O7:O${last}`).format.wrapText=true;
  calc.getRange(`AB7:AB${last}`).format.columnWidth=70;queue.getRange(`W7:W${last}`).format.columnWidth=70;
  const ties=new Map(data.intervencao.map((r,i)=>[r.chave,i+1]));
  const matrix=baseMatrix(data.intervencao,ties);
  const notes=calc.getRange(`Q${START}:T${last}`).values;
  matrix.forEach((row,i)=>notes[i].forEach((v,c)=>row[16+c]=v));
  const nameWidth=Math.max(42,...data.intervencao.map(r=>String(r.nome).length+2));
  const cw=Array.from({length:37},(_,i)=>i===0?68:i===1?nameWidth:[21,27].includes(i)?70:i>=20?50:18);
  fitRows(calc,START,last,cw,matrix,true,20);
  const qi=[0,1,2,3,4,5,6,30,7,8,11,12,20,21,22,23,24,17,16,18,19,27,28,33];
  const qm=matrix.map((r,i)=>[i+1,...qi.map(c=>r[c])]);
  const qw=Array.from({length:25},(_,i)=>i===1?68:i===2?nameWidth:i===8?36:[14,22].includes(i)?70:i>=13?50:18);
  fitRows(queue,START,last,qw,qm,true,20);
  if(data.grupos.length) {
    const sheet=wb.worksheets.getItem('Grupos'),end=START+data.grupos.length-1;
    sheet.getRange(`G${START}:G${end}`).values=data.grupos.map(g=>[groupSummary(g)]);
    sheet.getRange(`G7:G${end}`).format.columnWidth=75;sheet.getRange(`G7:G${end}`).format.wrapText=true;
    const layout=sheet.getRange(`A${START}:M${end}`).values;
    fitRows(sheet,START,end,Array.from({length:13},(_,i)=>i===6?75:i>=6?55:28),layout,false,12);
  }
}

function build(data) {
  validate(data);progress('construir_abas');const wb=Workbook.create();scaffold(wb);
  const n=data.intervencao.length,last=START+n-1;
  const ties=new Map([...data.intervencao].sort((a,b)=>a.chave.localeCompare(b.chave,'en')).map((r,i)=>[r.chave,i+1]));
  const calc=wb.worksheets.getItem('Cálculos');
  calc.getRange('A4').values=[['Base por aplicação. Edite notas/revisão em Q:T, sempre na linha da chave. Fila apenas consulta essas células.']];
  calc.getRange('A5').values=[['Classes: 0 sem evidência, 1 lacuna B, 2 unidade própria E/F, 3 B atingida. Desempate pela chave estável, em todo o intervalo.']];
  const headers=['Chave da aplicação','Nome restrito','Ano','Turma','Componente','Participou (1/0)','Categoria CAEd original',
    'Acertos observados','Oportunidades','Resultado disponível (1/0)','Desempate por chave','Alvo B (itens)','Lacuna B (itens)',
    'Classe de prioridade','Critério secundário','Posição na fila','Notas docentes (editar)','Revisão docente (editar)',
    'Apoio acordado (editar)','Data de reavaliação (editar)','H prioritárias C/D','BNCC e ressalvas','Atividade sugerida',
    'Medidas e unidades originais','Apoio sugerido','Fonte local','Linha da fonte','Grupos revisáveis','Limites',
    'Instrumento de itens (1/0)','Estado da medida','C/D total observado','Contexto do instrumento','Próxima ação docente',
    'Precedentes por classe','Precedentes por necessidade','Precedentes por chave'];
  writeTable(calc,headers,baseMatrix(data.intervencao,ties),'BaseAplicacoes');
  baseFormulas(calc,n);
  calc.getRange(`Q${START}:T${last}`).format.fill='#FFF0BF';
  calc.getRange(`R${START}:R${last}`).dataValidation={rule:{type:'list',values:['pendente','em revisão','revisado']}};
  calc.getRange(`A7:A${last}`).format.columnWidth=30;calc.getRange(`B7:B${last}`).format.columnWidth=42;
  calc.getRange(`U7:AC${last}`).format.columnWidth=50;
  calc.getRange(`AF${START}:AF${last}`).setNumberFormat('0.0%');
  calc.getRange(`M${START}:M${last}`).conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0,format:{fill:'#FFF0D7',font:{color:'#824000'}}});
  calc.freezePanes.freezeColumns(2);
  const meta=wb.worksheets.getItem('Metas');
  meta.getRange('A4').values=[['Edite B5:B7 (âmbar). Meta A usa categoria CAEd original. Meta B só se aplica a leitura/matemática com itens.']];
  meta.getRange('A5:B7').values=[['Meta A',data.metas.A],['Meta B',data.metas.B],['Ordenação (1 necessidade, 2 proximidade)',1]];
  meta.getRange('A5:A7').format.columnWidth=30;meta.getRange('B5:B7').format.fill='#FFF0BF';
  meta.getRange('B5:B6').setNumberFormat('0.0%');
  meta.getRange('B7').dataValidation={rule:{type:'list',values:['1','2']}};
  meta.getRange('A8').values=[['Estado dos controles']];
  meta.getRange('B8').formulas=[['=IF(AND(ISNUMBER(B5),ISNUMBER(B6),ISNUMBER(B7),B5>=0,B5<=1,B6>=0,B6<=1,OR(B7=1,B7=2)),"válido","controle inválido")']];
  const opportunities=[...new Set(data.intervencao.filter(r=>!own(r.componente)&&r.disponivel).map(r=>r.oportunidades))];
  meta.getRange('C5:D7').values=[['Oportunidades originais',opportunities[0]??'n.a.'],['Alvo B (itens)',''],['Unidade','itens']];
  meta.getRange('D6').formulas=[['=IF(ISNUMBER(D5),CEILING(D5*$B$6,1),"n.a.")']];
  meta.getRange('A9').values=[['As duas metas são independentes. Meta B atual: 18/22. Sem corte oficial em acertos para a Meta A.']];
  meta.getRange('A10').values=[['Linhas escola/turma se sobrepõem. Não somar metas das turmas nem aplicações de componentes como estudantes distintos.']];
  const mh=['Ano','Componente','Nível','Turma','Contexto','Cadastros','Participantes','Com resultado','Adequados CAEd','Alvo A','Conversões A','Taxa A','Válidos B','Atingiram B','Soma lacunas B'];
  meta.getRange('A12:O12').values=[mh];
  meta.getRange('A12:O12').format={fill:'#294F73',font:{name:'Arial',size:10,color:'#FFFFFF',bold:true},wrapText:true,rowHeight:42};
  meta.getRange(`A13:O${12+data.componentes.length}`).format.columnWidth=18;
  const mr=[];
  for(let i=0;i<data.componentes.length;i++) {
    const ctx=data.componentes[i],r=13+i;
    meta.getRange(`A${r}:E${r}`).values=[[ctx.ano_escolar,ctx.componente,ctx.nivel||'escola',ctx.turma||'',instrument(ctx)]];
    const ranges=[`'Cálculos'!$AG$${START}:$AG$${last}`,'$E'+r];
    if(ctx.nivel==='turma') ranges.push(`'Cálculos'!$D$${START}:$D$${last}`,'$D'+r);
    const base=ranges.join(',');
    const count=(extra='')=>`COUNTIFS(${base}${extra?','+extra:''})`;
    const cr=c=>`'Cálculos'!$${c}$${START}:$${c}$${last}`;
    const lm=!own(ctx.componente);
    mr.push([
      '='+count(),'='+count(cr('F')+',1'),'='+count(cr('J')+',1'),
      lm?'='+count(cr('F')+',1,'+cr('G')+',"Adequado"'):'="n.a."',
      lm?`=IF($B$8<>"válido","controle inválido",IF(G${r}=0,"n.a.",CEILING(G${r}*$B$5,1)))`:'="n.a."',
      lm?`=IF($B$8<>"válido","controle inválido",IF(G${r}=0,"n.a.",MAX(0,J${r}-I${r})))`:'="n.a."',
      lm?`=IF(G${r}=0,"n.a.",I${r}/G${r})`:'="n.a."',
      lm?'='+count(cr('J')+',1,'+cr('AD')+',1'):'="n.a."',
      lm?`=IF($B$8<>"válido","controle inválido",${count(cr('J')+',1,'+cr('AD')+',1,'+cr('M')+',0')})`:'="n.a."',
      lm?`=IF($B$8<>"válido","controle inválido",SUMIFS(${cr('M')},${base},${cr('J')},1,${cr('AD')},1))`:'="n.a."'
    ]);
  }
  meta.getRange(`F13:O${12+data.componentes.length}`).formulas=mr;
  meta.getRange(`L13:L${12+data.componentes.length}`).setNumberFormat('0.0%');
  meta.getRange(`E12:E${12+data.componentes.length}`).format.columnWidth=30;
  meta.getRange(`B12:B${12+data.componentes.length}`).format.columnWidth=22;
  meta.getRange('A5:B8').format.font={name:'Arial',size:10};
  meta.getRange('A5:A8').format.columnWidth=45;
  meta.getRange('A7').format.wrapText=true;meta.getRange('A7:B7').format.rowHeight=36;
  meta.freezePanes.freezeRows(12);
  const queue=wb.worksheets.getItem('Intervenção nominal');
  queue.getRange('A4').values=[['Fila recalculada. Para registrar revisão, procure a chave em Cálculos e edite Q:T. Não escrever sobre as fórmulas da fila.']];
  queue.getRange('A5').values=[['Ausências pedem evidência; maiores lacunas permanecem no apoio. Meta A não possui distância individual oficial em acertos.']];
  const qh=['Ordem','Chave estável','Nome restrito','Ano','Turma','Componente','Participou (1/0)','Categoria original','Estado/unidade','Acertos','Oportunidades','Alvo B','Lacuna B','H prioritárias C/D','BNCC e ressalvas','Atividade sugerida','Medidas originais','Apoio sugerido','Revisão docente','Notas docentes','Apoio acordado','Data reavaliação','Grupos revisáveis','Limites','Próxima ação docente'];
  writeTable(queue,qh,Array.from({length:n},()=>qh.map(()=>'')),'FilaIntervencao');
  const sourceCols=['A','B','C','D','E','F','G','AE','H','I','L','M','U','V','W','X','Y','R','Q','S','T','AB','AC','AH'];
  const qm=[];
  queue.getRange(`Z7`).values=[['Índice da base (consulta por posição)']];
  queue.getRange(`Z${START}:Z${last}`).formulas=Array.from({length:n},(_,i)=>[`=MATCH(A${START+i},'Cálculos'!$P$${START}:$P$${last},0)`]);
  queue.getRange(`A${START}:A${last}`).values=Array.from({length:n},(_,i)=>[i+1]);
  for(let i=0;i<n;i++) {
    const r=START+i;
    const match=`$Z${r}`;
    qm.push(sourceCols.map(c=>{
      const ref=`INDEX('Cálculos'!$${c}$${START}:$${c}$${last},${match})`;
      return ['H','I','Q','S','T','U','V','AB'].includes(c)?`=IF(${ref}="","",${ref})`:'='+ref;
    }));
  }
  queue.getRange(`B${START}:Y${last}`).formulas=qm;
  queue.getRange(`C7:C${last}`).format.columnWidth=42;queue.getRange(`B7:B${last}`).format.columnWidth=30;
  queue.getRange(`N7:Y${last}`).format.columnWidth=50;queue.freezePanes.freezeColumns(3);
  const hs=wb.worksheets.getItem('Habilidades');
  hs.getRange('A4').values=[['Uma linha por medida original, sem fanout curricular. Valores ausentes ficam vazios; disponibilidade é explícita.']];
  hs.getRange('A5').values=[['Habilidade por contexto e posição. BNCC documental não comprova domínio. O alvo B é total, sem exigir 80% em cada H.']];
  const hheaders=['Chave da aplicação','Ano','Turma','Componente','Posição/campo','Valor observado','Oportunidades','Unidade original','Disponível (1/0)','CAEd','BNCC documental','Fonte local','Linha fonte','Ressalvas'];
  const hr=data.habilidades.map(r=>[r.chave,r.ano_escolar,r.turma,r.componente,r.posicao||r.campo_original,
    r.valor??r.numerador??'',r.denominador??'',r.unidade,r.disponibilidade?1:0,r.codigo_caed||'',r.bncc||'',r.fonte||r.caminho||'',r.linha_fonte??'',r.ressalvas||'']);
  writeTable(hs,hheaders,hr,'MedidasIndividuais');
  hs.getRange(`A7:A${Math.max(8,START+hr.length-1)}`).format.columnWidth=30;
  hs.getRange(`E7:E${Math.max(8,START+hr.length-1)}`).format.columnWidth=45;
  hs.getRange(`H7:H${Math.max(8,START+hr.length-1)}`).format.columnWidth=32;
  hs.getRange(`N7:N${Math.max(8,START+hr.length-1)}`).format.columnWidth=60;
  const gs=wb.worksheets.getItem('Grupos');
  gs.getRange('A4').values=[['Análises pré-calculadas T08: mudar metas não refaz grupos, correlações ou propagação. Reexecutar o pipeline com versão/hash.']];
  gs.getRange('A5').values=[['O/P com geometrias iguais em L1/L2/L3/L5/M2 e seleções distintas L1/L2: sensibilidade numérica, sem benefício curricular demonstrado.']];
  const gh=['Ano','Componente','Cenário/braço','Grupo revisável','N','Critério','Distribuição observada','Cobertura','Habilidades e currículo','Estabilidade','Reavaliação','Fontes/hash','Ressalvas'];
  const gr=data.grupos.map(g=>[g.contexto?.ano_escolar??'',g.contexto?.componente??'',g.recorte||g.tipo||'',g.titulo_perfil||g.nome||g.grupo_id,g.n??g.n_intervalo??'',g.criterio_pertencimento||'suprimido N<5',
    groupSummary(g),
    g.cobertura?`Células ${g.cobertura.celulas_disponiveis}/${g.cobertura.celulas_previstas}; ausentes ${g.cobertura.celulas_ausentes}; sem cobertura ${g.cobertura.alunos_sem_cobertura}`:'suprimida',
    (g.habilidades||[]).map(h=>`${h.posicao} ${h.acertos}/${h.oportunidades}; ${(h.curriculo||[]).map(c=>c.codigo_bncc).join(', ')}`).join('\n')||'Unidades próprias ou detalhes suprimidos',
    g.estabilidade?['seeds','subamostras'].map(k=>`${k}: ${g.estabilidade[k]?.avaliaveis}/${g.estabilidade[k]?.planejadas}; Jaccard mediana ${g.estabilidade[k]?.jaccard?.mediana?.toFixed(3)}, p10 ${g.estabilidade[k]?.jaccard?.p10?.toFixed(3)}; dissoluções ${g.estabilidade[k]?.dissolucoes}`).join('\n'):'Sem seleção estável ou grupo por regra/categoria; ver contexto no relatório',
    g.reavaliacao?.gatilho||'Revisão docente pendente',(g.fontes_sha256||[]).join('\n'),
    'Geometrias iguais O/P em L1/L2/L3/L5/M2; seleções distintas L1/L2. Causa específica não isolada. Sem benefício curricular demonstrado. Detalhes integrais no relatório agregado T10.']);
  writeTable(gs,gh,gr,'PerfisRevisaveis',{width:28});
  const sources=wb.worksheets.getItem('Fontes e Auditoria');
  sources.getRange('A4').values=[['FONTES (entrada). Identidade local provisória. Sem validação temporal/pedagógica externa. Armazenamento não certifica ACL.']];
  sources.getRange('A5').values=[['Versões e hashes identificam análises pré-calculadas. Atualização de dados/grupos/BNCC exige reexecução; não é fórmula Excel.']];
  const sr=Object.entries(data.fontes).map(([k,v])=>[k,typeof v==='string'?v:JSON.stringify(v)]);
  const sl=writeTable(sources,['Fonte/versão','SHA256/contrato'],sr,'FontesInput',{width:46});
  sources.getRange(`B7:B${sl}`).format.columnWidth=90;
  const curricularStart=sl+4;
  sources.getRange(`A${curricularStart-1}`).values=[['FONTES CURRICULARES (entrada). Contexto/versão/ocorrência explícitos; associação não é domínio BNCC.']];
  const ch=['Ano avaliado','Componente','Posição','CAEd','Descritor CAEd','BNCC','Texto BNCC','Página MEC','Localizador BNCC','Estado contextual','Ressalva semântica','Peso documental','SHA PDF','Ocorrência PDF','Fonte mapa','Versão mapa','Versão BNCC'];
  const cv=(data.curriculo||[]).map(v=>[v.ano_avaliado,v.componente,v.posicao,v.codigo_caed,v.texto_caed,v.codigo_bncc,v.texto_bncc,
    v.pagina_matriz,JSON.stringify(v.localizador_bncc),v.status_contextual,v.status_semantico,v.peso_analitico,v.sha256_pdf,v.ocorrencia_id,v.fonte_posicao,v.versao_posicao,JSON.stringify(v.bncc?.proveniencia_dataset||{})]);
  sources.getRange(`A${curricularStart}:Q${curricularStart}`).values=[ch];
  sources.getRange(`A${curricularStart}:Q${curricularStart}`).format={fill:'#294F73',font:{name:'Arial',size:10,color:'#FFFFFF',bold:true},wrapText:true,rowHeight:40};
  if(cv.length){
    sources.getRange(`A${curricularStart+1}:Q${curricularStart+cv.length}`).values=cv.map(row=>row.map(safe));
    sources.tables.add(`A${curricularStart}:Q${curricularStart+cv.length}`,true,'CurriculoInput');
  }
  const audit=curricularStart+cv.length+4;
  sources.getRange(`A${audit}`).values=[['AUDITORIA (terminal; não alimenta cálculos)']];
  sources.getRange(`A${audit+1}:B${audit+3}`).values=[['Aplicações esperadas',n],['Unidades próprias sem meta de itens','Escrita/Fluência'],['Atualização complexa','Reexecutar pipeline; análise externa ao Excel']];
  sources.getRange(`A${audit+4}`).values=[['Aplicações na base']];
  sources.getRange(`B${audit+4}`).formulas=[[`=COUNTA('Cálculos'!$A$${START}:$A$${last})`]];
  sources.getRange(`A${audit+6}`).values=[['Limites']];
  for(let i=0;i<data.limites.length;i++) sources.getRange(`A${audit+7+i}`).values=[[data.limites[i]]];
  sources.getRange(`A${audit+7}:A${audit+7+data.limites.length}`).format.columnWidth=90;
  // Ajuste por conteúdo: descrições permanecem em células legíveis, sem fonte reduzida.
  progress('ajuste_calculos');
  calc.getRange(`A7:A${last}`).format.columnWidth=68;
  calc.getRange(`B7:B${last}`).format.columnWidth=Math.max(42,...data.intervencao.map(r=>String(r.nome).length+2));
  progress('calculos_wrap');
  calc.getRange(`U${START}:AH${last}`).format.wrapText=true;
  const layoutMatrix=baseMatrix(data.intervencao,ties);
  fitRows(calc,START,last,headers.map((_,i)=>i===0?68:i===1?Math.max(42,...data.intervencao.map(r=>String(r.nome).length+2)):i>=20?50:18),layoutMatrix);
  progress('ajuste_fila');
  queue.getRange(`B7:B${last}`).format.columnWidth=68;
  queue.getRange(`C7:C${last}`).format.columnWidth=Math.max(42,...data.intervencao.map(r=>String(r.nome).length+2));
  queue.getRange(`N${START}:Y${last}`).format.wrapText=true;
  const index=c=>[...c].reduce((a,ch)=>a*26+ch.charCodeAt(0)-64,0)-1;
  const queueLayout=layoutMatrix.map((r,i)=>[i+1,...sourceCols.map(c=>r[index(c)])]);
  fitRows(queue,START,last,qh.map((_,i)=>i===1?68:i===2?Math.max(42,...data.intervencao.map(r=>String(r.nome).length+2)):i>=13?50:18),queueLayout,true);
  if(hr.length) {
    progress('ajuste_habilidades');
    hs.getRange(`A7:A${START+hr.length-1}`).format.columnWidth=68;
    hs.getRange(`E${START}:N${START+hr.length-1}`).format.wrapText=true;
    fitRows(hs,START,START+hr.length-1,hheaders.map((_,i)=>i===0?68:i===4?45:i===7?32:i===13?60:18),hr);
  }
  if(gr.length) {
    progress('ajuste_grupos');
    gs.getRange(`C${START}:M${START+gr.length-1}`).format.wrapText=true;
    gs.getRange(`G7:M${START+gr.length-1}`).format.columnWidth=55;
    fitRows(gs,START,START+gr.length-1,gh.map((_,i)=>i>=6?55:28),gr);
  }
  sources.getRange(`A${curricularStart+1}:Q${curricularStart+cv.length}`).format.font={name:'Arial',size:10};
  progress('ajuste_fontes');
  sources.getRange(`C${curricularStart}:Q${curricularStart+cv.length}`).format.columnWidth=35;
  sources.getRange(`E${curricularStart}:E${curricularStart+cv.length}`).format.columnWidth=65;
  sources.getRange(`G${curricularStart}:G${curricularStart+cv.length}`).format.columnWidth=85;
  sources.getRange(`I${curricularStart}:I${curricularStart+cv.length}`).format.columnWidth=75;
  sources.getRange(`A${curricularStart+1}:Q${curricularStart+cv.length}`).format.wrapText=true;
  fitRows(sources,curricularStart+1,curricularStart+cv.length,ch.map((_,i)=>i===0?46:i===1?90:i===4?65:i===6?85:i===8?75:35),cv);
  sources.getRange(`A${audit+7}:A${audit+7+data.limites.length}`).format.wrapText=true;
  fitRows(sources,audit+7,audit+6+data.limites.length,[90],data.limites.map(v=>[v]));
  applyPresentation(wb,data);
  return {wb,ties,last,base:calc,queue,meta,hr,audit,curricularStart};
}

function queueValues(state) { return state.queue.getRange(`B${START}:B${state.last}`).values.map(r=>r[0]); }
function gaps(state,rows) {
  const values=state.base.getRange(`M${START}:M${state.last}`).values;
  return Object.fromEntries(rows.map((r,i)=>[r.chave,typeof values[i][0]==='number'?values[i][0]:null]));
}
function queueNotes(state,keys) {
  const matrix=state.queue.getRange(`T${START}:T${state.last}`).values;
  return Object.fromEntries(keys.map((key,i)=>[key,matrix[i][0]||'']));
}
function expectedOrder(rows,target,mode) {
  // Referência independente da fórmula: comparação direta de tuplas, sem COUNTIFS/rank.
  const tuple=r=>{const lm=!own(r.componente),gap=lm&&r.disponivel?Math.max(0,Math.ceil(r.oportunidades*target-1e-12)-r.acertos):null;
    const cls=!r.disponivel?0:lm?(gap>0?1:3):2;return [cls,cls===1?(mode===1?-gap:gap):0,r.chave];};
  return [...rows].sort((a,b)=>{const x=tuple(a),y=tuple(b);return x[0]-y[0] || x[1]-y[1] || x[2].localeCompare(y[2],'en');}).map(r=>r.chave);
}
function assertEqual(a,b,label){if(JSON.stringify(a)!==JSON.stringify(b))throw new Error('contraprova '+label);}
function formulaErrors(wb,sheets=names,address=null) {
  const issues=[];
  for(const name of sheets) {
    const sheet=wb.worksheets.getItem(name),range=address?sheet.getRange(address):sheet.getUsedRange();
    const values=range.values,formulas=range.formulas;
    for(let r=0;r<values.length;r++)for(let c=0;c<values[r].length;c++) {
      if(formulas[r]?.[c] && typeof values[r][c]==='string' && /^#(?:REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!|SPILL!|CALC!)/.test(values[r][c]))issues.push([name,r,c]);
    }
  }
  return issues;
}
async function verify(state,data) {
  // Escritas recalculam dependências automaticamente (API pública). O recálculo
  // integral inicial/final é explícito; os ensaios leem resultados das alterações.
  progress('verificar_formulas');
  stage='recalcular';const {wb,meta,base}=state;wb.recalculate();
  progress('verificar_ordem_base');
  const initial=queueValues(state);assertEqual(initial,expectedOrder(data.intervencao,data.metas.B,1),'ordem base');
  progress('verificar_notas_base');
  const notesInitial=queueNotes(state,initial);
  const initialGaps=gaps(state,data.intervencao);
  for(const r of data.intervencao) {
    const expected=!own(r.componente)&&r.disponivel?Math.max(0,Math.ceil(r.oportunidades*data.metas.B-1e-12)-r.acertos):null;
    if(initialGaps[r.chave]!==expected) throw new Error('contraprova lacuna');
  }
  progress('verificar_meta50');
  meta.getRange('B6').values=[[.5]];const half=queueValues(state);
  assertEqual(half,expectedOrder(data.intervencao,.5,1),'meta alterada');
  progress('verificar_proximidade');
  meta.getRange('B5:B7').values=[[data.metas.A],[data.metas.B],[2]];const near=queueValues(state);
  assertEqual(near,expectedOrder(data.intervencao,data.metas.B,2),'proximidade');
  meta.getRange('B7').values=[[1]];
  progress('verificar_permutacao');
  const reversedRows=[...data.intervencao].reverse();
  writeBase(wb,reversedRows,state.ties);const reverse=queueValues(state);
  assertEqual(reverse,initial,'ordem fisica reversa');
  progress('verificar_notas_permutadas');
  const notesReverse=queueNotes(state,reverse);
  assertEqual(notesReverse,notesInitial,'notas na fila por chave');
  const noteValues=base.getRange(`Q${START}:Q${state.last}`).values;
  const notes=Object.fromEntries(reversedRows.map((r,i)=>[r.chave,noteValues[i][0]||'']));
  const notesOK=data.intervencao.every(r=>notes[r.chave]===(r.notas_docentes||''));
  if(!notesOK) throw new Error('notas desvinculadas');
  progress('restaurar_base');writeBase(wb,data.intervencao,state.ties);
  // Meta A também reage ao controle e mantém categoria original, sem derivar corte em itens.
  progress('verificar_metaA');const beforeA=meta.getRange(`J13:J${12+data.componentes.length}`).values;
  meta.getRange('B5').values=[[.5]];
  const afterA=meta.getRange(`J13:J${12+data.componentes.length}`).values;
  const counts=meta.getRange(`G13:G${12+data.componentes.length}`).values;
  data.componentes.forEach((c,i)=>{if(!own(c.componente)&&counts[i][0]>0&&afterA[i][0]!==Math.ceil(counts[i][0]*.5))throw new Error('meta A');});
  meta.getRange('B5').values=[[data.metas.A]];
  assertEqual(meta.getRange(`J13:J${12+data.componentes.length}`).values,beforeA,'restauracao A');
  progress('verificar_controles_invalidos');let invalidOK=true;
  for(const [cell,value] of [['B5',''],['B6',''],['B6',1.1],['B7',0]]) {
    meta.getRange(cell).values=[[value]];
    invalidOK &&= meta.getRange('B8').values[0][0]==='controle inválido';
    invalidOK &&= base.getRange(`L${START}:L${state.last}`).values.every(r=>r[0]==='controle inválido');
    meta.getRange('B5:B7').values=[[data.metas.A],[data.metas.B],[1]];
  }
  // Zero é um controle permitido; vazio deve permanecer inválido.
  meta.getRange('B6').values=[[0]];
  invalidOK &&= meta.getRange('B8').values[0][0]==='válido';
  meta.getRange('B6').values=[[data.metas.B]];
  if(!invalidOK)throw new Error('controles invalidos ocultos');
  progress('verificar_fluxo_docente');const saved=base.getRange(`R${START}:T${START}`).values;
  base.getRange(`R${START}:T${START}`).values=[['revisado','','']];
  const step1=base.getRange(`AH${START}`).values[0][0];
  base.getRange(`S${START}`).values=[['Apoio artificial']];
  const step2=base.getRange(`AH${START}`).values[0][0];
  base.getRange(`T${START}`).values=[['2026-11-01']];
  const step3=base.getRange(`AH${START}`).values[0][0];
  const workflowOK=step1==='Registrar apoio acordado'&&step2==='Definir data de reavaliação'&&step3==='Acompanhar na data registrada';
  base.getRange(`R${START}:T${START}`).values=saved;
  if(!workflowOK)throw new Error('fluxo docente incompleto');
  const sourceSheet=wb.worksheets.getItem('Fontes e Auditoria');
  const curriculum=data.curriculo||[];
  if(curriculum.length) {
    const recovered=sourceSheet.getRange(`D${state.curricularStart+1}:I${state.curricularStart+curriculum.length}`).values;
    curriculum.forEach((v,i)=>assertEqual(recovered[i],[v.codigo_caed,v.texto_caed,v.codigo_bncc,v.texto_bncc,v.pagina_matriz,JSON.stringify(v.localizador_bncc)],'fonte curricular'));
  }
  stage='inspecionar';
  // Contraprova de que o detector encontra uma falha real, antes de limpar a célula.
  progress('verificar_detector_erros');
  meta.getRange('Z1').formulas=[['=1/0']];
  const detectorOK=formulaErrors(wb,['Metas'],'Z1').length===1;
  meta.getRange('Z1').clear({applyTo:'contents'});
  progress('verificar_erros_todas_abas');
  if(!detectorOK || formulaErrors(wb).length)throw new Error('detector de erros');
  progress('inspecionar_api_publica');
  const inspected=await wb.inspect({kind:'table',range:`'Metas'!F12:O${Math.min(18,12+data.componentes.length)}`,include:'values,formulas',tableMaxRows:7,tableMaxCols:10,maxChars:2500});
  const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:3000});
  // Inspeções ficam em memória: só hashes/contagens saem do builder.
  if(/"(?:value|text|displayValue)"\s*:\s*"#(?:REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!|SPILL!|CALC!)/.test(errors.ndjson))throw new Error('erro de formula');
  return {ordem_inicial:initial,lacunas_iniciais:initialGaps,ordem_meta50:half,ordem_proximidade:near,
    ordem_reversa:reverse,nota_permanece_com_chave:notesOK,inspecao_sha256:hash(inspected.ndjson),erros_scan_sha256:hash(errors.ndjson),
    notas_fila_inicial:notesInitial,notas_fila_reversa:notesReverse,controles_invalidos_expostos:invalidOK,
    fontes_curriculares_conferidas:curriculum.length,fluxo_pre_requisitos_verificado:workflowOK,
    detector_erros_comprovado:detectorOK,
    controle_A_alterado_restaurado:true,controle_B_alterado_restaurado:true,ordenacao_alterada_restaurada:true};
}

function syntheticData(data) {
  // Somente comprimentos máximos saem das linhas reais. Nenhum escore, H,
  // pertencimento, identidade, nota ou fonte individual é copiado para a prévia.
  const maior_nome=Math.max(17,...data.intervencao.map(r=>String(r.nome).length));
  const noteLength=Math.max(14,...data.intervencao.map(r=>String(r.notas_docentes||'').length));
  const components=['LEITURA','LEITURA','MATEMATICA','MATEMATICA','ESCRITA','ESCRITA','FLUENCIA','FLUENCIA'];
  const rows=components.map((componente,i)=>({
    chave:('ARTIFICIAL'+String(i+1).padStart(3,'0')).padEnd(64,'X'),
    nome:'PESSOA ARTIFICIAL'.padEnd(maior_nome,'X'),ano_escolar:2,turma:'ARTIFICIAL',componente,
    participacao:i!==7,disponivel:i!==7,categoria:i%2?'Adequado':'Abaixo',
    acertos:i<4?i*3:null,oportunidades:i<4?22:null,
    habilidades_prioritarias:i<4?[{posicao:'H01',acertos:0,oportunidades:2,vinculos:[],atividade:'ATIVIDADE ARTIFICIAL'}]:[],
    medidas:own(componente)?[{campo_original:'TAREFA ARTIFICIAL',valor:i%3,unidade:'unidade artificial',disponibilidade:i!==7}]:[],
    grupos:[],notas_docentes:'ARTIFICIAL'.padEnd(noteLength,'X'),revisao_docente:'pendente',
    apoio_sugerido:'APOIO ARTIFICIAL',fonte:'ARTIFICIAL',linha_fonte:1,instrumento:'ARTIFICIAL-'+componente
  }));
  const habilidades=rows.flatMap((r,i)=>Array.from({length:2},()=>({chave:r.chave,ano_escolar:2,turma:'ARTIFICIAL',
    componente:r.componente,posicao:'H01',valor:r.disponivel?i%3:null,denominador:r.disponivel?2:null,unidade:own(r.componente)?'unidade artificial':'itens',
    disponibilidade:r.disponivel,codigo_caed:'ARTIFICIAL',bncc:'ARTIFICIAL',fonte:'ARTIFICIAL',linha_fonte:1,ressalvas:'DADOS ARTIFICIAIS'})));
  return {versao_schema:data.versao_schema,metas:data.metas,fontes:data.fontes,limites:data.limites,
    grupos:data.grupos,curriculo:data.curriculo,complexos:data.complexos,
    sintetico:true,intervencao:rows,habilidades,maior_nome,
    componentes:components.filter((c,i)=>components.indexOf(c)===i).map(componente=>({ano_escolar:2,componente,nivel:'escola',turma:null,instrumento:'ARTIFICIAL-'+componente}))};
}

function previewPayload(data) {
  const artificial=syntheticData(data);
  // Teste visual de comprimentos extremos: letras substituídas por X, preservando
  // somente comprimento/quebras dos textos; vínculo com qualquer aluno é descartado.
  const ties=new Map(data.intervencao.map((r,i)=>[r.chave,i+1]));
  const actualMatrix=baseMatrix(data.intervencao,ties);
  const sentence='Frase inteiramente fictícia para verificar espaço e quebra. ';
  artificial.comprimentos_artificiais={};
  artificial.regra_texto_artificial='frase-ficticia-v1';
  for(const c of [20,21,22,23,24,25,27,28]) {
    const longest=actualMatrix.map(row=>String(row[c]||'')).sort((a,b)=>b.length-a.length)[0]||'';
    artificial.comprimentos_artificiais[c]=longest.split('\n').map(line=>sentence.repeat(Math.ceil(line.length/sentence.length)).slice(0,line.length)).join('\n');
  }
  return artificial;
}

function prepareArtificial(artificial) {
  if(artificial.sintetico!==true || !artificial.comprimentos_artificiais)throw new Error('Previa precisa de contrato artificial');
  progress('renderizar_sintetico');
  const previewState=build(artificial),{wb,base}=previewState;
  const artificialMatrix=baseMatrix(artificial.intervencao,previewState.ties);
  for(const [index,artificialText] of Object.entries(artificial.comprimentos_artificiais)) {
    const c=Number(index);
    base.getRange(`${col(c)}${START}:${col(c)}${previewState.last}`).values=[[artificialText]];
    artificialMatrix.forEach(row=>row[c]=artificialText);
  }
  fitRows(base,START,previewState.last,Array.from({length:37},(_,i)=>i===0?68:i===1?artificial.maior_nome+2:[21,27].includes(i)?70:i>=20?50:18),artificialMatrix,true,20);
  const q=wb.worksheets.getItem('Intervenção nominal');
  const qi=[0,1,2,3,4,5,6,30,7,8,11,12,20,21,22,23,24,17,16,18,19,27,28,33];
  const qlayout=artificialMatrix.map((r,i)=>[i+1,...qi.map(c=>r[c])]);
  fitRows(q,START,previewState.last,Array.from({length:25},(_,i)=>i===1?68:i===2?artificial.maior_nome+2:i===8?36:[14,22].includes(i)?70:i>=13?50:18),qlayout,true,20);
  for(const sheetName of ['Cálculos','Intervenção nominal','Habilidades'])
    wb.worksheets.getItem(sheetName).getRange('A4').values=[['PRÉVIA ARTIFICIAL: identidades, observações, H, pertencimento e notas gerados por regra explícita.']];
  wb.recalculate();return {wb,previewState};
}

async function renderArtificial(artificial,out) {
  const {wb,previewState}=prepareArtificial(artificial);await fs.mkdir(out,{recursive:true});
    const views=[['Metas','A2:D7'],['Metas','A12:D23'],['Metas','F12:O23'],
      ['Intervenção nominal','A2:G17'],['Intervenção nominal','H7:M17'],['Intervenção nominal','N7:Q11'],['Intervenção nominal','R7:Y11'],
      ['Habilidades','A2:I17'],['Habilidades','J7:N14'],['Grupos','A2:F14'],['Grupos','G7:M11'],
      ['Cálculos','A2:J17'],['Cálculos','K7:T17'],['Cálculos','U7:AH11'],['Fontes e Auditoria','A2:B18'],
      ['Fontes e Auditoria',`D${previewState.curricularStart}:K${previewState.curricularStart+3}`]];
    for(let i=0;i<views.length;i++) {
      const [sheetName,range]=views[i];const preview=await wb.render({sheetName,range,scale:1.4,format:'png'});
      await fs.writeFile(path.join(out,`${String(i+1).padStart(2,'0')}-${sheetName.replaceAll(' ','-')}.png`),new Uint8Array(await preview.arrayBuffer()));
    }
  return views.length;
}

async function preparePreview(data,out) {
  const folder=path.join(out,'previas-sinteticas');await fs.mkdir(folder,{recursive:true});
  const input=path.join(folder,'entrada-artificial.json');
  const artificial=previewPayload(data);await fs.writeFile(input,json(artificial));
  const {wb}=prepareArtificial(artificial);
  const destination=path.join(folder,'inspecao-artificial.xlsx');
  const blob=await SpreadsheetFile.exportXlsx(wb);await blob.save(destination);
  return {isolada_sem_dados_individuais_reais:true,status:'preparada_sem_render_local',
    tentativa_automatica:false,codigo_saida:null,imagens:0,esperadas:16,
    copia_artificial_sha256:hash(await fs.readFile(destination)),
    entrada_artificial_sha256:hash(await fs.readFile(input)),
    limite:'Renderer Windows indisponivel (render-minimo01/02, 0xC0000005). Nao repetido. Copia artificial pronta para leitor alternativo; inspecao visual pendente.'};
}

async function refineLayout(data,source,out) {
  validate(data);progress('importar_para_ajuste_visual');
  const inputHash=hash(await fs.readFile(source));
  const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
  const previousControls=wb.worksheets.getItem('Metas').getRange('B5:B8').values;
  const rows=[START,Math.floor((START+data.intervencao.length-1)/2),START+data.intervencao.length-1];
  const previousFormulas=rows.map(r=>wb.worksheets.getItem('Cálculos').getRange(`L${r}:P${r}`).formulas);
  progress('ajustar_apresentacao');applyPresentation(wb,data);wb.recalculate();
  await fs.mkdir(out,{recursive:true});
  const target=path.join(out,'intervencao-restrita.xlsx');
  if(path.resolve(source)===path.resolve(target))throw new Error('Preservar original antes do ajuste');
  progress('exportar_ajuste_visual');const blob=await SpreadsheetFile.exportXlsx(wb);await blob.save(target);
  progress('reabrir_ajuste_visual');const reopened=await SpreadsheetFile.importXlsx(await FileBlob.load(target));reopened.recalculate();
  assertEqual(reopened.worksheets.getItem('Metas').getRange('B5:B8').values,previousControls,'controles no ajuste');
  assertEqual(rows.map(r=>reopened.worksheets.getItem('Cálculos').getRange(`L${r}:P${r}`).formulas),previousFormulas,'formulas amostradas no ajuste');
  const report={status:'exportado_reaberto',escopo:'Somente estilos e resumos agregados Grupos!G; invariancia integral conferida independentemente fora do autor.',
    origem_sha256:inputHash,xlsx_sha256:hash(await fs.readFile(target)),builder_sha256:hash(await fs.readFile(fileURLToPath(import.meta.url))),
    controles_preservados:true,formulas_amostradas_preservadas:true,aplicacoes:data.intervencao.length};
  await fs.writeFile(path.join(out,'layout-verificacao.json'),json(report));
  if(data.sintetico!==true)await fs.writeFile(path.join(root,'evidencias/T10/layout-resultado.json'),json(report));
  console.log(JSON.stringify(report));
}

async function main() {
  const [mode,input,out,extra]=process.argv.slice(2);const inputBytes=await fs.readFile(input);const data=JSON.parse(inputBytes.toString('utf8'));
  if(mode==='--refine-layout') {await refineLayout(data,out,extra);return;}
  if(mode==='--render-artificial') {await renderArtificial(data,out);return;}
  if(!['--build','--verify-fixture','--prepare-artificial'].includes(mode))throw new Error('Modo desconhecido');
  const authorHash=hash(await fs.readFile(fileURLToPath(import.meta.url)));
  data.fontes['autoria/builder_js_sha256']=authorHash;
  data.fontes['autoria/entrada_checkpoint_sha256']=hash(inputBytes);
  if(mode==='--prepare-artificial') {console.log(JSON.stringify(await preparePreview(data,out)));return;}
  if(mode==='--verify-fixture' && data.sintetico!==true) throw new Error('fixture deve ser sintetica');
  const state=build(data);const report=await verify(state,data);
  const artificial=syntheticData(data);
  report.previa_sem_observacoes_individuais_reais=true;
  if(mode==='--verify-fixture')report.amostra_previa_artificial={intervencao:artificial.intervencao,habilidades:artificial.habilidades,maior_nome:artificial.maior_nome};
  await fs.mkdir(out,{recursive:true});
  progress('recalcular_exportacao');state.wb.recalculate();
  const destination=path.join(out,mode==='--verify-fixture'?'fixture.xlsx':'intervencao-restrita.xlsx');
  progress('exportar');const xlsx=await SpreadsheetFile.exportXlsx(state.wb);await xlsx.save(destination);
  progress('reabrir');const reopened=await SpreadsheetFile.importXlsx(await FileBlob.load(destination));reopened.recalculate();
  const qs=reopened.worksheets.getItem('Intervenção nominal').getRange(`B${START}:B${state.last}`).values.map(r=>r[0]);
  assertEqual(qs,report.ordem_inicial,'roundtrip fila');progress('conferir_roundtrip');
  const rebase=reopened.worksheets.getItem('Cálculos');
  assertEqual(rebase.getRange(`L${START}:P${state.last}`).formulas,state.base.getRange(`L${START}:P${state.last}`).formulas,'roundtrip formulas');
  const revalues=rebase.getRange(`L${START}:P${state.last}`).values.flat();
  if(revalues.some(v=>typeof v==='string' && v.startsWith('#')))throw new Error('roundtrip erro');
  report.roundtrip_sem_erros=true;report.xlsx_sha256=hash(await fs.readFile(destination));
  report.builder_sha256=authorHash;report.entrada_sha256=hash(inputBytes);
  report.abas=names;report.aplicacoes=data.intervencao.length;report.medidas=data.habilidades.length;
  report.engine='artifact-tool JS, runtime oficial 26.1020.11127; sem execução no Excel nativo';
  if(mode==='--build') {
    progress('preparar_copia_artificial');report.renderizacao=await preparePreview(data,out);
  }
  if(data.sintetico===true)await fs.writeFile(path.join(out,'verificacao.json'),json(report));
  else {
    // Nenhuma identificação individual em recibo público ou console.
    const {ordem_inicial,lacunas_iniciais,ordem_meta50,ordem_proximidade,ordem_reversa,notas_fila_inicial,notas_fila_reversa,...publicReport}=report;
    publicReport.fila_conferida_todas_linhas=true;publicReport.ordem_fisica_reversa_conferida=true;
    await fs.writeFile(path.join(root,'evidencias/T10/workbook-resultado.json'),json(publicReport));
    console.log(JSON.stringify(publicReport));
  }
}

main().catch(async error=>{
  const target=path.join(root,'restrito/t10/falhas');await fs.mkdir(target,{recursive:true});
  await fs.writeFile(path.join(target,`${Date.now()}.log`),String(error.stack));
  console.error(JSON.stringify({status:'falha',etapa:stage,tipo:error.name,detalhe:'log local restrito'}));process.exitCode=1;
});
