/** Diagnóstico público de render: uma célula exclusivamente artificial. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const runtime=path.join(root,'.superpowers/sdd/implementation-plan/runtime-probe');
const req=createRequire(pathToFileURL(path.join(runtime,'entry.mjs')));
const {Workbook}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const wb=Workbook.create(),sheet=wb.worksheets.add('Artificial');
sheet.getRange('A1').values=[['ARTIFICIAL']];
sheet.getRange('A1').format.columnWidth=30;
const format=process.argv[2]||'png';
const out=path.join(root,'.superpowers/sdd/implementation-plan/render-minimo.'+format);
console.log(JSON.stringify({etapa:'antes_render_minimo'}));
const png=await wb.render({sheetName:'Artificial',range:'A1:B3',scale:1,format});
console.log(JSON.stringify({etapa:'apos_render_minimo'}));
await fs.writeFile(out,new Uint8Array(await png.arrayBuffer()));
console.log(JSON.stringify({etapa:'salvo',somente_artificial:true}));
