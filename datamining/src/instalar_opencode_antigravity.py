"""
Script de Instalação e Integração Completa do OpenCode Ecosystem Core no Antigravity
===================================================================================
Origem: \\\\wsl.localhost\\Ubuntu\\home\\marceloclaro\\opencode-ecosystem-core
Destino: C:\\Users\\marce\\.gemini\\config\\plugins\\opencode-ecosystem-core
         C:\\Users\\marce\\.gemini\\config\\mcp_config.json
         C:\\Users\\marce\\.gemini\\config\\rules\\opencode_ecosystem_rules.md
"""
import os
import sys
import json
import shutil
from pathlib import Path

WSL_SOURCE = Path(r"\\wsl.localhost\Ubuntu\home\marceloclaro\opencode-ecosystem-core")
GEMINI_CONFIG = Path(r"C:\Users\marce\.gemini\config")
PLUGIN_DEST = GEMINI_CONFIG / "plugins" / "opencode-ecosystem-core"
RULES_DEST = GEMINI_CONFIG / "rules"
MCP_CONFIG_PATH = GEMINI_CONFIG / "mcp_config.json"

def verificar_origem():
    print(f"[*] Verificando diretório de origem: {WSL_SOURCE}")
    if not WSL_SOURCE.exists():
        raise FileNotFoundError(f"Origem não encontrada: {WSL_SOURCE}")
    print("    [+] Origem verificada com sucesso!")

def criar_plugin_base():
    print(f"[*] Criando estrutura do plugin em: {PLUGIN_DEST}")
    PLUGIN_DEST.mkdir(parents=True, exist_ok=True)
    skills_dir = PLUGIN_DEST / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    agents_dir = PLUGIN_DEST / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    plugin_json = {
        "name": "opencode-ecosystem-core",
        "version": "4.1.0",
        "description": "Suite completa OpenCode Ecosystem Core: 312 agentes, 16 MCPs, raciocinio formal Z3/SymPy, scanners noologicos, medicina virtual, peer-review academico e orquestracao multiagente.",
        "author": {
            "name": "Marcelo Claro",
            "email": "marceloclaro@gmail.com"
        },
        "repository": "https://github.com/MarceloClaro/opencode-ecosystem-core",
        "license": "MIT",
        "keywords": [
            "opencode",
            "multiagent",
            "scanners",
            "mci",
            "deep-research",
            "medico-virtual",
            "peer-review",
            "z3",
            "sympy",
            "litert-lm"
        ]
    }
    
    with open(PLUGIN_DEST / "plugin.json", "w", encoding="utf-8") as f:
        json.dump(plugin_json, f, indent=2, ensure_ascii=False)
    print("    [+] plugin.json criado.")

def copiar_e_adaptar_skills():
    print("[*] Copiando e adaptando Skills do ecossistema...")
    skills_source = WSL_SOURCE / "skills"
    skills_dest = PLUGIN_DEST / "skills"

    # 1. Skills da pasta skills/
    if skills_source.exists():
        for item in skills_source.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                skill_slug = item.name.replace("_", "-")
                dest_item = skills_dest / skill_slug
                print(f"    -> Copiando skill: {item.name} -> {skill_slug}")
                if dest_item.exists():
                    shutil.rmtree(dest_item)
                shutil.copytree(item, dest_item)
                
                # Ajustar frontmatter se necessário
                skill_md = dest_item / "SKILL.md"
                content = skill_md.read_text(encoding="utf-8")
                if "name: instructions" in content:
                    content = content.replace("name: instructions", f"name: {skill_slug}")
                    skill_md.write_text(content, encoding="utf-8")
                elif not content.startswith("---"):
                    # Adicionar frontmatter caso falte
                    header = f"---\nname: {skill_slug}\ndescription: Habilidade especializada do OpenCode Ecosystem Core: {skill_slug}.\n---\n\n"
                    skill_md.write_text(header + content, encoding="utf-8")

    # 2. Skills de Fine-Tuning (.agents/skills)
    fine_skills_source = WSL_SOURCE / ".agents" / "skills"
    if fine_skills_source.exists():
        for item in fine_skills_source.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                skill_slug = item.name.replace("_", "-")
                dest_item = skills_dest / skill_slug
                print(f"    -> Copiando fine-tuning skill: {item.name} -> {skill_slug}")
                if dest_item.exists():
                    shutil.rmtree(dest_item)
                shutil.copytree(item, dest_item)
                
                skill_md = dest_item / "SKILL.md"
                content = skill_md.read_text(encoding="utf-8")
                if "name: instructions" in content:
                    content = content.replace("name: instructions", f"name: {skill_slug}")
                    skill_md.write_text(content, encoding="utf-8")

    # 3. Adicionar Skill Mestra do OpenCode Ecosystem
    opencode_master_skill = skills_dest / "opencode-ecosystem-orchestrator"
    opencode_master_skill.mkdir(parents=True, exist_ok=True)
    master_skill_content = """---
name: opencode-ecosystem-orchestrator
description: >-
  Orquestrador mestre do OpenCode Ecosystem Core. Permite ao Antigravity acessar
  os 312 agentes especializados, scanners noológicos/teleológicos, motores de
  raciocínio formal (Z3, SymPy), barramento MCI e orquestração distribuída.
---

# OpenCode Ecosystem Orchestrator — Antigravity Integration

Este módulo conecta o Antigravity à malha neural de 312 agentes e 16 MCPs do OpenCode Ecosystem Core localizado em `/home/marceloclaro/opencode-ecosystem-core`.

## Capacidades Disponíveis

1. **Scanners Epistêmicos e Cognitivos**:
   - `noological_scanner`: Detecção de lacunas epistêmicas e limites conceituais.
   - `teleological_scanner`: Verificação de alinhamento teleológico e propósito.
   - `potentiality_v2`: Estimativa de potencialidade evolutiva em 6 dimensões.
   - `social_impact`: Auditoria de impacto social e conformidade ética/ESG.

2. **Motores de Raciocínio Formal**:
   - `z3_verify`: Verificação de invariantes lógicas e prova de teoremas via Z3 Theorem Prover.
   - `sympy_analyze`: Análise matemática simbólica, cálculo diferencial/integral e matrizes.
   - `critical_analyze`: Detecção automática de falácias, vieses e inconsistências argumentativas.

3. **Metacognitive Interconnect (MCI)**:
   - Barramento semântico e memória episódica contínua entre sessões e agentes.

4. **Ponte de Execução MCP**:
   - As ferramentas do ecossistema podem ser invocadas via servidores MCP configurados no Antigravity (`opencode_antigravity_bridge`, `opencode_mci`, `opencode_ecosystem_network`).
"""
    (opencode_master_skill / "SKILL.md").write_text(master_skill_content, encoding="utf-8")
    print("    [+] Skill mestra opencode-ecosystem-orchestrator instalada.")

