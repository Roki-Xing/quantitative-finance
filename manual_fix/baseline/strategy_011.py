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
        self.dataclose = self.datas[0]
        self.datahigh = self.datas[1]
        self.datalow = self.datas[2]
        self.datavolume = self.datas[3]
        
        self.sma_short = btind.SMA(period=self.p.short_window)
        self.sma_long = btind.SMA(period=self.p.long_window)
        
        self.crossover = btind.CrossOver(self.sma_short, self.sma_long)
        self.short_signal = btind.CrossOver(self.sma_short, self.sma_long, relation=-1)

    def next(self):
        if self.position.size == 0:
            if self.crossover > 0 and self.dataclose[0] > self.sma_long[0] and self.datavolume[0] > self.datavolume[-1]:
                self.buy()
                self.buyprice = self.dataclose[0]
                self.stop_loss_price = self.buyprice * (1 - self.p.stop_loss)
                self.take_profit_price = self.buyprice * (1 + self.p.take_profit)
            elif self.position.size > 0:
            if self.short_signal < 0:
                self.close()
            elif self.dataclose[0] < self.stop_loss_price:
                self.close()
            elif self.dataclose[0] >= self.take_profit_price:
                self.close()
                self.buy()
                self.buyprice = self.dataclose[0]
                self.stop_loss_price = self.buyprice * (1 - self.p.stop_loss)
                self.take_profit_price = self.buyprice * (1 + self.p.take_profit)