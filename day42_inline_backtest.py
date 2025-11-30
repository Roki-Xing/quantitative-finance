#!/usr/bin/env python3
"""Day 42-43: Backtest with built-in strategy"""

import backtrader as bt
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data")
RESULTS_DIR = Path("/root/autodl-tmp/eoh/backtest_results/batch1")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Load data
df = pd.read_csv(DATA_DIR / "000001.csv")
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期', inplace=True)
df = df.rename(columns={'开盘':'open', '收盘':'close', '最高':'high', '最低':'low', '成交量':'volume'})
df = df[['open', 'high', 'low', 'close', 'volume']]

print("="*60)
print("DAY 42-43: STRATEGY BACKTEST")
print("="*60)
print(f"Data: {len(df)} bars ({df.index[0].date()} ~ {df.index[-1].date()})")
print()

# Define strategies inline
class SMAStrategy(bt.Strategy):
    params = (('fast', 20), ('slow', 50), ('sl', 0.05), ('tp', 0.15))
    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow)
        self.cross = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None
        self.entry = 0.0
    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy(): self.entry = order.executed.price
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None
    def next(self):
        if self.order: return
        if not self.position:
            if self.cross > 0:
                self.order = self.buy(size=int(self.broker.get_cash()/self.data.close[0]))
        else:
            c = self.data.close[0]
            if c <= self.entry*(1-self.p.sl) or c >= self.entry*(1+self.p.tp) or self.cross < 0:
                self.order = self.sell(size=self.position.size)

class RSIStrategy(bt.Strategy):
    params = (('period', 14), ('oversold', 30), ('overbought', 70), ('sl', 0.04), ('tp', 0.10))
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.period)
        self.order = None
        self.entry = 0.0
    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy(): self.entry = order.executed.price
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None
    def next(self):
        if self.order: return
        if not self.position:
            if self.rsi[0] < self.p.oversold:
                self.order = self.buy(size=int(self.broker.get_cash()/self.data.close[0]))
        else:
            c = self.data.close[0]
            if c <= self.entry*(1-self.p.sl) or c >= self.entry*(1+self.p.tp) or self.rsi[0] > self.p.overbought:
                self.order = self.sell(size=self.position.size)

class MACDStrategy(bt.Strategy):
    params = (('fast', 12), ('slow', 26), ('signal', 9), ('sl', 0.05), ('tp', 0.12))
    def __init__(self):
        self.macd = bt.indicators.MACD(self.data.close, period_me1=self.p.fast, period_me2=self.p.slow, period_signal=self.p.signal)
        self.order = None
        self.entry = 0.0
    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy(): self.entry = order.executed.price
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None
    def next(self):
        if self.order: return
        if not self.position:
            if self.macd.macd[0] > 0 and self.macd.macd[-1] <= 0:
                self.order = self.buy(size=int(self.broker.get_cash()/self.data.close[0]))
        else:
            c = self.data.close[0]
            if c <= self.entry*(1-self.p.sl) or c >= self.entry*(1+self.p.tp) or (self.macd.macd[0] < 0 and self.macd.macd[-1] >= 0):
                self.order = self.sell(size=self.position.size)

class BollingerStrategy(bt.Strategy):
    params = (('period', 20), ('devfactor', 2), ('sl', 0.04), ('tp', 0.10))
    def __init__(self):
        self.bb = bt.indicators.BollingerBands(self.data.close, period=self.p.period, devfactor=self.p.devfactor)
        self.order = None
        self.entry = 0.0
    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy(): self.entry = order.executed.price
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None
    def next(self):
        if self.order: return
        if not self.position:
            if self.data.close[0] < self.bb.bot[0]:
                self.order = self.buy(size=int(self.broker.get_cash()/self.data.close[0]))
        else:
            c = self.data.close[0]
            if c <= self.entry*(1-self.p.sl) or c >= self.entry*(1+self.p.tp) or c > self.bb.mid[0]:
                self.order = self.sell(size=self.position.size)

# Run backtests
strategies = [
    ("SMA_Crossover", SMAStrategy),
    ("RSI_Oversold", RSIStrategy),
    ("MACD_Zero_Cross", MACDStrategy),
    ("Bollinger_Bounce", BollingerStrategy),
]

results = []
for name, strat_cls in strategies:
    try:
        cerebro = bt.Cerebro(stdstats=False)
        cerebro.addstrategy(strat_cls)
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.02)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        initial = cerebro.broker.getvalue()
        strats = cerebro.run()
        final = cerebro.broker.getvalue()
        strat = strats[0]

        sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio') or 0
        maxdd = strat.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0)
        trades = strat.analyzers.trades.get_analysis().get('total', {}).get('total', 0)

        ret = (final - initial) / initial * 100
        result = {"name": name, "final": round(final, 2), "return_pct": round(ret, 2),
                  "sharpe": round(sharpe, 4), "max_dd": round(maxdd, 2), "trades": trades, "status": "OK"}
        print(f"[{name:20}] Return: {ret:>7.2f}% | Sharpe: {sharpe:>7.4f} | MaxDD: {maxdd:>6.2f}% | Trades: {trades}")
    except Exception as e:
        result = {"name": name, "status": "FAILED", "error": str(e)[:50]}
        print(f"[{name:20}] FAILED: {str(e)[:50]}")
    results.append(result)

# Save results
output = {"date": datetime.now().isoformat(), "data": "000001.SZ", "results": results}
with open(RESULTS_DIR / "backtest_results.json", 'w') as f:
    json.dump(output, f, indent=2)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
ok = [r for r in results if r["status"] == "OK"]
print(f"Successful: {len(ok)}/{len(results)}")
if ok:
    best = max(ok, key=lambda x: x["sharpe"])
    print(f"Best strategy: {best['name']} (Sharpe={best['sharpe']:.4f}, Return={best['return_pct']:.2f}%)")
    avg_ret = sum(r["return_pct"] for r in ok) / len(ok)
    avg_sharpe = sum(r["sharpe"] for r in ok) / len(ok)
    print(f"Average: Return={avg_ret:.2f}%, Sharpe={avg_sharpe:.4f}")
print(f"\nResults saved: {RESULTS_DIR / 'backtest_results.json'}")
