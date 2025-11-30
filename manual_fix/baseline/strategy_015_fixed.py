import backtrader as bt

class MomentumStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('macd_period1', 12),
        ('macd_period2', 26),
        ('macd_period_signal', 9),
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.macd = bt.indicators.MACD(self.data.close,
                                        period_me1=self.p.macd_period1,
                                        period_me2=self.p.macd_period2,
                                        period_signal=self.p.macd_period_signal)
        self.order = None
        self.entry_price = None

    def next(self):
        # Check pending orders
        if self.order:
            return

        # Entry logic
        if not self.position:
            # Buy signal: RSI oversold + MACD bearish (contrarian)
            if self.rsi < 30 and self.macd.macd < self.macd.signal:
                self.order = self.buy()
                self.entry_price = self.data.close[0]
        else:
            # Exit logic for long positions
            if self.position.size > 0:
                # Take profit
                if self.data.close[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.sell()
                    self.entry_price = None
                # Stop loss
                elif self.data.close[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.sell()
                    self.entry_price = None
                # Exit on RSI overbought
                elif self.rsi > 70:
                    self.order = self.sell()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
