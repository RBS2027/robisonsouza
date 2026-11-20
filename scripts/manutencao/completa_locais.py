# Completa as páginas de estado (estudopsicossocial) e de cidade (robisonsouza):
# fases/prazos do CPC, o que enviar, o que o assistente técnico não faz, e perguntas novas.
import glob,re,json,html
R='/home/claude/'
def faq_ld(t,novas,troca=None):
    def f(m):
        try:d=json.loads(m.group(2))
        except Exception:return m.group(0)
        hit=[False]
        def walk(o):
            if isinstance(o,dict):
                if o.get('@type')=='FAQPage':
                    hit[0]=True
                    for q in o['mainEntity']:
                        if troca and q['name']==troca[0]: q['name']=troca[1]
                    have={q['name'] for q in o['mainEntity']}
                    pos=len(o['mainEntity'])-1
                    for q,a in novas:
                        if q not in have: o['mainEntity'].insert(pos,{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}});pos+=1
                for v in o.values():walk(v)
            elif isinstance(o,list):
                for v in o:walk(v)
        walk(d)
        return m.group(1)+json.dumps(d,ensure_ascii=False)+m.group(3) if hit[0] else m.group(0)
    return re.sub(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)',f,t,flags=re.S)

# ---------- estudopsicossocial: páginas de estado ----------
n=0
for p in sorted(glob.glob(R+'estudopsicossocial/blog/assistente-tecnico-em-estudo-psicossocial-*/index.html')):
    t=open(p,encoding='utf-8').read();o=t
    h1=html.unescape(re.sub(r'<[^>]+>','',re.search(r'<h1[^>]*>(.*?)</h1>',t,flags=re.S).group(1)))
    m=re.search(r'Psicossocial ((?:no|na|em) .+)$',h1)
    if not m or 'id="em-que-fase"' in t or 'id="online-e-suficiente-presencial-e-excecao"' not in t: print('pulado',p);continue
    loc=m.group(1);prep,uf=loc.split(' ',1);de={'no':'do','na':'da','em':'de'}[prep]
    t=t.replace(f'Tribunal de Justiça de {uf}',f'Tribunal de Justiça {de} {uf}').replace(f'interior de {uf}',f'interior {de} {uf}')
    q_old=f'É possível contratar assistente técnico para processo {loc} morando em SP?';q_new=f'É possível contratar assistente técnico para processo {loc} com o profissional sediado em São Paulo?'
    t=t.replace(f'<dt>{q_old}</dt>',f'<dt>{q_new}</dt>')
    bloco=f'''<h2 id="em-que-fase">Em que fase do processo ainda dá tempo</h2>
<p>As regras são as do Código de Processo Civil e valem em qualquer comarca {de} {uf}. Quando o juiz determina o estudo como perícia e nomeia quem vai realizá-lo, cada fase abre uma possibilidade diferente:</p>
<table>
<thead><tr><th>Fase do processo</th><th>O que o assistente técnico pode fazer</th><th>Base legal</th></tr></thead>
<tbody>
<tr><td>Estudo determinado, ainda não realizado</td><td>Indicação como assistente técnico e apresentação dos quesitos, em 15 dias da intimação da nomeação</td><td>CPC, art. 465, §1º</td></tr>
<tr><td>Estudo em andamento</td><td>Quesitos suplementares e ciência prévia das diligências, com antecedência mínima de 5 dias</td><td>CPC, arts. 469 e 466, §2º</td></tr>
<tr><td>Laudo juntado</td><td>Parecer técnico sobre o método e as conclusões, em 15 dias da intimação</td><td>CPC, art. 477, §1º</td></tr>
<tr><td>Depois da manifestação sobre o laudo</td><td>Pedido de esclarecimentos em audiência e, quando a matéria não ficou suficientemente esclarecida, pedido de nova perícia</td><td>CPC, arts. 477, §3º, e 480</td></tr>
</tbody>
</table>
<p>Por isso a data da intimação importa: é a partir dela que os prazos são contados.</p>

<h2 id="o-que-enviar">O que enviar para a análise inicial</h2>
<ul>
<li>A decisão que determinou o estudo psicossocial e a data em que o advogado foi intimado;</li>
<li>A petição inicial e a contestação, para entender o que está em disputa;</li>
<li>Os laudos, relatórios e pareceres já juntados;</li>
<li>Quando houver, as atas das audiências.</li>
</ul>
<p>Com esse material, a análise inicial indica o que cabe fazer na fase em que o processo {loc} está.</p>

<h2 id="o-que-nao-faz">O que o assistente técnico não faz</h2>
<p>O assistente técnico não atende nem avalia a criança, e não acompanha as entrevistas conduzidas pelo psicólogo perito: a Resolução CFP nº 08/2010 (art. 2º) estabelece que o assistente técnico não deve estar presente durante os procedimentos do perito. O trabalho é feito sobre os autos, os quesitos e o laudo. Também não há promessa de resultado: o parecer examina o método e as conclusões do laudo, e a decisão é sempre do juiz.</p>

'''
    t=t.replace('<h2 id="online-e-suficiente-presencial-e-excecao">',bloco+'<h2 id="online-e-suficiente-presencial-e-excecao">',1)
    t=t.replace('<li><a href="#online-e-suficiente-presencial-e-excecao">','<li><a href="#em-que-fase">Em que fase ainda dá tempo</a></li><li><a href="#o-que-enviar">O que enviar para a análise inicial</a></li><li><a href="#o-que-nao-faz">O que o assistente técnico não faz</a></li><li><a href="#online-e-suficiente-presencial-e-excecao">',1)
    novas=[('Qual o prazo para indicar assistente técnico no estudo psicossocial?','Quinze dias contados da intimação do despacho que nomeia o perito, junto com os quesitos (CPC, art. 465, §1º).'),
           ('O laudo já foi juntado: ainda dá para fazer algo?','Sim. As partes têm 15 dias para se manifestar sobre o laudo, e o assistente técnico pode apresentar parecer no mesmo prazo (CPC, art. 477, §1º).')]
    dd=''.join(f'<dt>{q}</dt><dd>{a}</dd>\n' for q,a in novas)
    k=t.rfind('<dt>')
    t=t[:k]+dd+t[k:]
    t=faq_ld(t,novas,(q_old,q_new))
    t=re.sub(r'Leitura de \d+ min','Leitura de 6 min',t,count=1)
    txt=re.sub(r'<[^>]+>',' ',re.search(r'<p class="lead">.*?</dl>',t,flags=re.S).group(0)) if re.search(r'<p class="lead">.*?</dl>',t,flags=re.S) else None
    if txt: t=re.sub(r'"wordCount": \d+',f'"wordCount": {len(txt.split())}',t)
    t=re.sub(r'"dateModified": "[^"]*"','"dateModified": "2026-11-20"',t)
    if t!=o: open(p,'w',encoding='utf-8').write(t);n+=1
