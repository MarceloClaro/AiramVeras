/** Uma consulta pública focal para o bloqueio observado de renderização. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const req=createRequire(pathToFileURL(path.join(root,'.superpowers/sdd/implementation-plan/runtime-probe/entry.mjs')));
const {Workbook}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const wb=Workbook.create();
const query=process.argv[2]||'workbook.render';
const result=wb.help(query,{include:'index,notes,examples',maxChars:6500,...(query==='worksheet.*'?{search:'hidden|visibility|column'}:{})});
await fs.writeFile(path.join(root,'evidencias/T10/'+(query==='workbook.render'?'render':'coluna')+'-api-publica.json'),JSON.stringify(result,null,2));
console.log(result.ndjson);
