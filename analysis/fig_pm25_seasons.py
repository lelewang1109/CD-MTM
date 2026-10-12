"""Show all four exploratory months with their sparse motion denominators."""
import json
from pathlib import Path
import numpy as np
import task_reference as tr,figstyle as fs
from pm25_seasons import PERIODS,PLAN
fs.apply();plan=json.loads(PLAN.read_text());assert plan['status']=='complete'
j=json.loads((tr.OUT/'eval_projection.json').read_text())
fig,axs=tr.plt.subplots(1,2,figsize=(fs.TEXT_W,2.2),layout='constrained')
names=list(PERIODS);x=np.arange(4)
for k,m in enumerate(('ST-MTM','A','R 20%')):
 vals=[next(v for v in j[n]['proxy'] if v['method']==m and v['k']==2 and v['eps']==.02) for n in names]
 axs[1].bar(x+(k-1)*.24,[v['error']*100 for v in vals],width=.23,label=m)
labels=[]
for i,n in enumerate(names):
 c=json.loads((tr.OUT/f'replicate_{n}.json').read_text())['certificate']
 axs[0].bar(i,100*c['conflict_share'],color='#d55e00')
 labels.append(n.split('_')[-1].title())
 clear=next(v['clear'] for v in j[n]['proxy'] if v['method']=='A' and v['k']==2 and v['eps']==.02)
 axs[1].text(i,104,f'n={clear}',ha='center',fontsize=7)
axs[0].set(ylabel='conflict frames (%)',ylim=(0,100),title='Shared 100 km smoothing; 30 days/month')
axs[1].set(ylabel='total 2-D proxy error (%)',ylim=(0,115),title='Exploratory; sparse cases')
for a in axs:a.set_xticks(x,labels)
axs[1].legend(loc='upper left',bbox_to_anchor=(0,.83),fontsize=6.5)
for ext in ('pdf','png'):fig.savefig(tr.OUT/f'fig_pm25_seasons.{ext}',dpi=300)
tr.plt.close(fig)