print('ep',n)

# ---------- robisonsouza: páginas de cidade ----------
n=0
for p in sorted(glob.glob(R+'robisonsouza/assistente-tecnico-em-psicologia-forense-*/index.html')):
    t=open(p,encoding='utf-8').read();o=t
    if 'class="cidade-lk"' not in t or 'id="o-que-enviar"' in t or '<h2 id="perguntas-frequentes">' not in t: continue
    h1=html.unescape(re.sub(r'<[^>]+>','',re.search(r'<h1[^>]*>(.*?)</h1>',t,flags=re.S).group(1)))
    loc=re.search(r'Forense ((?:no|na|em) .+)$',h1).group(1)
    bloco=f'''<h2 id="o-que-enviar">O que enviar e o que é entregue</h2>
<p>Para a análise inicial de um processo {loc}, o advogado envia:</p>
<ul>
<li>os autos em PDF, com a decisão que nomeou o perito ou designou o depoimento especial;</li>
<li>a data da intimação, para a contagem dos prazos;</li>
<li>o arquivo de mídia do depoimento especial, quando ele já tiver sido realizado;</li>
<li>os laudos e relatórios psicológicos ou sociais já juntados.</li>
</ul>
<p>O que é entregue depende da fase em que o processo está:</p>
<table>
<thead><tr><th>Fase</th><th>Entrega</th></tr></thead>
<tbody>
<tr><td>Perícia ou estudo psicossocial ainda não realizado</td><td>Indicação como assistente técnico e quesitos</td></tr>
<tr><td>Depoimento especial já realizado</td><td>Análise técnica do vídeo do depoimento especial</td></tr>
<tr><td>Laudo juntado</td><td>Parecer técnico sobre o método e as conclusões</td></tr>
<tr><td>Condenação definitiva</td><td>Parecer técnico para instruir a revisão criminal</td></tr>
</tbody>
</table>
'''
    t=t.replace('<h2 id="perguntas-frequentes">',bloco+'<h2 id="perguntas-frequentes">',1)
    t=t.replace('<a href="#perguntas-frequentes">Perguntas frequentes</a></aside>','<a href="#o-que-enviar">O que enviar e o que é entregue</a><a href="#perguntas-frequentes">Perguntas frequentes</a></aside>',1)
    q='O prazo para o parecer sobre o laudo já passou. Ainda há o que fazer?'
    a='Depende da fase. O CPC permite pedir esclarecimentos do perito em audiência (art. 477, §3º) e nova perícia quando a matéria não ficou suficientemente esclarecida (art. 480). No processo penal com condenação definitiva, o caminho é a revisão criminal (CPP, art. 621).'
    t=t.replace('<p><strong>Como iniciar o atendimento?</strong>',f'<p><strong>{q}</strong><br>{a}</p>\n<p><strong>Como iniciar o atendimento?</strong>',1)
    t=faq_ld(t,[(q,a)])
    t=re.sub(r'"dateModified": ?"[^"]*"','"dateModified": "2026-11-20"',t)
    if t!=o: open(p,'w',encoding='utf-8').write(t);n+=1
print('rs',n)
