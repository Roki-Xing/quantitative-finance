import backtrader as bt
import backtrader.indicators as btind

class ComprehensiveStrategy(bt.Strategy):
    params = (
        ('fast_ma_period', 20),
        ('slow_ma_period', 50),
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('stop_loss_percent', 0.05),
        ('take_profit_percent', 0.05),
    )

    def __init__(self):
        self.fast_ma = btind.SMA(period=self.p.fast_ma_period)
        self.slow_ma = btind.SMA(period=self.p.slow_ma_period)
        self.rsi = btind.RSI(period=self.p.rsi_period)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.fast_ma > self.slow_ma and self.rsi < self.p.rsi_lower:
                self.order = self.buy()
                self.entry_price = self.data.close[0]
            elif self.fast_ma < self.slow_ma and self.rsi > self.p.rsi_upper:
                self.order = self.sell()
                self.entry_price = self.data.close[0]
        else:
            # Exit logic for long positions
            if self.position.size > 0:
                stop_loss_price = self.entry_price * (1 - self.p.stop_loss_percent)
                take_profit_price = self.entry_price * (1 + self.p.take_profit_percent)
                if self.data.close[0] <= stop_loss_price:
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] >= take_profit_price:
                    self.order = self.close()
                    self.entry_price = None
            # Exit logic for short positions
            elif self.position.size < 0:
                stop_loss_price = self.entry_price * (1 + self.p.stop_loss_percent)
                take_profit_price = self.entry_price * (1 - self.p.take_profit_percent)
                if self.data.close[0] >= stop_loss_price:
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] <= take_profit_price:
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
