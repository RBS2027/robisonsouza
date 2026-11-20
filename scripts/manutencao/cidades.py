import re,json,html,datetime
HOJE=datetime.date.today().isoformat(); BR=datetime.date.today().strftime('%d/%m/%Y')
M=open('assistente-tecnico-em-psicologia-forense-no-ceara/index.html',encoding='utf-8').read()
DOM='https://robisonsouza.com.br'
F1='<a href="https://www.tjsp.jus.br/ejus/Noticias/Visualizar/50769" rel="noopener" target="_blank">notícia do TJSP de 5 de abril de 2018</a>'
F2='<a href="https://www.tjsp.jus.br/ejus/Noticias/Visualizar/111189" rel="noopener" target="_blank">notícia do TJSP de 10 de setembro de 2025</a>'
F3='<a href="https://www.cnj.jus.br/projeto-de-depoimento-especial-e-apresentado-a-integrantes-do-ministerio-publico/" rel="noopener" target="_blank">notícia do Conselho Nacional de Justiça</a>'
COMUM_FAM=f'<p>Nas varas de família, o tema ganhou novo alcance. Segundo {F2}, o depoimento especial, originalmente aplicado em casos criminais, passou a ser exigido também quando há alegação de alienação parental, com base na Lei nº 14.340/2022 e na Recomendação nº 157/2024 do CNJ.</p>'
def faq_html(p): return '\n'.join(f'<p><strong>{html.escape(q,quote=False)}</strong><br>{html.escape(a,quote=False)}</p>' for q,a in p)
C={
'assistente-tecnico-em-psicologia-forense-em-campinas':dict(nome='Campinas',h1='Assistente Técnico em Psicologia Forense em Campinas',
 title='Assistente técnico em psicologia em Campinas | Robison Souza',
 desc='Assistente técnico em psicologia para processos da comarca de Campinas (TJSP): depoimento especial, estudo psicossocial e contestação de laudos, online ou presencial.',
 secoes=[('campinas-e-o-depoimento-especial','Campinas e o depoimento especial: o que consta nas fontes oficiais',
 f'''<p>Campinas tem um lugar próprio na história do depoimento especial em São Paulo. De acordo com {F1}, o método começou no estado em 2011, com projeto-piloto implementado em São Caetano do Sul, Atibaia e Campinas. A mesma notícia informa que, em 2018, o Judiciário paulista contava com 20 salas de depoimento especial no interior e na Grande São Paulo e 8 na Capital, e que o depoimento é colhido em sala própria, na presença de psicólogo ou assistente social capacitado, com transmissão ao vivo para a sala de audiência.</p>
<p>A comarca é sede da 4ª Região Administrativa Judiciária do TJSP, e o fórum local é a Cidade Judiciária. Para quem tem processo ali, isso significa uma comarca com mais de uma década de prática no procedimento, e gravações que podem ser analisadas tecnicamente.</p>
{COMUM_FAM}'''),
 ('o-que-o-assistente-tecnico-faz','O que o assistente técnico faz em um processo de Campinas',
 '''<p>O trabalho é o mesmo em qualquer comarca, e as regras são as do CPC e da Lei nº 13.431/2017:</p>
<ul>
<li><strong>Antes da perícia ou do estudo psicossocial:</strong> indicação como assistente técnico e formulação dos quesitos, em 15 dias da intimação do despacho que nomeia o perito (CPC, art. 465, §1º).</li>
<li><strong>No depoimento especial:</strong> análise técnica do vídeo do depoimento especial, com verificação do procedimento do art. 12 da Lei nº 13.431/2017 (esclarecimento inicial, livre narrativa, perguntas em bloco, gravação).</li>
<li><strong>Depois do laudo:</strong> parecer técnico em 15 dias da intimação (CPC, art. 477, §1º), com exame do método e das conclusões.</li>
<li><strong>Na revisão criminal:</strong> parecer sobre a prova psicológica que sustentou a condenação.</li>
</ul>
<p>O assistente técnico não avalia a criança nem a outra parte (Resolução CFP nº 08/2010). O trabalho é feito sobre os autos, os laudos e as gravações.</p>'''),
 ('como-funciona-a-distancia','Como funciona, na prática',
 '''<p>Todo o trabalho é feito 100% online. O advogado envia os autos em PDF e, quando houver, o arquivo de mídia do depoimento. A análise inicial indica o que é possível fazer na fase em que o processo está e quais prazos estão correndo. As peças técnicas são entregues ao advogado, prontas para protocolo. O acompanhamento de audiências e de reuniões técnicas ocorre por videoconferência. Atendimento presencial, apenas sob consulta e acordo.</p>''')],
 faq=[('Atende processos de Campinas e das cidades vizinhas?','Sim. O trabalho é feito 100% online, a partir dos autos digitais, para processos de Campinas e de qualquer outra comarca do país.'),
  ('O depoimento especial em Campinas pode ser analisado depois de realizado?','Sim. O depoimento é gravado em áudio e vídeo (Lei nº 13.431/2017, art. 12, VI), e a análise técnica é feita sobre o vídeo do depoimento especial e os autos.'),
  ('Qual o prazo para indicar assistente técnico?','Quinze dias contados da intimação do despacho que nomeia o perito, junto com os quesitos (CPC, art. 465, §1º). Depois do laudo, ainda cabe parecer em 15 dias (art. 477, §1º).'),
  ('Como enviar os documentos de um processo de Campinas?','Pelo WhatsApp, por mensagem, ou por e-mail, em formato digital: PDF dos autos e, se houver, o arquivo de mídia do depoimento.')]),
'assistente-tecnico-em-psicologia-forense-em-guarulhos':dict(nome='Guarulhos',h1='Assistente Técnico em Psicologia Forense em Guarulhos',
 title='Assistente técnico em psicologia em Guarulhos | Robison Souza',
 desc='Assistente técnico em psicologia para processos da comarca de Guarulhos (TJSP): depoimento especial, estudo psicossocial e contestação de laudos, online ou presencial.',
 secoes=[('guarulhos-e-o-depoimento-especial','Guarulhos entre as primeiras comarcas com depoimento especial',
 f'''<p>Guarulhos está entre as primeiras comarcas paulistas a adotar o depoimento especial. Uma {F3} sobre o grupo de trabalho do TJSP registra que a iniciativa, da Coordenadoria da Infância e da Juventude do tribunal, foi implementada em junho de 2011 e contemplava, à época, quatro comarcas do estado: Guarulhos, Campinas, São Caetano do Sul e Atibaia.</p>
<p>Segundo {F1}, em 2018 o Judiciário paulista já contava com 20 salas de depoimento especial no interior e na Grande São Paulo e 8 na Capital. O depoimento é colhido em sala própria, na presença de psicólogo ou assistente social capacitado, e transmitido ao vivo para a sala de audiência, de onde o juiz, o promotor e os defensores acompanham.</p>
{COMUM_FAM}'''),
 ('quando-procurar','Quando procurar o assistente técnico',
 '''<p>Em três momentos o trabalho técnico muda o que a parte consegue fazer no processo:</p>
<ul>
<li><strong>Quando o juiz determina perícia psicológica ou estudo psicossocial.</strong> Abre-se o prazo de 15 dias para indicar assistente técnico e apresentar quesitos (CPC, art. 465, §1º). É o momento de definir o que o perito terá de responder.</li>
<li><strong>Quando há depoimento especial marcado ou já realizado.</strong> A análise do vídeo do depoimento especial verifica se o procedimento do art. 12 da Lei nº 13.431/2017 foi seguido e em que condições o relato foi produzido.</li>
<li><strong>Quando o laudo é juntado.</strong> A parte tem 15 dias para se manifestar e apresentar o parecer do assistente técnico (CPC, art. 477, §1º). O juiz deve indicar na sentença por que considera ou deixa de considerar as conclusões do laudo, levando em conta o método (art. 479).</li>
</ul>
<p>Também é possível atuar depois da condenação, com parecer para revisão criminal. Em todos os casos, o assistente técnico trabalha sobre autos, laudos e gravações, sem avaliar a criança ou a outra parte (Resolução CFP nº 08/2010).</p>'''),
 ('atendimento-online','Atendimento 100% online',
 '''<p>O advogado ou a parte envia os autos em PDF e a mídia do depoimento, quando existir. A análise inicial aponta os prazos em curso e o que cabe fazer em cada fase. Quesitos e pareceres são entregues ao advogado, prontos para protocolo, e as audiências e reuniões técnicas são acompanhadas por videoconferência. Atendimento presencial, apenas sob consulta e acordo.</p>''')],
 faq=[('Atende processos da comarca de Guarulhos?','Sim. O trabalho é 100% online, sobre os autos digitais, e alcança Guarulhos e qualquer outra comarca do país.'),
  ('É possível contestar um laudo psicológico de um processo de Guarulhos?','Sim. No prazo de 15 dias da intimação sobre o laudo, a parte apresenta o parecer do assistente técnico, que examina o método e as conclusões (CPC, art. 477, §1º).'),
  ('O assistente técnico participa do depoimento especial?','A lei prevê que o juiz consulte os assistentes técnicos sobre perguntas complementares, depois da livre narrativa (Lei nº 13.431/2017, art. 12, IV). A análise do vídeo pode ser feita depois do ato.'),
  ('Como iniciar o atendimento?','Por mensagem no WhatsApp (12) 99740-2674, com o envio dos autos em PDF para a análise inicial.')]),
}
REL=[('/tribunal-de-justica-do-estado-de-sao-paulo/','Guia','Tribunal de Justiça do Estado de São Paulo'),('/depoimento-especial-em-sao-paulo/','Depoimento especial','Depoimento Especial em São Paulo'),('/estudo-psicosocial-em-sao-paulo/','Estudo psicossocial','Estudo Psicossocial em São Paulo')]
OUT=[('https://depoimentoespecial.com.br/blog/assistente-tecnico-em-depoimento-especial-no-vale-do-paraiba/','Depoimento Especial','Assistente Técnico em Depoimento Especial no Vale do Paraíba'),('https://peritoempsicologiaforense.com.br/contestacao-de-laudo-psicologico/','Perito em Psicologia Forense · página do serviço','Contestação de laudo psicológico'),('https://assistente.tec.br/como-indicar-assistente-tecnico/','Assistente Técnico · guia para advogados','Como indicar assistente técnico')]
import os
for slug,c in C.items():
    t=M; url=f'{DOM}/{slug}/'; e=html.escape
    t=re.sub(r'<title>.*?</title>',f'<title>{e(c["title"])}</title>',t,count=1,flags=re.S)
    for sel in ('name="description"','property="og:description"','name="twitter:description"'): t=re.sub(r'(<meta %s content=")[^"]*(")'%sel,lambda m:m.group(1)+e(c['desc'])+m.group(2),t,count=1)
    for sel in ('property="og:title"','name="twitter:title"'): t=re.sub(r'(<meta %s content=")[^"]*(")'%sel,lambda m:m.group(1)+e(c['title'])+m.group(2),t,count=1)
    t=t.replace(DOM+'/assistente-tecnico-em-psicologia-forense-no-ceara/',url)
    t=re.sub(r'https://robisonsouza\.com\.br/assets/capas/assistente-tecnico-em-psicologia-forense-no-ceara\.webp\?v=\d+',DOM+'/assets/og-padrao.jpg',t)
    lds=[{"@context":"https://schema.org","@type":"Article","headline":c['h1'],"description":c['desc'],"datePublished":HOJE,"dateModified":HOJE,"inLanguage":"pt-BR","mainEntityOfPage":url},
         {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Início","item":DOM+"/"},{"@type":"ListItem","position":2,"name":"Blog","item":DOM+"/blog/"},{"@type":"ListItem","position":3,"name":c['h1'],"item":url}]},
         {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in c['faq']]}]
    art=json.loads(re.search(r'<script type="application/ld\+json"[^>]*>(\{"@context": ?"https://schema.org", ?"@type": ?"Article".*?)</script>',M,re.S).group(1))
    for k in ('author','publisher','image'):
        if k in art and k!='image': lds[0][k]=art[k]
    lds[0]['image']=DOM+'/assets/og-padrao.jpg'
    it=iter(lds)
    t=re.sub(r'(<script type="application/ld\+json"[^>]*>)(\{"@context": ?"https://schema.org", ?"@type": ?"(?:Article|BreadcrumbList|FAQPage)".*?)(</script>)',lambda m:m.group(1)+json.dumps(next(it),ensure_ascii=False)+m.group(3),t,flags=re.S)
    i=t.find('<article class="prosa">'); j=t.find('<!-- rede-2027 -->'); k=t.find('<!-- /rede-2027 -->')
    corpo=f'<article class="prosa">\n<p class="migalha"><a href="/blog/">Blog</a> &middot; {BR}</p>\n<h1>{e(c["h1"])}</h1>\n<div class="assinatura"><span class="chip">Perito em Psicologia Forense</span> Robison Souza &middot; CRP 06/156275</div>\n'
    corpo+=f'<p><strong>Em resumo:</strong> advogados e partes com processo na comarca de {c["nome"]}, do Tribunal de Justiça de São Paulo, podem contar com assistência técnica em psicologia para depoimento especial, estudo psicossocial, contestação de laudos e revisão criminal. O trabalho é feito 100% online, sobre os autos digitais.</p>\n'
    for hid,h2,txt in c['secoes']: corpo+=f'<h2 id="{hid}">{h2}</h2>\n{txt}\n'
    corpo+=f'<h2 id="perguntas-frequentes">Perguntas frequentes</h2>\n{faq_html(c["faq"])}\n<p><em>Conteúdo informativo. As informações sobre a comarca foram extraídas das fontes oficiais indicadas no texto, consultadas em {BR}.</em></p>\n\n'
    cards=lambda L,ext: ''.join(f'<a class="rede27-c" href="{u}"{" rel=\"noopener\"" if ext else ""}><span class="rede27-r">{r}</span><span class="rede27-t">{n}</span></a>' for u,r,n in L)
    rede=f'<!-- rede-2027 --><section class="rede27" aria-label="Leituras relacionadas"><h2 class="rede27-h" id="continue-lendo">Continue lendo neste site</h2><div class="rede27-g">{cards(REL,0)}</div><h2 class="rede27-h" id="mesmo-tema-outros-sites">O mesmo tema nos outros sites do Instituto</h2><div class="rede27-g">{cards(OUT,1)}</div></section>'
    t=t[:i]+corpo+rede+t[k:]
    sm=''.join(f'<a href="#{hid}">{h2}</a>' for hid,h2,_ in c['secoes'])+'<a href="#perguntas-frequentes">Perguntas frequentes</a>'
    t=re.sub(r"(<strong class=\"sub-hero\">).*?(</strong>)",lambda m:m.group(1)+"Processos da comarca de "+c["nome"]+", no TJSP, podem contar com assistência técnica especializada em psicologia forense."+m.group(2),t,count=1,flags=re.S)
    t=re.sub(r'(<aside class="sumario"><strong>Neste artigo</strong>).*?(</aside>)',lambda m:m.group(1)+sm+m.group(2),t,count=1,flags=re.S)
    os.makedirs(slug,exist_ok=True); open(slug+'/index.html','w',encoding='utf-8').write(t)
    s=open('sitemap.xml',encoding='utf-8').read()
    if url not in s: open('sitemap.xml','w',encoding='utf-8').write(s.replace('</urlset>',f'<url><loc>{url}</loc><lastmod>{HOJE}</lastmod></url></urlset>'))
    print(slug,len(re.sub(r'<[^>]+>',' ',corpo).split()),'palavras', t.count('ceara'),t.count('Ceará'))
