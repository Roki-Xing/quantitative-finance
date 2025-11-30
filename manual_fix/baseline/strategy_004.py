import backtrader as bt
import backtrader.indicators as btind

class VolatilityBreakoutStrategy(bt.Strategy):
    params = (
        ('atr_period', 14),  # period for ATR calculation
        ('atr_multiple', 2.0),  # multiple for stop-loss and take-profit
        ('stop_loss_pcnt', 0.05),  # percentage for stop-loss
        ('take_profit_pcnt', 0.05),  # percentage for take-profit
    )

    def __init__(self):
        self.order = None
        self.atr = btind.ATR(period=self.p.atr_period)
        self.higher_high = btind.HighestHigh(period=2)
        self.lower_low = btind.LowestLow(period=2)

    def next(self):
        if self.position.size == 0:
            if self.higher_high > self.lower_low and self.higher_high > self.data.high(0) * self.p.atr_multiple:
                self.buy(size=self.broker.cash * 0.9 / self.data.close)
                self.order = self.buy(size=self.broker.cash * 0.9 / self.data.close)
                self.set_stop_loss()
                self.set_take_profit()
            else:
            if self.higher_high < self.data.close * (1 - self.p.stop_loss_pcnt) or self.lower_low > self.data.close * (1 + self.p.take_profit_pcnt):
                self.close(size=self.position.size)

    def set_stop_loss(self):
        stop_price = self.data.close * (1 - self.p.stop_loss_pcnt)
        self.broker.set_stop_loss(self.order, price=stop_price)

    def set_take_profit(self):
        take_price = self.data.close * (1 + self.p.take_profit_pcnt)
        self.broker.set_take_profit(self.order, price=take_price)