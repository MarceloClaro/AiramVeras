// Importa somente a entrada pública. Não cria workbook nem chama marcador.
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const base = process.argv[2];
const require = createRequire(path.join(base, 'package.json'));
const api = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const exports = Object.fromEntries(['Workbook','SpreadsheetFile','FileBlob'].map(name => [name, typeof api[name] === 'function']));
console.log(JSON.stringify({ exports, node: process.version, autoria_executada: false }));
if (Object.values(exports).some(value => !value)) process.exitCode = 2;
