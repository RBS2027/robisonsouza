#!/usr/bin/env python3
"""
Verificação de qualidade DEFINITIVA — consolida todas as checagens feitas manualmente
até 25/08/2026 (estrutura HTML, SEO técnico, links internos, imagens, favicon, sitemap).
Roda via GitHub Actions em todo push e diariamente. Corrige sozinho o que é 100% seguro
(mecânico); o resto vira Issue no GitHub pra revisão.
"""
import glob, re, os, sys
from html.parser import HTMLParser
from collections import defaultdict

REPO = os.getcwd()


def detect_domain():
    """Domínio do próprio site, lido do sitemap.xml — usado para achar links internos
    escritos como URL absoluta (https://dominio/pagina/) em vez de caminho relativo."""
    try:
        sm = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read()
        m = re.search(r'<loc>https?://(?:www\.)?([a-zA-Z0-9.-]+)', sm)
        return m.group(1) if m else None
    except Exception:
        return None


DOMAIN = detect_domain()
VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}


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
                self.errors.append(f"<{self.stack[-1][0]}> aberta linha {self.stack[-1][1][0]} nunca fechada")
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        else:
            self.errors.append(f"</{tag}> sem abertura correspondente")


def all_pages():
    return glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True)


def fix_unescaped_quotes_in_meta(content):
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


AUTOFIXERS = [fix_unescaped_quotes_in_meta]




def check_blog_listing_completeness():
    """Todo artigo em blog/posts.json precisa ter um link pra ele dentro de blog/index.html —
    achado real em 29/08/2026: robisonsouza só linkava 66 de 417 (robô nunca fez backfill
    do histórico da migração). Também acusa entradas fósseis no posts.json (artigo que não
    existe mais como página) e artigos publicados fora do posts.json (órfãos de verdade)."""
    problems = {"sem_link_na_listagem": [], "fosseis_no_posts_json": [], "publicado_sem_registro": []}
    posts_path = os.path.join(REPO, "blog", "posts.json")
    index_path = os.path.join(REPO, "blog", "index.html")
    if not (os.path.exists(posts_path) and os.path.exists(index_path)):
        return problems
    try:
        posts = json.load(open(posts_path, encoding="utf-8"))
    except Exception:
        return problems
    with open(index_path, encoding="utf-8") as fh:
        idx_html = fh.read()
    existing_slugs = {f.split("/index.html")[0] for f in glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True) if "/_fila/" not in f}
    existing_slugs = {os.path.relpath(s, REPO) for s in existing_slugs}
    for p in posts:
        slug = p.get("slug", "")
        if slug not in existing_slugs and os.path.join("blog", slug) not in existing_slugs:
            problems["fosseis_no_posts_json"].append(slug)
        elif (f'/{slug}/"' not in idx_html) and (f'/blog/{slug}/"' not in idx_html):
            problems["sem_link_na_listagem"].append(slug)
    registered = {p.get("slug", "") for p in posts}
    for f in glob.glob(os.path.join(REPO, "blog", "*", "index.html")):
        slug = os.path.basename(os.path.dirname(f))
        if slug not in registered:
            problems["publicado_sem_registro"].append(slug)
    return {k: v for k, v in problems.items() if v}



