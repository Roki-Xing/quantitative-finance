import backtrader as bt
import backtrader.indicators as btind

class TrendFollowingStrategy(bt.Strategy):
    params = (
        ('short_window', 20),
        ('long_window', 50),
        ('risk', 0.02),  # 2% risk per trade
        ('stop_loss', 0.05),  # 5% stop loss
        ('take_profit', 0.1)  # 10% take profit
    )

    def __init__(self):
        self.order = None
        self.entry_price = None
        self.dataclose = self.datas[0].close
        self.sma_short = btind.SMA(period=self.p.short_window)
        self.sma_long = btind.SMA(period=self.p.long_window)

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.dataclose > self.sma_long:
                size = int(self.broker.getvalue() * self.p.risk / self.dataclose)
                self.order = self.buy(size=size)
                self.entry_price = self.dataclose[0]
            elif self.dataclose < self.sma_short:
                size = int(self.broker.getvalue() * self.p.risk / self.dataclose)
                self.order = self.sell(size=size)
                self.entry_price = self.dataclose[0]
        else:
            # Exit logic for long positions
            if self.position.size > 0:
                if self.dataclose[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose > self.sma_long and self.dataclose < self.sma_short:
                    self.order = self.close()
                    self.entry_price = None
            # Exit logic for short positions
            elif self.position.size < 0:
                if self.dataclose[0] <= self.entry_price * (1 - self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose[0] >= self.entry_price * (1 + self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose < self.sma_long and self.dataclose > self.sma_short:
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
