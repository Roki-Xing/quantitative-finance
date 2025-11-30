import backtrader as bt
import backtrader.indicators as btind

class PriceVolumeStrategy(bt.Strategy):
    params = (
        ('pfast', 20),
        ('pslow', 50),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
        ('volume_factor', 1.5),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datavolume = self.datas[0].volume

        self.smafast = btind.SMA(self.data.close, period=self.p.pfast)
        self.smaslow = btind.SMA(self.data.close, period=self.p.pslow)
        self.crossover = btind.CrossOver(self.smafast, self.smaslow)
        self.volume_sma = btind.SMA(self.datavolume, period=self.p.pfast)

        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy on golden cross with high volume
            if self.crossover > 0 and self.datavolume[0] > self.volume_sma[0] * self.p.volume_factor:
                self.order = self.buy()
                self.entry_price = self.dataclose[0]
            # Sell on death cross with high volume
            elif self.crossover < 0 and self.datavolume[0] > self.volume_sma[0] * self.p.volume_factor:
                self.order = self.sell()
                self.entry_price = self.dataclose[0]
        else:
            # Long position exit
            if self.position.size > 0:
                if self.dataclose[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
            # Short position exit
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
