import backtrader as bt
import backtrader.indicators as btind

class VolatilityBreakoutStrategy(bt.Strategy):
    params = (
        ('pfast', 14),
        ('pslow', 28),
        ('maperiod', 20),
        ('atrratio', 3),
        ('pstop', 0.05),
        ('ptarget', 0.05)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.order = None
        self.entry_price = None
        self.aatr = btind.ATR(self.data, period=self.p.maperiod)
        self.smafast = btind.SMA(self.data, period=self.p.pfast)
        self.smaslow = btind.SMA(self.data, period=self.p.pslow)
        self.bollinger = btind.BBands(self.data, period=self.p.maperiod, devfactor=self.p.atrratio)

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy signal: price breaks above Bollinger upper band with SMA confirmation
            if self.dataclose[0] > self.bollinger.lines.top[0] and self.dataclose[0] > self.smafast[0]:
                self.order = self.buy()
                self.entry_price = self.dataclose[0]
            # Sell signal: price breaks below Bollinger lower band with SMA confirmation
            elif self.dataclose[0] < self.bollinger.lines.bot[0] and self.dataclose[0] < self.smafast[0]:
                self.order = self.sell()
                self.entry_price = self.dataclose[0]
        else:
            # Exit logic for long positions
            if self.position.size > 0:
                if self.dataclose[0] >= self.entry_price * (1 + self.p.ptarget):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose[0] <= self.entry_price * (1 - self.p.pstop):
                    self.order = self.close()
                    self.entry_price = None
            # Exit logic for short positions
            elif self.position.size < 0:
                if self.dataclose[0] <= self.entry_price * (1 - self.p.ptarget):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose[0] >= self.entry_price * (1 + self.p.pstop):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
