import backtrader as bt
import backtrader.indicators as btind

class MomentumStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('rsi_threshold', 30),
        ('macd_threshold', 0),
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.rsi = btind.RSI(self.data, period=self.p.rsi_period)
        self.macd = btind.MACD(self.data, period_me1=self.p.macd_fast, period_me2=self.p.macd_slow, period=self.p.macd_signal)
        self.signal = self.macd.macd - self.macd.signal

    def next(self):
        if self.position.size == 0:
            if self.rsi < self.p.rsi_threshold and self.signal > self.p.macd_threshold:
                self.buy()
                self.buyprice = self.dataclose[0]
                self.buycomm = 100
            else:
            if self.rsi > 70 and self.signal < -self.p.macd_threshold:
                self.close()
            elif self.dataclose[0] > self.buyprice * (1 + self.p.take_profit):
                self.close()
            elif self.dataclose[0] < self.buyprice * (1 - self.p.stop_loss):
                self.close()

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        print('Profit: %.2f' % trade.pnl)

cerebro = bt.Cerebro()

cerebro.addstrategy(MomentumStrategy)
cerebro.adddata(bt.feeds.PandasData(dataname='data.csv'))

cerebro.run()
cerebro.plot()