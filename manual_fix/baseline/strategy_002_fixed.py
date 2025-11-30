import backtrader as bt
import backtrader.indicators as btind

class MeanReversionBollingerStrategy(bt.Strategy):
    params = (
        ('bb_period', 20),
        ('bb_deviation', 2),
        ('stop_loss_percent', 0.05),
        ('take_profit_percent', 0.05),
    )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.bollinger = btind.BBands(self.data.close, period=self.p.bb_period, devfactor=self.p.bb_deviation)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy when price touches lower band (oversold)
            if self.data_close[0] < self.bollinger.lines.bot[0]:
                self.order = self.buy()
                self.entry_price = self.data_close[0]
            # Sell when price touches upper band (overbought)
            elif self.data_close[0] > self.bollinger.lines.top[0]:
                self.order = self.sell()
                self.entry_price = self.data_close[0]
        else:
            # Long position exit
            if self.position.size > 0:
                # Take profit
                if self.data_close[0] >= self.entry_price * (1 + self.p.take_profit_percent):
                    self.order = self.close()
                    self.entry_price = None
                # Stop loss
                elif self.data_close[0] <= self.entry_price * (1 - self.p.stop_loss_percent):
                    self.order = self.close()
                    self.entry_price = None
            # Short position exit
            elif self.position.size < 0:
                # Take profit for short
                if self.data_close[0] <= self.entry_price * (1 - self.p.take_profit_percent):
                    self.order = self.close()
                    self.entry_price = None
                # Stop loss for short
                elif self.data_close[0] >= self.entry_price * (1 + self.p.stop_loss_percent):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
