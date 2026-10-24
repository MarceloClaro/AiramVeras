import { fileURLToPath } from 'node:url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
const client = new Client({name:'verificacao-instalacao',version:'1.0.0'});
try {
 await client.connect(new StdioClientTransport({command:process.execPath,args:[fileURLToPath(new URL('./node_modules/@bncc/mcp/dist/servidor.js',import.meta.url))]}));
 console.log(JSON.stringify(await client.listTools(),null,2));
 console.log(JSON.stringify(await client.callTool({name:'bncc_estatisticas',arguments:{}}),null,2));
 console.log(JSON.stringify(await client.callTool({name:'bncc_lookup',arguments:{codigo:'EF01LP01'}}),null,2));
} finally {await client.close();}

