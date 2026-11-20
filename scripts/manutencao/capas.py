from PIL import Image,ImageFilter,ImageEnhance
import numpy as np,os,glob,sys,zlib
U='/mnt/user-data/uploads/'
SRC=dict(A='3415d937-image.jpg',C='48fb76c4-image.jpg',E='98ba570b-image.jpg',F='7a03009a-image.jpg',H='c1d88495-image.jpg')
# recortes: (alto 630 -> painel 0,84) e (alto 450 -> painel 1,2)
CROP={'E':((60,60,1062,1250),(60,150,1062,985)),'C':((0,120,900,1190),(0,130,900,880)),'A':((60,30,1062,1220),(60,60,1062,895)),'H':((0,150,900,1220),(0,160,900,910)),'F':((130,10,770,770),(60,10,840,660))}
X0,X1=672,800   # início e fim da transição; painel de X0 a 1200
_c={}
def panel(k,H):
    key=(k,H)
    if key not in _c:
        im=ImageEnhance.Contrast(Image.open(U+SRC[k]).convert('RGB')).enhance(1.05).crop(CROP[k][0 if H>=600 else 1])
        pw=1200-X0;s=max(pw/im.width,H/im.height);im=im.resize((round(im.width*s)+1,round(im.height*s)+1),Image.LANCZOS)
        x=(im.width-pw)//2;im=im.crop((x,0,x+pw,H)).filter(ImageFilter.UnsharpMask(1.2,40,2));_c[key]=np.asarray(im).astype(np.float32)
    return _c[key]
ORD=['E','C','A','H','F']
def patch(f,out=None):
    im=Image.open(f).convert('RGB');a=np.asarray(im).astype(np.float32);H,W,_=a.shape
    if W!=1200: return False
    bg=np.median(a[:,18:30],axis=1)            # cor de fundo linha a linha (margem esquerda, sem texto)
    cream=(bg.min(axis=1)>200)                 # linhas de fundo claro (fora das faixas de cima e de baixo)
    if cream.mean()<0.6: return False          # modelo antigo, sem foto: não mexer
    k=ORD[zlib.crc32(os.path.basename(f).encode())%len(ORD)]
    p=panel(k,H);pw=W-X0
    ramp=np.clip((np.arange(pw)-0)/(X1-X0),0,1)[None,:,None]
    reg=np.repeat(bg[:,None,:],pw,axis=1)
    mix=reg*(1-ramp)+p*ramp
    rows=np.where(cream)[0]
    a[rows,X0:,:]=mix[rows]
    # fora das linhas claras (faixas): mantém a cor da faixa de ponta a ponta
    nr=np.where(~cream)[0];a[nr,X0:,:]=reg[nr]
    o=out or f;res=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    if o.lower().endswith('.webp'): res.save(o,'WEBP',quality=80,method=4)
    else: res.save(o,'JPEG',quality=84,optimize=True,progressive=True)
    return True
if __name__=='__main__':
    for f in sys.argv[1:]: patch(f)
