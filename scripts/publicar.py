# -*- coding: utf-8 -*-
"""Publica 1 artigo/dia da _fila para a raiz do site (perito)."""
import os, json, re, shutil, datetime, html, sys
HOJE = datetime.date.today()
MESES = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
fila = sorted(d for d in os.listdir('_fila') if os.path.isdir(os.path.join('_fila', d)))
if not fila:
    print('fila vazia'); sys.exit(0)
item = fila[0]
pasta = os.path.join('_fila', item)
meta = json.load(open(os.path.join(pasta, 'meta.json'), encoding='utf-8'))
slug, h1, desc = meta['slug'], meta['h1'], meta['desc']
t = open(os.path.join(pasta, 'index.html'), encoding='utf-8').read()
t = t.replace('{{DATA}}', HOJE.strftime('%d/%m/%Y'))
os.makedirs(slug, exist_ok=True)
open(os.path.join(slug, 'index.html'), 'w', encoding='utf-8').write(t)
shutil.rmtree(pasta)
# posts.json (novo primeiro)
posts = json.load(open('blog/posts.json', encoding='utf-8'))
posts.insert(0, {'slug': slug, 'titulo': h1, 'desc': desc, 'date': HOJE.isoformat()})
json.dump(posts, open('blog/posts.json', 'w', encoding='utf-8'), ensure_ascii=False)
# card no índice do blog
idx = open('blog/index.html', encoding='utf-8').read()
card = f'<div class="cartao"><p class="migalha">{HOJE.strftime("%d/%m/%Y")}</p><h3><a href="/{slug}/" style="text-decoration:none">{html.escape(h1)}</a></h3><p>{html.escape(desc)}</p></div>'
idx = re.sub(r'(<div class="grade-servicos"[^>]*>)', r'\1' + card, idx, count=1)
idx = re.sub(r'(\d+) artigos t', lambda m: f'{int(m.group(1))+1} artigos t', idx, count=1)
open('blog/index.html', 'w', encoding='utf-8').write(idx)
# sitemap
sm = open('sitemap.xml', encoding='utf-8').read()
url = f'https://peritoempsicologiaforense.com.br/{slug}/'
if url not in sm:
    sm = sm.replace('</urlset>', f'<url><loc>{url}</loc></url></urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
# feed
feed = open('blog/feed.xml', encoding='utf-8').read()
import email.utils
item_xml = f'<item><title>{html.escape(h1)}</title><link>{url}</link><guid>{url}</guid><pubDate>{email.utils.format_datetime(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))))}</pubDate><description>{html.escape(desc)}</description></item>'
feed = feed.replace('</description>', '</description>' + item_xml, 1)
open('blog/feed.xml', 'w', encoding='utf-8').write(feed)
print('publicado:', slug, '| restam na fila:', len(fila) - 1)
