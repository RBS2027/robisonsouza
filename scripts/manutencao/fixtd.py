import re,html,json,os,glob
H='/home/claude/'
def setmeta(p,title=None,desc=None):
    s=open(p,encoding='utf-8').read();o=s
    if desc:
        m=re.search(r'<meta\s+name="description"\s+content="(.*?)"',s,re.S);old=m.group(1)
        new=html.escape(desc,quote=True)
        s=s.replace(old,new)
        ou=html.unescape(old);j=json.dumps(ou,ensure_ascii=False)[1:-1]
        if j!=old: s=s.replace(j,json.dumps(desc,ensure_ascii=False)[1:-1])
        assert len(desc)<=162 and len(desc)>=110,(p,len(desc))
    if title:
        m=re.search(r'<title>(.*?)</title>',s,re.S);old=m.group(1)
        s=s.replace('<title>'+old+'</title>','<title>'+html.escape(title,quote=False)+'</title>')
        base=old.replace(' | Robison Souza','');nb=html.escape(title.replace(' | Robison Souza',''),quote=True)
        for prop in ('og:title','twitter:title'):
            s=re.sub(r'(<meta\s+(?:property|name)="%s"\s+content=")(%s|%s)(")'%(prop,re.escape(old),re.escape(base)),lambda m:m.group(1)+nb+m.group(3),s)
        assert len(title)<=65,(p,len(title))
    s=re.sub(r'"dateModified":\s*"[^"]*"','"dateModified": "2026-11-19"',s) if '"dateModified": "' in s else s
    if s!=o: open(p,'w',encoding='utf-8').write(s);return 1
    return 0
n=0
# A) perito: páginas de estado
for p in glob.glob(H+'perito/pericia-psicologica-*-cadastro-de-peritos-do-tj*/index.html'):
    s=open(p,encoding='utf-8').read()
    t=html.unescape(re.search(r'<title>(.*?)</title>',s).group(1));d=html.unescape(re.search(r'<meta\s+name="description"\s+content="(.*?)"',s).group(1))
    m=re.match(r'Perícia psicológica (.+?): cadastro de peritos do (TJ\w+)',t)
    if not m: continue
    m2=re.match(r'Como o perito psicólogo é escolhido nos processos (.+?): o cadastro',d)
    n+=setmeta(p,f'Perícia psicológica {m.group(1)}: peritos do {m.group(2)}',f'Como o perito psicólogo é escolhido nos processos {m2.group(1)}: o cadastro do {m.group(2)}, a base legal e como a parte pode acompanhar e contestar o laudo.')
# B) modelos de estado ep / de
for p in glob.glob(H+'estudopsicossocial/blog/assistente-tecnico-em-estudo-psicossocial-*/index.html'):
    s=open(p,encoding='utf-8').read();d=html.unescape(re.search(r'<meta\s+name="description"\s+content="(.*?)"',s).group(1))
    m=re.match(r'Assistência técnica em estudo psicossocial para processos em tramitação ([^:.]+?)\.$',d)
    if m and 'noindex' not in s[:3000]: n+=setmeta(p,None,f'Assistência técnica em estudo psicossocial para processos em tramitação {m.group(1)}: quesitos, acompanhamento e análise do laudo, 100% online.')
for p in glob.glob(H+'depoimentoespecial/blog/assistente-tecnico-em-depoimento-especial-*/index.html'):
    s=open(p,encoding='utf-8').read();d=html.unescape(re.search(r'<meta\s+name="description"\s+content="(.*?)"',s).group(1))
    m=re.match(r'Análise técnica de depoimento especial para processos em tramitação ([^:.]+?)\.$',d)
    if m and 'noindex' not in s[:3000]: n+=setmeta(p,None,f'Análise técnica de depoimento especial para processos em tramitação {m.group(1)}: análise do vídeo, quesitos e parecer técnico, 100% online.')
