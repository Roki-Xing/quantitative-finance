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
        self.dataclose = self.datas[0].close
        self.sma_short = btind.SMA(period=self.p.short_window)
        self.sma_long = btind.SMA(period=self.p.long_window)

    def next(self):
        if self.position:
            if self.dataclose > self.sma_long and self.dataclose < self.sma_short:
                self.close()
            elif self.dataclose < self.sma_long and self.dataclose > self.sma_short:
                self.close()

        if not self.position:
            if self.dataclose > self.sma_long:
                self.buy(size=self.broker.getvalue() * self.p.risk / self.dataclose)
            elif self.dataclose < self.sma_short:
                self.sell(size=self.broker.getvalue() * self.p.risk / self.dataclose)

        # Set stop-loss and take-profit
        if self.position:
            if self.position.size > 0:
                self.broker.set_stoploss(self.dataclose * (1 - self.p.stop_loss), size=self.position.size)
                self.broker.set_lagging_stop()
            elif self.position.size < 0:
                self.broker.set_stoploss(self.dataclose * (1 + self.p.stop_loss), size=abs(self.position.size))
                self.broker.set_lagging_stop()

            if self.position.size > 0 and self.dataclose > self.sma_long * (1 + self.p.take_profit):
                self.close()
            elif self.position.size < 0 and self.dataclose < self.sma_short * (1 - self.p.take_profit):
                self.close()