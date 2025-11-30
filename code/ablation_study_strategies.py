"""
Ablation Study - 4 Strategy Variants
=====================================

Purpose: Prove synergistic effect of adaptive components
Author: Claude Code AI Assistant
Date: 2025-11-27
Python: 3.8+

Strategy Variants:
1. Baseline_Fixed: $200 stop + 20 shares (original)
2. ATR_Only: ATR×3 stop + 20 shares
3. Risk2Pct_Only: $200 stop + 2% risk position
4. Full_Adaptive: ATR×3 stop + 2% risk position

Expected Result:
- Baseline: ~2.4%
- ATR Only: ~5-6% (stop improvement)
- Risk2Pct Only: ~7-9% (position improvement)
- Full Adaptive: ~10.4% (synergistic effect > additive)
"""

import backtrader as bt
import pandas as pd
import numpy as np


# =============================================================================
# Strategy 1: Baseline (Fixed Parameters)
# =============================================================================

class Strategy_Baseline_Fixed(bt.Strategy):
    """
    Original Strategy #13 with fixed parameters
    - Fixed $200 stop-loss
    - Fixed 20 shares position
    """
    params = (
        ('sma_fast', 5),
        ('sma_mid', 10),
        ('sma_slow', 20),
        ('rsi_period', 7),
        ('rsi_threshold', 50),
        ('stop_loss_amount', 200),  # Fixed $200
        ('position_size', 20),       # Fixed 20 shares
    )

    def __init__(self):
        # Simple Dual MA + RSI
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.p.sma_fast)
        self.sma_mid = bt.indicators.SMA(self.data.close, period=self.p.sma_mid)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.p.sma_slow)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)

        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy signal: Fast SMA crosses above Slow SMA + RSI > threshold
            if self.crossover > 0 and self.rsi[0] > self.p.rsi_threshold:
                self.order = self.buy(size=self.p.position_size)
                self.entry_price = self.data.close[0]
        else:
            # Fixed dollar stop-loss
            current_loss = (self.data.close[0] - self.entry_price) * self.position.size
            if current_loss < -self.p.stop_loss_amount:
                self.order = self.close()

            # Exit on bearish crossover
            if self.crossover < 0:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
            if order.isbuy():
                self.entry_price = order.executed.price


# =============================================================================
# Strategy 2: ATR Only (Adaptive Stop-Loss Only)
# =============================================================================

class Strategy_ATR_Only(bt.Strategy):
    """
    ATR adaptive stop-loss + Fixed position size
    - ATR × 3 dynamic stop-loss
    - Fixed 20 shares position
    """
    params = (
        ('sma_fast', 5),
        ('sma_mid', 10),
        ('sma_slow', 20),
        ('rsi_period', 7),
        ('rsi_threshold', 50),
        ('atr_period', 14),
        ('atr_multiplier', 3.0),    # ATR adaptive stop
        ('position_size', 20),       # Fixed 20 shares
    )

    def __init__(self):
        # Simple Dual MA + RSI
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.p.sma_fast)
        self.sma_mid = bt.indicators.SMA(self.data.close, period=self.p.sma_mid)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.p.sma_slow)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)

        # ATR for adaptive stop-loss
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)

        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy signal: Fast SMA crosses above Slow SMA + RSI > threshold
            if self.crossover > 0 and self.rsi[0] > self.p.rsi_threshold:
                self.order = self.buy(size=self.p.position_size)
                self.entry_price = self.data.close[0]
        else:
            # ATR adaptive stop-loss
            atr_stop_distance = self.atr[0] * self.p.atr_multiplier
            dynamic_stop_loss = atr_stop_distance * self.position.size
            current_loss = (self.data.close[0] - self.entry_price) * self.position.size

            if current_loss < -dynamic_stop_loss:
                self.order = self.close()

            # Exit on bearish crossover
            if self.crossover < 0:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
            if order.isbuy():
                self.entry_price = order.executed.price


# =============================================================================
# Strategy 3: Risk2Pct Only (Adaptive Position Sizing Only)
# =============================================================================

