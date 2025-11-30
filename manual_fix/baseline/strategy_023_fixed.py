import backtrader as bt
import backtrader.indicators as btind

class PriceVolumeStrategy(bt.Strategy):
    params = (
        ('short_window', 20),
        ('long_window', 50),
        ('stop_loss_pct', 0.05),
        ('take_profit_pct', 0.10),
        ('risk_reward_ratio', 2.0),
    )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.data_volume = self.datas[0].volume
        self.sma_short = btind.SMA(period=self.p.short_window)
        self.sma_long = btind.SMA(period=self.p.long_window)
        self.rsi = btind.RSI(self.data_close, period=14)
        self.buy_signal = btind.CrossOver(self.sma_short, self.sma_long)
        self.sell_signal = btind.CrossOver(self.sma_long, self.sma_short)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.buy_signal > 0 and self.rsi < 30:
                if self.broker.getcash() > 1000:
                    size = int(self.broker.getcash() * 0.9 / self.data_close[0])
                    self.order = self.buy(size=size)
                    self.entry_price = self.data_close[0]
            elif self.sell_signal > 0 and self.rsi > 70:
                if self.broker.getcash() > 1000:
                    size = int(self.broker.getcash() * 0.9 / self.data_close[0])
                    self.order = self.sell(size=size)
                    self.entry_price = self.data_close[0]
        else:
            # Exit logic for long positions
            if self.position.size > 0:
                if self.data_close[0] >= self.entry_price * (1 + self.p.take_profit_pct):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data_close[0] <= self.entry_price * (1 - self.p.stop_loss_pct):
                    self.order = self.close()
                    self.entry_price = None
            # Exit logic for short positions
            elif self.position.size < 0:
                if self.data_close[0] <= self.entry_price * (1 - self.p.take_profit_pct):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data_close[0] >= self.entry_price * (1 + self.p.stop_loss_pct):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
