#!/usr/bin/env python3
"""
Baseline Strategy for Backtest Validation
A simple, working strategy to validate the backtest framework
"""

import backtrader as bt
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class BaselineSMAStrategy(bt.Strategy):
    """Simple Moving Average Crossover - Baseline"""

    params = (
        ('fast_period', 20),
        ('slow_period', 50),
        ('stop_loss', 0.05),
        ('take_profit', 0.15),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None
        self.entry_price = 0.0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Completed:
            if order.isbuy():
                self.entry_price = order.executed.price
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0 and self.data.close[0] > self.fast_ma[0]:
                size = int(self.broker.get_cash() / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
        else:
            current = self.data.close[0]
            if current <= self.entry_price * (1 - self.params.stop_loss):
                self.order = self.sell(size=self.position.size)
            elif current >= self.entry_price * (1 + self.params.take_profit):
                self.order = self.sell(size=self.position.size)
            elif self.crossover < 0:
                self.order = self.sell(size=self.position.size)