class Strategy_Risk2Pct_Only(bt.Strategy):
    """
    Fixed stop-loss + 2% risk position sizing
    - Fixed $200 stop-loss
    - 2% risk management position sizing
    """
    params = (
        ('sma_fast', 5),
        ('sma_mid', 10),
        ('sma_slow', 20),
        ('rsi_period', 7),
        ('rsi_threshold', 50),
        ('stop_loss_amount', 200),   # Fixed $200
        ('risk_percent', 0.02),      # 2% risk management
    )

    def __init__(self):
        # Simple Dual MA + RSI
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.p.sma_fast)
        self.sma_mid = bt.indicators.SMA(self.data.close, period=self.p.sma_mid)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.p.sma_slow)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)

        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy signal
            if self.crossover > 0 and self.rsi[0] > self.p.rsi_threshold:
                # 2% risk position sizing
                account_value = self.broker.getvalue()
                risk_amount = account_value * self.p.risk_percent

                # Position = risk amount / stop loss per share
                price = self.data.close[0]
                stop_loss_per_share = min(self.p.stop_loss_amount / 20, price * 0.1)  # Cap at 10%

                position_size = int(risk_amount / stop_loss_per_share)
                position_size = max(1, min(position_size, 100))  # Limit: 1-100 shares

                self.order = self.buy(size=position_size)
                self.entry_price = self.data.close[0]
        else:
            # Fixed dollar stop-loss
            current_loss = (self.data.close[0] - self.entry_price) * self.position.size
            if current_loss < -self.p.stop_loss_amount:
                self.order = self.close()

            # Exit on bearish crossover
            if self.crossover < 0:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
            if order.isbuy():
                self.entry_price = order.executed.price


# =============================================================================
# Strategy 4: Full Adaptive (Both Components)
# =============================================================================

class Strategy_Full_Adaptive(bt.Strategy):
    """
    ATR adaptive stop-loss + 2% risk position sizing
    - ATR × 3 dynamic stop-loss
    - 2% risk management position sizing
    - Expected synergistic effect
    """
    params = (
        ('sma_fast', 5),
        ('sma_mid', 10),
        ('sma_slow', 20),
        ('rsi_period', 7),
        ('rsi_threshold', 50),
        ('atr_period', 14),
        ('atr_multiplier', 3.0),    # ATR adaptive stop
        ('risk_percent', 0.02),      # 2% risk management
    )

    def __init__(self):
        # Simple Dual MA + RSI
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.p.sma_fast)
        self.sma_mid = bt.indicators.SMA(self.data.close, period=self.p.sma_mid)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.p.sma_slow)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)

        # ATR for adaptive stop-loss
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)

        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy signal
            if self.crossover > 0 and self.rsi[0] > self.p.rsi_threshold:
                # 2% risk position sizing with ATR-based stop distance
                account_value = self.broker.getvalue()
                risk_amount = account_value * self.p.risk_percent

                # ATR adaptive stop distance
                atr_stop_distance = self.atr[0] * self.p.atr_multiplier

                # Position = risk amount / stop distance
                position_size = int(risk_amount / atr_stop_distance)
                position_size = max(1, min(position_size, 100))  # Limit: 1-100 shares

                self.order = self.buy(size=position_size)
                self.entry_price = self.data.close[0]
        else:
            # ATR adaptive stop-loss
            atr_stop_distance = self.atr[0] * self.p.atr_multiplier
            dynamic_stop_loss = atr_stop_distance * self.position.size
            current_loss = (self.data.close[0] - self.entry_price) * self.position.size

            if current_loss < -dynamic_stop_loss:
                self.order = self.close()

            # Exit on bearish crossover
            if self.crossover < 0:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
            if order.isbuy():
                self.entry_price = order.executed.price


# =============================================================================
# Helper Functions
# =============================================================================

def get_strategy_by_name(strategy_name):
    """Return strategy class by name"""
    strategies = {
        'Baseline_Fixed': Strategy_Baseline_Fixed,
        'ATR_Only': Strategy_ATR_Only,
        'Risk2Pct_Only': Strategy_Risk2Pct_Only,
        'Full_Adaptive': Strategy_Full_Adaptive
    }
    return strategies.get(strategy_name)


if __name__ == '__main__':
    print("=" * 80)
    print("Ablation Study - 4 Strategy Variants")
    print("=" * 80)
    print("\nAvailable Strategies:")
    print("  1. Baseline_Fixed:  $200 stop + 20 shares")
    print("  2. ATR_Only:        ATR×3 stop + 20 shares")
    print("  3. Risk2Pct_Only:   $200 stop + 2% risk position")
    print("  4. Full_Adaptive:   ATR×3 stop + 2% risk position")
    print("\nPurpose: Prove synergistic effect")
    print("Expected: Full_Adaptive > (ATR_Only + Risk2Pct_Only - Baseline)")
    print("=" * 80)
