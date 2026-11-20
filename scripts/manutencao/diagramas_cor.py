# Acerta as cores dos diagramas à paleta (azul-marinho + cobre) e o tamanho dos títulos das colunas.
import re,glob,json
def fix(svg):
    svg=re.sub(r'(<text[^>]*fill=")#C9A227(")',r'\1#F3EEE7\2',svg)
    svg=svg.replace('#C9A227','#A66F3E').replace('#1c4a3a','#24334a').replace('#4a5a55','#566173')
    svg=re.sub(r'(<text x="(?:206|554)\.0" y="99" text-anchor="middle" font-size=")22(")',r'\g<1>18\2',svg)
    return svg
if __name__=='__main__':
    n=0
    for r in ['robisonsouza','perito','depoimentoespecial','estudopsicossocial','assistente']:
        for p in glob.glob(f'/home/claude/{r}/**/index.html',recursive=True):
            s=open(p,encoding='utf-8').read()
            if 'class="diagrama"' not in s: continue
            t=re.sub(r'<figure class="diagrama">.*?</figure>',lambda m:fix(m.group(0)),s,flags=re.S)
            if t!=s: open(p,'w',encoding='utf-8').write(t);n+=1
    j='/home/claude/robisonsouza/scripts/manutencao/diagramas.json';d=json.load(open(j,encoding='utf-8'))
    for k in d: d[k]['svg']=fix(d[k]['svg'])
    json.dump(d,open(j,'w',encoding='utf-8'),ensure_ascii=False,indent=1);print(n)
