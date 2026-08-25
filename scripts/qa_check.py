#!/usr/bin/env python3
"""
Verificação automática de qualidade — roda via GitHub Actions em todo push e diariamente.
Corrige sozinho o que é 100% seguro (mecânico); reporta o resto como issue do GitHub.
"""
import glob, re, os, sys
from html.parser import HTMLParser
from collections import defaultdict

REPO = os.getcwd()
VOID = {'br','img','input','meta','link','hr','area','base','col','embed','source','track','wbr'}


class Balancer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        elif tag in [s[0] for s in self.stack]:
            while self.stack and self.stack[-1][0] != tag:
                self.errors.append(f"linha {self.getpos()[0]}: <{self.stack[-1][0]}> aberta linha {self.stack[-1][1][0]} nunca fechada antes de </{tag}>")
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        else:
            self.errors.append(f"linha {self.getpos()[0]}: </{tag}> sem abertura correspondente")


def all_pages():
    return glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True)


def fix_unescaped_quotes_in_meta(content):
    """Corrige aspas literais dentro de content="..." de <meta name=description> — sempre seguro."""
    changed = False
    out = []
    for m in re.finditer(r'<meta name="description" content="', content):
        start = m.end()
        end_tag = content.find('">', start)
        if end_tag == -1:
            continue
        segment = content[start:end_tag]
        if '"' in segment:
            out.append((start, end_tag, segment.replace('"', '&quot;')))
            changed = True
    if not changed:
        return content, False
    for start, end_tag, fixed in sorted(out, key=lambda x: -x[0]):
        content = content[:start] + fixed + content[end_tag:]
    return content, True


def main():
    pages = all_pages()
    real_pages = [p for p in pages if "/_fila/" not in p]

    autofixed = []
    struct_errors = {}
    seo_issues = defaultdict(list)
    img_no_alt = defaultdict(int)

    for f in pages:  # aplica o autofix também nos rascunhos da _fila
        c = open(f, encoding="utf-8", errors="replace").read()
        c2, changed = fix_unescaped_quotes_in_meta(c)
        if changed:
            open(f, "w", encoding="utf-8").write(c2)
            autofixed.append(os.path.relpath(f, REPO))

    titles = defaultdict(list)
    for f in real_pages:
        c = open(f, encoding="utf-8", errors="replace").read()
        rel = os.path.relpath(f, REPO)

        p = Balancer()
        try:
            p.feed(c)
        except Exception as e:
            struct_errors[rel] = [f"parser crash: {e}"]
            continue
        problems = list(p.errors)
        if p.stack:
            problems.append(f"tags nunca fechadas: {[s[0] for s in p.stack]}")
        if problems:
            struct_errors[rel] = problems

        tm = re.search(r'<title>([^<]*)</title>', c)
        if not tm:
            seo_issues[rel].append("sem <title>")
        else:
            titles[tm.group(1).strip()].append(rel)

        dm = re.search(r'<meta name="description" content="([^"]*(?:&quot;[^"]*)*)"', c)
        if not dm or len(dm.group(1)) < 10:
            seo_issues[rel].append("meta description ausente ou vazia")
        elif "Piloto v2" in dm.group(1):
            seo_issues[rel].append("meta description ainda é o placeholder 'Piloto v2'")

        n_no_alt = len(re.findall(r'<img(?![^>]*\balt=)[^>]*>', c))
        if n_no_alt:
            img_no_alt[rel] = n_no_alt

    dup_titles = {t: srcs for t, srcs in titles.items() if len(srcs) > 1}

    # ---- monta relatório ----
    lines = []
    if autofixed:
        lines.append(f"## Corrigido automaticamente ({len(autofixed)} arquivo(s))")
        lines.append("Aspas literais não escapadas em meta description (quebrava o HTML):")
        for f in autofixed[:30]:
            lines.append(f"- {f}")
        lines.append("")

    if struct_errors:
        lines.append(f"## ⚠️ HTML com estrutura quebrada ({len(struct_errors)} página(s)) — precisa de revisão manual")
        for rel, probs in list(struct_errors.items())[:20]:
            lines.append(f"- **{rel}**: {probs[0]}")
        lines.append("")

    if dup_titles:
        lines.append(f"## ⚠️ Títulos duplicados ({len(dup_titles)} grupo(s))")
        for t, srcs in list(dup_titles.items())[:10]:
            lines.append(f"- \"{t[:60]}\" → {', '.join(srcs)}")
        lines.append("")

    if seo_issues:
        lines.append(f"## ⚠️ SEO técnico ({len(seo_issues)} página(s))")
        for rel, probs in list(seo_issues.items())[:20]:
            lines.append(f"- **{rel}**: {'; '.join(probs)}")
        lines.append("")

    if img_no_alt:
        lines.append(f"## ⚠️ Imagens sem alt ({sum(img_no_alt.values())} em {len(img_no_alt)} página(s))")
        for rel, n in list(img_no_alt.items())[:20]:
            lines.append(f"- **{rel}**: {n} imagem(ns)")
        lines.append("")

    report = "\n".join(lines)
    has_manual_issues = bool(struct_errors or dup_titles or seo_issues or img_no_alt)

    with open(os.environ.get("GITHUB_STEP_SUMMARY", "/tmp/qa_summary.md"), "a", encoding="utf-8") as fh:
        if report:
            fh.write(report)
        else:
            fh.write("## ✅ Tudo limpo — nenhum problema encontrado.\n")

    # sinaliza pro workflow se: (a) algo foi autofixado -> precisa commitar; (b) sobrou algo manual -> abrir/atualizar issue
    print(f"AUTOFIXED={'1' if autofixed else '0'}")
    print(f"MANUAL_ISSUES={'1' if has_manual_issues else '0'}")
    if report:
        with open("/tmp/qa_report_body.md", "w", encoding="utf-8") as fh:
            fh.write(report if has_manual_issues else "")

    sys.exit(0)


if __name__ == "__main__":
    main()
