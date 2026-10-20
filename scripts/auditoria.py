# -*- coding: utf-8 -*-
"""Auditoria em lote das categorias MANUAL / AINDA NÃO CHECADO do CHECK LIST SITES RBS.
Uso: python3 auditoria.py <pasta_repo> <dominio>"""
import sys, os, re, json, glob, collections
from html.parser import HTMLParser

ROOT, DOM = sys.argv[1], sys.argv[2]
os.chdir(ROOT)
PAGES = sorted(p for p in glob.glob("**/index.html", recursive=True) if not p.startswith("_fila/"))
PAGES += [p for p in ["404.html"] if os.path.exists(p)]
R = collections.defaultdict(list)
def add(cat, page, msg): R[cat].append((page, msg))

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.h=[]; s.ids=collections.Counter(); s.imgs=[]; s.links=[]; s.inputs=[]; s.scripts=[]; s.css=[]
        s.stack=[]; s.text_h=[]; s.cur_h=None; s.buf=""; s.ldjson=[]; s.in_ld=False; s.meta={}; s.has_skip=False; s.anchors=[]
        s.title=""; s.in_title=False; s.nav=0; s.landmarks=collections.Counter(); s.buttons=[]; s.forms=[]
    def handle_starttag(s, t, a):
        a=dict(a)
        if t in("h1","h2","h3","h4"): s.cur_h=t; s.buf=""
        if "id" in a: s.ids[a["id"]]+=1
        if t=="img": s.imgs.append(a)
        if t=="a":
            s.links.append(a)
            h=a.get("href","")
            if h.startswith("#"): s.anchors.append(h[1:])
            if h.startswith("#") and "pular" in (a.get("class","")+h).lower(): s.has_skip=True
        if t in("input","textarea","select"): s.inputs.append(a)
        if t=="script":
            s.scripts.append(a)
            if a.get("type")=="application/ld+json": s.in_ld=True; s.buf=""
        if t=="link": s.css.append(a)
        if t=="meta":
            k=a.get("name") or a.get("property")
            if k: s.meta[k]=a.get("content","")
        if t=="title": s.in_title=True; s.buf=""
        if t in("main","nav","header","footer","aside"): s.landmarks[t]+=1
        if t=="button": s.buttons.append(a)
        if t=="form": s.forms.append(a)
    def handle_data(s,d):
        if s.cur_h or s.in_ld or s.in_title: s.buf+=d
    def handle_endtag(s,t):
        if t==s.cur_h: s.h.append((t,re.sub(r"\s+"," ",s.buf).strip())); s.cur_h=None
        if t=="script" and s.in_ld: s.ldjson.append(s.buf); s.in_ld=False
        if t=="title": s.title=s.buf.strip(); s.in_title=False

titles=collections.defaultdict(list); descs=collections.defaultdict(list)
inbound=collections.Counter(); words={}
sitemap=open("sitemap.xml",encoding="utf-8").read() if os.path.exists("sitemap.xml") else ""
sm_urls=set(re.findall(r"<loc>([^<]+)</loc>",sitemap))
css_versions=collections.Counter()

