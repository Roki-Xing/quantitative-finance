import backtrader as bt
import backtrader.indicators as btind

class MomentumStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('rsi_threshold', 30),
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.rsi = btind.RSI(self.data, period=self.p.rsi_period)
        self.macd = btind.MACD(self.data, period_me1=self.p.macd_fast,
                               period_me2=self.p.macd_slow, period_signal=self.p.macd_signal)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy on RSI oversold or MACD bullish crossover
            if self.rsi < self.p.rsi_threshold and self.dataclose > self.dataclose[-1]:
                self.order = self.buy()
                self.entry_price = self.dataclose[0]
            elif self.macd.macd > self.macd.signal and self.macd.macd > 0:
                self.order = self.buy()
                self.entry_price = self.dataclose[0]
        else:
            if self.position.size > 0:
                # Take profit
                if self.dataclose[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                # Stop loss
                elif self.dataclose[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
                # Exit on RSI overbought
                elif self.rsi > 70:
                    self.order = self.close()
                    self.entry_price = None
                # Exit on MACD bearish crossover
                elif self.macd.macd < self.macd.signal:
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
