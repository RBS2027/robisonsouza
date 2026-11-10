#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza, nas páginas de serviço, o bloco com os artigos mais recentes de cada tema.
Roda ao fim de publicar.py; é idempotente (substitui o bloco entre os marcadores cluster-2026)."""
import re, json, os, html
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(REPO)
CLUSTERS = [('assistente-tecnico-em-estudo-psicossocial', 'Artigos sobre estudo psicossocial', 'psicossocial|estudo social', None), ('assistente-tecnico-em-depoimento-especial', 'Artigos recentes sobre depoimento especial', 'depoimento especial|escuta especializada|entrevista forense', None), ('estudos-psicossociais', 'Artigos sobre estudo psicossocial', 'psicossocial|estudo social', None), ('depoimento-especial', 'Artigos recentes sobre depoimento especial', 'depoimento especial|escuta especializada|entrevista forense', None), ('parecer-psicologico-para-revisao-criminal', 'Artigos sobre prova psicológica no processo criminal', 'revisão criminal|condena|criminal|júri|inquérito|penal', 'depoimento especial'), ('como-contestar-um-laudo-psicologico-judicial', 'Artigos sobre contestação de laudos e documentos psicológicos', 'laudo|impugna|contest|quesito|parecer', 'depoimento especial'), ('acusado-injustamente', 'Artigos sobre falsas acusações', 'fals[ao]s? |acusa|inocen', 'depoimento especial e'), ('assistente-tecnico-em-falsas-acusacoes', 'Artigos sobre falsas acusações', 'fals[ao]s? |acusa|inocen', 'depoimento especial e'), ('alienacao-parental-o-que-e-sinais-e-a-lei-12-318-2010', 'Artigos sobre alienação parental e violência psicológica', 'aliena|violência psicológica|maus-tratos|negligência', None), ('assistente-tecnico-em-alienacao-parental-e-violencias', 'Artigos sobre alienação parental e violências', 'aliena|violência|maus-tratos|negligência|abuso', 'depoimento especial e')]
def main():
    P = json.load(open('blog/posts.json', encoding='utf-8'))
    for pagina, titulo, pat, excl in CLUSTERS:
        f = pagina + '/index.html'
        if not os.path.exists(f): continue
        sel = [p for p in P if re.search(pat, p['titulo'], re.I) and p['slug'] != pagina
               and not (excl and re.search(excl, p['titulo'], re.I)) and os.path.isdir(p['slug'])]
        sel = sorted(sel, key=lambda p: p.get('date', ''), reverse=True)[:12]
        if len(sel) < 4: continue
        cards = ''.join('<div class="cartao"><h3><a href="/%s/">%s</a></h3></div>' % (p['slug'], html.escape(p['titulo'])) for p in sel)
        bloco = '<!-- cluster-2026 --><h2 id="artigos-sobre-o-tema">%s</h2><div class="grade-servicos" style="margin:1.2rem 0 2rem">%s</div><!-- /cluster-2026 -->\n' % (html.escape(titulo), cards)
        t = open(f, encoding='utf-8').read()
        t = re.sub(r'<!-- cluster-2026 -->.*?<!-- /cluster-2026 -->\n?', '', t, flags=re.S)
        a0 = t.find('<article'); a1 = t.find('</article>')
        c = [t.find(m, a0) for m in ('<div class="faixa-cta">', '<p class="rbs-cta-2026">', '<!-- rbs-nav-2026 -->')]
        c = [x for x in c if a0 < x < a1]
        i = min(c) if c else a1
        open(f, 'w', encoding='utf-8').write(t[:i] + bloco + t[i:])
if __name__ == '__main__':
    main()
