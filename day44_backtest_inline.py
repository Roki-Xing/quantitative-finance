#!/usr/bin/env python3
"""Day 44: Backtest 10 Fixed Strategies (Inline)"""
import backtrader as bt
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import logging

logging.disable(logging.CRITICAL)

DATA_DIR = Path('/root/autodl-tmp/eoh/backtest_data')
RESULTS_DIR = Path('/root/autodl-tmp/eoh/backtest_results/batch1_fixed')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print('='*60)
print('DAY 44: BACKTEST FIXED STRATEGIES')
print('='*60)

# Load data - use 000002 (万科A) for higher volatility
df = pd.read_csv(DATA_DIR / '000002.csv')
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期', inplace=True)
df = df.rename(columns={'开盘':'open', '收盘':'close', '最高':'high', '最低':'low', '成交量':'volume'})
df = df[['open', 'high', 'low', 'close', 'volume']]
print(f'Data: {len(df)} bars ({df.index[0].date()} ~ {df.index[-1].date()})')

# Strategy 1: Dual MA Crossover
class DualMAStrategy(bt.Strategy):
    params = (('fast', 20), ('slow', 50), ('stop_loss', 0.05), ('take_profit', 0.15))
    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow)
        self.cross = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if not self.position:
            if self.cross > 0:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or self.cross < 0:
                self.order = self.sell(size=self.position.size)

# Strategy 2: MACD Zero Cross
class MACDZeroStrategy(bt.Strategy):
    params = (('fast', 12), ('slow', 26), ('signal', 9), ('stop_loss', 0.04), ('take_profit', 0.12))
    def __init__(self):
        self.macd = bt.indicators.MACD(self.data.close, period_me1=self.p.fast, period_me2=self.p.slow, period_signal=self.p.signal)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if not self.position:
            if self.macd.macd[0] > 0 and self.macd.macd[-1] <= 0:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or (self.macd.macd[0] < 0 and self.macd.macd[-1] >= 0):
                self.order = self.sell(size=self.position.size)

# Strategy 3: RSI Oversold
class RSIOversoldStrategy(bt.Strategy):
    params = (('period', 14), ('oversold', 30), ('overbought', 70), ('stop_loss', 0.03), ('take_profit', 0.08))
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.period)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if not self.position:
            if self.rsi[0] < self.p.oversold:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or self.rsi[0] > self.p.overbought:
                self.order = self.sell(size=self.position.size)

# Strategy 4: Bollinger Bands
class BollingerStrategy(bt.Strategy):
    params = (('period', 20), ('devfactor', 2), ('stop_loss', 0.04), ('take_profit', 0.10))
    def __init__(self):
        self.bb = bt.indicators.BollingerBands(self.data.close, period=self.p.period, devfactor=self.p.devfactor)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if not self.position:
            if c < self.bb.bot[0]:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or c > self.bb.mid[0]:
                self.order = self.sell(size=self.position.size)

# Strategy 5: Momentum
class MomentumStrategy(bt.Strategy):
    params = (('mom_period', 10), ('vol_period', 20), ('stop_loss', 0.05), ('take_profit', 0.12))
    def __init__(self):
        self.momentum = bt.indicators.Momentum(self.data.close, period=self.p.mom_period)
        self.vol_ma = bt.indicators.SMA(self.data.volume, period=self.p.vol_period)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if not self.position:
            if self.momentum[0] > 0 and self.data.volume[0] > self.vol_ma[0]:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or self.momentum[0] < 0:
                self.order = self.sell(size=self.position.size)

# Strategy 6: ATR Channel
class ATRChannelStrategy(bt.Strategy):
    params = (('sma_period', 20), ('atr_period', 14), ('atr_mult', 2), ('stop_loss', 0.05), ('take_profit', 0.15))
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.sma_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if not self.position:
            upper = self.sma[0] + self.p.atr_mult * self.atr[0]
            if c > upper:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            lower = self.sma[0] - self.atr[0]
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or c < lower:
                self.order = self.sell(size=self.position.size)

# Strategy 7: Triple Filter
class TripleFilterStrategy(bt.Strategy):
    params = (('fast', 10), ('medium', 20), ('slow', 50), ('stop_loss', 0.04), ('take_profit', 0.12))
    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.med_ma = bt.indicators.SMA(self.data.close, period=self.p.medium)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if not self.position:
            if self.fast_ma[0] > self.med_ma[0] > self.slow_ma[0]:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or self.fast_ma[0] < self.med_ma[0]:
                self.order = self.sell(size=self.position.size)

# Strategy 8: Mean Reversion
class MeanReversionStrategy(bt.Strategy):
    params = (('period', 20), ('entry_z', -2), ('exit_z', 0), ('stop_loss', 0.03), ('take_profit', 0.06))
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
        self.std = bt.indicators.StdDev(self.data.close, period=self.p.period)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if self.std[0] <= 0: return
        zscore = (c - self.sma[0]) / self.std[0]
        if not self.position:
            if zscore < self.p.entry_z:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or zscore > self.p.exit_z:
                self.order = self.sell(size=self.position.size)

