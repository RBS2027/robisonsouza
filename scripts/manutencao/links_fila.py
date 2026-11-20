import os,re,html,collections,unicodedata,json
STOP=set('de da do das dos e em no na nos nas o a os as um uma para por com que como quando se ao aos sobre entre seu sua mais nao ou ser qual quais'.split())
def toks(s): return set(w for w in re.sub(r'[^a-z0-9 ]',' ',unicodedata.normalize('NFKD',s.lower()).encode('ascii','ignore').decode()).split() if len(w)>3 and w not in STOP)
LEAD=['Sobre este tema, veja também: ','Para aprofundar, leia também: ','Outros artigos relacionados a este ponto: ']
D=json.load(open('/home/claude/work/diagramas.json'))
G={'ap':D['66292e']['svg'],'vicios':D['03ac16']['svg'],'de':D['917e80']['svg'],'ep':D['6db801']['svg'],'guarda':D['4a6e12']['svg'],'pxa':D['018eaf']['svg'],'fluxo':D['df3e83']['svg']}
def tema(sl):
    if 'alienacao-parental' in sl: return 'ap'
    if re.search(r'contest|impugn|prejudic|vicio|erro|falh|nulidade|desfavoravel',sl) and re.search(r'laudo|estudo|relatorio|pericia',sl): return 'vicios'
    if re.search(r'depoimento-especial|escuta',sl): return 'de'
    if re.search(r'psicossocial',sl): return 'ep'
    if re.search(r'assistente-tecnico|quesito|parecer',sl): return 'pxa'
    if 'guarda' in sl: return 'guarda'
    if re.search(r'pericia|perito|laudo',sl): return 'fluxo'
INT=[(r'assistente-tecnico',3),(r'contest|impugn',3),(r'quanto-custa|honorarios|valor',3),(r'contratar|preciso|urgente',3),(r'parecer',2),(r'revisao-criminal',2),(r'falsa-acusacao|acusado',2),(r'quesito',2),(r'defesa',2),(r'laudo',1),(r'desfavoravel|prejudic',2)]
def info(p,u):
    s=open(p,encoding='utf-8').read()
    a=s.find('<article');b=s.find('<!-- rede-2027',a)
    if a<0: return None
    if b<0: b=s.find('</article>',a)
    m=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S)
    if b<0 or not m: return None
    h1=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',m.group(1)))).strip()
    t=re.search(r'Tema deste artigo: <a href="(/temas/[^"]+)"',s);art=s[a:b]
    out=set(h if h.endswith('/') else h+'/' for h in re.findall(r'href="(/[^"#?]*)',art))-{u}
    return dict(p=p,h1=h1,tema=t.group(1) if t else '',out=out,tk=toks(h1),done='class="veja-tb"' in art,diag='figure class="diagrama"' in s)
for r in ['robisonsouza','perito','depoimentoespecial','estudopsicossocial','assistente']:
    base='/home/claude/'+r;P={}
    for d,ds,fs in os.walk(base):
        ds[:]=[x for x in ds if x not in('.git','_fila','scripts','assets','temas')]
        if 'index.html' not in fs: continue
        s=open(d+'/index.html',encoding='utf-8').read()
        if re.search(r'<meta[^>]+robots[^>]+noindex',s) or not re.search(r'"@type": ?"(Article|BlogPosting)"',s): continue
        u=d[len(base):]+'/'
        if re.search(r'psicologia-forense-(em|no|na)-|cadastro-de-peritos|assistente-tecnico-em-(depoimento-especial|estudo-psicossocial)-(em|no|na)-',u): continue
        x=info(d+'/index.html',u)
        if x: P[u]=x
    inb=collections.Counter()
    for u,x in P.items():
        for h in x['out']:
            if h in P: inb[h]+=1
    nl=nd=0;got=collections.Counter();dcount=collections.Counter()
    F=sorted(os.listdir(base+'/_fila')) if os.path.isdir(base+'/_fila') else []
    for i,d in enumerate(F):
        p=f'{base}/_fila/{d}/index.html'
        if not os.path.exists(p): continue
        x=info(p,'/_fila/'+d+'/')
        if not x: continue
        s=open(p,encoding='utf-8').read();ch=False
        if r!='assistente' and not x['done'] and len(x['out'])<12:
            c=[u for u,y in P.items() if u not in x['out'] and got[u]<3 and (not x['tema'] or y['tema']==x['tema'])]
            c=[(len(x['tk']&P[u]['tk'])/(len(x['tk']|P[u]['tk']) or 1),u) for u in c]
            c=sorted([z for z in c if z[0]>0],key=lambda z:(-z[0],inb[z[1]]+got[z[1]]))[:2]
            if c:
                a=s.find('<article');b=s.find('<!-- rede-2027',a)
                if b<0: b=s.find('</article>',a)
                art=s[a:b];m=None
                for mm in re.finditer(r'<h2[^>]*>(.*?)</h2>',art,re.S):
                    if re.search(r'perguntas|frequentes|faq',mm.group(1),re.I): m=mm;break
                pos=a+m.start() if m else b
                links=[f'<a href="{u}">{html.escape(P[u]["h1"],quote=False)}</a>' for _,u in c]
                s=s[:pos]+f'<p class="veja-tb">{LEAD[i%3]}{" e ".join(links)}.</p>\n'+s[pos:]
                for _,u in c: got[u]+=1
                nl+=len(c);ch=True
        sl=re.sub(r'^\d+(-\d+)?-','',d);t=tema(sl);sc=sum(w for rx,w in INT if re.search(rx,sl))
        if t and sc>=3 and not x['diag'] and dcount[t]<4 and sum(dcount.values())<12:
            a=s.find('<article');h=s.find('<h2',a);e=s.find('</p>',h);nx=s.find('<h2',h+3)
            if a>=0 and h>=0 and e>=0 and not (nx>0 and e>nx):
                g=G[t]
                if r!='robisonsouza': g=re.sub(r'href="(/[^"#?]*)"',lambda m:m.group(0) if os.path.exists(base+m.group(1)+'index.html') else 'href="https://robisonsouza.com.br'+m.group(1)+'"',g)
                s=s[:e+4]+'\n'+g+'\n'+s[e+4:];dcount[t]+=1;nd+=1;ch=True
        if ch: open(p,'w',encoding='utf-8').write(s)
    print(r,'fila',len(F),'| links novos',nl,'| diagramas',nd)
