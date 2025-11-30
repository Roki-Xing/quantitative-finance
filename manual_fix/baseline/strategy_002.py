import backtrader as bt
import backtrader.indicators as btind

class MeanReversionBollingerStrategy(bt.Strategy):
    params = (
        ('bb_period', 20),
        ('bb_stddev', 2),
        ('bb_deviation', 2),
        ('stop_loss_percent', 0.05),
        ('take_profit_percent', 0.05),
    )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.bollinger = btind.BBands(self.data, period=self.p.bb_period, devfactor=self.p.bb_deviation)

    def next(self):
        if not self.position:
            if self.data_close < self.bollinger.lines.bot:
                if self.data_close > self.bollinger.lines.bot * (1 - self.p.stop_loss_percent):
                    self.buy()
                elif self.data_close > self.bollinger.lines.top:
                if self.data_close < self.bollinger.lines.top * (1 + self.p.stop_loss_percent):
                    self.sell()
                else:
            if self.data_close > self.bollinger.lines.top * (1 + self.p.take_profit_percent):
                self.sell()
            elif self.data_close < self.bollinger.lines.bot * (1 - self.p.stop_loss_percent):
                self.close()

cerebro = bt.Cerebro()

cerebro.addstrategy(MeanReversionBollingerStrategy)

cerebro.addstrategy(MeanReversionBollingerStrategy, bb_period=20, bb_stddev=2, bb_deviation=2, stop_loss_percent=0.05, take_profit_percent=0.05)

cerebro.adddata(bt.feeds.PandasData(dataname='your_data.csv', fromdate=datetime(2020, 1, 1), todate=datetime(2020, 12, 31)))

cerebro.run()

cerebro.plot()