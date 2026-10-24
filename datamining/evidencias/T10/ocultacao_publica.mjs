/** Consulta publica focal da superficie Range para ocultacao. Nao autoriza XLSX. */
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const req=createRequire(pathToFileURL(path.join(root,'.superpowers/sdd/implementation-plan/runtime-probe/entry.mjs')));
const {Workbook}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
console.log(Workbook.create().help('range.*',{search:'hidden|hide|column',include:'index,notes,examples',maxChars:11000}).ndjson);
