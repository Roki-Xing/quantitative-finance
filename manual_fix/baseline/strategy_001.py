import backtrader as bt
import backtrader.feeds as btfeeds

class TrendFollowingStrategy(bt.Strategy):
    params = (
        ('fast_ma_period', 20),
        ('slow_ma_period', 50),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(period=self.p.fast_ma_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(period=self.p.slow_ma_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if self.position.size == 0:
            if self.crossover > 0:
                self.buy(size=self.broker.cash * 0.1)
                self.sell(exectype=bt.Order.Stop, size=self.position.size, price=self.data.close * (1 - self.p.stop_loss), parent=self.position)
                self.sell(exectype=bt.Order.Limit, size=self.position.size, price=self.data.close * (1 + self.p.take_profit), parent=self.position)
            elif self.crossover < 0:
            self.close()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            if order.status == order.Completed:
                if order.isbuy():
                    self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (order.executed.price, order.executed.value, order.executed.comm))
                else:
                    self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (order.executed.price, order.executed.value, order.executed.comm))
            self.log('------------------')

cerebro = bt.Cerebro()

cerebro.addstrategy(TrendFollowingStrategy)

cerebro.addfeed(
    data = btfeeds.YahooFinanceData(
        dataname='AAPL',
        fromdate = bt.datetime(2020, 1, 1),
        todate = bt.datetime(2022, 12, 31)
    )
)

cerebro.run()
cerebro.plot()