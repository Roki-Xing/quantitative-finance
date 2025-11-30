import backtrader as bt
import backtrader.indicators as btind

class MeanReversionBollingerBandsStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2),
        ('pfast', 10),
        ('pslow', 30),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.sma = btind.SMA(period=self.p.pfast)
        self.sma_slow = btind.SMA(period=self.p.pslow)
        self.bollinger = btind.BBands(period=self.p.period, devfactor=self.p.devfactor, plot=False)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy when price near lower band and SMA conditions met
            if self.bollinger.bot[0] < self.sma[0] and self.sma[0] > self.sma_slow[0]:
                self.order = self.buy()
                self.entry_price = self.data.close[0]
            # Sell when price near upper band and SMA conditions met
            elif self.bollinger.top[0] > self.sma[0] and self.sma[0] < self.sma_slow[0]:
                self.order = self.sell()
                self.entry_price = self.data.close[0]
        else:
            # Exit logic for long positions
            if self.position.size > 0:
                if self.data.close[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
            # Exit logic for short positions
            elif self.position.size < 0:
                if self.data.close[0] <= self.entry_price * (1 - self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] >= self.entry_price * (1 + self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
