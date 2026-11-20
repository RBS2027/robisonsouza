import re,os,json,html,collections,sys
R={'robisonsouza':'robisonsouza.com.br','perito':'peritoempsicologiaforense.com.br','depoimentoespecial':'depoimentoespecial.com.br','estudopsicossocial':'estudopsicossocial.com.br','assistente':'assistente.tec.br'}
PROIB=[r'92088',r'gratuit',r'valores justos',r'an[áa]lise de credibilidade',r'09/2018',r'\bVitor\b',r'Psic[óo]logo Jur[íi]dico,? CRP',r'Perito do TJSP',r'Paulista,? 352',r'Caixa Postal',r'porte de arma',r'bari[áa]tric']
for r,dom in R.items():
    base='/home/claude/'+r;pages={}
    for d,ds,fs in os.walk(base):
        ds[:]=[x for x in ds if x not in('.git','node_modules','scripts')]
        if 'index.html' in fs: pages[d[len(base):]+'/']=open(d+'/index.html',encoding='utf-8',errors='ignore').read()
    allfiles=set()
    for d,ds,fs in os.walk(base):
        ds[:]=[x for x in ds if x!='.git']
        for f in fs: allfiles.add((d[len(base):]+'/'+f))
    red=open(base+'/_redirects',encoding='utf-8').read() if os.path.exists(base+'/_redirects') else ''
    redsrc=set(l.split()[0].rstrip('/')+'/' for l in red.splitlines() if l.strip() and not l.startswith('#') and len(l.split())>=2)
    sm=open(base+'/sitemap.xml',encoding='utf-8').read() if os.path.exists(base+'/sitemap.xml') else ''
    smu=set(re.findall(r'<loc>https://[^/]+(/[^<]*)</loc>',sm))
    C=collections.Counter();ex=collections.defaultdict(list)
    h1s=collections.defaultdict(list)
    for u,s in pages.items():
        fila=u.startswith('/_fila/');noidx=bool(re.search(r'<meta[^>]+robots[^>]+noindex',s)) or 'http-equiv="refresh"' in s
        m=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S)
        if m: h1s[re.sub(r'<[^>]+>','',m.group(1)).strip().lower()].append(u)
        if fila: continue
        for h in set(re.findall(r'href="(/[^"#?]*)',s)):
            if h.startswith('//'): continue
            t=h if h.endswith('/') or '.' in h.rsplit('/',1)[-1] else h+'/'
            if t not in pages and t not in allfiles and t.rstrip('/')+'/' not in redsrc and h not in allfiles and not h.startswith('/cdn-cgi'):
                C['link interno quebrado']+=1;ex['link interno quebrado'].append(u+' -> '+h)
        if noidx: continue
        if u not in smu and u!='/404/': C['fora do sitemap']+=1;ex['fora do sitemap'].append(u)
        c=re.search(r'<link rel="canonical" href="([^"]*)"',s)
        if not c: C['sem canonical']+=1;ex['sem canonical'].append(u)
        elif c.group(1)!='https://'+dom+u: C['canonical diferente']+=1;ex['canonical diferente'].append(u+' -> '+c.group(1))
        if not m: C['sem h1']+=1;ex['sem h1'].append(u)
        if len(re.findall(r'<h1[\s>]',s))>1: C['mais de um h1']+=1;ex['mais de um h1'].append(u)
        for j in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
            try: json.loads(j)
            except Exception: C['json-ld inválido']+=1;ex['json-ld inválido'].append(u)
        if 'og:image' not in s: C['sem og:image']+=1;ex['sem og:image'].append(u)
        for im in re.findall(r'<img\b[^>]*>',s):
            if 'alt=' not in im: C['img sem alt']+=1;ex['img sem alt'].append(u)
        txt=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
        for p in PROIB:
            if re.search(p,txt,re.I): C['termo: '+p]+=1;ex['termo: '+p].append(u)
        for w in re.findall(r'wa\.me/(\d+)',s):
            if w!='5512997402674': C['whatsapp diferente']+=1;ex['whatsapp diferente'].append(u+' '+w)
    for u in smu:
        if u not in pages and u not in allfiles: C['sitemap aponta p/ inexistente']+=1;ex['sitemap aponta p/ inexistente'].append(u)
        elif u in pages and re.search(r'<meta[^>]+robots[^>]+noindex',pages[u]): C['sitemap com noindex']+=1;ex['sitemap com noindex'].append(u)
    for h,us in h1s.items():
        if len(us)>1: C['h1 repetido']+=1;ex['h1 repetido'].append(' = '.join(us))
    print('==',r,len(pages),dict(C))
    if len(sys.argv)>1:
        for k,v in ex.items():
            print('  --',k)
            for x in v[:int(sys.argv[1])]: print('     ',x)
