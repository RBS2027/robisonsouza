from PIL import Image
import numpy as np,glob,sys,os
CREAM=np.array([243,238,231],np.float32);BROWN=np.array([59,48,40],np.float32);NAVY=np.array([24,34,47],np.float32)
def recolor(f,full=False):
    im=Image.open(f).convert('RGB');a=np.asarray(im).astype(np.float32);H,W,_=a.shape
    if W!=1200: return False
    marg=np.median(a[:,18:30],axis=1)
    if (marg.min(axis=1)>200).mean()<0.6: return False     # modelo antigo (verde): não mexer
    lum=a.mean(axis=2);rb=a[...,0]-a[...,2]
    t=np.clip((CREAM.mean()-lum)/(CREAM.mean()-BROWN.mean()),0,1.25)   # 0 = creme, 1 = marrom do texto
    isb=(rb<34)&(t>0.04)&((lum<205) if full else True)                                    # tons da linha creme→marrom (não cobre)
    mask=np.zeros((H,W),bool);mask[:,:(W if full else 668)]=True             # área do texto
    dark_rows=(marg.max(axis=1)<140)&((marg[:,0]-marg[:,2])<40)   # faixa escura de baixo (marrom), de ponta a ponta
    mask[dark_rows,:]=True
    m=mask&isb
    new=CREAM[None,None,:]+np.minimum(t,1.0)[...,None]*(NAVY-CREAM)[None,None,:]
    # faixa escura: tom um pouco mais claro que o texto, como no original
    a[m]=new[m]
    out=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    if f.lower().endswith('.webp'): out.save(f,'WEBP',quality=82,method=4)
    else: out.save(f,'JPEG',quality=85,optimize=True,progressive=True)
    return True
