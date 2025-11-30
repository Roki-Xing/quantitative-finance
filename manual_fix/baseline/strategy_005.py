import backtrader as bt
import backtrader.indicators as btind

class PriceVolumeStrategy(bt.Strategy):
    params = (
        ('pfast', 20),
        ('pslow', 50),
        ('maperiod', 15),
        ('printlog', False),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
        ('buy_volume', 0.1),
        ('sell_volume', 0.1)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataopen = self.datas[0].open
        self.datavolume = self.datas[0].volume

        self.smafast = btind.SMA(period=self.p.pfast)
        self.smalslow = btind.SMA(period=self.p.pslow)

        self.crossover = bt.ind.CrossOver(self.smafast, self.smalslow)
        self.volume = self.datavolume

    def next(self):
        if self.position.size == 0:
            if self.crossover > 0 and self.volume > self.p.buy_volume * self.datavolume[-1]:
                self.buy(size=100)
                self.broker.setcommission(commission=0.001)
            elif self.crossover < 0 and self.volume > self.p.sell_volume * self.datavolume[-1]:
            self.sell(size=100)
            self.broker.setcommission(commission=0.001)

        if self.position:
            if self.dataclose[-1] < self.dataclose[-2] * (1 - self.p.stop_loss):
                self.close()
            elif self.dataclose[-1] > self.dataclose[-2] * (1 + self.p.take_profit):
                self.close()

cerebro = bt.Cerebro()

cerebro.addstrategy(PriceVolumeStrategy)

cerebro.adddata(bt.feeds.BacktraderCSVData(dataname='data.csv'))

cerebro.broker.setcash(10000.0)
cerebro.addsizer(bt.sizers.FixedSize)
cerebro.broker.setcommission(commission=0.001)

cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())