universe = ['RBM0']                  # 策略交易的期货合约，此处选择螺纹钢主力合约
start = "2017-01-01"                 # 回测开始时间
end   = "2017-03-07"                 # 回测结束时间
capital_base = 1000000               # 初始可用资金
refresh_rate = 5                     # 算法调用周期
freq = 'm'                           # 算法调用频率：m-> 分钟；d-> 日；
margin_rate = {'IF': 0.16, 'RB': 0.1}  #交易保证金比率
commission = {'IF':(5, 5, 'perShare'), 'RB': (5, 5,'perShare')} #交易佣金费率。
slippage = Slippage(0.000025, 'perValue') #交易滑点。

def initialize(futures_account):           # 初始化虚拟期货账户，一般用于设置计数器，回测辅助变量等。
    account.buy_signal = 0
    account.sell_signal = 0
    pass

### 回测算法逻辑，每次数据推送运行一次
def handle_data(futures_account):
    symbol = get_symbol('RBM0')
    
    # 返回dict
    all_data = get_symbol_history(symbol, time_range=100)
    
    if len(all_data) == 0:
        return

    close_price = np.array(all_data[symbol]['closePrice'])
    upper,middle,lower = talib.BBANDS(close_price, timeperiod=14)
    last_price = close_price[-1]
    
    # 多 开单
    if last_price > upper[-1] and account.buy_signal==0:
        account.buy_signal = 1
        order(symbol, 100, 'open')
        print futures_account.current_date,'--',futures_account.current_time,'--','多-开'
    
    # 多 平仓
    if last_price < middle[-1] and account.buy_signal == 1:
        account.buy_signal = 0
        order(symbol, 100, 'close')
        print futures_account.current_date,'--',futures_account.current_time,'--','多-平'
        
    # 空 开仓
    if last_price < lower[-1] and account.sell_signal ==0:
        account.sell_signal = 1
        order(symbol, 100, 'close')
        print futures_account.current_date,'--',futures_account.current_time,'--','空-开'
        
    #空 平仓
    if last_price > middle[-1] and account.sell_signal == 1:
        account.sell_signal = 0
        order(symbol, 100, 'open')
        print futures_account.current_date,'--',futures_account.current_time,'--','空-平'