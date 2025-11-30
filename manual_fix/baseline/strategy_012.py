import backtrader as bt
import backtrader.indicators as btind

class MultiFactorComprehensiveStrategy(bt.Strategy):
    params = (
        ('maperiod1', 20),
        ('maperiod2', 50),
        ('maperiod3', 100),
        ('stop_loss', 0.05),
        ('take_profit', 0.1),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.sma1 = btind.SMA(period=self.p.maperiod1)
        self.sma2 = btind.SMA(period=self.p.maperiod2)
        self.sma3 = btind.SMA(period=self.p.maperiod3)
        self.rsi = btind.RSI(self.datas[0], period=14)
        self.bollinger = btind.BBands(self.datas[0], period=self.p.maperiod1, devfactor=2)
        self.signal = btind.CrossOver(self.sma1, self.sma2)
        self.signal2 = btind.CrossOver(self.sma2, self.sma3)
        self.signal3 = btind.CrossOver(self.rsi, 30)
        self.signal4 = btind.CrossOver(self.bollinger.lines.boll, self.bollinger.lines.mid)

    def next(self):
        if self.dataclose[0] > self.sma1[0] and self.dataclose[0] > self.sma2[0] and self.dataclose[0] > self.sma3[0] and self.rsi[0] < 30 and self.bollinger.lines.boll[0] > self.bollinger.lines.mid[0]:
            if self.position.size == 0:
                self.buy(size=100)
                self.buyprice = self.dataclose[0]
                self.buycomm = self.broker.comm
            elif self.dataclose[0] < self.sma1[0] and self.dataclose[0] < self.sma2[0] and self.dataclose[0] < self.sma3[0] and self.rsi[0] > 70 and self.bollinger.lines.boll[0] < self.bollinger.lines.mid[0]:
            if self.position.size == 0:
                self.sell(size=100)
                self.sellprice = self.dataclose[0]
                self.sellcomm = self.broker.comm

        if self.position.size > 0:
            if self.dataclose[0] < self.buyprice * (1 - self.p.stop_loss):
                self.close(size=100)
            elif self.dataclose[0] > self.buyprice * (1 + self.p.take_profit):
                self.close(size=100)
            elif self.position.size < 0:
            if self.dataclose[0] > self.sellprice * (1 - self.p.stop_loss):
                self.close(size=100)
            elif self.dataclose[0] < self.sellprice * (1 + self.p.take_profit):
                self.close(size=100)