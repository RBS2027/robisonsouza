# -*- coding: utf-8 -*-
"""Revisão diária do site perito: fila íntegra, páginas com CSS, sem {{DATA}} publicado."""
import os, json, sys, glob
prob = []
for d in sorted(glob.glob('_fila/*/')):
    if not os.path.exists(d + 'index.html'): prob.append(d + ': sem index.html')
    if not os.path.exists(d + 'meta.json'): prob.append(d + ': sem meta.json')
    else:
        try:
            m = json.load(open(d + 'meta.json', encoding='utf-8'))
            assert m.get('slug') and m.get('h1') and m.get('desc')
        except Exception:
            prob.append(d + ': meta.json invalido')
n = 0
for f in glob.glob('**/index.html', recursive=True):
    t = open(f, encoding='utf-8').read()
    n += 1
    if '/assets/site.css' not in t: prob.append(f + ': sem css')
    if '_fila' not in f and '{{DATA}}' in t: prob.append(f + ': {{DATA}} nao substituido')
fila = len(glob.glob('_fila/*/'))
if fila < 5: prob.append(f'FILA BAIXA: {fila} artigos restantes')
print(f'Revisao perito: {n} paginas | fila: {fila}')
if prob:
    print('REVISAO REPROVOU:', ' | '.join(prob[:8])); sys.exit(1)
print('Tudo OK')
