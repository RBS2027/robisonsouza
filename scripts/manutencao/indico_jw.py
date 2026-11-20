# Quadro "Procure um advogado especializado" (Dra. Jamily Wenceslau) nos artigos de temas de defesa
# (falsas acusações, crimes sexuais, inquérito, medida protetiva, revisão criminal, Júri). Não repete.
import glob,re,html,sys
R='/home/claude/'
INC=r'fals[ao]s? acusa|falsamente|injustamente|caluniosa|infundad|medida protetiva|revis[ãa]o criminal|inqu[ée]rito|processo criminal|per[íi]cia criminal|pericial criminal|processo penal|apela[çc][ãa]o criminal|tribunal do j[úu]ri|absolvi|acusado|condenad|condena[çc][ãa]o se|defensiva|para a defesa|crimes? sexua(l|is)|transitada em julgado|alega[çc][ãa]o simult|acusa[çc][ãa]o de abuso|alega[çc][ãa]o de abuso|prova [úu]nica|contesta[çc][ãa]o de depoimento|delegacia|importuna[çc][ãa]o|persegui[çc][ãa]o \(stalking|arquivamento|contexto da acusa|pris[ãa]o preventiva|oitivas anteriores|grupos reflexivos'
EXC=r'feminic|explora[çc][ãa]o sexual|aliciamento|para crian[çc]as: lei henry|medo de encontrar|primeira revela[çc][ãa]o|psicologia criminal|ex-detento|insanidade|imputabilidade|execu[çc][ãa]o penal|condena[çc][ãa]o criminal do genitor|perda do poder familiar|agressor condenado|bullying|viol[êe]ncia psicol|abuso psicol'
def box(site):
    pg='/indicacao-dra-jamily-wenceslau/' if site=='robisonsouza' else 'https://robisonsouza.com.br/indicacao-dra-jamily-wenceslau/'
    return ('<!-- indico-jw --><aside class="indico-jw" aria-label="Orientação" style="margin:2rem 0;padding:.9rem 1.15rem;background:#FBF8F3;border:1px solid #E4DACB;border-radius:12px;font-size:.96rem">'
    '<p style="margin:0"><strong>Ainda sem advogado?</strong> A orientação é sempre procurar um profissional especializado no assunto. A Dra. Jamily Wenceslau, advogada criminalista (OAB/SP 453.755), é uma das profissionais que indico. '
    f'<a href="{pg}">Saiba mais</a>.</p></aside><!-- /indico-jw -->\n')
SITES=['robisonsouza','depoimentoespecial','estudopsicossocial']  # sites voltados às partes; não entra no perito nem no assistente (para advogados)
def titulo(s):
    m=re.search(r'<h1[^>]*>(.*?)</h1>',s,flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>','',m.group(1))).strip().lower() if m else ''
if __name__=='__main__':
    tot=0
    for r in SITES:
        n=f=0
        for p in sorted(glob.glob(R+f'{r}/**/index.html',recursive=True)):
            s=open(p,encoding='utf-8').read()
            if ('"BlogPosting"' not in s and '"Article"' not in s) or '<!-- rede-2027 -->' not in s or '<!-- indico-jw -->' in s: continue
            t=titulo(s)
            if not re.search(INC,t) or re.search(EXC,t): continue
            s=s.replace('<!-- rede-2027 -->',box(r)+'<!-- rede-2027 -->',1)
            open(p,'w',encoding='utf-8').write(s)
            if '/_fila/' in p: f+=1
            else: n+=1
        print(r,'no ar',n,'fila',f);tot+=n+f
    print('total',tot)
