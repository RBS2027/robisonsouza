#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Texto duplicado entre os sites do Instituto.
1) grava assets/impressao.json: uma impressão digital (amostra de trechos de 8 palavras) de cada página aberta ao Google;
2) baixa a impressão dos outros sites e aponta pares de páginas com 40% ou mais de texto igual.
Nunca interrompe a publicação: o que encontrar entra no relatório da verificação diária."""
import re, os, glob, html, json, hashlib, urllib.request
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(REPO)
EU = re.search(r'<link rel="canonical" href="https://([^/]+)/', open('index.html', encoding='utf-8').read()).group(1)
TODOS = [a + b for a, b in (('robisonsouza', '.com.br'), ('peritoempsicologia', 'forense.com.br'), ('depoimento', 'especial.com.br'), ('estudo', 'psicossocial.com.br'), ('assistente', '.tec.br'))]
LIMITE = 0.40; AMOSTRA = 16
IGNORAR = re.compile(r'/(politica-de-privacidade|obrigado|quem-sou|contato|404|temas)(/|$)')
def corpo(t):
    t = re.sub(r'<(script|style|header|footer|nav|form|aside)\b.*?</\1>', ' ', t, flags=re.S)
    m = re.search(r'<(article|main)\b.*?</\1>', t, re.S)
    if m: t = m.group(0)
    t = re.sub(r'<section class="rede27".*?</section>', ' ', t, flags=re.S)
    return re.sub(r'[^\wà-ÿ]+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)).lower()).split()
def impressao(p):
    s = set()
    for i in range(len(p) - 7):
        h = int(hashlib.md5(' '.join(p[i:i + 8]).encode()).hexdigest()[:10], 16)
        if h % AMOSTRA == 0: s.add(h)
    return sorted(s)
def local():
    F = {}
    for f in sorted(glob.glob('**/index.html', recursive=True)):
        if f.startswith(('_fila/', '_gerador/', 'scripts/')): continue
        t = open(f, encoding='utf-8').read()
        url = '/' + f[:-10]
        if 'content="noindex' in t or IGNORAR.search(url): continue
        imp = impressao(corpo(t))
        if len(imp) >= 12: F[url] = imp
    return F
def remoto(dom):
    base = os.environ.get('DUP_LOCAL')
    try:
        if base:
            pasta = {'robisonsouza.com.br': 'robisonsouza', TODOS[1]: 'perito', TODOS[2]: 'depoimentoespecial', TODOS[3]: 'estudopsicossocial', TODOS[4]: 'assistente'}[dom]
            return json.load(open(os.path.join(base, pasta, 'assets', 'impressao.json'), encoding='utf-8'))
        rq = urllib.request.Request(f'https://{dom}/assets/impressao.json', headers={'User-Agent': 'Mozilla/5.0 (verificacao-instituto)'})
        return json.loads(urllib.request.urlopen(rq, timeout=40).read().decode('utf-8'))
    except Exception as e:
        print(f'aviso: sem impressão de {dom} ({type(e).__name__})'); return None
def main():
    F = local()
    os.makedirs('assets', exist_ok=True)
    novo = json.dumps(F, separators=(',', ':'), sort_keys=True)
    cam = 'assets/impressao.json'
    if not os.path.exists(cam) or open(cam, encoding='utf-8').read() != novo: open(cam, 'w', encoding='utf-8').write(novo)
    idx = {}
    for u, imp in F.items():
        for h in imp: idx.setdefault(h, []).append(u)
    achados = []
    for dom in TODOS:
        if dom == EU: continue
        R = remoto(dom)
        if not R: continue
        for ru, rimp in R.items():
            cont = {}
            for h in rimp:
                for u in idx.get(h, ()): cont[u] = cont.get(u, 0) + 1
            for u, n in cont.items():
                frac = n / max(1, min(len(rimp), len(F[u])))
                if u == '/' and ru == '/': continue  # páginas iniciais: selos, avaliações reais do Google e formulário são iguais por definição
                if frac >= LIMITE: achados.append((round(frac * 100), u, f'https://{dom}{ru}'))
    achados.sort(reverse=True)
    print(f'DUPLICADOS_ENTRE_SITES={len(achados)}')
    if achados:
        L = [f'## ⚠️ Texto repetido entre sites ({len(achados)} par(es) com 40% ou mais de texto igual)']
        L += [f'- **{p}%** — `{u}` (este site) e {r}' for p, u, r in achados[:25]] + ['']
        for a in achados[:25]: print(' ', a)
        with open('/tmp/qa_report_body.md', 'a', encoding='utf-8') as fh: fh.write('\n' + '\n'.join(L))
if __name__ == '__main__': main()
