import pandas as pd
import numpy as np
from CAL.PyCAL import *
import functools
import datetime

def st_remove(source_universe, st_date=None):
    """
    给定股票列表,去除其中在某日被标为ST的股票
    Args:
        source_universe (list of str): 需要进行筛选的股票列表
        st_date (datetime): 进行筛选的日期,默认为调用当天
    Returns:
        list: 去掉ST股票之后的股票列表

    Examples:
        >> universe = set_universe('A')
        >> universe_without_st = st_remove(universe)
    """
    st_date = st_date if st_date is not None else datetime.datetime.now().strftime('%Y%m%d')
    df_ST = DataAPI.SecSTGet(secID=source_universe, beginDate=st_date, endDate=st_date, field=['secID'])
    return [s for s in source_universe if s not in list(df_ST['secID'])]

def new_remove(ticker,tradeDate= None,day = 75):
    tradeDate = tradeDate if tradeDate is not None else datetime.datetime.now()
    period = '-' + str(day) + 'B'
    pastDate = cal.advanceDate(tradeDate,period)
    pastDate = pastDate.strftime("%Y-%m-%d")

    tickerDist={}
    tickerShort=[] 
    for index in range(len(ticker)):
        OneTickerShort=ticker[index][0:6]
        tickerShort.append(OneTickerShort)
        tickerDist[OneTickerShort]=ticker[index]

    ipo_date = DataAPI.SecIDGet(partyID=u"",assetClass=u"",ticker=tickerShort,cnSpell=u"",field=u"ticker,listDate",pandas="1")
    remove_list = ipo_date[ipo_date['listDate'] > pastDate]['ticker'].tolist()
    remove_list=[values for keys,values in tickerDist.items() if keys in remove_list ] 
    return [stk for stk in ticker if stk not in remove_list] 

def univClear(univ, account, date):
    # 1. 去除停牌股票
    univ = [s for s in univ if s in account.universe]

    # 2. 去除ST股
    df_ST = DataAPI.SecSTGet(secID=univ, beginDate=date, endDate=date, field=['secID'])
    univ = [s for s in univ if s not in list(df_ST['secID'])]
    
    # 下面这种方法是暴力去掉名字里含有 ST 等字样的股票
    df_ST = DataAPI.EquGet(secID=univ,field=u"secID,secShortName",pandas="1")
    STlist = list(df_ST.loc[df_ST.secShortName.str.contains('S'), 'secID'])
    univ = [s for s in univ if s not in STlist]
    
    # 3. 去除流动性差的股票
    tv = account.get_attribute_history('turnoverValue', 20)
    mtv = {sec: sum(tvs)/20. for sec, tvs in tv.iteritems()}
    univ = [s for s in univ if mtv.get(s, 0) >= 10000000]

    # 4. 去除新上市或复牌的股票
    opn = account.get_attribute_history('openPrice', 1)
    univ = [s for s in univ if not (np.isnan(opn.get(s, 0)[0]) or opn.get(s, 0)[0] == 0)]
    
    return univ
            
def train(yesterday,_universe,period,start,nn):
    start2=str(int(start[:4])-nn)+'-'+str(start[5:7])+'-'+str(start[-2:])
    for stk in _universe:
        # print stk
        data=DataAPI.MktEqumGet(beginDate=start2,endDate=yesterday,secID=stk,field=u"secID,endDate,chgPct",pandas="1")
        data['month']=0
        for i in range(len(data['endDate'])):
            data['month'][i]=data['endDate'][i][5:7]

        indexdata=DataAPI.MktIdxmGet(beginDate=start2,endDate=yesterday,indexID=u"000300.ZICN",field=u"endDate,chgPct",pandas="1")
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
        factime=str(int(start[:4])-nn)+'-'+str(start[5:7])+'-'+str(start[-2:])
        cal_dates = DataAPI.TradeCalGet(exchangeCD=u"XSHG", beginDate=factime, endDate=yesterday).sort('calendarDate')
        cal_dates = cal_dates[cal_dates['isOpen']==1]
        all_date = cal_dates.ix[:,['exchangeCD','calendarDate']]
        all_date.columns = ['exchangeCD','tradeDate']
        del all_date['exchangeCD']
        all_date[stk]=0
        all_date=all_date.reset_index(drop=True)
        for i in range(len(all_date['tradeDate'])):
            if str(all_date.ix[i,'tradeDate'][5:7])=='01':
                all_date.ix[i,stk]=d['winrate'][0]
            if str(all_date.ix[i,'tradeDate'][5:7])=='02':
                all_date.ix[i,stk]=d['winrate'][1]
            if str(all_date.ix[i,'tradeDate'][5:7])=='03':
                all_date.ix[i,stk]=d['winrate'][2]
            if str(all_date.ix[i,'tradeDate'][5:7])=='04':
                all_date.ix[i,stk]=d['winrate'][3]
            if str(all_date.ix[i,'tradeDate'][5:7])=='05':
                all_date.ix[i,stk]=d['winrate'][4]
            if str(all_date.ix[i,'tradeDate'][5:7])=='06':
                all_date.ix[i,stk]=d['winrate'][5]
            if str(all_date.ix[i,'tradeDate'][5:7])=='07':
                all_date.ix[i,stk]=d['winrate'][6]
            if str(all_date.ix[i,'tradeDate'][5:7])=='08':
                all_date.ix[i,stk]=d['winrate'][7]
            if str(all_date.ix[i,'tradeDate'][5:7])=='09':
                all_date.ix[i,stk]=d['winrate'][8]
            if str(all_date.ix[i,'tradeDate'][5:7])=='10':
                all_date.ix[i,stk]=d['winrate'][9]
            if str(all_date.ix[i,'tradeDate'][5:7])=='11':
                all_date.ix[i,stk]=d['winrate'][10]
            if str(all_date.ix[i,'tradeDate'][5:7])=='12':
                all_date.ix[i,stk]=d['winrate'][11]
        # if all_date.columns[1]=='600000.XSHG':
        if all_date.columns[1]=='000001.XSHE':
            start_data=all_date
        else:
            start_data = pd.merge(start_data,all_date,on='tradeDate')
    start_data=start_data.set_index('tradeDate')
    perdiv=start_data.loc[[str(yesterday)],:]
    perdiv=perdiv.T.sort_values(by=str(yesterday),ascending=False)
    secID2=pd.DataFrame(perdiv.index,columns=['secID'])
    perdiv=pd.DataFrame(perdiv.values,columns=['perdiv'])
    perdiv=pd.concat([perdiv,secID2],axis=1)
    perdiv=perdiv.dropna()
    perdiv=perdiv.sort(columns='perdiv',ascending=False)
    perdiv=perdiv[perdiv['perdiv']>0.6]
    buylist=perdiv['secID'].tolist()
    return buylist