# C) individuais
D={
'robisonsouza/comportamento-nao-verbal-no-depoimento-especial':(None,'Como o comportamento não verbal da criança é lido no depoimento especial, os limites técnicos dessa leitura e por que nenhum sinal isolado sustenta conclusão.'),
'robisonsouza/guarda-compartilhada-morando-em-outro-estado':(None,'Guarda compartilhada com pais em cidades ou estados diferentes: como fica a convivência, o lar de referência e o que o estudo psicossocial costuma avaliar.'),
'robisonsouza/psicologia-juridica-e-violencia-domestica':(None,'O papel da psicologia jurídica nos processos de violência doméstica: avaliações, laudos, limites técnicos e como a parte pode acompanhar a prova psicológica.'),
'robisonsouza/atuacao-nacional-perito-assistente-tecnico-em-psicologia-forense':(None,'Assistência técnica em psicologia forense para advogados e partes de qualquer estado: como funciona o trabalho 100% online, dos autos ao parecer técnico.'),
'robisonsouza/intimacao-guarda-compartilhada':(None,'Recebeu intimação em ação de guarda compartilhada? Veja prazos, o que esperar do estudo psicossocial e quando indicar assistente técnico em psicologia.'),
'robisonsouza/poder-familiar-o-que-e':(None,'Poder familiar: o que é, quais direitos e deveres envolve, quando pode ser suspenso ou perdido e como a prova psicológica entra nessas ações.'),
'robisonsouza/politica-de-privacidade':(None,'Política de privacidade do site: sem rastreamento próprio, dados de contato protegidos por sigilo profissional e os direitos garantidos pela LGPD.'),
'robisonsouza/modelo-guarda-compartilhada':(None,'Modelo de pedido de guarda compartilhada: o que o documento precisa conter, pontos de atenção técnica e como a prova psicológica reforça o pedido.'),
'robisonsouza/guarda-compartilhada-jusbrasil':(None,'Guarda compartilhada: como funciona, o que a lei prevê, o lar de referência, a convivência e o papel do estudo psicossocial na decisão do juiz.'),
'robisonsouza/quem-sou':(None,'Robison de Souza Alves Pereira, Perito em Psicologia Forense, CRP 06/156275, Perito Auxiliar da Justiça · TJSP nº 66.627. Formação e áreas de atuação.'),
'robisonsouza/assistente-tecnico-em-disputa-de-guarda-envolvendo-exposicao-digital-da-crianca-sharenting':(None,'Exposição da criança nas redes sociais (sharenting) em disputa de guarda: como o tema aparece na perícia e o que o assistente técnico pode apontar.'),
'robisonsouza/falsas-memorias-e-testemunho-infantil-o-que-a-ciencia-diz':(None,'O que a ciência diz sobre falsas memórias no testemunho infantil, como a sugestão afeta o relato e o que isso muda na análise do depoimento especial.'),
'robisonsouza/estudo-psicossocial-o-que-e-e-quando-e-solicitado':(None,'Estudo psicossocial: o que é, quem realiza, em quais processos o juiz determina e como a parte pode acompanhar com quesitos e assistente técnico.'),
'robisonsouza/divergencia-entre-perito-e-assistente-tecnico-art-479-do-cpc':(None,'Quando perito e assistente técnico divergem: o que diz o art. 479 do CPC, como o juiz valora o laudo e como fundamentar tecnicamente a discordância.'),
'robisonsouza/estudo-psicossocial-o-que-muda-no-seu-processo':(None,'Como o estudo psicossocial influencia a decisão em processos de família, o que o relatório avalia e o que a parte pode fazer antes e depois do laudo.'),
'robisonsouza/checklist-laudo-psicologico-e-a-resolucao-cfp-06-2019':(None,'Checklist para conferir se o laudo psicológico cumpre a Resolução CFP 06/2019: estrutura, fundamentação, método, conclusão e vícios mais comuns.'),
'robisonsouza/erros-do-advogado-ao-lidar-com-assistente-tecnico-o-que-evitar':(None,'Os erros mais comuns do advogado ao trabalhar com assistente técnico em psicologia: prazos, quesitos, documentos e integração à estratégia do caso.'),
'robisonsouza/o-psicologo-juridico-no-direito-de-familia':(None,'A atuação do psicólogo no Direito de Família: perícia, estudo psicossocial e assistência técnica em disputas de guarda, convivência e alienação parental.'),
'robisonsouza/alienacao-parental-e-a-guarda-compartilhada-como-meio-preventivo':(None,'Como a guarda compartilhada funciona como meio de prevenir a alienação parental, o que a Lei 12.318/2010 prevê e como o tema é avaliado na perícia.'),
'robisonsouza/revisional-de-alimentos-guarda-compartilhada':(None,'Revisional de alimentos e guarda compartilhada: quando o valor ou a convivência podem ser revistos e como a prova técnica psicológica entra no pedido.'),
'robisonsouza/quanto-tempo-leva-um-processo-de-alienacao-parental-prazos-e-fases':(None,'Quanto tempo leva um processo de alienação parental: a tramitação prioritária da Lei 12.318/2010, as fases, a perícia e o que costuma atrasar.'),
'robisonsouza/violencia-psicologica-como-provar':(None,'Violência psicológica: como a lei define, quais provas costumam ser aceitas e qual o papel do laudo e do parecer psicológico nesses processos.'),
'robisonsouza/vieses-cognitivos-na-pericia-psicologica':(None,'Vieses cognitivos na perícia psicológica: viés de confirmação, ancoragem e outros erros que comprometem o laudo, e como identificá-los e contestá-los.'),
'robisonsouza/publicacoes':(None,'Livro e guia sobre depoimento especial, artigos técnicos publicados nos cinco sites, currículo Lattes e perfis profissionais de Robison Souza.'),
'robisonsouza/exoneracao-de-alimentos-guarda-compartilhada':(None,'Exoneração de alimentos na guarda compartilhada: por que a guarda não extingue a pensão automaticamente e quando o pedido de exoneração é cabível.'),
'robisonsouza/assistente-tecnico-em-depoimento-especial-funcao-lei-13-431-2017-e-atuacao-na-escuta':(None,'A função do assistente técnico no depoimento especial segundo a Lei 13.431/2017: análise do vídeo, quesitos, parecer técnico e limites da atuação.'),
'robisonsouza/perguntas-frequentes':(None,'Respostas às dúvidas mais comuns sobre assistência técnica em psicologia, perícia psicológica, prazos do CPC, parecer técnico e atuação em todo o Brasil.'),
'robisonsouza/assistente-tecnico-em-psicologia-forense-em-belo-horizonte':('Assistente técnico em psicologia em Belo Horizonte',None),
'robisonsouza/assistente-tecnico-em-psicologia-forense-em-ribeirao-preto':('Assistente técnico em psicologia em Ribeirão Preto',None),
'robisonsouza/assistente-tecnico-em-psicologia-forense-no-rio-de-janeiro-capital':('Assistente técnico em psicologia no Rio de Janeiro (capital)',None),
'perito/avaliacao-psicologica-no-contexto-juridico-normas':(None,'Avaliação psicológica no contexto jurídico: as normas do CFP que regem a perícia, o que diferencia a avaliação forense e o que o laudo deve conter.'),
'perito/politica-de-privacidade':(None,'Como este site trata seus dados: sem rastreamento próprio, contato protegido por sigilo profissional e direitos assegurados pela LGPD ao titular.'),
'perito/psicologia-aplicada-ao-processo-onde-muda-o-resultado':('Psicologia aplicada ao processo: onde muda o resultado','Os pontos do processo judicial em que a psicologia entra, como perícia, depoimento e estudo psicossocial, e como o conhecimento técnico muda o resultado.'),
'perito/preciso-de-assistente-tecnico':(None,'Cinco perguntas objetivas para saber se o seu processo precisa de assistente técnico em psicologia: perícia, estudo psicossocial ou depoimento especial.'),
'perito/guarda-compartilhada-negada-hipoteses-e-laudos':(None,'Guarda compartilhada negada: as hipóteses legais de exceção, a fundamentação exigida do juiz e o peso do laudo psicológico e do estudo psicossocial.'),
'perito/regulamentacao-de-convivencia-desenho-tecnico':('Regulamentação de convivência: o desenho técnico','Regulamentação de convivência: como o estudo técnico orienta o calendário de convivência da criança e o que a parte pode propor e questionar.'),
'perito/para-que-serve-a-psicologia-juridica-hoje':(None,'Para que serve a psicologia jurídica hoje: o que ela entrega ao processo em perícias, estudos psicossociais, depoimento especial e assistência técnica.'),
'perito/perguntas-frequentes':(None,'Dúvidas comuns sobre perícia psicológica, assistência técnica, parecer psicológico, prazos, custos e atuação 100% online em processos de todo o Brasil.'),
'depoimentoespecial/blog/depoimento-especial-e-investigacao-criminal-o-papel-na-fase-preliminar':(None,'Depoimento especial na investigação criminal: o papel da escuta na fase preliminar, antes da denúncia, e o que a defesa pode acompanhar e questionar.'),
'estudopsicossocial/blog/abandono-afetivo-e-estudo-psicossocial':(None,'Abandono afetivo e estudo psicossocial: como se prova o descumprimento do dever de cuidado e o dano, e o que o relatório técnico pode demonstrar.'),
'estudopsicossocial/blog/estudo-psicossocial-com-citacao-incorreta-como-isso-compromete-o-relatorio':(None,'Estudo psicossocial com citação incorreta de autores ou normas: como esse erro compromete a fundamentação do relatório e como apontá-lo nos autos.'),
'estudopsicossocial/blog/quanto-custa-assistente-tecnico':(None,'Quanto custa um assistente técnico em estudo psicossocial: o que compõe os honorários, as etapas do trabalho e por que o escopo define o valor.'),
'estudopsicossocial/blog/mudanca-de-escola-e-decisoes-conjuntas':(None,'Decisões conjuntas na guarda compartilhada: escola, tratamentos e religião dependem de ambos os genitores. Veja o que fazer quando não há acordo.'),
'estudopsicossocial/blog/estudo-psicossocial-com-conclusao-generica-como-identificar-esse-vicio':(None,'Estudo psicossocial com conclusão genérica: como identificar esse vício técnico, por que ele enfraquece o relatório e como usá-lo na contestação.'),
'estudopsicossocial/blog/estudo-psicossocial-e-acao-possessoria-prazo-para-solicitar-a-avaliacao':(None,'Estudo psicossocial e ação possessória: em que casos a avaliação técnica cabe e qual o momento processual mais adequado para solicitá-la.'),
'estudopsicossocial/blog/assistente-tecnico-em-estudo-psicossocial-em-sao-paulo':('Assistente Técnico em Estudo Psicossocial em São Paulo','Estudo psicossocial em processos do TJSP: quem faz, o que a parte pode pedir e como o assistente técnico atua com quesitos e análise do laudo, 100% online.'),
}
for k,(t,d) in D.items(): n+=setmeta(H+k+'/index.html',t,d)
print('alterados',n)
