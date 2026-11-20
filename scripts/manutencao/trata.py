from PIL import Image,ImageFilter,ImageEnhance,ImageOps,ImageDraw
import numpy as np,os
U='/mnt/user-data/uploads/'
SRC=dict(A='3415d937-image.jpg',B='a5b70ba9-image.jpg',C='48fb76c4-image.jpg',D='ba7f5619-image.jpg',E='98ba570b-image.jpg',F='7a03009a-image.jpg',G='49f74e9f-image.jpg',H='c1d88495-image.jpg')
def load(k): return Image.open(U+SRC[k]).convert('RGB')
def grade(im,contrast=1.06,sharp=1.0,warm=0.0):
    im=ImageEnhance.Contrast(im).enhance(contrast)
    if warm:
        a=np.asarray(im).astype(np.float32);a[...,0]*=1+warm;a[...,2]*=1-warm;im=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    return im
def finish(im,size,sharp=60):
    im=im.resize(size,Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1.2,percent=sharp,threshold=2))
def extend(sub,W,H,pos=0.62,seed=1):
    """coloca o retrato (altura H) numa tela W×H, estendendo o fundo de estúdio para os lados"""
    s=sub.resize((round(sub.width*H/sub.height),H),Image.LANCZOS);sw=s.width
    x0=max(0,min(W-sw,round(W*pos-sw/2)));F=min(110,sw//5)
    can=Image.new('RGB',(W,H))
    def fill(strip,w,flip):
        col=strip.resize((1,H),Image.BOX).filter(ImageFilter.GaussianBlur(6))
        f=np.asarray(col.resize((max(1,w),H),Image.BILINEAR)).astype(np.float32)
        ramp=np.linspace(1.0,0.86,max(1,w))[None,:,None]
        if flip: ramp=ramp[:,::-1,:]
        return Image.fromarray(np.clip(f*ramp,0,255).astype(np.uint8))
    lw=x0+F;rw=W-(x0+sw-F)
    if x0>0: can.paste(fill(s.crop((0,0,40,H)),lw,True),(0,0))
    if x0+sw<W: can.paste(fill(s.crop((sw-40,0,sw,H)),rw,False),(x0+sw-F,0))
    if x0==0: can.paste(s.crop((0,0,F,H)),(0,0))
    if x0+sw>=W: can.paste(s.crop((sw-F,0,sw,H)),(x0+sw-F,0))
    m=np.full((H,sw),255,np.float32);r=np.linspace(0,255,F)
    if x0>0: m[:,:F]=r[None,:]
    if x0+sw<W: m[:,sw-F:]=r[::-1][None,:]
    can.paste(s,(x0,0),Image.fromarray(m.astype(np.uint8)))
    rng=np.random.default_rng(seed);a=np.asarray(can).astype(np.float32);a+=rng.normal(0,1.5,a.shape[:2])[...,None];return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def save(im,name,q=82):
    os.makedirs('out',exist_ok=True)
    if name.endswith('.webp'): im.save('out/'+name,'WEBP',quality=q,method=6)
    else: im.save('out/'+name,'JPEG',quality=q,optimize=True,progressive=True)
    print(name,im.size,os.path.getsize('out/'+name)//1024,'KB')
# 1) miniatura do autor (4:5) — foto F, olhando para a câmera
F_=grade(load('F'));save(finish(F_.crop((262,22,612,460)).resize((350,438)),(320,400),70),'retrato-thumb.webp',84)
# 2) retrato 4:5 (de/ep/as) — foto D, P&B com leve tom quente
D_=load('D');g=ImageOps.grayscale(D_);D2=ImageOps.colorize(g,(10,9,8),(250,247,242),mid=(128,124,119));save(finish(grade(D2,1.04),(900,1125),50),'retrato.webp',84)
# 3) retrato oficial 900x603 (quem-sou rs/perito) — foto H
H_=grade(load('H'),1.05);save(finish(H_.crop((0,150,900,753)),(900,603),50),'retrato-oficial.jpg',86)
# 4) fundo/abertura 1200x800 (+640x427) — foto C (poltrona), fundo estendido
C_=grade(load('C'),1.05);c=C_.crop((0,110,900,1310));e=extend(c,1200,800,pos=0.66,seed=2);save(e.filter(ImageFilter.UnsharpMask(1.2,40,2)),'escritorio.webp',80);save(e.resize((640,427),Image.LANCZOS),'escritorio-m.webp',78)
# 5) de: perfil-neutro 1100x760 — foto F, meio corpo, fundo estendido
f=F_.crop((0,10,900,950));save(extend(f,1100,760,pos=0.5,seed=3).filter(ImageFilter.UnsharpMask(1.2,40,2)),'perfil-neutro.webp',82)
# 6) de: consultorio 1200x800 — foto H inteira, fundo estendido
h=H_.crop((0,120,900,1420));save(extend(h,1200,800,pos=0.5,seed=4).filter(ImageFilter.UnsharpMask(1.2,40,2)),'consultorio.webp',80)
# 7) de: livro 1200x821 — foto E
E_=grade(load('E'),1.05);save(extend(E_.crop((0,50,1122,1200)),1200,821,pos=0.5,seed=5).filter(ImageFilter.UnsharpMask(1.2,40,2)),'livro.webp',82)
# 8) de: escrivaninha 1200x805 — foto A
A_=grade(load('A'),1.04);save(extend(A_.crop((0,30,1122,1180)),1200,805,pos=0.5,seed=6).filter(ImageFilter.UnsharpMask(1.2,40,2)),'escrivaninha.webp',82)
