from scipy.stats.stats import pearsonr

start = '2018-01-01'
end  = '2019-01-01'
benchmark = 'HS300'
universe = ['', '']
capital_base = 1000000

def initialize(account):
    account.cutoff = 0.9
    account.prev_prc1 = 0
    account.prev_prc2 = 0
    account.prev_prcb = 0

def handle_data(account):
    if len(account.universe) < 2: return
    
    clsp = account.get_attribute_history('closePrice', 5)
    stk1, stk2 = universe
    px1, px2 = clsp[stk1], clsp[stk2]
       
    prc1, prc2 = px1[-1], px2[-1]
    prcb = account.get_symbol_history('benchmark', 1)['return'][0]
    
    if account.prev_prc1 == 0:
        account.prev_prc1 = prc1
        account.prev_prc2 = prc2
        account.prev_prcb = prcb
        return

    corval, pval = pearsonr(px1, px2)
    
    if abs(corval) < account.cutoff:
        return
    
    mov1, mov2 = adj(prc1, prc2, prcb, account.prev_prc1, account.prev_prc2, account.prev_prcb)

    amount = 100000 / prc2    
    if mov1 > 0:
        order(stk2, amount)
    elif mov1 < 0:
        if account.valid_secpos.get(stk2, 0) > amount:
            order(stk2, -amount)
        else:
            order_to(stk2, 0)
            
    amount = 100000 / prc1
    if mov2 > 0:
        order(stk1, amount)
    elif mov2 < 0:
        if account.valid_secpos.get(stk1, 0) > amount:
            order(stk1, -amount)
        else:
            order_to(stk1, 0)
    
    account.prev_prc1 = prc1
    account.prev_prc2 = prc2
    account.prev_prcb = prcb

def adj(x, y, base, prev_x, prev_y, prev_base):
    dhs = base / prev_base - 1
    dx = x / prev_x - 1 - dhs
    dy = y / prev_y - 1 - dhs
    return dx, dy