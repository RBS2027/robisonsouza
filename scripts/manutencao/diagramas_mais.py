# Leva os diagramas explicativos a artigos publicados cujo título trata do mesmo tema (um por artigo, sem repetir).
import json,re,glob,html,collections,sys
R='/home/claude/'
d=json.load(open(R+'robisonsouza/scripts/manutencao/diagramas.json',encoding='utf-8'))
NO=r'inss|previdenci|trabalh'
RG=[('917e80',r'depoimento especial|escuta especializada',r'como funciona|etapas|procedimento|passo|sala|protocolo|entrevist|rito|fases|audi[êe]ncia|grava[çc][ãa]o|v[íi]deo',None),
('6db801',r'estudo psicossocial|estudo social|estudo biopsicossocial',r'como funciona|etapas|prazo|quanto tempo|entrevista|visita|passo|fases|demora|como [ée] feito',None),
('03ac16',r'laudo|parecer|estudo',r'v[íi]cio|falha|erro|nulidade|contestar|contesta[çc][ãa]o|impugn|fragilidade|inconsist|nova per[íi]cia|segunda per[íi]cia',NO),
('df3e83',r'per[íi]cia|perito|laudo',r'prazo|quesito|nomea|15 dias|esclareciment|etapas|como funciona|passo a passo|fluxo',NO+r'|penal|criminal|crime'),
('018eaf',r'assistente t[ée]cnico',r'perito',None),
('4a6e12',r'guarda (compartilhada|unilateral|alternada)|tipos de guarda|modalidades de guarda',r'diferen[çc]a|tipos|modalidades| x | ou |qual|como funciona|o que [ée]',None),
('66292e',r'aliena[çc][ãa]o parental',r'medidas|art\. 6|san[çc]|multa|invers[ãa]o|consequ[êe]ncias jur[íi]dicas|o que diz a lei',None)]
FORA=r'erros? (comuns )?na formula|cadastro de peritos|f[ée]rias|fim de semana|pens[ãa]o|\bidade\b|quinzena|2 anos|^audi[êe]ncia|revis[ãa]o de guarda|visita assistida|forma[çc][ãa]o continuada|supervis[ãa]o|data retroativa|possess[óo]ria|atua[çc][ãa]o nacional|habilita[çc][ãa]o'
ALT={'df3e83':'8b2e08','03ac16':'ff31c6'}
tot=collections.Counter()
for r,pat in (('robisonsouza','*/index.html'),('perito','*/index.html'),('depoimentoespecial','blog/*/index.html'),('estudopsicossocial','blog/*/index.html'),('assistente','blog/*/index.html')):
    n=collections.Counter()
    for p in sorted(glob.glob(R+f'{r}/{pat}')):
        s=open(p,encoding='utf-8').read()
        if ('"BlogPosting"' not in s and '"Article"' not in s) or 'class="diagrama"' in s: continue
        t=html.unescape(re.sub(r'<[^>]+>','',re.search(r'<h1[^>]*>(.*?)</h1>',s,flags=re.S).group(1))).lower()
        if re.search(FORA,t): continue
        k=next((k for k,a,b,no in RG if re.search(a,t) and re.search(b,t) and not (no and re.search(no,t))),None)
        if not k or n[k]>=20: continue
        key=k if r=='robisonsouza' else ALT.get(k,k)
        a=s.find('<article');a=a if a>=0 else s.find('<main')
        h=s.find('<h2',a)
        if h<0: continue
        e=s.find('</p>',h)
        nx=s.find('<h2',h+3)
        if e<0 or (nx>0 and e>nx): continue
        s=s[:e+4]+'\n'+d[key]['svg']+'\n'+s[e+4:]
        s=re.sub(r'"dateModified": ?"[^"]*"','"dateModified": "2026-11-20"',s)
        open(p,'w',encoding='utf-8').write(s);n[k]+=1
    print(r,dict(n),sum(n.values()));tot[r]=sum(n.values())
print(sum(tot.values()))
