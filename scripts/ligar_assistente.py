# -*- coding: utf-8 -*-
"""Liga este site ao assistente.tec.br (rodapé "Outros sites") em todas as páginas e na fila.
SÓ RODAR DEPOIS que o assistente.tec.br novo estiver no ar (Cloudflare Pages + DNS).
Uso (na raiz do repositório):
    python3 scripts/ligar_assistente.py            # simulação: só conta
    python3 scripts/ligar_assistente.py --aplicar  # grava
Idempotente: página que já tem o link não é alterada."""
import glob, re, sys

APLICAR = "--aplicar" in sys.argv
ALVO = "https://assistente.tec.br"
PADROES = [
    # robisonsouza / perito: <h3 class="ft">Outros sites</h3><a ...>...</a><a ...>...</a>
    (re.compile(r'(Outros sites</h3>(?:<a href="https://[^"]+" rel="noopener">[^<]+</a>)+)'),
     r'\1<a href="%s" rel="noopener">assistente.tec.br</a>' % ALVO),
    # portais: <strong>Outros sites</strong><br><a ...>...</a><br><a ...>...</a></p>
    (re.compile(r'(Outros sites</strong>(?:<br><a href="https://[^"]+" rel="noopener">[^<]+</a>)+)'),
     r'\1<br><a href="%s" rel="noopener">assistente.tec.br</a>' % ALVO),
]
n = sem = 0
for f in glob.glob("**/*.html", recursive=True):
    h = open(f, encoding="utf-8").read()
    if "assistente.tec.br" in h:
        continue
    novo = h
    for pat, rep in PADROES:
        novo, k = pat.subn(rep, novo, count=1)
        if k:
            break
    if novo == h:
        sem += 1
        continue
    n += 1
    if APLICAR:
        open(f, "w", encoding="utf-8").write(novo)
print(("GRAVADAS" if APLICAR else "SIMULACAO") + ": %d paginas recebem o link; %d sem bloco 'Outros sites'" % (n, sem))
