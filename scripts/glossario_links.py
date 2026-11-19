#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liga, no texto dos artigos, a 1ª menção a termos do glossário (máx. 2 por artigo) à definição em /glossario/#termo.
Dá âncora (id) a cada termo do glossário. Idempotente; é chamado ao final de scripts/temas.py."""
import re, os, glob, html, unicodedata
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(REPO)
GENERICOS = {'assistente técnico', 'quesitos', 'estudo psicossocial', 'depoimento especial', 'alienação parental', 'guarda compartilhada', 'laudo pericial', 'parecer técnico',
             'credibilidade', 'simetria', 'esclarecimentos', 'falsa acusação', 'revisão criminal', 'perita do juízo', 'laudo psicossocial', 'melhor interesse da criança', 'entrevista de avaliação'}
BOILER = re.compile(r'seu processo tem|seu e-mail|100% online|online ou presencial|WhatsApp|marque uma consulta|entre em contato|artigo t[eé]cnico por dia', re.I)
def slug(x):
    x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', x).strip('-')
def termos():
    f = 'glossario/index.html'
    if not os.path.exists(f): return []
    t = open(f, encoding='utf-8').read(); t0 = t
    a = t.find('<h1'); b = t.find('<!-- rede-2027 -->'); b = b if b > 0 else t.find('<footer')
    usados = set(re.findall(r'\bid="([^"]+)"', t)); T = []; vistos = set()
    def marca(m):
        tag, attrs, txt = m.group(1), m.group(2), m.group(3)
        nome = html.unescape(re.sub(r'<[^>]+>', '', txt)).strip()
        mid = re.search(r'\bid="([^"]+)"', attrs)
        if mid: i = mid.group(1)
        else:
            i = slug(nome) or 'termo'; k = i; n = 2
            while k in usados: k = f'{i}-{n}'; n += 1
            i = k; usados.add(i); attrs += f' id="{i}"'
        base = re.split(r'\s[—(]', nome)[0].strip()
        if base.lower() not in vistos and base.lower() not in GENERICOS and len(base) >= 7:
            vistos.add(base.lower()); T.append((base, i))
        return f'<{tag}{attrs}>{txt}</{tag}>'
    meio = re.sub(r'<(h3|dt)((?:\s[^>]*)?)>(.*?)</\1>', marca, t[a:b], flags=re.S)
    t = t[:a] + meio + t[b:]
    if t != t0: open(f, 'w', encoding='utf-8').write(t)
    return sorted(T, key=lambda x: -len(x[0]))
def main():
    T = termos(); n = 0; arts = 0
    if not T: print('glossário: sem termos'); return
    for f in glob.glob('*/index.html') + glob.glob('blog/*/index.html'):
        if f.startswith(('glossario/', 'temas/', '_fila/')): continue
        t = open(f, encoding='utf-8').read(); t0 = t
        if not re.search(r'"@type"\s*:\s*"(Article|BlogPosting)"', t): continue
        t = re.sub(r'<a class="gl-lk" href="[^"]*">(.*?)</a>', r'\1', t, flags=re.S)
        m = re.search(r'<article class="pros[ae]">', t); j = t.find('<!-- rede-2027 -->')
        if m and j > m.start():
            i = m.start(); feitos = []
            def troca_p(mm):
                p = mm.group(0)
                if len(feitos) >= 2 or '<a ' in p or BOILER.search(p): return p
                partes = re.split(r'(<[^>]+>)', p)
                for k, seg in enumerate(partes):
                    if seg.startswith('<'): continue
                    for nome, hid in T:
                        if hid in feitos: continue
                        x = re.search(r'(?<![\wÀ-ÿ-])(' + re.escape(nome) + r')(?![\wÀ-ÿ-])', seg, re.I)
                        if x:
                            partes[k] = seg[:x.start()] + f'<a class="gl-lk" href="/glossario/#{hid}">' + x.group(1) + '</a>' + seg[x.end():]
                            feitos.append(hid); return ''.join(partes)
                return p
            corpo = re.sub(r'<p>(?:(?!</p>).)*</p>', troca_p, t[i:j], flags=re.S)
            t = t[:i] + corpo + t[j:]; n += len(feitos); arts += bool(feitos)
        if t != t0: open(f, 'w', encoding='utf-8').write(t)
    print(f'glossário: {len(T)} termos ligáveis | {n} links em {arts} artigos')
if __name__ == '__main__': main()
