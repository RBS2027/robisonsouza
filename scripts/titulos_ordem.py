#!/usr/bin/env python3
"""Corrige saltos na ordem dos títulos (ex.: h3 logo após h1) com um título intermediário
visível só para leitores de tela. Idempotente; roda ao fim do publicar.py."""
import re, os, glob
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EST='position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0'
def rotulo(rel):
    if rel.startswith(('blog/','temas/')): return 'Artigos'
    for k,v in (('glossario','Termos'),('perguntas-frequentes','Perguntas e respostas'),('quem-sou','Sobre'),
                ('contato','Canais de contato'),('obrigado','Próximos passos'),('inscrito','Próximos passos'),('politica','Tópicos')):
        if k in rel: return v
    return 'Conteúdo desta página'
H=re.compile(r'<h([1-6])\b[^>]*>',re.I)
ABRE=re.compile(r'<(a|article|li|div)\b[^>]*>',re.I)
def fora(t):
    return [(m.start(),m.end()) for m in re.finditer(r'<(script|style)\b[\s\S]*?</\1>',t,re.I)]
n=0
for f in glob.glob(os.path.join(ROOT,'**','index.html'),recursive=True):
    rel=os.path.relpath(f,ROOT)
    if rel.startswith(('_fila','.git','node_modules')): continue
    orig=open(f,encoding='utf-8',errors='ignore').read()
    t=re.sub(r'<h[2-5] class="vh-ord"[^>]*>[^<]*</h[2-5]>','',orig)
    for _ in range(6):
        ign=fora(t)
        hs=[(int(m.group(1)),m.start()) for m in H.finditer(t) if not any(a<=m.start()<b for a,b in ign)]
        alvo=next(((a,b) for a,b in zip(hs,hs[1:]) if b[0]-a[0]>1),None)
        if not alvo: break
        (na,pant),(nb,pos)=alvo
        ins=pos
        ini=max(pant+4,pos-500)
        janela=t[ini:pos]
        cands=[m for m in ABRE.finditer(janela)]
        for m in reversed(cands):
            tag=m.group(1).lower()
            if f'</{tag}>' not in janela[m.end():].lower():
                ins=ini+m.start(); break
        t=t[:ins]+f'<h{na+1} class="vh-ord" style="{EST}">{rotulo(rel)}</h{na+1}>'+t[ins:]
    if t!=orig:
        open(f,'w',encoding='utf-8').write(t); n+=1
print('titulos-ordem:',n,'página(s) ajustada(s)')
