import backtrader as bt
import backtrader.indicators as btind

class VolatilityBreakoutStrategy(bt.Strategy):
    params = (
        ('fast_ma_period', 14),
        ('slow_ma_period', 28),
        ('atr_period', 14),
        ('atr_multiplier', 2.0),
        ('stop_loss', 0.05),
        ('take_profit', 0.10)
    )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.fast_ma = btind.SMA(self.data.close, period=self.params.fast_ma_period)
        self.slow_ma = btind.SMA(self.data.close, period=self.params.slow_ma_period)
        self.atr = btind.ATR(self.data, period=self.params.atr_period)
        self.order = None
        self.entry_price = None

    def next(self):
        # Check pending orders
        if self.order:
            return

        # Entry logic - breakout strategy
        if not self.position:
            # Bullish breakout: close crosses above slow MA with high volatility
            if (self.data_close[0] > self.slow_ma[0] and
                self.data_close[-1] <= self.slow_ma[-1] and
                self.atr[0] > self.atr[-5]):  # Increasing volatility
                self.order = self.buy()
                self.entry_price = self.data_close[0]

            # Bearish breakout: close crosses below slow MA with high volatility
            elif (self.data_close[0] < self.slow_ma[0] and
                  self.data_close[-1] >= self.slow_ma[-1] and
                  self.atr[0] > self.atr[-5]):
                self.order = self.sell()
                self.entry_price = self.data_close[0]

        # Exit logic
        else:
            # Long position exit
            if self.position.size > 0:
                # Take profit
                if self.data_close[0] >= self.entry_price * (1 + self.params.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                # Stop loss
                elif self.data_close[0] <= self.entry_price * (1 - self.params.stop_loss):
                    self.order = self.close()
                    self.entry_price = None

            # Short position exit
            elif self.position.size < 0:
                # Take profit for short
                if self.data_close[0] <= self.entry_price * (1 - self.params.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                # Stop loss for short
                elif self.data_close[0] >= self.entry_price * (1 + self.params.stop_loss):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
