Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$raiz = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$itens = @(
    @{ nome = 'publico'; arquivo = 'estatistica/t09/checkpoint.json'; esquema = 'docs/esquema-t09.json'; esperado = '150592d325fde9c80bfd98717a974b3a53e816987601b1b3968168e558f14339' },
    @{ nome = 'restrito'; arquivo = 'restrito/t09/checkpoint.json'; esquema = 'docs/esquema-restrito-t09.json'; esperado = '0e8359f648e3a4a01dce2a817d2fb7fb5397b31752a83c04ca2082f37cbc0901' }
)
$falhas = 0
foreach ($item in $itens) {
    $arquivo = Join-Path $raiz $item.arquivo
    $esquema = Join-Path $raiz $item.esquema
    $hash = (Get-FileHash -LiteralPath $arquivo -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne $item.esperado) { Write-Output "$($item.nome):hash_divergente"; $falhas++; continue }
    try {
        $valido = Test-Json -LiteralPath $arquivo -SchemaFile $esquema -ErrorAction Stop
        if ($valido) { Write-Output "$($item.nome):schema_valido" }
        else { Write-Output "$($item.nome):schema_invalido"; $falhas++ }
    } catch {
        # A mensagem do validador pode conter valores individuais; não divulgá-la.
        Write-Output "$($item.nome):schema_erro:$($_.Exception.GetType().Name)"
        $falhas++
    }
}
if ($falhas) { exit 1 }