for pg in PAGES:
    raw=open(pg,encoding="utf-8",errors="replace").read()
    path="/"+pg.replace("index.html","") if pg!="404.html" else "/404.html"
    p=P(); p.feed(raw)
    url=DOM+path
    # 1 estrutura
    h1=[h for h in p.h if h[0]=="h1"]
    if len(h1)!=1: add("1.H1", pg, f"{len(h1)} H1")
    prev=1
    for t,txt in p.h:
        lv=int(t[1])
        if lv>prev+1: add("1.heading-pulo", pg, f"{t} após h{prev}: {txt[:50]}"); break
        prev=lv
    dup=[i for i,c in p.ids.items() if c>1]
    if dup: add("1.id-duplicado", pg, ",".join(dup[:5]))
    if "<!-- wp:" in raw or "<!-- /wp:" in raw: add("1.residuo-wp", pg, "comentário wp:")
    # 2 SEO
    can=re.search(r'<link rel="canonical" href="([^"]+)"',raw)
    if not can: add("2.canonical", pg, "ausente")
    elif pg!="404.html" and can.group(1)!=url: add("2.canonical", pg, f"{can.group(1)} ≠ {url}")
    rob=p.meta.get("robots","")
    if pg!="404.html" and "noindex" in rob and path not in("/obrigado/","/inscrito/"): add("2.noindex", pg, rob)
    if "max-image-preview:large" not in rob and "noindex" not in rob and pg!="404.html": add("2.robots-sem-max-image", pg, rob or "sem meta robots")
    tl=len(p.title); dl=len(p.meta.get("description",""))
    if tl>65: add("2.title-longo", pg, f"{tl} chars")
    if dl and (dl<70 or dl>165): add("2.desc-tamanho", pg, f"{dl} chars")
    if pg!="404.html":
        titles[p.title].append(pg); descs[p.meta.get("description","")].append(pg)
    # 3 schema: FAQ visível
    for s in p.ldjson:
        try: j=json.loads(s)
        except Exception: continue
        objs=j if isinstance(j,list) else [j]
        for o in objs:
            if isinstance(o,dict) and o.get("@type")=="FAQPage":
                for q in o.get("mainEntity",[]):
                    name=q.get("name","")
                    if name and name[:40] not in raw: add("3.faq-invisivel", pg, name[:60])
            if isinstance(o,dict) and o.get("@type") in("Article","BlogPosting"):
                dp=o.get("datePublished",""); dm=o.get("dateModified","")
                vis=re.search(r"Publicado em (\d{1,2}) de (\w+) de (\d{4})",raw)
                if dp and vis:
                    MES={"janeiro":1,"fevereiro":2,"março":3,"abril":4,"maio":5,"junho":6,"julho":7,"agosto":8,"setembro":9,"outubro":10,"novembro":11,"dezembro":12}
                    try:
                        if int(dp[:4])!=int(vis.group(3)) or int(dp[5:7])!=MES.get(vis.group(2),0) or int(dp[8:10])!=int(vis.group(1)):
                            add("9.data-incoerente", pg, f"schema {dp} x visível {vis.group(0)}")
                    except Exception: pass
                if "{{DATA" in raw: add("9.placeholder-data", pg, "{{DATA}} não substituído")
    # 4 links
    for a in p.links:
        h=a.get("href","")
        if a.get("target")=="_blank" and "noopener" not in a.get("rel",""): add("4.blank-sem-noopener", pg, h[:60])
        if h.startswith("/") and not h.startswith("//"):
            inbound[h.split("#")[0].split("?")[0]]+=1
        elif h.startswith(DOM):
            inbound[h[len(DOM):].split("#")[0].split("?")[0]]+=1
        if h.startswith("http://"): add("8.conteudo-misto-link", pg, h[:60])
    for an in p.anchors:
        if an and an not in p.ids and an!="conteudo": add("8.ancora-sem-id", pg, an)
    # 5 imagens
    for i,im in enumerate(p.imgs):
        src=im.get("src","")
        if src.startswith("http://"): add("8.conteudo-misto-img", pg, src[:60])
        if not im.get("width") or not im.get("height"): add("5.img-sem-dimensao", pg, src[-50:])
        if i>1 and im.get("loading")!="lazy" and im.get("fetchpriority")!="high" and "logo" not in src: add("5.img-sem-lazy", pg, src[-50:])
        if re.search(r"\.(jpe?g|png)(\?|$)",src) and "og" not in src and "favicon" not in src and "apple" not in src: add("5.img-nao-webp", pg, src[-50:])
    # 6 performance
    for s in p.scripts:
        if s.get("src") and not s.get("async") and not s.get("defer") and "type" not in s: add("6.script-bloqueante", pg, s["src"][-50:])
    for c in p.css:
        if c.get("rel")=="stylesheet":
            m=re.search(r"\?v=(\d+)",c.get("href","")); css_versions[m.group(1) if m else "SEM"]+=1
            if not m: add("6.css-sem-versao", pg, c.get("href",""))
    # 7 acessibilidade
    if not p.has_skip and pg!="404.html": add("7.sem-skip-link", pg, "")
    if p.landmarks["main"]!=1 and pg!="404.html": add("7.landmark-main", pg, f"{p.landmarks['main']} <main>")
    for b in p.buttons:
        if not b.get("aria-label") and b.get("aria-expanded") is None and "menu" in (b.get("class","")+b.get("id","")).lower(): add("7.menu-sem-aria", pg, "")
    for f in p.forms:
        for inp in p.inputs:
            pass
    for a in p.links:
        if "wa.me" in a.get("href","") and not a.get("aria-label") and not re.search(r"[A-Za-z]", a.get("title","")): pass
    # 9 conteúdo
    body=re.sub(r"<script.*?</script>|<style.*?</style>","",raw,flags=re.S)
    txt=re.sub(r"<[^>]+>"," ",body)
    wc=len(txt.split()); words[pg]=wc
    if "Psicólogo Jurídico" in raw and "Psicologia Jurídica" not in raw: add("9.titulacao", pg, "Psicólogo Jurídico")
    if "Perito do TJSP" in raw: add("9.titulacao", pg, "Perito do TJSP")
    if re.search(r"Especialista em Psicologia Jur[ií]dica", raw): add("9.titulacao", pg, "Especialista (CFP pendente)")
    if "Av. Paulista, 352" in raw or "Caixa Postal" in raw: add("11.endereco-antigo", pg, "")
    if pg!="404.html" and "CRP" not in raw: add("11.rodape-sem-crp", pg, "")
    if pg!="404.html" and "1471" not in raw: add("11.rodape-sem-endereco", pg, "")
    if pg!="404.html" and url not in sm_urls and "noindex" not in rob: add("4.fora-do-sitemap", pg, "")
    if pg!="404.html" and "G-9JZ4XB8LZB" not in raw and "gtag" not in raw: add("10.sem-ga4", pg, "")
    if "sameAs" in raw:
        for s in p.ldjson:
            m=re.findall(r'"sameAs":\s*\[(.*?)\]',s,flags=re.S)
            for x in m: R["14.sameAs"].append((pg, re.sub(r"\s","",x)[:200]))

