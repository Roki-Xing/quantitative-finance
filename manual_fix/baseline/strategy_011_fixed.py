import backtrader as bt
import backtrader.indicators as btind

class PriceVolumeStrategy(bt.Strategy):
    params = (
        ('short_window', 20),
        ('long_window', 50),
        ('stop_loss', 0.05),
        ('take_profit', 0.05)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datavolume = self.datas[0].volume

        self.sma_short = btind.SMA(self.data.close, period=self.p.short_window)
        self.sma_long = btind.SMA(self.data.close, period=self.p.long_window)
        self.crossover = btind.CrossOver(self.sma_short, self.sma_long)
        self.volume_sma = btind.SMA(self.datavolume, period=self.p.short_window)

        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy on golden cross with volume confirmation
            if self.crossover > 0 and self.datavolume[0] > self.volume_sma[0]:
                self.order = self.buy()
                self.entry_price = self.dataclose[0]
            # Sell on death cross
            elif self.crossover < 0:
                self.order = self.sell()
                self.entry_price = self.dataclose[0]
        else:
            if self.position.size > 0:
                if self.dataclose[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
            elif self.position.size < 0:
                if self.dataclose[0] <= self.entry_price * (1 - self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose[0] >= self.entry_price * (1 + self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
