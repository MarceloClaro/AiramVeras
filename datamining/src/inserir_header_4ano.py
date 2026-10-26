# -*- coding: utf-8 -*-
import shutil

def main():
    with open('docs/index.html', 'r', encoding='utf-8') as f:
        text = f.read()

    idx = text.find('DOSSIE_MESTRE_3ANO')
    end_a = text.find('</a>', idx) + 4
    bloco_3 = text[idx-50:end_a]
    
    novo_b = bloco_3 + """\n            <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2 py-1.5 rounded-lg bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/70 transition flex items-center gap-1 font-semibold text-[11px]"
                title="Dossiê Pedagógico Mestre 4º Ano A e B (1.720 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3 h-3 text-indigo-400"></i> 4º Ano A e B (1720p)
            </a>"""

    text = text[:idx-50] + novo_b + text[end_a:]
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    shutil.copy('docs/index.html', 'index.html')
    print("Header atualizado e sincronizado com sucesso!")

if __name__ == '__main__':
    main()