for t,ps in titles.items():
    if len(ps)>1: add("2.title-duplicado", ps[0], f"{len(ps)}x: {t[:60]}")
for d,ps in descs.items():
    if len(ps)>1 and d: add("2.desc-duplicada", ps[0], f"{len(ps)}x")
for pg in PAGES:
    path="/"+pg.replace("index.html","")
    if pg!="404.html" and inbound[path]==0 and path!="/": add("4.orfa", pg, "0 links internos")
arts=[(w,pg) for pg,w in words.items() if ("/blog/" in pg or ("robison" in DOM or "perito" in DOM) and pg.count("/")==1)]
curtos=[(w,pg) for w,pg in arts if w<1200]
for w,pg in sorted(curtos)[:400]: add("9.artigo-curto", pg, f"{w} palavras")
# arquivos globais
for f in ["robots.txt","llms.txt","llms-full.txt","_headers","sitemap.xml","404.html"]:
    if not os.path.exists(f): add("13.arquivo-ausente", f, "")
if os.path.exists("robots.txt"):
    rb=open("robots.txt").read()
    for bot in ["GPTBot","ClaudeBot","PerplexityBot","Google-Extended"]:
        if bot not in rb: add("13.robots-ia", "robots.txt", f"{bot} não citado")
    if "Sitemap:" not in rb: add("13.robots-sitemap", "robots.txt", "")
css=glob.glob("assets/*.css")
for c in css:
    s=open(c,encoding="utf-8",errors="replace").read()
    if "prefers-reduced-motion" not in s: add("7.sem-reduced-motion", c, "")
    if "focus-visible" not in s: add("7.sem-focus-visible", c, "")
    m=re.search(r"(input|textarea)[^{]*\{[^}]*font-size:\s*([\d.]+)(px|rem|em)",s)
    if m and ((m.group(3)=="px" and float(m.group(2))<16) or (m.group(3)!="px" and float(m.group(2))<1)): add("7.input-fontsize", c, m.group(0)[:60])
hd=open("_headers").read() if os.path.exists("_headers") else ""
for h in ["Strict-Transport-Security","X-Frame-Options","Referrer-Policy","X-Content-Type-Options"]:
    if h not in hd: add("8.header-ausente", "_headers", h)
fila=glob.glob("_fila/*/index.html")
for f in fila:
    raw=open(f,encoding="utf-8",errors="replace").read()
    txt=re.sub(r"<[^>]+>"," ",re.sub(r"<script.*?</script>","",raw,flags=re.S)); w=len(txt.split())
    probs=[]
    if w<1200: probs.append(f"{w} palavras")
    if "FAQPage" not in raw: probs.append("sem FAQ")
    if "art-hero" not in raw and "capas/" not in raw and "wp-image" not in raw and "<img" not in raw.split("<h2")[0]: probs.append("sem capa")
    if probs: add("15.fila-padrao", f, "; ".join(probs))
print(json.dumps({"dominio":DOM,"paginas":len(PAGES),"fila":len(fila),"css_versions":dict(css_versions),
    "resumo":{k:len(v) for k,v in sorted(R.items())},
    "detalhe":{k:v[:12] for k,v in sorted(R.items())}}, ensure_ascii=False, indent=1))