def atualizar_mcp_config():
    print(f"[*] Registrando MCP Servers do OpenCode em: {MCP_CONFIG_PATH}")
    if MCP_CONFIG_PATH.exists():
        with open(MCP_CONFIG_PATH, "r", encoding="utf-8") as f:
            mcp_data = json.load(f)
    else:
        mcp_data = {"mcpServers": {}}

    servers = mcp_data.setdefault("mcpServers", {})

    novos_servidores = {
        "opencode_antigravity_bridge": {
            "command": "wsl.exe",
            "args": [
                "-d", "Ubuntu", "--", "bash", "-c",
                "cd /home/marceloclaro/opencode-ecosystem-core && .venv/bin/python integrations/antigravity/antigravity_mcp_server.py"
            ]
        },
        "opencode_mci": {
            "command": "wsl.exe",
            "args": [
                "-d", "Ubuntu", "--", "bash", "-c",
                "cd /home/marceloclaro/opencode-ecosystem-core && .venv/bin/python mci/mcp_server.py"
            ]
        },
        "opencode_ecosystem_network": {
            "command": "wsl.exe",
            "args": [
                "-d", "Ubuntu", "--", "bash", "-c",
                "cd /home/marceloclaro/opencode-ecosystem-core && .venv/bin/python -m integrations.ecosystem_mcp"
            ]
        },
        "opencode_colibri": {
            "command": "wsl.exe",
            "args": [
                "-d", "Ubuntu", "--", "bash", "-c",
                "cd /home/marceloclaro/opencode-ecosystem-core && .venv/bin/python colibri/colibri_mcp_server.py"
            ]
        }
    }

    for k, v in novos_servidores.items():
        servers[k] = v
        print(f"    [+] MCP Server configurado: {k}")

    with open(MCP_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(mcp_data, f, indent=2, ensure_ascii=False)
    print("    [+] mcp_config.json atualizado com sucesso.")

def criar_regras_globais():
    print(f"[*] Criando regras globais do OpenCode em: {RULES_DEST}")
    RULES_DEST.mkdir(parents=True, exist_ok=True)
    rules_file = RULES_DEST / "opencode_ecosystem_rules.md"

    rules_content = """# Diretrizes Globais do OpenCode Ecosystem Core no Antigravity

Quando interagir com componentes, agentes ou códigos do OpenCode Ecosystem Core:

1. **Idioma Obrigatório**: Todo conteúdo explicativo, alertas e relatórios devem ser em Português Brasileiro formal (`pt-BR`).
2. **Arquitetura SDD & TDD**: Todo novo recurso ou alteração estrutural deve ser precedido por Especificação Técnica (SDD) e coberto por testes formais (TDD) com cobertura mínima de 90%.
3. **Segurança e Fail-Closed**: Princípio de menor privilégio, fail-closed diante de parâmetros incertos e respeito estrito a dados sensíveis (Zero-PII).
4. **Ponte Antigravity & OpenCode**: Delegar tarefas pesadas de pesquisa, geração de imagens e automação de browser aos mecanismos nativos do Antigravity, mantendo orquestração simbólica e metaraciocínio no OpenCode Core.
"""
    rules_file.write_text(rules_content, encoding="utf-8")
    print("    [+] Regras globais registradas com sucesso.")

def main():
    print("=" * 70)
    print("INSTALADOR OPENCODE ECOSYSTEM CORE -> ANTIGRAVITY")
    print("=" * 70)
    verificar_origem()
    criar_plugin_base()
    copiar_e_adaptar_skills()
    atualizar_mcp_config()
    criar_regras_globais()
    print("=" * 70)
    print("[SUCCESS] OpenCode Ecosystem Core instalado com sucesso no Antigravity!")
    print("=" * 70)

if __name__ == "__main__":
    main()