def check_oversized_images():
    """Imagens acima de 300KB pesam no LCP/performance — achado real em 29/08/2026
    (nenhuma encontrada nos 4 sites, mas vale checar sempre que novo conteúdo entrar)."""
    problems = []
    for f in glob.glob(os.path.join(REPO, "assets", "**", "*"), recursive=True):
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            try:
                size = os.path.getsize(f)
            except OSError:
                continue
            if size > 300 * 1024:
                problems.append((os.path.relpath(f, REPO), size // 1024))
    return problems


def check_corrupted_schema_url_fields():
    """Campo "url" dentro de qualquer bloco JSON-LD deve ser uma URL de verdade (começar
    com http). Achado real em 29/08/2026: um artigo tinha a descrição inteira concatenada
    no campo url por um bug de geração de schema, sem separador."""
    problems = []
    for f in glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True):
        if "/_fila/" in f:
            continue
        with open(f, encoding="utf-8") as fh:
            c = fh.read()
        for block in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', c, re.S):
            try:
                data = json.loads(block)
            except Exception:
                continue
            candidates = data if isinstance(data, list) else [data]
            for node in candidates:
                if not isinstance(node, dict):
                    continue
                url_val = node.get("url")
                if isinstance(url_val, str) and url_val and not url_val.startswith("http"):
                    problems.append(os.path.relpath(f, REPO))
    return problems



def check_schema_mismatched_with_page():
    """O "name"/"headline" do schema WebPage/Article deve corresponder ao <h1> real da
    própria página — um schema com título de OUTRA página é sinal de bloco copiado por
    engano (achado real em 29/08/2026 no artigo conflito-de-lealdade: schema Article
    inteiro pertencia a um artigo diferente)."""
    problems = []
    for f in glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True):
        if "/_fila/" in f:
            continue
        with open(f, encoding="utf-8") as fh:
            c = fh.read()
        h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", c, re.S)
        if not h1_m:
            continue
        h1_text = re.sub(r"<[^>]+>", "", h1_m.group(1)).strip().lower()
        if not h1_text:
            continue
        for block in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', c, re.S):
            try:
                data = json.loads(block)
            except Exception:
                continue
            candidates = data if isinstance(data, list) else [data]
            for node in candidates:
                if not isinstance(node, dict) or node.get("@type") not in ("WebPage", "Article"):
                    continue
                schema_title = (node.get("name") or node.get("headline") or "").strip().lower()
                if not schema_title:
                    continue
                if schema_title not in h1_text and h1_text not in schema_title:
                    problems.append((os.path.relpath(f, REPO), schema_title[:60]))
    return problems


def check_fila_slug_collisions(existing_paths):
    """Detecta slugs duplicados dentro da fila e slugs da fila que colidem com pastas já publicadas."""
    import json
    fila_dir = os.path.join(REPO, "_fila")
    dup_in_fila = defaultdict(list)
    fila_vs_published = []
    if os.path.isdir(fila_dir):
        for entry in sorted(os.listdir(fila_dir)):
            meta_path = os.path.join(fila_dir, entry, "meta.json")
            if not os.path.isfile(meta_path):
                continue
            try:
                meta = json.load(open(meta_path, encoding="utf-8"))
            except Exception:
                continue
            slug = meta.get("slug", "")
            if not slug:
                continue
            dup_in_fila[slug].append(entry)
            if ("/" + slug + "/") in existing_paths:
                fila_vs_published.append((entry, slug))
    dup_in_fila = {s: e for s, e in dup_in_fila.items() if len(e) > 1}
    return dup_in_fila, fila_vs_published


def check_wrong_domain_in_scripts():
    """Scripts do robô (publicar.py, revisao.py, indexnow_bulk.py etc.) devem referenciar
    SÓ o próprio domínio. Um domínio de outro site .com.br hardcoded ali é sinal de
    template copiado de outro repo sem trocar o domínio (bug real, silencioso, recorrente
    a cada publicação automática — achado em 29/08/2026 no robisonsouza)."""
    problems = []
    if not DOMAIN:
        return problems
    for f in glob.glob(os.path.join(REPO, "scripts", "*.py")):
        with open(f, encoding="utf-8") as fh:
            c = fh.read()
        for m in set(re.findall(r'https?://([a-zA-Z0-9.-]+\.com\.br)', c)):
            if m != DOMAIN and not m.startswith('www.' + DOMAIN):
                problems.append((os.path.relpath(f, REPO), m))
    return problems


