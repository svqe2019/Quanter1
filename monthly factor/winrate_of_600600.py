from CAL.PyCAL import *
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib import rc
rc('mathtext', default='regular')

data=DataAPI.MktEqumGet(beginDate=u"20100101",endDate=u"20180701",secID='600600.XSHG',field=u"secID,endDate,chgPct",pandas="1")
data['month']=0
for i in range(len(data['endDate'])):
    data['month'][i]=data['endDate'][i][5:7]

indexdata=DataAPI.MktIdxmGet(beginDate=u"20070101",endDate=u"20180701",indexID=u"000905.ZICN",field=u"endDate,chgPct",pandas="1")
d=pd.DataFrame(np.arange(24.0).reshape((12,2)),columns=['month','winrate'])
finaldata=pd.merge(data,indexdata,on='endDate')
finaldata['excessRet']=finaldata['chgPct_x']-finaldata['chgPct_y']
del finaldata['chgPct_x']
del finaldata['chgPct_y']
for i in range(1,13):
    tmp_data=finaldata[finaldata['month']==i]
    winrate=(float(len(tmp_data[tmp_data['excessRet']>0]))+1)/(len(tmp_data['excessRet'])+2)
    b=int(i)-1
    d['month'][b]=i
    d['winrate'][b]=winrate

#画图
print d
fig = plt.figure(figsize=(10, 8))
plt.plot(d['month'],d['winrate'])
plt.show()