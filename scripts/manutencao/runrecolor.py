import sys,glob,os
sys.path.insert(0,'/home/claude/work/fotos');import recolor
from PIL import Image
import numpy as np
R='/home/claude/'
n=s=0
for pat in ['robisonsouza/assets/capas/*','perito/assets/capas/*','depoimentoespecial/assets/img/blog/*','estudopsicossocial/assets/img/blog/*','assistente/assets/img/blog/*','depoimentoespecial/assets/img/og/*','estudopsicossocial/assets/img/og/*','assistente/assets/img/og/*']:
    for f in sorted(glob.glob(R+pat)):
        if not f.lower().endswith(('.webp','.jpg','.jpeg')): continue
        if recolor.recolor(f): n+=1
        else: s+=1
for f in ['robisonsouza/assets/og-padrao.jpg','perito/assets/og-padrao.jpg','depoimentoespecial/assets/img/og.jpg','estudopsicossocial/assets/img/og.jpg','assistente/assets/img/og.jpg']:
    print(f,recolor.recolor(R+f,full=True))
print('capas',n,'puladas',s)
NAVY=np.array([24,34,47],np.float32)
def icon(f,green):
    im=Image.open(f);sizes=None
    if f.endswith('.ico'): sizes=sorted(im.ico.sizes()); im=max((im.ico.getimage(z) for z in sizes),key=lambda i:i.width)
    a=np.asarray(im.convert('RGBA')).astype(np.float32);rgb=a[...,:3]
    g=np.array(green,np.float32);t=np.clip((255-rgb.mean(axis=2))/(255-g.mean()),0,1)[...,None]
    a[...,:3]=255+t*(NAVY-255)
    o=Image.fromarray(a.astype(np.uint8),'RGBA')
    if sizes: o.save(f,sizes=sizes)
    else: o.save(f)
for r in ['depoimentoespecial','estudopsicossocial','assistente']:
    for x in ['favicon.png','apple-touch-icon.png']: icon(R+r+'/assets/img/'+x,(14,39,33))
for r in ['robisonsouza','perito']: icon(R+r+'/favicon.ico',(8,28,22))
