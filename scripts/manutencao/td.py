import re,os,sys,html,collections
R=['robisonsouza','perito','depoimentoespecial','estudopsicossocial','assistente']
rows=[]
for r in R:
    for d,_,fs in os.walk('/home/claude/'+r):
        if '/.git' in d or '/node_modules' in d: continue
        for f in fs:
            if f!='index.html': continue
            p=os.path.join(d,f);s=open(p,encoding='utf-8',errors='ignore').read()
            if re.search(r'<meta[^>]+robots[^>]+noindex',s) or 'http-equiv="refresh"' in s: continue
            t=re.search(r'<title>(.*?)</title>',s,re.S);m=re.search(r'<meta\s+name="description"\s+content="(.*?)"',s,re.S)
            t=html.unescape(t.group(1).strip()) if t else '';m=html.unescape(m.group(1).strip()) if m else ''
            rows.append((r,p.replace('/home/claude/'+r,'').replace('index.html',''),t,m))
if __name__=='__main__':
    for r in R:
        rr=[x for x in rows if x[0]==r];ct=collections.Counter(x[2] for x in rr);cd=collections.Counter(x[3] for x in rr)
        tl=[x for x in rr if len(x[2])>65];ts=[x for x in rr if len(x[2])<30];dl=[x for x in rr if len(x[3])>165];ds=[x for x in rr if len(x[3])<110]
        dt=sum(v for v in ct.values() if v>1);dd=sum(v for v in cd.values() if v>1)
        print(r,len(rr),'tit>65:',len(tl),'tit<30:',len(ts),'desc>165:',len(dl),'desc<110:',len(ds),'tit dup:',dt,'desc dup:',dd)
