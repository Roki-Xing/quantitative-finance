#!/usr/bin/env python3
"""Day 45: Portfolio Strategy - Combined Best Strategies"""
import backtrader as bt
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import logging

logging.disable(logging.CRITICAL)

DATA_DIR = Path('/root/autodl-tmp/eoh/backtest_data')
RESULTS_DIR = Path('/root/autodl-tmp/eoh/backtest_results/portfolio')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print('='*60)
print('DAY 45: PORTFOLIO BACKTEST')
print('='*60)

# Load data for two stocks
def load_data(symbol):
    df = pd.read_csv(DATA_DIR / f'{symbol}.csv')
    df['日期'] = pd.to_datetime(df['日期'])
    df.set_index('日期', inplace=True)
    df = df.rename(columns={'开盘':'open', '收盘':'close', '最高':'high', '最低':'low', '成交量':'volume'})
    return df[['open', 'high', 'low', 'close', 'volume']]

# Combined Portfolio Strategy
class PortfolioStrategy(bt.Strategy):
    """
    Portfolio combining Momentum and RSI strategies
    - Momentum: Primary trend following
    - RSI: Mean reversion for oversold conditions
    """
    params = (
        ('mom_period', 10),
        ('vol_period', 20),
        ('rsi_period', 14),
        ('oversold', 30),
        ('overbought', 70),
        ('stop_loss', 0.04),
        ('take_profit', 0.10),
        ('position_pct', 0.45),  # 45% per strategy
    )

    def __init__(self):
        # Momentum indicators
        self.momentum = bt.indicators.Momentum(self.data.close, period=self.p.mom_period)
        self.vol_ma = bt.indicators.SMA(self.data.volume, period=self.p.vol_period)

        # RSI indicator
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)

        # State tracking
        self.order = None
        self.entry_price = 0.0
        self.entry_reason = ''
        self.trade_count = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Completed:
            if order.isbuy():
                self.entry_price = order.executed.price
                self.trade_count += 1
        self.order = None

    def next(self):
        if self.order:
            return

        c = self.data.close[0]
        cash = self.broker.get_cash()

        if not self.position:
            # Entry Logic: Momentum OR RSI

            # Momentum signal: Positive momentum + High volume
            mom_signal = self.momentum[0] > 0 and self.data.volume[0] > self.vol_ma[0]

            # RSI signal: Oversold
            rsi_signal = self.rsi[0] < self.p.oversold

            if mom_signal or rsi_signal:
                size = int(cash * self.p.position_pct / c)
                if size > 0:
                    self.order = self.buy(size=size)
                    self.entry_reason = 'MOM' if mom_signal else 'RSI'

        else:
            # Exit Logic: Stop-loss, Take-profit, or Signal reversal
            pnl_pct = (c - self.entry_price) / self.entry_price

            # Stop-loss
            if pnl_pct <= -self.p.stop_loss:
                self.order = self.sell(size=self.position.size)
            # Take-profit
            elif pnl_pct >= self.p.take_profit:
                self.order = self.sell(size=self.position.size)
            # Momentum exit
            elif self.entry_reason == 'MOM' and self.momentum[0] < 0:
                self.order = self.sell(size=self.position.size)
            # RSI exit
            elif self.entry_reason == 'RSI' and self.rsi[0] > self.p.overbought:
                self.order = self.sell(size=self.position.size)


def run_backtest(symbol, strategy_class):
    try:
        df = load_data(symbol)
        cerebro = bt.Cerebro(stdstats=False)
        cerebro.addstrategy(strategy_class)
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
            'status': 'SUCCESS',
            'symbol': symbol,
            'final': round(final, 2),
            'return_pct': round((final - initial) / initial * 100, 2),
            'sharpe': round(sharpe, 4),
            'max_dd': round(maxdd, 2),
            'trades': trades
        }
    except Exception as e:
        return {'status': 'FAILED', 'symbol': symbol, 'error': str(e)[:80]}


# Run backtests on multiple symbols
symbols = ['000001', '000002']
results = []

print(f"\nTesting Portfolio Strategy on {len(symbols)} stocks\n")

for symbol in symbols:
    print(f'[{symbol}]', end=' ')
    r = run_backtest(symbol, PortfolioStrategy)
    results.append(r)
    if r['status'] == 'SUCCESS':
        print(f"Return: {r['return_pct']:>7.2f}% | Sharpe: {r['sharpe']:>7.4f} | MaxDD: {r['max_dd']:>6.2f}% | Trades: {r['trades']}")
    else:
        print(f"FAILED: {r.get('error', 'Unknown')}")

# Calculate portfolio average
successful = [r for r in results if r['status'] == 'SUCCESS']
if successful:
    avg_return = sum(r['return_pct'] for r in successful) / len(successful)
    avg_sharpe = sum(r['sharpe'] for r in successful) / len(successful)
    avg_dd = sum(r['max_dd'] for r in successful) / len(successful)

# Save results
output = {
    'date': datetime.now().isoformat(),
    'strategy': 'Portfolio (Momentum + RSI)',
    'results': results,
    'portfolio_stats': {
        'avg_return': round(avg_return, 2) if successful else 0,
        'avg_sharpe': round(avg_sharpe, 4) if successful else 0,
        'avg_max_dd': round(avg_dd, 2) if successful else 0,
    }
}

with open(RESULTS_DIR / 'portfolio_results.json', 'w') as f:
    json.dump(output, f, indent=2)

# Summary
print()
print('='*60)
print('PORTFOLIO SUMMARY')
print('='*60)
print(f'Stocks tested: {len(symbols)}')
print(f'Successful: {len(successful)}/{len(results)}')
if successful:
    print(f'Avg Return: {avg_return:.2f}%')
    print(f'Avg Sharpe: {avg_sharpe:.4f}')
    print(f'Avg MaxDD: {avg_dd:.2f}%')

# Compare with single strategies
print()
print('='*60)
print('COMPARISON: Portfolio vs Single Strategies (on 000002)')
print('='*60)
print(f'05_Momentum:    Return=+17.62%, Sharpe=0.1533, MaxDD=39.99%')
print(f'03_RSIOversold: Return= -5.13%, Sharpe=-0.1616, MaxDD=38.35%')
portfolio_000002 = next((r for r in results if r['symbol'] == '000002'), None)
if portfolio_000002 and portfolio_000002['status'] == 'SUCCESS':
    print(f"Portfolio:      Return={portfolio_000002['return_pct']:>+6.2f}%, Sharpe={portfolio_000002['sharpe']:.4f}, MaxDD={portfolio_000002['max_dd']:.2f}%")

print(f"\nResults saved: {RESULTS_DIR / 'portfolio_results.json'}")
