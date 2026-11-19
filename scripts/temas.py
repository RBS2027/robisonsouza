#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Páginas-guia por tema (/temas/ e /temas/<tema>/) e o link "Tema deste artigo" em cada artigo.
Roda ao fim de publicar.py; é idempotente. Usa a página /publicacoes/ (ou /perguntas-frequentes/) como modelo."""
import re, os, html, glob, json, datetime
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(REPO)
DOM = re.search(r'<link rel="canonical" href="https://([^/]+)/', open('index.html', encoding='utf-8').read()).group(1)
HOJE = datetime.date.today().isoformat()
MARCA = {'robisonsouza.com.br': 'Robison Souza', 'peritoempsicologiaforense.com.br': 'Perito Forense', 'depoimentoespecial.com.br': 'Depoimento Especial', 'estudopsicossocial.com.br': 'Estudo Psicossocial'}.get(DOM, 'Robison Souza')
def tit(x):
    return x + ' | ' + MARCA if len(x + ' | ' + MARCA) <= 65 else x
# ordem = prioridade: o artigo entra no primeiro tema que casar com o título
TEMAS = [
 ('revisao-criminal', 'Revisão criminal', r'revis[aã]o criminal', 'Artigos sobre o parecer psicológico como prova nova na revisão criminal e sobre o reexame da prova psicológica que sustentou a condenação.'),
 ('depoimento-especial', 'Depoimento especial', r'depoimento especial|escuta especializada|oitiva|entrevista forense|entrevistador', 'Artigos sobre a oitiva de crianças e adolescentes prevista na Lei 13.431/2017: como é feita, o que observar no vídeo do depoimento especial e como o assistente técnico atua.'),
 ('estudo-psicossocial', 'Estudo psicossocial', r'psicossocial|estudo social', 'Artigos sobre o estudo psicossocial nas ações de família: como é feito, o que avalia, como formular quesitos e como analisar o laudo.'),
 ('alienacao-parental', 'Alienação parental', r'aliena[cç][aã]o parental|alienad|lei 12\.318', 'Artigos sobre alienação parental e a perícia prevista na Lei 12.318/2010: o que o laudo deve conter e como a prova técnica é examinada.'),
 ('falsas-acusacoes', 'Falsas acusações', r'fals[ao]s? (acusa|den[uú]n|mem[oó]r)|acusad[oa]|acusa[cç][aã]o|abuso sexual', 'Artigos sobre acusações em disputas judiciais: cronologia das escutas, hipóteses alternativas, falsas memórias e exame do método do laudo.'),
 ('contestacao-de-laudos', 'Laudos, pareceres e quesitos', r'laudo|parecer|quesito|per[ií]cia|perit[oa]|impugna', 'Artigos sobre laudo psicológico, parecer técnico, quesitos e perícia: prazos, requisitos da Resolução CFP nº 06/2019 e como contestar um laudo.'),
 ('assistente-tecnico', 'Assistente técnico', r'assistente t[eé]cnic|assist[eê]ncia t[eé]cnica', 'Artigos sobre o papel do psicólogo assistente técnico: quando indicar, prazos, honorários e limites da atuação.'),
 ('guarda-e-convivencia', 'Guarda e convivência', r'guarda|conviv[eê]ncia|visita|genitor|filh[oa]s?\b|pens[aã]o|div[oó]rcio', 'Artigos sobre guarda, convivência e os conflitos de família em que a prova psicológica pesa na decisão.'),
]
RESTO = ('psicologia-juridica', 'Psicologia jurídica e forense', None, 'Artigos sobre psicologia jurídica e forense em geral: conceitos, áreas de atuação e temas que não se encaixam nos demais grupos.')
def artigos():
    A = []
    for f in glob.glob('*/index.html') + glob.glob('blog/*/index.html'):
        t = open(f, encoding='utf-8').read()
        if not re.search(r'"@type"\s*:\s*"(Article|BlogPosting)"', t) or re.search(r'<meta name="robots" content="noindex', t): continue
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S); d = re.search(r'<meta name="description" content="([^"]*)"', t)
        dt = re.search(r'"datePublished"\s*:\s*"([^"]*)"', t)
        A.append({'f': f, 'url': '/' + f[:-10], 'h1': html.unescape(re.sub(r'<[^>]+>', '', h1.group(1)).strip()) if h1 else '', 'desc': html.unescape(d.group(1)) if d else '', 'data': dt.group(1) if dt else ''})
    return A
def classifica(A):
    G = {s: [] for s, *_ in TEMAS + [RESTO]}
    for a in A:
        for s, n, pat, _ in TEMAS:
            if re.search(pat, a['h1'], re.I): G[s].append(a); break
        else: G[RESTO[0]].append(a)
    for s, *_ in TEMAS:                      # tema pequeno demais vai para o grupo geral
        if 0 < len(G[s]) < 4: G[RESTO[0]] += G[s]; G[s] = []
    return {s: sorted(v, key=lambda a: a['data'], reverse=True) for s, v in G.items() if v}
def pagina(modelo, slug, titulo, h1, desc, rotulo, corpo, trilha):
    url = f'https://{DOM}/{slug}/' ; t = modelo; e = html.escape
    t = re.sub(r'<title>.*?</title>', f'<title>{e(titulo)}</title>', t, count=1, flags=re.S)
    for sel in ('name="description"', 'property="og:description"', 'name="twitter:description"'): t = re.sub(r'(<meta %s content=")[^"]*(")' % sel, lambda m: m.group(1) + e(desc) + m.group(2), t, count=1)
    for sel in ('property="og:title"', 'name="twitter:title"'): t = re.sub(r'(<meta %s content=")[^"]*(")' % sel, lambda m: m.group(1) + e(titulo) + m.group(2), t, count=1)
    t = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), t, count=1)
    t = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), t, count=1)
    t = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">', t, count=1)
    lds = [json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "description": desc, "url": url, "inLanguage": "pt-BR", "dateModified": HOJE}, ensure_ascii=False),
           json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": f'https://{DOM}{u}'} for i, (n, u) in enumerate(trilha)]}, ensure_ascii=False)]
    t = re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>\s*', '', t, flags=re.S)
    t = t.replace('</head>', ''.join(f'<script type="application/ld+json">{x}</script>' for x in lds) + '</head>', 1)
    t = re.sub(r'(<section class="heroi"[^>]*><div class="wrap">)(?:<div class="rotulo">.*?</div>)?<h1>.*?</h1>', lambda m: m.group(1) + f'<div class="rotulo">{e(rotulo)}</div><h1>{e(h1)}</h1>', t, count=1, flags=re.S)
    i = t.find('<article class="prosa">'); j = t.find('</article>', i); assert 0 < i < j
    t = t[:i] + '<article class="prosa">\n' + corpo + '\n' + t[j:]
    os.makedirs(slug, exist_ok=True); open(f'{slug}/index.html', 'w', encoding='utf-8').write(t)
TERMOS = [(r'depoimentos? especia(?:l|is)', 'depoimento-especial'), (r'estudos? psicossocia(?:l|is)', 'estudo-psicossocial'), (r'aliena[cç][aã]o parental', 'alienacao-parental'),
          (r'revis(?:ão|ões) crimina(?:l|is)', 'revisao-criminal'), (r'falsas? acusa(?:ção|ções)', 'falsas-acusacoes'), (r'assistentes? técnicos?', 'assistente-tecnico'),
          (r'guarda compartilhada', 'guarda-e-convivencia'), (r'quesitos', 'contestacao-de-laudos')]
def links_no_texto(G, termos, abre):
    """Liga, no corpo de cada artigo, a 1ª menção a outro tema à página-guia dele (máx. 2 por artigo). Idempotente."""
    n = 0
    for s, itens in G.items():
        for a in itens:
            t = open(a['f'], encoding='utf-8').read(); t0 = t
            t = re.sub(r'<a class="(?:tema-lk|gl-lk)" href="[^"]*">(.*?)</a>', r'\1', t, flags=re.S)
            i = t.find(abre); j = t.find('<p class="rede27-tema">')
            if i < 0 or j < i:
                if t != t0: open(a['f'], 'w', encoding='utf-8').write(t)
                continue
            corpo = t[i:j]; feitos = set()
            def troca_p(m):
                p = m.group(0)
                if len(feitos) >= 2 or '<a ' in p or re.search(r'seu processo tem|seu e-mail|100% online|WhatsApp|marque uma consulta|entre em contato|artigo t[eé]cnico por dia', p, re.I): return p
                partes = re.split(r'(<[^>]+>)', p)
                for k, seg in enumerate(partes):
                    if seg.startswith('<') or len(feitos) >= 2: continue
                    for pat, alvo in termos:
                        if alvo == s or alvo in feitos or alvo not in G: continue
                        mm = re.search(r'(?<![\wÀ-ÿ-])(' + pat + r')(?![\wÀ-ÿ-])', seg, re.I)
                        if mm:
                            seg = seg[:mm.start()] + f'<a class="tema-lk" href="/temas/{alvo}/">' + mm.group(1) + '</a>' + seg[mm.end():]
                            feitos.add(alvo); break
                    partes[k] = seg
                    if '<a class="tema-lk"' in seg: break
                return ''.join(partes)
            corpo = re.sub(r'<p>(?:(?!</p>).)*</p>', troca_p, corpo, flags=re.S)
            t = t[:i] + corpo + t[j:]
            if t != t0: open(a['f'], 'w', encoding='utf-8').write(t)
            n += len(feitos)
    return n
def main():
    base = 'publicacoes/index.html' if os.path.exists('publicacoes/index.html') else 'perguntas-frequentes/index.html'
    modelo = open(base, encoding='utf-8').read()
    modelo = re.sub(r'<!-- rede-2027 -->.*?</section>', '', modelo, flags=re.S)
    zap = re.search(r'href="(https://wa\.me/[^"]+)"', modelo).group(1)
    CTA = f'<p class="rbs-cta-2026"><strong>Precisa de análise do seu caso?</strong> Se o seu processo tem depoimento especial, estudo psicossocial ou revisão criminal, entre em contato e marque uma consulta. <a href="{zap}" rel="noopener">Marcar consulta pelo WhatsApp</a>.</p>'
    A = artigos(); G = classifica(A); NOME = {s: (n, intro) for s, n, _, intro in TEMAS + [RESTO]}
    e = html.escape
    for s, itens in G.items():
        n, intro = NOME[s]
        cards = ''.join(f'<div class="cartao"><h3><a href="{a["url"]}" style="text-decoration:none">{e(a["h1"])}</a></h3><p>{e(a["desc"])}</p></div>' for a in itens)
        outros = ' · '.join(f'<a href="/temas/{x}/">{e(NOME[x][0])}</a>' for x in G if x != s)
        corpo = (f'<p>{e(intro)} São {len(itens)} artigos, do mais recente para o mais antigo.</p>\n<h2 id="artigos">Todos os artigos sobre {e(n[0].lower() + n[1:])}</h2>\n'
                 f'<div class="grade-servicos" style="margin:1.2rem 0 2rem">{cards}</div>\n<h2 id="outros-temas">Outros temas</h2>\n<p>{outros} · <a href="/temas/">todos os temas</a></p>\n{CTA}')
        pagina(modelo, f'temas/{s}', tit(f'{n}: {len(itens)} artigos'), f'{n}: todos os artigos', f'{len(itens)} artigos sobre {n[0].lower() + n[1:]}, organizados em uma só página. {intro}'[:152].rsplit(' ', 1)[0] + '.', 'Guia por tema', corpo, [('Início', '/'), ('Temas', '/temas/'), (n, f'/temas/{s}/')])
    lista = ''.join(f'<div class="cartao"><h3><a href="/temas/{s}/" style="text-decoration:none">{e(NOME[s][0])}</a></h3><p>{len(v)} artigos. {e(NOME[s][1])}</p></div>' for s, v in G.items())
    pagina(modelo, 'temas', tit('Artigos organizados por tema'), 'Todos os artigos, organizados por tema', f'Os {len(A)} artigos deste site reunidos em {len(G)} temas: depoimento especial, estudo psicossocial, laudos, guarda, alienação parental e outros.'[:155], 'Guia por tema',
           f'<p>Este site reúne {len(A)} artigos técnicos. Para facilitar a leitura, eles estão agrupados em {len(G)} temas. Escolha o que tem relação com o seu processo.</p>\n<div class="grade-servicos grade-temas" style="margin:1.2rem 0 2rem">{lista}</div>\n{CTA}', [('Início', '/'), ('Temas', '/temas/')])
    # link "Tema deste artigo" em cada artigo
    n_art = 0
    for s, itens in G.items():
        marca = f'<p class="rede27-tema">Tema deste artigo: <a href="/temas/{s}/">{e(NOME[s][0])} — ver todos os artigos</a></p>'
        for a in itens:
            t = open(a['f'], encoding='utf-8').read(); t0 = t
            t = re.sub(r'<p class="rede27-tema">.*?</p>', '', t, flags=re.S)
            k = t.find('<h2 class="rede27-h"')
            if k < 0: continue
            t = t[:k] + marca + t[k:]
            if t != t0: open(a['f'], 'w', encoding='utf-8').write(t); n_art += 1
    n_lk = links_no_texto(G, TERMOS, '<article class="prosa">')
    # sitemap
    sm = open('sitemap.xml', encoding='utf-8').read()
    for u in ['temas'] + [f'temas/{s}' for s in G]:
        loc = f'https://{DOM}/{u}/'
        if loc not in sm: sm = sm.replace('</urlset>', f'<url><loc>{loc}</loc><lastmod>{HOJE}</lastmod></url></urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
    print('temas:', {s: len(v) for s, v in G.items()}, '| artigos com link de tema atualizado:', n_art, '| links no texto:', n_lk)
if __name__ == '__main__':
    main()
    import subprocess, sys
    subprocess.run([sys.executable, 'scripts/glossario_links.py'], check=False)