# Strategy 9: Volume Breakout
class VolumeBreakoutStrategy(bt.Strategy):
    params = (('high_period', 20), ('low_period', 10), ('vol_mult', 2), ('stop_loss', 0.05), ('take_profit', 0.15))
    def __init__(self):
        self.highest = bt.indicators.Highest(self.data.high, period=self.p.high_period)
        self.lowest = bt.indicators.Lowest(self.data.low, period=self.p.low_period)
        self.vol_ma = bt.indicators.SMA(self.data.volume, period=20)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if not self.position:
            if c >= self.highest[-1] and self.data.volume[0] > self.p.vol_mult * self.vol_ma[0]:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or c < self.lowest[0]:
                self.order = self.sell(size=self.position.size)

# Strategy 10: Volatility Squeeze
class VolatilitySqueezeStrategy(bt.Strategy):
    params = (('bb_period', 20), ('bb_dev', 2), ('kc_period', 20), ('kc_mult', 1.5), ('stop_loss', 0.04), ('take_profit', 0.10))
    def __init__(self):
        self.bb = bt.indicators.BollingerBands(self.data.close, period=self.p.bb_period, devfactor=self.p.bb_dev)
        self.atr = bt.indicators.ATR(self.data, period=self.p.kc_period)
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.kc_period)
        self.mom = bt.indicators.Momentum(self.data.close, period=12)
        self.order = None
        self.entry_price = 0.0
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]: return
        if order.status == order.Completed:
            if order.isbuy(): self.entry_price = order.executed.price
        self.order = None
    def next(self):
        if self.order: return
        c = self.data.close[0]
        if not self.position:
            kc_upper = self.sma[0] + self.p.kc_mult * self.atr[0]
            squeeze_off = self.bb.top[0] > kc_upper
            if squeeze_off and self.mom[0] > 0:
                self.order = self.buy(size=int(self.broker.get_cash()*0.95/c))
        else:
            if c <= self.entry_price*(1-self.p.stop_loss) or c >= self.entry_price*(1+self.p.take_profit) or (self.mom[0] < 0 and self.mom[-1] >= 0):
                self.order = self.sell(size=self.position.size)

# Strategy list
strategies = [
    ('01_DualMA', DualMAStrategy),
    ('02_MACDZero', MACDZeroStrategy),
    ('03_RSIOversold', RSIOversoldStrategy),
    ('04_Bollinger', BollingerStrategy),
    ('05_Momentum', MomentumStrategy),
    ('06_ATRChannel', ATRChannelStrategy),
    ('07_TripleFilter', TripleFilterStrategy),
    ('08_MeanReversion', MeanReversionStrategy),
    ('09_VolumeBreakout', VolumeBreakoutStrategy),
    ('10_VolSqueeze', VolatilitySqueezeStrategy),
]

def run_backtest(name, strat_class):
    try:
        cerebro = bt.Cerebro(stdstats=False)
        cerebro.addstrategy(strat_class)
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.02)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        initial = cerebro.broker.getvalue()
        results = cerebro.run()
        final = cerebro.broker.getvalue()
        strat = results[0]

        sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio') or 0
        maxdd = strat.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0)
        trades = strat.analyzers.trades.get_analysis().get('total', {}).get('total', 0)

        return {
            'status': 'SUCCESS', 'final': round(final, 2),
            'return_pct': round((final - initial) / initial * 100, 2),
            'sharpe': round(sharpe, 4), 'max_dd': round(maxdd, 2), 'trades': trades
        }
    except Exception as e:
        return {'status': 'FAILED', 'error': str(e)[:80]}

# Run all backtests
results = []
print()
for name, strat_class in strategies:
    print(f'[{name}]', end=' ')
    r = run_backtest(name, strat_class)
    r['strategy'] = name
    results.append(r)
    if r['status'] == 'SUCCESS':
        print(f"Return: {r['return_pct']:>7.2f}% | Sharpe: {r['sharpe']:>7.4f} | MaxDD: {r['max_dd']:>6.2f}% | Trades: {r['trades']}")
    else:
        print(f"FAILED: {r.get('error', 'Unknown')}")

# Save results
with open(RESULTS_DIR / 'backtest_results.json', 'w') as f:
    json.dump({'date': datetime.now().isoformat(), 'data': '000001.SZ', 'results': results}, f, indent=2)

# Summary
print()
print('='*60)
print('SUMMARY')
print('='*60)
success = [r for r in results if r['status'] == 'SUCCESS']
print(f'Success: {len(success)}/{len(results)}')

if success:
    avg_ret = sum(r['return_pct'] for r in success) / len(success)
    avg_sharpe = sum(r['sharpe'] for r in success) / len(success)
    best = max(success, key=lambda x: x['sharpe'])
    worst = min(success, key=lambda x: x['sharpe'])
    print(f'Avg Return: {avg_ret:.2f}%')
    print(f'Avg Sharpe: {avg_sharpe:.4f}')
    print(f"Best: {best['strategy']} (Sharpe={best['sharpe']:.4f})")
    print(f"Worst: {worst['strategy']} (Sharpe={worst['sharpe']:.4f})")

print(f"\nResults saved: {RESULTS_DIR / 'backtest_results.json'}")
