#!/usr/bin/env python3
"""Insere, nas páginas-pilar, a lista de artigos da série (links de entrada). Idempotente."""
import re, ast, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src=open(os.path.join(ROOT,'scripts','serie_jw.py')).read()
S=ast.literal_eval(re.search(r'SERIE = (\[.*?\n\])',src,re.S).group(1))
PRE={'rs':'','pe':'','de':'blog/','ep':'blog/','as':'blog/'}
HUBS={
 'rs':{'falsas-acusacoes-o-olhar-da-psicologia-forense':['Falsas Acusações'],
       'como-provar-falsa-acusacao':['Psicologia do Testemunho','Conflito Familiar','Crimes Sexuais','Psicologia Forense'],
       'parecer-psicologico-para-revisao-criminal':['Revisão Criminal'],
       'documentario-absolvido-mas-morto':['Saúde Mental','Saúde Mental do Acusado']},
 'pe':{'pericia-em-falsas-acusacoes-como-o-perito-analisa-a-consistencia-do-relato':['Perícia Psicológica','Método Pericial'],
       'indenizacao-por-falsa-acusacao-como-a-pericia-psicologica-demonstra-o-dano':['Perícia do Dano','Dano Psíquico','Violência Doméstica']},
 'de':{'analise-de-entrevista-forense':None},
 'ep':{'blog/falsas-acusacoes-e-o-estudo-psicossocial':None},
 'as':{'criminal':['Processo Criminal','Estratégia de Defesa','Fase Policial','Tribunal do Júri','Crimes Contra a Liberdade','Relação com o Cliente'],
       'assistente-tecnico-na-revisao-criminal':['Revisão Criminal'],
       'familia':['Família']},
}
site={'robisonsouza':'rs','perito':'pe','depoimentoespecial':'de','estudopsicossocial':'ep','assistente':'as'}[os.path.basename(ROOT)]
n=0
for hub,labels in HUBS[site].items():
    f=os.path.join(ROOT,hub,'index.html')
    if not os.path.isfile(f): print('sem página',hub); continue
    t=open(f,encoding='utf-8').read()
    base=re.sub(r'\n?<!-- hub-serie -->.*?<!-- /hub-serie -->\n?','',t,flags=re.S)
    itens=[s for s in S if s[0]==site and (labels is None or s[3] in labels)
           and os.path.isfile(os.path.join(ROOT,PRE[site]+s[1],'index.html'))
           and f'href="/{PRE[site]}{s[1]}/"' not in base and PRE[site]+s[1]!=hub]
    if not itens:
        if base!=t: open(f,'w',encoding='utf-8').write(base); n+=1
        continue
    lis=''.join(f'<li><a href="/{PRE[site]}{s[1]}/">{s[2]}</a></li>' for s in itens)
    bloco=f'<!-- hub-serie --><section class="hub-serie" aria-label="Artigos da série"><h2 id="serie-de-artigos">Artigos sobre este tema</h2><ul>{lis}</ul></section><!-- /hub-serie -->\n'
    for marca in ('<!-- serie-jw -->','<!-- rede-2027 -->'):
        i=base.find(marca)
        if i>=0: break
    else:
        i=base.rfind('</main>')
        if i<0: print('sem âncora',hub); continue
    novo=base[:i]+bloco+base[i:]
    if novo!=t: open(f,'w',encoding='utf-8').write(novo); n+=1
    print(hub,len(itens))
print('hub-serie:',n,'página(s) atualizada(s)')
