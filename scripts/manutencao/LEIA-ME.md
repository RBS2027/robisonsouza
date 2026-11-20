# Ferramentas de manutenção dos 5 sites (MKT2027)

Guardadas em 19/11/2026. Rodam com os cinco repositórios clonados lado a lado em /home/claude
(robisonsouza, perito, depoimentoespecial, estudopsicossocial, assistente).

| Arquivo | O que faz |
|---|---|
| aud.py | Varredura: links internos quebrados, sitemap, canonical, h1, JSON-LD, termos vedados, WhatsApp diferente do oficial |
| td.py | Títulos e descrições: longos, curtos, repetidos |
| fixtd.py | Reescrita dos títulos e descrições fracos (19/11/2026) |
| links.py | Distribuição de links internos: artigos pouco citados recebem links de artigos do mesmo tema (parágrafo class="veja-tb") |
| presencial.py | Troca de "100% online, presencial apenas sob consulta" por "em todo o território nacional, online ou presencial" |
| capitais_c.py + cidades.py | Gerador das páginas de comarca do robisonsouza (só com fato local de fonte oficial) |
| estados_pe.py | Gerador das páginas de estado do perito (cadastro de peritos por tribunal) |
| fixnormas.py | Correções de leis e resoluções citadas (auditoria de 19/11/2026) |
| diagramas.json | Os 7 diagramas explicativos reutilizados nos artigos |

Regras que estas ferramentas pressupõem: contato só pelo WhatsApp (12) 99740-2674; atuação "em todo o
território nacional, online ou presencial"; "condições de produção do relato", nunca "análise de
credibilidade" como método; só afirmar o que tem fonte oficial.
