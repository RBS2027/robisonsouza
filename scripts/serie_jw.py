#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liga entre si os artigos da série "falsas acusações, separação e saúde mental do acusado".
Em cada artigo JÁ PUBLICADO da série, insere o bloco "Leia também nesta série" com até 5 links
para outros artigos da série que também já estejam no ar (neste site e nos outros quatro).
Idempotente; roda no início de scripts/publicar.py. Só liga o que existe: nunca cria link quebrado."""
import os, re, html, urllib.request
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(REPO)
DOMS = {'rs': 'robisonsouza.com.br', 'pe': 'peritoempsicologiaforense.com.br', 'de': 'depoimentoespecial.com.br', 'ep': 'estudopsicossocial.com.br', 'as': 'assistente.tec.br'}
NOMES = {'rs': 'Robison Souza', 'pe': 'Perito em Psicologia Forense', 'de': 'Depoimento Especial', 'ep': 'Estudo Psicossocial', 'as': 'Assistente Técnico'}
DOM = re.search(r'<link rel="canonical" href="https://([^/]+)/', open('index.html', encoding='utf-8').read()).group(1)
EU = [k for k, v in DOMS.items() if v == DOM][0]
SERIE = [
 ("as", "como-discutir-a-motivacao-do-relato-sem-atacar-a-vitima-limites-legais-e-tecnicos", "Motivação do relato: como discutir em juízo", "Estratégia de Defesa"),
 ("as", "acusacoes-reciprocas-como-o-advogado-organiza-a-prova-psicologica-quando-os-dois-se-acusam", "Acusações recíprocas: organizar a prova", "Estratégia de Defesa"),
 ("as", "revisao-da-medida-protetiva-o-que-a-prova-tecnica-psicologica-pode-acrescentar-ao-pedido", "Revisão de medida protetiva e prova técnica", "Estratégia de Defesa"),
 ("as", "pedido-de-arquivamento-do-inquerito-apoiado-em-parecer-psicologico-quando-faz-sentido", "Arquivamento do inquérito com parecer psicológico", "Fase Policial"),
 ("as", "investigacao-defensiva-onde-o-parecer-psicologico-entra", "Investigação defensiva e parecer psicológico", "Estratégia de Defesa"),
 ("as", "retratacao-da-vitima-adulta-anos-depois-da-condenacao-como-vira-prova-na-revisao-criminal", "Retratação da vítima e revisão criminal", "Revisão Criminal"),
 ("as", "assistente-tecnico-psicologo-no-tribunal-do-juri-quando-pode-ser-ouvido-em-plenario", "Assistente técnico psicólogo no Tribunal do Júri", "Tribunal do Júri"),
 ("as", "perseguicao-stalking-como-se-prova-o-dano-psicologico-e-como-se-responde-a-acusacao-infundada", "Stalking: prova do dano e defesa técnica", "Crimes Contra a Liberdade"),
 ("as", "cliente-acusado-em-sofrimento-como-o-advogado-reconhece-acolhe-e-encaminha", "Cliente em sofrimento: o que o advogado pode fazer", "Relação com o Cliente"),
 ("as", "quando-o-acusado-morre-no-curso-do-processo-o-que-acontece-com-a-acao-e-com-a-familia", "Morte do acusado: o processo e a família", "Estratégia de Defesa"),
 ("as", "quando-o-ministerio-publico-pede-a-absolvicao-o-papel-da-prova-psicologica", "Ministério Público pede absolvição: a prova", "Estratégia de Defesa"),
 ("as", "sindrome-da-mulher-de-potifar-na-defesa-por-que-o-rotulo-nao-basta-e-o-que-o-parecer-acrescenta", "Síndrome de Potifar na defesa: o que usar", "Estratégia de Defesa"),
 ("de", "oitivas-anteriores-a-lei-13431-como-analisar-hoje-um-depoimento-colhido-sem-protocolo", "Oitivas antigas: como analisar um depoimento sem protocolo", "Análise Técnica"),
 ("de", "varias-criancas-da-mesma-escola-relatam-o-mesmo-fato-como-analisar-a-contaminacao-entre-relatos", "Várias crianças relatam: contaminação entre relatos", "Análise Técnica"),
 ("de", "quando-o-adolescente-demonstra-duvida-no-depoimento-especial-como-ler-a-ambivalencia", "Dúvida do adolescente no depoimento especial", "Análise Técnica"),
 ("de", "acusacao-surgida-durante-a-disputa-de-guarda-o-que-observar-no-video-do-depoimento-especial", "Acusação na guarda e o depoimento especial", "Análise Técnica"),
 ("ep", "depois-da-absolvicao-criminal-como-se-retoma-a-convivencia-com-o-filho", "Absolvido: como retomar a convivência com o filho", "Análise Técnica"),
 ("ep", "grupos-reflexivos-para-autores-de-violencia-o-que-o-relatorio-de-frequencia-diz-ao-processo-de-guarda", "Grupo reflexivo e guarda: o que o relatório diz", "Análise Técnica"),
 ("ep", "pai-ou-mae-que-cria-o-filho-sozinho-e-e-acusado-quem-cuida-da-crianca-durante-o-processo", "Pai solo acusado: quem cuida do filho", "Família e Processo Criminal"),
 ("ep", "acusacao-no-meio-do-divorcio-como-o-estudo-psicossocial-lida-com-versoes-opostas", "Acusação no divórcio e o estudo psicossocial", "Família e Processo Criminal"),
 ("ep", "estudo-psicossocial-quando-os-dois-pais-se-acusam-como-a-equipe-evita-tomar-partido", "Estudo psicossocial com acusações recíprocas", "Método do Estudo"),
 ("pe", "indenizacao-por-falsa-acusacao-como-a-pericia-psicologica-demonstra-o-dano", "Indenização por falsa acusação: a perícia do dano", "Perícia do Dano"),
 ("pe", "crime-sexual-contra-adulto-com-deficiencia-intelectual-capacidade-de-relatar-e-de-consentir", "Deficiência intelectual: relatar e consentir", "Método Pericial"),
 ("pe", "formulario-nacional-de-avaliacao-de-risco-o-que-e-e-como-deve-ser-lido-no-processo", "Formulário de Avaliação de Risco: como ler", "Violência Doméstica"),
 ("pe", "dano-a-familia-do-acusado-como-a-pericia-psicologica-avalia-o-dano-reflexo", "Dano reflexo à família do acusado: a perícia", "Perícia do Dano"),
 ("pe", "estresse-pos-traumatico-depois-de-processo-criminal-como-a-pericia-avalia", "Estresse pós-traumático após processo: perícia", "Dano Psíquico"),
 ("pe", "como-a-pericia-avalia-a-motivacao-do-relato-sem-presumir-ma-fe-nem-veracidade", "Motivação do relato: como a perícia avalia", "Método Pericial"),
 ("pe", "avaliacao-psicologica-do-acusado-o-que-o-exame-pode-e-nao-pode-dizer-sobre-o-fato", "Avaliação psicológica do acusado: limites", "Método Pericial"),
 ("pe", "vulnerabilidade-do-adulto-no-interrogatorio-como-a-pericia-avalia-a-sugestionabilidade", "Sugestionabilidade do adulto no interrogatório", "Método Pericial"),
 ("rs", "absolvido-mas-marcado-o-dano-psicologico-que-continua-depois-da-absolvicao", "Absolvido, mas marcado: o dano após a absolvição", "Falsas Acusações"),
 ("rs", "a-familia-do-acusado-o-que-filhos-conjuge-e-pais-atravessam-durante-o-processo", "A família do acusado durante o processo", "Falsas Acusações"),
 ("rs", "exposicao-do-acusado-nas-redes-antes-do-julgamento-efeitos-psicologicos-e-como-documentar", "Acusado exposto nas redes antes do julgamento", "Falsas Acusações"),
 ("rs", "prisao-preventiva-por-acusacao-depois-afastada-efeitos-psicologicos-e-registro-do-dano", "Prisão preventiva e absolvição: o registro do dano", "Falsas Acusações"),
 ("rs", "importunacao-sexual-quando-a-unica-prova-e-o-relato-de-um-adulto", "Importunação sexual: quando só há o relato", "Crimes Sexuais"),
 ("rs", "mensagens-prints-e-audios-entre-os-adultos-o-que-revelam-sobre-o-contexto-da-acusacao", "Mensagens e áudios: o contexto da acusação", "Falsas Acusações"),
 ("rs", "acusacao-de-crime-sexual-contra-servidor-ou-militar-a-prova-psicologica-no-processo-disciplinar", "Servidor acusado: prova psicológica no disciplinar", "Falsas Acusações"),
 ("rs", "sinais-de-sofrimento-grave-em-quem-responde-a-processo-o-que-a-familia-e-o-advogado-devem-observar", "Acusado em sofrimento: sinais que pedem atenção", "Saúde Mental"),
 ("rs", "como-atravessar-um-processo-por-falsa-acusacao-sem-adoecer-orientacoes-praticas", "Como atravessar o processo sem adoecer", "Saúde Mental"),
 ("rs", "acusado-deve-fazer-terapia-durante-o-processo-o-que-o-terapeuta-pode-e-nao-pode-levar-aos-autos", "Terapia durante o processo: o que vai aos autos", "Saúde Mental"),
 ("rs", "como-falar-de-suicidio-ao-comentar-casos-de-falsa-acusacao-cuidados-de-quem-publica", "Suicídio e falsa acusação: como falar do tema", "Saúde Mental"),
 ("rs", "morte-psiquica-o-colapso-da-identidade-de-quem-e-acusado-injustamente", "Morte psíquica: o colapso de quem é acusado", "Saúde Mental"),
 ("rs", "por-que-muitos-absolvidos-nao-buscam-reparacao-a-desistencia-como-autoprotecao", "Por que muitos absolvidos não buscam reparação", "Saúde Mental"),
 ("rs", "professor-acusado-por-alunos-o-que-a-defesa-tecnica-examina-primeiro", "Professor acusado por alunos: a defesa técnica", "Falsas Acusações"),
 ("rs", "o-primeiro-passo-para-se-reconstruir-depois-de-uma-acusacao-injusta", "Como se reconstruir depois de acusação injusta", "Saúde Mental"),
 ("rs", "cvv-188-como-funciona-e-quando-ligar-durante-um-processo-judicial", "CVV 188: como funciona e quando ligar", "Saúde Mental"),
 ("rs", "luto-por-suicidio-de-quem-respondia-a-processo-como-apoiar-a-familia", "Luto por suicídio: como apoiar a família", "Saúde Mental"),
 ("rs", "falsas-acusacoes-em-numeros-o-que-as-pesquisas-mostram-e-o-que-nao-mostram", "Falsas acusações em números: o que se sabe", "Falsas Acusações"),
 ("rs", "sindrome-da-mulher-de-potifar-o-que-e-de-onde-vem-e-por-que-nao-e-diagnostico-psicologico", "Síndrome da Mulher de Potifar: o que é", "Falsas Acusações"),
 ("rs", "acusacoes-que-surgem-na-separacao-o-que-a-psicologia-do-testemunho-examina", "Acusações na separação: o que se examina", "Falsas Acusações"),
 ("rs", "rotulos-e-sindromes-no-processo-o-que-a-psicologia-reconhece-e-o-que-nao-reconhece", "Rótulos e síndromes no processo judicial", "Psicologia Forense"),
 ("rs", "da-separacao-ao-processo-criminal-as-etapas-da-escalada-do-conflito", "Da separação ao processo: a escalada", "Conflito Familiar"),
 ("rs", "palavra-contra-palavra-entre-adultos-como-a-psicologia-examina-o-relato-sem-testemunhas", "Palavra contra palavra: como se examina", "Psicologia do Testemunho"),
 ("rs", "como-a-memoria-reconstroi-a-historia-do-casal-depois-da-separacao", "Memória e separação: a história recontada", "Psicologia do Testemunho"),
 ("rs", "quando-os-dois-se-acusam-acusacoes-reciprocas-e-o-que-a-analise-tecnica-examina", "Acusações recíprocas: o que se examina", "Conflito Familiar"),
 ("rs", "a-influencia-de-familiares-e-amigos-no-relato-de-um-adulto-como-a-versao-se-forma-em-grupo", "Influência de familiares e amigos no relato", "Psicologia do Testemunho"),
 ("rs", "por-que-inocentes-as-vezes-admitem-ou-se-calam-a-psicologia-da-confissao-e-do-silencio", "Por que inocentes admitem ou se calam", "Psicologia do Testemunho"),
 ("rs", "vergonha-e-culpa-de-quem-e-acusado-injustamente-por-que-aparecem-e-como-lidar", "Vergonha e culpa de quem é acusado", "Saúde Mental"),
 ("rs", "voltar-ao-trabalho-depois-de-uma-acusacao-o-que-esperar-e-como-se-preparar", "Voltar ao trabalho depois de uma acusação", "Saúde Mental"),
 ("rs", "afastado-dos-filhos-por-uma-acusacao-o-luto-da-convivencia-interrompida", "Afastado dos filhos por uma acusação", "Saúde Mental")
]
FIXAS = [('rs', 'documentario-absolvido-mas-morto', 'Documentário “Absolvido, mas morto”: minha participação', 'Documentário')]
A, B = '<!-- serie-jw -->', '<!-- /serie-jw -->'
def local(slug):
    for p in (f'{slug}/index.html', f'blog/{slug}/index.html'):
        if os.path.exists(p): return p
_cache = {}
def no_ar(site, slug):
    """URL pública do artigo se ele já estiver publicado; senão None."""
    k = (site, slug)
    if k in _cache: return _cache[k]
    url = None
    if site == EU:
        p = local(slug)
        if p: url = '/' + p[:-10]
    else:
        for pref in ('', 'blog/'):
            u = f'https://{DOMS[site]}/{pref}{slug}/'
            try:
                req = urllib.request.Request(u, method='HEAD', headers={'User-Agent': 'serie-jw'})
                if urllib.request.urlopen(req, timeout=6).status == 200: url = u; break
            except Exception: pass
    _cache[k] = url; return url
def main():
    todos = [tuple(x) for x in SERIE] + FIXAS; n = 0
    for i, (site, slug, tit, rot) in enumerate(todos[:len(SERIE)]):
        if site != EU: continue
        p = local(slug)
        if not p: continue
        t = open(p, encoding='utf-8').read(); t0 = t
        t = re.sub(re.escape(A) + r'.*?' + re.escape(B) + r'\n?', '', t, flags=re.S)
        cand = [x for x in todos if x[1] != slug]
        cand = sorted(cand, key=lambda x: (x[3] != rot, (todos.index(x) - i) % len(todos)))
        links = []; por_site = {}
        for s2, sl2, t2, r2 in cand:
            if len(links) >= 5: break
            if s2 != EU and por_site.get(s2, 0) >= 1: continue
            if s2 == EU and por_site.get(s2, 0) >= 3: continue
            if f'/{sl2}/' in t: continue
            u = no_ar(s2, sl2)
            if not u: continue
            por_site[s2] = por_site.get(s2, 0) + 1
            extra = '' if s2 == EU else f' <small>({NOMES[s2]})</small>'
            rel = '' if s2 == EU else ' rel="noopener"'
            links.append(f'<li><a href="{u}"{rel}>{html.escape(t2)}</a>{extra}</li>')
        if links:
            bloco = f'{A}<section class="serie-jw" aria-label="Série"><h2 id="serie">Leia também nesta série</h2><ul>{"".join(links)}</ul></section>{B}\n'
            for marca in ('<!-- rede-2027 -->', '<div class="faixa-cta">', '</article>'):
                j = t.find(marca)
                if j > 0: t = t[:j] + bloco + t[j:]; break
        if t != t0: open(p, 'w', encoding='utf-8').write(t); n += 1
    print(f'serie-jw: {n} artigo(s) atualizado(s)')
if __name__ == '__main__': main()
