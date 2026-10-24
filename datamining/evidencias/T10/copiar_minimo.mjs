/** Diagnóstico público mínimo; somente quatro números artificiais. */
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const req=createRequire(pathToFileURL(path.join(root,'.superpowers/sdd/implementation-plan/runtime-probe/entry.mjs')));
const {Workbook}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const a=Workbook.create(),b=Workbook.create();
const target=a.worksheets.add('Artificial'),source=b.worksheets.add('Artificial');
target.getRange('A1:B2').values=[[1,3],[2,4]];
target.getRange('C1:C2').formulas=[['=A1+B1'],['=A2+B2']];
source.getRange('A1:B2').values=[[2,4],[1,3]];
source.getRange('C1:C2').formulas=[['=A1+B1'],['=A2+B2']];
console.log(JSON.stringify({etapa:'antes_copia_publica'}));
try {
  target.getRange('A1:C2').copyFrom(source.getRange('A1:C2'),'all');a.recalculate();
  const ok=JSON.stringify(target.getRange('A1:C2').values)==='[[2,4,6],[1,3,4]]';
  const formulas=JSON.stringify(target.getRange('C1:C2').formulas)==='[["=A1+B1"],["=A2+B2"]]';
  if(!ok||!formulas)throw new Error('Divergencia artificial');
  console.log(JSON.stringify({copia_entre_workbooks_publica_suportada:true,valores_formulas_conferidos:true}));
} catch(error) {console.log(JSON.stringify({copia_entre_workbooks_publica_suportada:false,tipo:error.name}));process.exitCode=1;}
