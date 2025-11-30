'''
Strategy #13 Adaptive Version
原版Strategy #13改进为自适应参数版本
'''
import backtrader as bt
from backtrader.indicators import SMA, RSI, ATR

class Strategy13Adaptive(bt.Strategy):
    '''
    Strategy #13的自适应参数版本
    
    原版问题：
    - 固定00止损 → 改为ATR动态止损
    - 固定20股 → 改为基于风险百分比的动态仓位
    
    改进：
    - 使用ATR衡量市场波动
    - 风险管理：每笔交易风险2%账户价值
    - 止损：3倍ATR
    '''
    params = (
        ('sma5_period', 5),
        ('sma10_period', 10),
        ('sma20_period', 20),
        ('rsi_period', 7),
        ('rsi_threshold', 35),
        ('atr_period', 14),
        ('atr_multiple', 3.0),     # 止损 = 入场价 - 3*ATR
        ('risk_factor', 0.02),     # 每笔交易风险2%账户价值
    )
    
    def __init__(self):
        # 技术指标（与原版相同）
        self.sma5 = SMA(self.data.close, period=self.params.sma5_period)
        self.sma10 = SMA(self.data.close, period=self.params.sma10_period)
        self.sma20 = SMA(self.data.close, period=self.params.sma20_period)
        self.rsi = RSI(self.data.close, period=self.params.rsi_period)
        
        # 新增：ATR用于动态止损和仓位计算
        self.atr = ATR(self.data, period=self.params.atr_period)
        
        self.order = None
        self.entry_price = None
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status == order.Completed:
            if order.isbuy():
                self.entry_price = order.executed.price
            elif order.issell():
                self.entry_price = None
        
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        # 获取ATR值，如果ATR无效则用2%价格作为后备
        atr_val = self.atr[0] if self.atr[0] > 0 else self.data.close[0] * 0.02
        
        # 有持仓时：动态ATR止损（替代固定00）
        if self.position:
            if self.entry_price:
                # 止损 = 入场价 - 3倍ATR
                trailing_stop = self.entry_price - atr_val * self.params.atr_multiple
                
                if self.data.close[0] < trailing_stop:
                    self.order = self.close()
                    self.entry_price = None
        
        # 无持仓时：入场逻辑（与原版相同）
        else:
            # SMA5上穿SMA10 且 RSI>35 且 SMA20>SMA10
            if (self.sma5[0] > self.sma10[0] and 
                self.sma5[-1] <= self.sma10[-1] and  # 交叉确认
                self.rsi[0] > self.params.rsi_threshold and 
                self.sma20[0] > self.sma10[0]):
                
                # 动态仓位计算（替代固定20股）
                # 风险 = 账户价值 * 2%
                risk_per_trade = self.broker.getvalue() * self.params.risk_factor
                
                # 仓位大小 = 风险金额 / (ATR * 止损倍数)
                # 这样确保无论股价高低，每笔交易的风险都是账户的2%
                position_size = int(risk_per_trade / (atr_val * self.params.atr_multiple))
                
                if position_size > 0:
                    self.order = self.buy(size=position_size)

# 兼容原框架的类名
Strat = Strategy13Adaptive