def check_self_serving_review_schema():
    """AggregateRating/Review schema sobre o próprio profissional/site (auto-referenciado)
    é contra as diretrizes do Google (risco de ação manual) e o tipo Person nunca é aceito
    pra essa marcação — decisão fixa: nunca usar. Achado e removido em 29/08/2026."""
    problems = []
    for f in glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True):
        if "/_fila/" in f:
            continue
        with open(f, encoding="utf-8") as fh:
            c = fh.read()
        if '"@type":"AggregateRating"' in c or '"@type": "AggregateRating"' in c or '"@type":"Review"' in c or '"@type": "Review"' in c:
            problems.append(os.path.relpath(f, REPO))
    return problems


def check_professional_title_violation():
    """Padrão de titulação oficial: NUNCA apresentar "Psicólogo Jurídico" emparelhado com
    "Perito em Psicologia Forense" como se fossem 2 títulos dele (título oficial é sempre
    só "Perito em Psicologia Forense"). Só sinaliza o padrão exato do bug achado em
    29/08/2026 ("Perito em Psicologia Forense e Psicólogo Jurídico" ou o inverso) —
    artigos que tratam do tema "psicólogo jurídico" em geral (assunto do blog) não entram."""
    problems = []
    padrao = re.compile(
        r"Perito em Psicologia Forense e Psicólogo Jurídico"
        r"|Psicólogo Jurídico e Perito em Psicologia Forense"
    )
    for f in glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True):
        if "/_fila/" in f:
            continue
        with open(f, encoding="utf-8") as fh:
            c = fh.read()
        title_m = re.search(r"<title>(.*?)</title>", c)
        desc_m = re.search(r'name="description"\s+content="([^"]*)"', c)
        for label, m in (("title", title_m), ("meta description", desc_m)):
            if m and padrao.search(m.group(1)):
                problems.append((os.path.relpath(f, REPO), label))
    return problems


def check_sitemap_domain_consistency():
    """Toda URL do sitemap.xml deve pertencer ao próprio domínio — uma URL de outro site
    ali é sinal do mesmo bug de domínio hardcoded (achado em 29/08/2026)."""
    problems = []
    if not DOMAIN:
        return problems
    try:
        sm = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read()
    except Exception:
        return problems
    for loc in re.findall(r"<loc>(https?://[^<]+)</loc>", sm):
        host = re.sub(r"^https?://(www\.)?", "", loc).split("/")[0]
        if host != DOMAIN:
            problems.append(loc)
    return problems


