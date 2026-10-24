"""Inspeção NTFS somente leitura; categorias minimizadas, sem certificar papéis."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def main():
    command=r"""$ErrorActionPreference='Stop'
$t10Path = 'C:/Users/marce/Downloads/Airam veras/datamining/restrito/outputs/01a16157-2a68-7253-9591-de126647cf53'
$t10Acl = Get-Acl -LiteralPath $t10Path
$t10Sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$t10Rules = @($t10Acl.Access | ForEach-Object {
  $t10Value = $_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value
  $t10Role = if($t10Value -eq $t10Sid){'usuario_atual'}elseif($t10Value -eq 'S-1-5-18'){'SYSTEM'}elseif($t10Value -eq 'S-1-5-32-544'){'Administradores'}else{'outra_identidade'}
  [ordered]@{categoria=$t10Role;tipo=$_.AccessControlType.ToString();direitos=$_.FileSystemRights.ToString();herdada=$_.IsInherited}
})
[ordered]@{heranca_protegida=$t10Acl.AreAccessRulesProtected;regras=$t10Rules;acl_alterada=$false;restricao_por_cargos_escolares_certificada=$false} | ConvertTo-Json -Depth 5 -Compress
"""
    run=subprocess.run(['C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe',
        '-NoProfile','-Command',command],capture_output=True,text=True,encoding='utf-8')
    if run.returncode:
        (ROOT/'evidencias/T10/acl-diagnostico.log').write_text(run.stderr,encoding='utf-8')
        raise RuntimeError('Inspecao NTFS falhou sem alterar permissoes; diagnostico local')
    result=json.loads(run.stdout);result['timestamp']=datetime.now(timezone.utc).isoformat()
    if type(result.get('heranca_protegida')) is not bool or not result.get('regras'):raise ValueError('ACL ausente/incompleta; nao validada')
    result['pendencia']='Identidades/perfis escolares de leitura/edicao ainda pendentes; nenhuma ACL alterada.'
    (ROOT/'evidencias/T10/acl-destino-resultado.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()
