import backtrader as bt
import backtrader.indicators as btind

class Strategy013Original(bt.Strategy):
    """
    Original Strategy #13 with FIXED parameters
    - Fixed 00 stop loss
    - Fixed 20 shares position
    - No market adaptation
    """
    params = (
        ('sma_fast', 5),
        ('sma_medium', 10),
        ('sma_slow', 20),
        ('rsi_period', 7),
        ('rsi_threshold', 35),
        ('stop_loss_amount', 200),  # Fixed 00 (or ¥200 for A-shares)
        ('position_size', 20),       # Fixed 20 shares
    )
    
    def __init__(self):
        # SMA indicators
        self.sma_5 = btind.SMA(self.data.close, period=self.params.sma_fast)
        self.sma_10 = btind.SMA(self.data.close, period=self.params.sma_medium)
        self.sma_20 = btind.SMA(self.data.close, period=self.params.sma_slow)
        
        # RSI indicator
        self.rsi = btind.RSI(self.data.close, period=self.params.rsi_period)
        
        # Track entry
        self.entry_price = None
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        # Check stop loss first (fixed 00 loss)
        if self.position:
            current_pl = (self.data.close[0] - self.entry_price) * self.position.size
            if current_pl < -self.params.stop_loss_amount:
                self.order = self.close()
                self.entry_price = None
                return
        
        # Entry logic: SMA crossover + RSI + trend filter
        if not self.position:
            # Crossover: SMA5 crosses above SMA10
            sma5_cross_sma10 = (self.sma_5[0] > self.sma_10[0] and 
                               self.sma_5[-1] <= self.sma_10[-1])
            
            # RSI filter: RSI > 35
            rsi_filter = self.rsi[0] > self.params.rsi_threshold
            
            # Trend filter: SMA20 > SMA10
            trend_filter = self.sma_20[0] > self.sma_10[0]
            
            if sma5_cross_sma10 and rsi_filter and trend_filter:
                # Fixed 20 shares (no risk management)
                self.order = self.buy(size=self.params.position_size)
                self.entry_price = self.data.close[0]
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
