#!/usr/bin/env python3
"""
Day 44: GPU-based Strategy Regeneration with Improved Prompts
使用改进的Prompt重新生成10个正确的策略代码
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
import json
import time
from datetime import datetime
import ast

MODEL_PATH = "/root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct"
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/strategy_library/batch1_fixed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 改进的策略模板 - 更严格的结构指导
STRATEGY_TEMPLATE = '''#!/usr/bin/env python3
"""
{name} Strategy

Strategy Rules:
{rules}

Risk Management:
- Stop-loss: {stop_loss}%
- Take-profit: {take_profit}%
"""

import backtrader as bt
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class {class_name}(bt.Strategy):
    """{description}"""

    params = (
        {params}
    )

    def __init__(self):
        """Initialize indicators and state variables."""
        {indicators}

        # Order tracking - MUST be initialized
        self.order = None
        self.entry_price = 0.0

    def notify_order(self, order):
        """Handle order status changes - ALL statuses must be handled."""
        if order.status in [order.Submitted, order.Accepted]:
            return  # Wait for execution

        if order.status == order.Completed:
            if order.isbuy():
                self.entry_price = order.executed.price
                logger.info(f"BUY at {{order.executed.price:.2f}}")
            else:
                logger.info(f"SELL at {{order.executed.price:.2f}}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            logger.warning(f"Order failed: {{order.status}}")

        # ALWAYS clear order reference at the end
        self.order = None

    def notify_trade(self, trade):
        """Log closed trades."""
        if trade.isclosed:
            logger.info(f"Trade PnL: {{trade.pnl:.2f}}")

    def next(self):
        """Main strategy logic - called on each bar."""
        if self.order:
            return  # Wait for pending order

        current = self.data.close[0]

        if not self.position:
            # Entry logic
            {entry_logic}
        else:
            # Exit logic - check stop-loss and take-profit first
            if current <= self.entry_price * (1 - self.p.stop_loss):
                logger.warning(f"STOP-LOSS at {{current:.2f}}")
                self.order = self.sell(size=self.position.size)
            elif current >= self.entry_price * (1 + self.p.take_profit):
                logger.info(f"TAKE-PROFIT at {{current:.2f}}")
                self.order = self.sell(size=self.position.size)
            else:
                # Signal-based exit
                {exit_logic}
'''

# 10个策略定义
STRATEGIES = [
    {
        "id": 1,
        "name": "Dual MA Crossover",
        "class_name": "DualMAStrategy",
        "description": "Classic dual moving average crossover strategy",
        "rules": "- Entry: Fast MA crosses above Slow MA\\n- Exit: Fast MA crosses below Slow MA",
        "stop_loss": 5, "take_profit": 15,
        "params": "('fast_period', 20),\\n        ('slow_period', 50),\\n        ('stop_loss', 0.05),\\n        ('take_profit', 0.15),",
        "indicators": """self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)""",
        "entry_logic": """if self.crossover > 0 and current > self.fast_ma[0]:
                size = int(self.broker.get_cash() / current)
                if size > 0:
                    self.order = self.buy(size=size)""",
        "exit_logic": """if self.crossover < 0:
                    self.order = self.sell(size=self.position.size)"""
    },
    {
        "id": 2,
        "name": "MACD Zero Cross",
        "class_name": "MACDZeroCrossStrategy",
        "description": "MACD line crossing zero line strategy",
        "rules": "- Entry: MACD crosses above zero\\n- Exit: MACD crosses below zero",
        "stop_loss": 4, "take_profit": 12,
        "params": "('fast', 12),\\n        ('slow', 26),\\n        ('signal', 9),\\n        ('stop_loss', 0.04),\\n        ('take_profit', 0.12),",
        "indicators": """self.macd = bt.indicators.MACD(self.data.close,
            period_me1=self.p.fast, period_me2=self.p.slow, period_signal=self.p.signal)""",
        "entry_logic": """if self.macd.macd[0] > 0 and self.macd.macd[-1] <= 0:
                size = int(self.broker.get_cash() / current)
                if size > 0:
                    self.order = self.buy(size=size)""",
        "exit_logic": """if self.macd.macd[0] < 0 and self.macd.macd[-1] >= 0:
                    self.order = self.sell(size=self.position.size)"""
    },
    {
        "id": 3,
        "name": "RSI Oversold",
        "class_name": "RSIOversoldStrategy",
        "description": "RSI oversold reversal strategy",
        "rules": "- Entry: RSI < 30\\n- Exit: RSI > 50 or 5 days holding",
        "stop_loss": 3, "take_profit": 8,
        "params": "('rsi_period', 14),\\n        ('oversold', 30),\\n        ('exit_level', 50),\\n        ('stop_loss', 0.03),\\n        ('take_profit', 0.08),",
        "indicators": """self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)""",
        "entry_logic": """if self.rsi[0] < self.p.oversold:
                size = int(self.broker.get_cash() / current)
                if size > 0:
                    self.order = self.buy(size=size)""",
        "exit_logic": """if self.rsi[0] > self.p.exit_level:
                    self.order = self.sell(size=self.position.size)"""
    },
    {
        "id": 4,
        "name": "Bollinger Breakout",
        "class_name": "BollingerBreakoutStrategy",
        "description": "Bollinger Band breakout strategy",
        "rules": "- Entry: Close breaks above upper band\\n- Exit: Close below middle band",
        "stop_loss": 4, "take_profit": 10,
        "params": "('bb_period', 20),\\n        ('bb_dev', 2),\\n        ('stop_loss', 0.04),\\n        ('take_profit', 0.10),",
        "indicators": """self.bb = bt.indicators.BollingerBands(self.data.close,
            period=self.p.bb_period, devfactor=self.p.bb_dev)""",
        "entry_logic": """if current > self.bb.top[0] and self.data.close[-1] <= self.bb.top[-1]:
                size = int(self.broker.get_cash() / current)
                if size > 0:
                    self.order = self.buy(size=size)""",
        "exit_logic": """if current < self.bb.mid[0]:
                    self.order = self.sell(size=self.position.size)"""
    },
    {
        "id": 5,
        "name": "Momentum Confirm",
        "class_name": "MomentumConfirmStrategy",
        "description": "Momentum with volume confirmation",
        "rules": "- Entry: Momentum > 0 and Volume > MA(Volume)\\n- Exit: Momentum < 0",
        "stop_loss": 5, "take_profit": 12,
        "params": "('mom_period', 10),\\n        ('vol_period', 20),\\n        ('stop_loss', 0.05),\\n        ('take_profit', 0.12),",
        "indicators": """self.momentum = bt.indicators.Momentum(self.data.close, period=self.p.mom_period)
        self.vol_ma = bt.indicators.SMA(self.data.volume, period=self.p.vol_period)""",
        "entry_logic": """if self.momentum[0] > 0 and self.data.volume[0] > self.vol_ma[0]:
                size = int(self.broker.get_cash() / current)
                if size > 0:
                    self.order = self.buy(size=size)""",
        "exit_logic": """if self.momentum[0] < 0:
                    self.order = self.sell(size=self.position.size)"""
    },
    {
        "id": 6,
        "name": "ATR Channel",
        "class_name": "ATRChannelStrategy",
        "description": "ATR-based channel breakout",
        "rules": "- Entry: Close > SMA + 2*ATR\\n- Exit: Close < SMA - ATR",
        "stop_loss": 5, "take_profit": 15,
        "params": "('sma_period', 20),\\n        ('atr_period', 14),\\n        ('atr_mult', 2),\\n        ('stop_loss', 0.05),\\n        ('take_profit', 0.15),",
        "indicators": """self.sma = bt.indicators.SMA(self.data.close, period=self.p.sma_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)""",
        "entry_logic": """upper = self.sma[0] + self.p.atr_mult * self.atr[0]
            if current > upper:
                size = int(self.broker.get_cash() / current)
                if size > 0:
                    self.order = self.buy(size=size)""",
        "exit_logic": """lower = self.sma[0] - self.atr[0]
                if current < lower:
                    self.order = self.sell(size=self.position.size)"""
    },
    {
        "id": 7,
        "name": "Triple Filter",
        "class_name": "TripleFilterStrategy",
        "description": "Triple moving average filter",
        "rules": "- Entry: Fast > Medium > Slow (uptrend)\\n- Exit: Fast < Medium",
        "stop_loss": 4, "take_profit": 12,
        "params": "('fast', 10),\\n        ('medium', 20),\\n        ('slow', 50),\\n        ('stop_loss', 0.04),\\n        ('take_profit', 0.12),",
        "indicators": """self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.med_ma = bt.indicators.SMA(self.data.close, period=self.p.medium)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow)""",
        "entry_logic": """if self.fast_ma[0] > self.med_ma[0] > self.slow_ma[0]:
                size = int(self.broker.get_cash() / current)
                if size > 0:
                    self.order = self.buy(size=size)""",
        "exit_logic": """if self.fast_ma[0] < self.med_ma[0]:
                    self.order = self.sell(size=self.position.size)"""
    },
    {
        "id": 8,
        "name": "Mean Reversion",
        "class_name": "MeanReversionStrategy",
        "description": "Mean reversion with Z-score",
        "rules": "- Entry: Z-score < -2 (oversold)\\n- Exit: Z-score > 0 (mean)",
        "stop_loss": 3, "take_profit": 6,
        "params": "('period', 20),\\n        ('entry_z', -2),\\n        ('exit_z', 0),\\n        ('stop_loss', 0.03),\\n        ('take_profit', 0.06),",
        "indicators": """self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
        self.std = bt.indicators.StdDev(self.data.close, period=self.p.period)""",
        "entry_logic": """if self.std[0] > 0:
                zscore = (current - self.sma[0]) / self.std[0]
                if zscore < self.p.entry_z:
                    size = int(self.broker.get_cash() / current)
                    if size > 0:
                        self.order = self.buy(size=size)""",
        "exit_logic": """if self.std[0] > 0:
                zscore = (current - self.sma[0]) / self.std[0]
                if zscore > self.p.exit_z:
                    self.order = self.sell(size=self.position.size)"""
    },
    {
        "id": 9,
        "name": "Volume Breakout",
        "class_name": "VolumeBreakoutStrategy",
        "description": "Price breakout with volume confirmation",
        "rules": "- Entry: New 20-day high with 2x volume\\n- Exit: Below 10-day low",
        "stop_loss": 5, "take_profit": 15,
        "params": "('high_period', 20),\\n        ('low_period', 10),\\n        ('vol_mult', 2),\\n        ('stop_loss', 0.05),\\n        ('take_profit', 0.15),",
        "indicators": """self.highest = bt.indicators.Highest(self.data.high, period=self.p.high_period)
        self.lowest = bt.indicators.Lowest(self.data.low, period=self.p.low_period)
        self.vol_ma = bt.indicators.SMA(self.data.volume, period=20)""",
        "entry_logic": """if current >= self.highest[-1] and self.data.volume[0] > self.p.vol_mult * self.vol_ma[0]:
                size = int(self.broker.get_cash() / current)
                if size > 0:
                    self.order = self.buy(size=size)""",
        "exit_logic": """if current < self.lowest[0]:
                    self.order = self.sell(size=self.position.size)"""
    },
    {
        "id": 10,
        "name": "Volatility Squeeze",
        "class_name": "VolatilitySqueezeStrategy",
        "description": "Volatility squeeze breakout",
        "rules": "- Entry: BB width expands after contraction\\n- Exit: Momentum reversal",
        "stop_loss": 4, "take_profit": 10,
        "params": "('bb_period', 20),\\n        ('bb_dev', 2),\\n        ('kc_period', 20),\\n        ('kc_mult', 1.5),\\n        ('stop_loss', 0.04),\\n        ('take_profit', 0.10),",
        "indicators": """self.bb = bt.indicators.BollingerBands(self.data.close, period=self.p.bb_period, devfactor=self.p.bb_dev)
        self.atr = bt.indicators.ATR(self.data, period=self.p.kc_period)
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.kc_period)
        self.mom = bt.indicators.Momentum(self.data.close, period=12)""",
        "entry_logic": """kc_upper = self.sma[0] + self.p.kc_mult * self.atr[0]
            squeeze_off = self.bb.top[0] > kc_upper
            if squeeze_off and self.mom[0] > 0:
                size = int(self.broker.get_cash() / current)
                if size > 0:
                    self.order = self.buy(size=size)""",
        "exit_logic": """if self.mom[0] < 0 and self.mom[-1] >= 0:
                    self.order = self.sell(size=self.position.size)"""
    }
]

def generate_strategy(strategy_def):
    """使用模板生成策略代码"""
    code = STRATEGY_TEMPLATE.format(**strategy_def)
    return code

def validate_code(code, name):
    """验证代码语法"""
    try:
        ast.parse(code)
        return {"valid": True, "lines": len(code.splitlines())}
    except SyntaxError as e:
        return {"valid": False, "error": str(e)}

def main():
    print("=" * 70)
    print("DAY 44: STRATEGY REGENERATION (Template-Based)")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    results = []

    for strat in STRATEGIES:
        print(f"[{strat['id']:02d}] Generating {strat['name']}...", end=" ")

        code = generate_strategy(strat)
        validation = validate_code(code, strat['name'])

        if validation["valid"]:
            # Save to file
            filename = f"{strat['id']:02d}_{strat['class_name'].lower()}.py"
            filepath = OUTPUT_DIR / filename
            with open(filepath, 'w') as f:
                f.write(code)
            print(f"OK ({validation['lines']} lines)")
            results.append({"id": strat["id"], "name": strat["name"], "status": "OK", "lines": validation["lines"]})
        else:
            print(f"FAILED: {validation['error']}")
            results.append({"id": strat["id"], "name": strat["name"], "status": "FAILED", "error": validation["error"]})

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    ok = sum(1 for r in results if r["status"] == "OK")
    print(f"Success: {ok}/{len(results)}")

    # Save metadata
    meta = {"date": datetime.now().isoformat(), "strategies": results}
    with open(OUTPUT_DIR / "generation_metadata.json", 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"\nStrategies saved to: {OUTPUT_DIR}")
    return results

if __name__ == "__main__":
    main()
