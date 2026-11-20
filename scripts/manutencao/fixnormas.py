import re,os,json
R=['robisonsouza','perito','depoimentoespecial','estudopsicossocial','assistente']
S=[ # (old,new) literais
('Resolução CFP nº 12/2011 (atuação em execução penal) e nº 06/2019, art. 12','Resolução CFP nº 06/2019, art. 12'),
('(avaliação socioeducativa — Res. CFP 12/2011)','(avaliação socioeducativa — Res. CFP 15/2022)'),
('com os limites da Res. CFP 12/2011)','com os limites do método)'),
('avaliação socioeducativa (Resolução CFP nº 12/2011 — contexto','avaliação socioeducativa (Resolução CFP nº 15/2022 — contexto'),
('é socioeducativa (Resolução CFP nº 12/2011)','é socioeducativa (Resolução CFP nº 15/2022)'),
('lógica socioeducativa (Resolução CFP nº 12/2011)','lógica socioeducativa (Resolução CFP nº 15/2022)'),
('Resolução CFP nº 12/2011 (atuação no socioeducativo)','Resolução CFP nº 15/2022 (atuação no socioeducativo)'),
('A Resolução CFP nº 12/2011, que regulamenta a atuação do psicólogo no sistema prisional e no socioeducativo, veda o exame criminológico com finalidade de prognóstico de reincidência e orienta','A Resolução CFP nº 15/2022, que estabelece normas para a atuação do psicólogo no sistema socioeducativo, orienta'),
('no SINASE e na Resolução CFP 12/2011','no SINASE e na Resolução CFP 15/2022'),
('e a Res. CFP 12/2011 veda prognóstico de reincidência. A internação','e não há método válido para prever a conduta futura de um adolescente. A internação'),
('categorias que o ECA não adota e que a Resolução CFP nº 12/2011 veda.','categorias que o ECA não adota e que a psicologia forense não sustenta com rigor.'),
('A Resolução CFP nº 12/2011 regula a atuação do psicólogo no sistema socioeducativo: orientada à garantia de direitos, sem exame criminológico com finalidade de prognóstico de reincidência.','A Resolução CFP nº 15/2022 estabelece normas para a atuação do psicólogo no sistema socioeducativo, orientada à garantia de direitos.'),
('e a Resolução CFP 12/2011 veda o prognóstico; a avaliação','e não há método que preveja a conduta futura; a avaliação'),
('e a Res. CFP 12/2011 veda prognóstico de reincidência.','e não há método válido para prever reincidência.'),
('a atuação no sistema prisional e socioeducativo, pela nº 12/2011;','a atuação no sistema socioeducativo, pela nº 15/2022;'),
('12/2011 (sistema prisional e socioeducativo)','15/2022 (sistema socioeducativo)'),
('dentro dos limites da Res. CFP 12/2011','dentro dos limites do método'),
(' Res. CFP 12/2011: vedação ao prognóstico de reincidência.',''),
('Não (Res. CFP 12/2011): prognóstico de reincidência, ‘periculosidade’ e nexo causal a partir do crime são vedados. O psicólogo avalia','Não com base científica: não há método que preveja a conduta de uma pessoa, e ‘periculosidade’ não é categoria psicológica. A Res. CFP 12/2011, que vedava esse prognóstico, foi anulada pela Justiça Federal em 2015; o limite que permanece é técnico. O psicólogo avalia'),
('A Resolução CFP 12/2011 veda ao psicólogo o prognóstico de reincidência como categoria (‘periculosidade’) e exige avaliação com método e limites.','A Resolução CFP 12/2011, que vedava ao psicólogo o prognóstico de reincidência, foi anulada pela Justiça Federal (decisão definitiva em 2015); o limite que permanece é técnico: avaliação com método e limites declarados.'),
('A Resolução CFP nº 12/2011 regula a atuação do psicólogo na execução penal: veda a elaboração de prognóstico criminológico de reincidência, a aferição de ‘periculosidade’ e o estabelecimento de nexo causal a partir do crime cometido — e permite a avaliação psicológica com método e limites.','A Resolução CFP nº 12/2011, que vedava ao psicólogo o prognóstico criminológico de reincidência, a aferição de ‘periculosidade’ e o nexo causal a partir do crime cometido, foi anulada pela Justiça Federal em ação civil pública, com decisão definitiva em 2015. O limite que permanece é técnico: a avaliação psicológica tem método e limites, e a conclusão deve caber nos dados (Res. CFP 06/2019).'),
('e a norma ética do psicólogo não mudou: avalia; não prevê.','e o limite técnico do psicólogo não mudou: avalia; não prevê.'),
('(vedado — Res. CFP 12/2011)','(sem base técnica)'),
('(ninguém pode — e a Resolução veda prometer)','(ninguém pode)'),
('impugnar com base na Res. CFP 12/2011 — a conclusão vedada é desconsiderável e enseja representação.','impugnar com base no método (Res. CFP 06/2019) — a conclusão sem fundamento técnico pode ser contestada.'),
('Prognóstico de reincidência (Res. CFP 12/2011).','Prognóstico de reincidência (sem base técnica).'),
('Prognóstico de reincidência (Res. 12/2011).','Prognóstico de reincidência (sem base técnica).'),
(' Res. CFP 12/2011: execução penal.',''),
('Lei 14.843/2024; Res. CFP 12/2011 — sem prognóstico de reincidência)','Lei 14.843/2024 — sem prognóstico de reincidência)'),
('(Res. CFP 12/2011 — vedado; e ninguém pode)','(ninguém pode)'),
('Afirmação vedada ao psicólogo na execução penal (Res. CFP 12/2011): o exame','Afirmação sem base técnica na execução penal (a Res. CFP 12/2011, que a vedava, foi anulada pela Justiça Federal em 2015): o exame'),
('(06/2019; 31/2022; 12/2011; 01/2018;','(06/2019; 31/2022; 01/2018;'),
(' 12/2011 (execução penal — vedação ao prognóstico);',''),
('sistema prisional e socioeducativo (Res. 12/2011)','sistema prisional e socioeducativo (Res. CFP 15/2022, no socioeducativo)'),
('(08/2010, 06/2019, 31/2022, 12/2011)','(08/2010, 06/2019, 31/2022)'),
('(Resolução CFP 12/2011 veda o exame criminológico com prognóstico de reincidência como categoria)','(sem prognóstico de reincidência como categoria)'),
('— e a Res. CFP 12/2011 continua vedando prognóstico de reincidência, ‘periculosidade’ e nexo entre traços e crime. O perito avalia sem prever.','— mas a psicologia segue sem método para prever reincidência; a Res. CFP 12/2011, que vedava esse prognóstico, foi anulada pela Justiça Federal em 2015. O perito avalia sem prever.'),
('e a Resolução CFP 12/2011 veda o que mais se espera dele (','e a ciência não oferece o que mais se espera dele ('),
('A Resolução CFP nº 12/2011 regula o psicólogo na execução: veda elaborar prognóstico criminológico de reincidência, aferir periculosidade e estabelecer nexo causal a partir do crime — e permite a ','A Resolução CFP nº 12/2011, que vedava ao psicólogo o prognóstico criminológico de reincidência, a aferição de periculosidade e o nexo causal a partir do crime, foi anulada pela Justiça Federal (decisão definitiva em 2015). Permanece o dever técnico da '),
('O perito que ‘prevê’ viola a norma ética;','O perito que ‘prevê’ afirma o que o método não sustenta;'),
('e sem nexo causal (Res. 12/2011)','e sem nexo causal'),
('impugnar com base na Res. CFP 12/2011 e no método — a conclusão vedada é desconsiderável e enseja representação.','impugnar com base no método (Res. CFP 06/2019) — a conclusão sem fundamento técnico pode ser contestada.'),
('diante de laudo com categoria vedada (','diante de laudo com categoria sem base técnica ('),
('(Res. 06/2019, 08/2010, 31/2022, 12/2011)','(Res. 06/2019, 08/2010, 31/2022)'),
(' 12/2011 (execução penal),',''),
('execução penal — Res. 12/2011)','execução penal — fatores de risco e de proteção)'),
('sistema socioeducativo e prisional (Res. CFP 12/2011)','sistema socioeducativo (Res. CFP 15/2022) e prisional'),
('(CFP 06/2019, 08/2010, 31/2022, 12/2011;','(CFP 06/2019, 08/2010, 31/2022;'),
('sistema prisional e socioeducativo (Res. CFP 12/2011)','sistema prisional e socioeducativo (Res. CFP 15/2022, no socioeducativo)'),
('sem prognóstico de reincidência (Res. CFP 12/2011).','sem prognóstico de reincidência.'),
# NT 04/2020
(' com base nos marcadores descritos na Nota Técnica CFP 04/2020.',' com base em critérios descritos na literatura científica sobre memória e sugestionabilidade.'),
('<p>A <strong>Nota Técnica CFP 04/2020</strong> orienta os psicólogos sobre os parâmetros técnicos adequados para a avaliação de credibilidade de relatos em casos de abuso sexual. A análise deve considerar:','<p>A análise deve considerar:'),
(', com base no Protocolo NICHD e na Nota Técnica CFP 04/2020',', com base no Protocolo NICHD e na literatura científica'),
('Análise das condições de produção do relato de relatos','Análise das condições de produção do relato'),
('<p>A <strong>Nota Técnica CFP 04/2020</strong> orienta os parâmetros técnicos para esse tipo de avaliação em contextos de suspeita de abuso sexual. Os mesmos princípios','<p>Os mesmos princípios'),
# NT 01/2023
('<p>A <strong>Nota Técnica CFP 01/2023</strong> atualizou orientações sobre avaliação psicológica em contextos jurídicos, com ênfase na utilização de instrumentos validados e na adequação metodológica dos procedimentos adotados pelo perito.','<p>A <strong>Resolução CFP 31/2022</strong> estabelece as diretrizes da avaliação psicológica e exige testes com parecer favorável no SATEPSI.'),
# Haia 1996
('A Convenção de 1996 (Decreto nº 10.947/2022) e o CPC (arts. 26 a 41) regem a cooperação.','O CPC (arts. 26 a 41) rege a cooperação.'),
('A Convenção da Haia de 1996 (Decreto nº 10.947/2022) trata da competência e da cooperação em matéria de responsabilidade parental, e o Código de Processo Civil (arts. 26 a 41) regula a cooperação jurídica internacional.','O Código de Processo Civil (arts. 26 a 41) regula a cooperação jurídica internacional; à Convenção da Haia de 1996, sobre responsabilidade parental, o Brasil não aderiu.'),
('; a de 1996 (Decreto nº 10.947/2022) trata de responsabilidade parental.','; à de 1996, sobre responsabilidade parental, o Brasil não aderiu.'),
('; Convenção da Haia de 1996 (Decreto nº 10.947/2022); acordos','; acordos'),
(', de 1996 (responsabilidade parental — Decreto 10.947/2022)',''),
# animais
('Com a aprovação da Lei 14.223, os animais domésticos passaram a ser reconhecidos como seres sencientes, e não mais como simples objetos ou bens móveis.','O Código Civil ainda classifica os animais como bens, mas há decisões judiciais que os tratam como seres sencientes, e o projeto de reforma do Código Civil propõe essa mudança.'),
# 13/2007
('a posterior <strong>Resolução CFP nº 013/2007</strong>, que instituiu o título de especialista na área','as resoluções do CFP sobre o título de especialista em Psicologia Jurídica, hoje a <strong>Resolução CFP nº 23/2022</strong>'),
('(Res. CFP 13/2007)','(Res. CFP 23/2022)'),
('(Res. CFP 13/2007 — especialidade;','(Res. CFP 23/2022 — especialidade;'),
('; 13/2007 (neuropsicologia)',''),
# 13/2022
('Res. CFP 13/2022 (alterando a 06/2019) e Res. 09/2024: meios tecnológicos.','Res. CFP 09/2024: meios tecnológicos.'),
# PLs
('O Projeto de Lei 4.573/2019, por exemplo, propõe a revogação total, argumentando que prejudica crianças e mulheres vítimas de violência.','O Projeto de Lei 2.812/2022, por exemplo, propõe a revogação total; em 11/11/2026, a Câmara dos Deputados rejeitou o recurso contra o envio do texto ao Senado, onde ele ainda será analisado. Enquanto isso, a lei segue em vigor.'),
('Embora haja discussões sobre sua revogação, incluindo o Projeto de Lei 1372/2023, não foi revogada.','Há projetos de revogação em tramitação (PL 1372/2023 e PL 2812/2022 — este enviado pela Câmara ao Senado em 11/11/2026), mas, enquanto nenhum for aprovado e sancionado, a lei não está revogada.'),
('<p>O PL 1372/2023 representa um ponto de inflexão','<p>Na Câmara dos Deputados, o PL 2812/2022, com o mesmo objetivo, foi aprovado nas comissões; em 11/11/2026, o plenário rejeitou o recurso contra o envio do texto ao Senado, onde ainda será analisado.</p>  <p>O PL 1372/2023 representa um ponto de inflexão'),
('12.318/2008','12.318/2010'),
('Em 2026, com a jurisprudência da Lei 14.713/23 plenamente consolidada, quando','Com a Lei 14.713/23, quando'),
]
NOTA='<p><strong>Atualização:</strong> a Resolução CFP 02/2022 foi revogada pela Resolução CFP 14/2023, que hoje trata da atuação do psicólogo na avaliação de riscos psicossociais relacionados ao trabalho.</p>'
ch={}
for r in R:
    for d,_,fs in os.walk('/home/claude/'+r):
        if '/.git' in d: continue
        for f in fs:
            if not f.endswith(('.html','.py','.json','.md')): continue
            p=os.path.join(d,f);t=open(p,encoding='utf-8',errors='ignore').read();o=t
            for a,b in S:
                if a in t: t=t.replace(a,b)
            if r=='perito' and f=='index.html' and 'CFP 02/2022' in t.replace('CFP nº 02','CFP 02') and 'Resolução CFP 14/2023' not in t:
                m=re.search(r'<h3[^>]*>[^<]*CFP (?:nº )?02/2022[^<]*</h3>\s*<p>.*?</p>',t,flags=re.S)
                if m: t=t[:m.end()]+'  '+NOTA+t[m.end():]
            if 'SBPJ' in t:
                t=re.sub(r'pautada pelas diretrizes da <strong>Sociedade Brasileira de Psicologia Jurídica \(SBPJ\)</strong>, exigindo','pautada por normas técnicas, exigindo',t)
            if '010/2010:</strong> dispõe especificamente' in t:
                li='<li><strong>Resolução CFP n.º 010/2010:</strong> dispõe especificamente sobre a atuação do psicólogo em relação à violência doméstica e familiar contra a mulher.</li>'
                novo='' if re.search(r'<li><strong>Resolução CFP n\.º 0?0?8/2010',t) else '<li><strong>Resolução CFP n.º 08/2010:</strong> dispõe sobre a atuação do psicólogo como perito e assistente técnico no Poder Judiciário.</li>'
                t=t.replace(li,novo)
            if t!=o:
                open(p,'w',encoding='utf-8').write(t);ch[p]=1
print(len(ch));open('alterados.txt','w').write('\n'.join(sorted(ch)))
for p in sorted(ch): print(p.replace('/home/claude/',''))
