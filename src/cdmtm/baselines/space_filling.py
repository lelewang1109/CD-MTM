"""Native sample linearizations by fixed canonical 2-D Hilbert/Morton curves.

Every scalar grid cell appears exactly once. A minimal power-of-two square
is used for indexing; out-of-domain cells are discarded, never interpolated.
Axes: x = grid column, y = grid row, origin (0,0). No rotation/orientation search
or feature-dependent ordering. These are sample-domain baselines, not packed
leaf-order layouts or bit-identical copies of an external Inviwo processor.
"""
from functools import lru_cache
import numpy as np

def _hilbert_xy(side, distance):
 x=y=0;t=int(distance);s=1
 while s<side:
  rx=(t//2)&1;ry=(t^rx)&1
  if ry==0:
   if rx==1:x,y=s-1-x,s-1-y
   x,y=y,x
  x+=s*rx;y+=s*ry;t//=4;s*=2
 return x,y

@lru_cache(maxsize=32)
def sample_order(shape, curve):
 ny,nx=map(int,shape)
 if min(ny,nx)<1:raise ValueError('Grid dimensions must be positive')
 if curve not in ('Hilbert','Morton'):raise ValueError(f'Unknown curve: {curve}')
 side=1<<(max(nx,ny)-1).bit_length();bits=(side-1).bit_length()
 if curve=='Hilbert':
  cells=[(x,y) for d in range(side*side) for x,y in [_hilbert_xy(side,d)] if x<nx and y<ny]
  order=np.array([y*nx+x for x,y in cells],dtype=int)
 else:
  y,x=np.indices((ny,nx));codes=np.zeros((ny,nx),dtype=np.uint64)
  for b in range(bits):codes|=((x.astype(np.uint64)>>b)&1)<<(2*b);codes|=((y.astype(np.uint64)>>b)&1)<<(2*b+1)
  order=np.argsort(codes.ravel(),kind='stable')
 if not np.array_equal(np.sort(order),np.arange(nx*ny)):raise AssertionError('Not a complete sample permutation')
 order.setflags(write=False)
 return order

def linearize(fields, curve):
 fields=np.asarray(fields,float)
 if fields.ndim!=3 or not np.isfinite(fields).all():raise ValueError('Expected finite T×Y×X scalar fields')
 return fields.reshape(len(fields),-1)[:,sample_order(fields.shape[1:],curve)].T

def inverse_order(shape,curve):
 order=sample_order(shape,curve);inverse=np.empty(len(order),int);inverse[order]=np.arange(len(order));return inverse

def merge_levels_on_line(values, anchor_ranks, kind):
 """Actual 1-D barriers between feature samples; no optimal refilling applied."""
 values=np.asarray(values,float);r=np.asarray(anchor_ranks,int)
 if kind not in ('join','split'):raise ValueError(kind)
 if r.ndim!=1 or np.any(r<0) or np.any(r>=len(values)):raise ValueError('Invalid anchors')
 result=np.diag(values[r])
 for i in range(len(r)):
  for j in range(i+1,len(r)):
   lo,hi=sorted((int(r[i]),int(r[j])));v=values[lo:hi+1]
   result[i,j]=result[j,i]=v.max() if kind=='join' else v.min()
 return result
