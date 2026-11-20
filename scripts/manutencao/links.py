import os,re,html,collections,unicodedata,sys
STOP=set('de da do das dos e em no na nos nas o a os as um uma para por com que como quando se ao aos sobre entre the seu sua mais não nao ou é ser qual quais'.split())
def toks(s): return set(w for w in re.sub(r'[^a-z0-9 ]',' ',unicodedata.normalize('NFKD',s.lower()).encode('ascii','ignore').decode()).split() if len(w)>3 and w not in STOP)
LEAD=['Sobre este tema, veja também: ','Para aprofundar, leia também: ','Outros artigos relacionados a este ponto: ']
tot={}
for r in ['robisonsouza','perito','depoimentoespecial','estudopsicossocial']:
    P={}
    for d,ds,fs in os.walk('/home/claude/'+r):
        ds[:]=[x for x in ds if x not in('.git','_fila','scripts','assets','temas')]
        if 'index.html' not in fs: continue
        p=d+'/index.html';s=open(p,encoding='utf-8').read()
        if re.search(r'<meta[^>]+robots[^>]+noindex',s) or not re.search(r'"@type": ?"(Article|BlogPosting)"',s): continue
        u=d[len('/home/claude/'+r):]+'/'
        a=s.find('<article');b=s.find('<!-- rede-2027',a)
        if a<0: continue
        if b<0: b=s.find('</article>',a)
        if b<0: continue
        m=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S)
        if not m: continue
        h1=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',m.group(1)))).strip()
        t=re.search(r'Tema deste artigo: <a href="(/temas/[^"]+)"',s)
        art=s[a:b]
        out=set(h if h.endswith('/') else h+'/' for h in re.findall(r'href="(/[^"#?]*)',art))-{u}
        local=bool(re.search(r'psicologia-forense-(em|no|na)-|cadastro-de-peritos|assistente-tecnico-em-(depoimento-especial|estudo-psicossocial)-(em|no|na)-',u))
        P[u]=dict(p=p,h1=h1,tema=t.group(1) if t else '',out=out,tk=toks(h1),a=a,b=b,local=local,done='class="veja-tb"' in art)
    inb=collections.Counter()
    for u,x in P.items():
        for h in x['out']:
            if h in P: inb[h]+=1
    need={u:max(0,2-inb[u]) for u,x in P.items() if not x['local']}
    add=collections.defaultdict(list)
    def score(src,dst): 
        a,b=P[src]['tk'],P[dst]['tk'];return len(a&b)/(len(a|b) or 1)
    # 1) alvos pouco citados recebem 2 links de artigos do mesmo tema
    for dst in sorted([u for u,n in need.items() if n>0],key=lambda u:inb[u]):
        cands=[s for s,x in P.items() if s!=dst and not x['done'] and not x['local'] and x['tema']==P[dst]['tema'] and dst not in x['out'] and dst not in add[s] and len(add[s])<3 and len(x['out'])+len(add[s])<12]
        cands.sort(key=lambda s:(-score(s,dst),len(P[s]['out'])+len(add[s])))
        for s in cands[:need[dst]]:
            if score(s,dst)<=0: continue
            add[s].append(dst)
    # 2) artigos com 0-2 links ganham até 3
    for src,x in P.items():
        if x['done'] or x['local']: continue
        while len(x['out'])+len(add[src])<3 and len(add[src])<3:
            c=[d for d,y in P.items() if d!=src and not y['local'] and d not in x['out'] and d not in add[src] and y['tema']==x['tema']]
            if not c: break
            c.sort(key=lambda d:(-score(src,d),inb[d]));
            if score(src,c[0])<=0: break
            add[src].append(c[0])
    n=l=0
    for i,(src,ds) in enumerate(sorted(add.items())):
        if not ds: continue
        x=P[src];s=open(x['p'],encoding='utf-8').read()
        a=s.find('<article');b=s.find('<!-- rede-2027',a)
        if b<0: b=s.find('</article>',a)
        art=s[a:b]
        # antes das perguntas frequentes, se houver; senão, no fim do texto
        m=None
        for mm in re.finditer(r'<h2[^>]*>(.*?)</h2>',art,re.S):
            if re.search(r'perguntas|frequentes|faq',mm.group(1),re.I): m=mm;break
        pos=a+m.start() if m else b
        links=[f'<a href="{d}">{html.escape(P[d]["h1"],quote=False)}</a>' for d in ds]
        txt=links[0] if len(links)==1 else ', '.join(links[:-1])+' e '+links[-1]
        par=f'<p class="veja-tb">{LEAD[i%3]}{txt}.</p>\n'
        s=s[:pos]+par+s[pos:];open(x['p'],'w',encoding='utf-8').write(s);n+=1;l+=len(ds)
    # medir depois
    inb2=collections.Counter(inb)
    for src,ds in add.items():
        for d in ds: inb2[d]+=1
    tot[r]=(n,l,sum(1 for u in need if inb[u]<=1),sum(1 for u in need if inb2[u]<=1),sum(1 for u,x in P.items() if not x['local'] and len(x['out'])<=2),sum(1 for u,x in P.items() if not x['local'] and len(x['out'])+len(add[u])<=2))
for r,v in tot.items(): print(r,'artigos alterados',v[0],'links novos',v[1],'| pouco citados:',v[2],'->',v[3],'| com 0-2 links:',v[4],'->',v[5])
