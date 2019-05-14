start = '2017-01-01'                       # 回测起始时间
end = '2018-07-02'                          # 回测结束时间
benchmark = 'HS300'                        # 策略参考标准
universe = DynamicUniverse('HS300')  # 证券池，支持股票和基金
capital_base = 10000000                      # 起始资金
freq = 'd'                                 # 策略类型，'d'表示日间策略使用日线回测，'m'表示日内策略使用分钟线回测
refresh_rate = Monthly(1)                           # 调仓频率
nn = 10

cal = Calendar('China.SSE')
period = Period('-1B')

def initialize(account):
    pass

def handle_data(account):
    
    today=account.current_date
    yesterday=cal.advanceDate(today,period)
    
    _universe1 = account.get_universe(exclude_halt=False)
    _universe2 = univClear(_universe1, account, account.current_date)
    _universe3 = new_remove(_universe2)
    _universe = st_remove(_universe3)
    
    buylist=train(yesterday,_universe,period,start,nn)

    # 先卖出
    for stock in account.avail_security_position.keys():
        if stock in _universe and stock not in buylist:
            account.order_to(stock,0)
            
    # 再买入
    for stock in buylist:
        account.order_pct_to(stock, 1.0/len(buylist))

  