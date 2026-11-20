import os,re,sys
NEW='Atuação em todo o território nacional, online ou presencial.'
LIT=[
("atua&ccedil;&atilde;o 100% online em todo o Brasil &mdash; presencial apenas sob consulta","atua&ccedil;&atilde;o em todo o territ&oacute;rio nacional, online ou presencial"),
("atua&ccedil;&atilde;o 100% online em todo o Brasil &mdash; presencial sob consulta","atua&ccedil;&atilde;o em todo o territ&oacute;rio nacional, online ou presencial"),
("atuação 100% online em todo o Brasil — presencial apenas sob consulta","atuação em todo o território nacional, online ou presencial"),
("atuação 100% online em todo o Brasil — presencial sob consulta","atuação em todo o território nacional, online ou presencial"),
(", 100% online. Atendimento 100% online — presencial apenas sob consulta e acordo entre as partes.",", online ou presencial."),
("Atendimento 100% online — presencial apenas sob consulta e acordo entre as partes.",NEW),
("Atendimento 100% online — presencial apenas sob consulta e acordo…",NEW),
("Atendimento 100% online &mdash; presencial apenas sob consulta e acordo entre as partes.",NEW),
("análise do laudo, 100% online.","análise do laudo, online ou presencial."),
("parecer técnico, 100% online.","parecer técnico, online ou presencial."),
("Online é suficiente — presencial é exceção pontual","Online ou presencial, em todo o país"),
("Online é suficiente — presencial é exceção","Online ou presencial, em todo o país"),
("A atuação é online em todo o Brasil — presencial é exceção pontual, quando desejado","A atuação é em todo o Brasil, de forma online ou presencial"),
("Sim, 100% online em todo o Brasil; presencial apenas sob consulta e acordo entre as partes.","Sim, em todo o território nacional, de forma online ou presencial."),
("A atuação é 100% online, em todo o Brasil, com presencial apenas sob consulta","A atuação é em todo o território nacional, de forma online ou presencial"),
(" — o trabalho não depende de presença física em lugar nenhum.","."),
(" — nunca como necessidade técnica do serviço.","."),
]
RX=[
(re.compile(r'Toda a atuação (?:pode e deve ser realizada online|é realizada 100% online), sem exceção'),'Toda a atuação pode ser realizada online'),
(re.compile(r'Caso haja preferência específica por atendimento presencial, isso também é possível ([^<"]{2,60}?), mediante contratação e acordo entre as partes\.'),r'Quando o caso pedir, o trabalho presencial também é possível \1, mediante contratação e acordo entre as partes.'),
(re.compile(r'Caso haja preferência específica por atendimento presencial, o deslocamento até ([^<"]{2,40}?) também é possível, mediante'),r'Quando o caso pedir, o trabalho presencial com deslocamento até \1 também é possível, mediante'),
(re.compile(r'(?:O a|A)tendimento presencial (?:é possível apenas|só acontece) mediante consulta e acordo específico,[^.<"]{0,80}\.'),'O trabalho presencial também é possível, conforme o caso.'),
(re.compile(r'Presencial só ocorre mediante contratação e acordo específico,[^.<"]{0,80}\.'),'O trabalho presencial também é possível, conforme o caso.'),
]
POS=re.compile(r'toda a atuação é (realizada|feita) 100% online')
n=0;tot={}
for r in ['robisonsouza','perito','depoimentoespecial','estudopsicossocial','assistente']:
    c=0
    for d,ds,fs in os.walk('/home/claude/'+r):
        ds[:]=[x for x in ds if x not in('.git','node_modules')]
        for f in fs:
            if not f.endswith(('.html','.py','.json','.xml','.txt','.md','.js')): continue
            p=os.path.join(d,f)
            try: s=open(p,encoding='utf-8').read()
            except Exception: continue
            o=s
            for a,b in LIT: s=s.replace(a,b)
            for rx,b in RX: s=rx.sub(b,s)
            if s!=o and 'O trabalho presencial também é possível, conforme o caso.' in s: s=POS.sub(r'toda a atuação pode ser \1 online',s)
            if s!=o: open(p,'w',encoding='utf-8').write(s);c+=1
    tot[r]=c
print(tot)