def main():
    pages = all_pages()
    real_pages = [p for p in pages if "/_fila/" not in p]

    existing_paths = set()
    for f in real_pages:
        rel = os.path.relpath(f, REPO)
        existing_paths.add("/" if rel == "index.html" else "/" + rel.rsplit("/index.html", 1)[0] + "/")

    autofixed = []
    for f in pages:
        c = open(f, encoding="utf-8", errors="replace").read()
        orig = c
        for fixer in AUTOFIXERS:
            c, changed = fixer(c)
            if changed:
                autofixed.append(os.path.relpath(f, REPO))
        if c != orig:
            open(f, "w", encoding="utf-8").write(c)

    struct_errors = {}
    seo_issues = defaultdict(list)
    img_no_alt = defaultdict(int)
    broken_links = defaultdict(list)
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
        if not dm or len(dm.group(1).replace("&quot;", '"')) < 10:
            seo_issues[rel].append("meta description ausente ou vazia")
        elif "Piloto v2" in dm.group(1):
            seo_issues[rel].append("meta description ainda é o placeholder 'Piloto v2'")

        if 'rel="icon"' not in c:
            seo_issues[rel].append("sem <link rel=icon> explícito")
        if 'apple-touch-icon' not in c:
            seo_issues[rel].append("sem apple-touch-icon")

        n_no_alt = len(re.findall(r'<img(?![^>]*\balt=)[^>]*>', c))
        if n_no_alt:
            img_no_alt[rel] = n_no_alt

        for src in re.findall(r'<img[^>]*src="(https?://[^"]*(?:wp-content|wordpress)[^"]*)"', c):
            broken_links[rel].append(f"imagem possivelmente quebrada (domínio antigo): {src}")

        for href in re.findall(r'href="(/[a-zA-Z0-9\-_/]*/)"', c):
            if href not in existing_paths and href not in ("/blog/",):
                broken_links[rel].append(f"link interno pra página inexistente: {href}")

        if DOMAIN:
            for href in re.findall(rf'href="https?://(?:www\.)?{re.escape(DOMAIN)}(/[a-zA-Z0-9\-_/]*/)"', c):
                if href not in existing_paths and href not in ("/blog/",):
                    broken_links[rel].append(f"link interno (URL absoluta) pra página inexistente: {href}")

    dup_titles = {t: srcs for t, srcs in titles.items() if len(srcs) > 1}

    sitemap_issues = []
    sitemap_path = os.path.join(REPO, "sitemap.xml")
    if os.path.exists(sitemap_path):
        sm = open(sitemap_path, encoding="utf-8", errors="replace").read()
        urls_in_sitemap = set(re.findall(r'<loc>https?://[^/]+(/[^<]*)</loc>', sm))
        noindex_hint = {"/inscrito/", "/obrigado/"}
        missing = sorted(p for p in existing_paths if p not in urls_in_sitemap and p not in noindex_hint)
        if missing:
            sitemap_issues = missing[:15]

    lines = []
    if autofixed:
        lines.append(f"## Corrigido automaticamente ({len(autofixed)} arquivo(s))")
        lines.append("Aspas literais não escapadas em meta description:")
        for f in sorted(set(autofixed))[:30]:
            lines.append(f"- {f}")
        lines.append("")

    if struct_errors:
        lines.append(f"## ⚠️ HTML com estrutura quebrada ({len(struct_errors)} página(s))")
        for rel, probs in list(struct_errors.items())[:20]:
            lines.append(f"- **{rel}**: {probs[0]}")
        lines.append("")

    if dup_titles:
        lines.append(f"## ⚠️ Títulos duplicados ({len(dup_titles)} grupo(s))")
        for t, srcs in list(dup_titles.items())[:10]:
            lines.append(f"- \"{t[:60]}\" -> {', '.join(srcs)}")
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

    if broken_links:
        lines.append(f"## ⚠️ Links/imagens possivelmente quebrados ({len(broken_links)} página(s))")
        for rel, probs in list(broken_links.items())[:20]:
            for pmsg in probs:
                lines.append(f"- **{rel}**: {pmsg}")
        lines.append("")

    if sitemap_issues:
        lines.append(f"## ⚠️ Páginas fora do sitemap.xml ({len(sitemap_issues)})")
        for pth in sitemap_issues:
            lines.append(f"- {pth}")
        lines.append("")


    wrong_domain_scripts = check_wrong_domain_in_scripts()
    if wrong_domain_scripts:
        lines.append(f"## \u26a0\ufe0f Domínio errado hardcoded em scripts ({len(wrong_domain_scripts)} caso(s))")
        for rel, dom in wrong_domain_scripts[:10]:
            lines.append(f"- **{rel}**: referencia {dom} (deveria ser {DOMAIN})")
        lines.append("")

    self_serving_review = check_self_serving_review_schema()
    if self_serving_review:
        lines.append(f"## \u26a0\ufe0f Schema AggregateRating/Review auto-referenciado ({len(self_serving_review)} página(s))")
        for rel in self_serving_review[:10]:
            lines.append(f"- **{rel}**: remover — viola diretriz do Google e decisão fixa do projeto")
        lines.append("")

    title_violations = check_professional_title_violation()
    if title_violations:
        lines.append(f"## \u26a0\ufe0f \"Psicólogo Jurídico\" usado como título ({len(title_violations)} caso(s))")
        for rel, label in title_violations[:15]:
            lines.append(f"- **{rel}** ({label}): título oficial é sempre \"Perito em Psicologia Forense\"")
        lines.append("")

    sitemap_wrong_domain = check_sitemap_domain_consistency()
    if sitemap_wrong_domain:
        lines.append(f"## \u26a0\ufe0f URLs de outro domínio no sitemap.xml ({len(sitemap_wrong_domain)})")
        for loc in sitemap_wrong_domain[:10]:
            lines.append(f"- {loc}")
        lines.append("")


    blog_listing_issues = check_blog_listing_completeness()
    blog_listing_issues = {k: v for k, v in blog_listing_issues.items() if v}
    if blog_listing_issues:
        total = sum(len(v) for v in blog_listing_issues.values())
        lines.append(f"## \u26a0\ufe0f Lista do blog fora de sincronia com posts.json ({total} caso(s))")
        for categoria, itens in blog_listing_issues.items():
            lines.append(f"- **{categoria}**: {len(itens)} — {', '.join(itens[:5])}")
        lines.append("")


    oversized_images = check_oversized_images()
    if oversized_images:
        lines.append(f"## \u26a0\ufe0f Imagens acima de 300KB ({len(oversized_images)})")
        for rel, kb in oversized_images[:15]:
            lines.append(f"- **{rel}**: {kb}KB")
        lines.append("")

    corrupted_schema_urls = check_corrupted_schema_url_fields()
    if corrupted_schema_urls:
        lines.append(f"## \u26a0\ufe0f Campo url corrompido em schema JSON-LD ({len(corrupted_schema_urls)} página(s))")
        for rel in corrupted_schema_urls[:15]:
            lines.append(f"- **{rel}**")
        lines.append("")


    schema_mismatches = check_schema_mismatched_with_page()
    if schema_mismatches:
        lines.append(f"## \u26a0\ufe0f Schema com título de outra página ({len(schema_mismatches)} caso(s))")
        for rel, titulo in schema_mismatches[:15]:
            lines.append(f"- **{rel}**: schema diz \"{titulo}\" — não bate com o H1 da página")
        lines.append("")

    dup_in_fila, fila_vs_published = check_fila_slug_collisions(existing_paths)
    if dup_in_fila:
        lines.append(f"## \u26a0\ufe0f Slugs duplicados na fila ({len(dup_in_fila)} caso(s))")
        for slug, entries in list(dup_in_fila.items())[:15]:
            lines.append(f"- **{slug}**: gerado em {', '.join(entries)}")
        lines.append("")
    if fila_vs_published:
        lines.append(f"## \u26a0\ufe0f Slugs da fila colidindo com página já publicada ({len(fila_vs_published)} caso(s))")
        for entry, slug in fila_vs_published[:15]:
            lines.append(f"- **{entry}** -> /{slug}/ já existe publicado")
        lines.append("")

    report = "\n".join(lines)
    has_manual_issues = bool(struct_errors or dup_titles or seo_issues or img_no_alt or broken_links or sitemap_issues or dup_in_fila or fila_vs_published or wrong_domain_scripts or self_serving_review or title_violations or sitemap_wrong_domain or blog_listing_issues or oversized_images or corrupted_schema_urls or schema_mismatches)

    with open(os.environ.get("GITHUB_STEP_SUMMARY", "/tmp/qa_summary.md"), "a", encoding="utf-8") as fh:
        fh.write(report if report else "## ✅ Tudo limpo — nenhum problema encontrado.\n")

    print(f"AUTOFIXED={'1' if autofixed else '0'}")
    print(f"MANUAL_ISSUES={'1' if has_manual_issues else '0'}")
    with open("/tmp/qa_report_body.md", "w", encoding="utf-8") as fh:
        fh.write(report if has_manual_issues else "")

    sys.exit(0)


if __name__ == "__main__":
    main()
