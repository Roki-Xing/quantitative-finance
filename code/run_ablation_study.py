"""
Ablation Study - Batch Execution Script
=======================================

Purpose: Run 40 independent backtests (4 strategies × 5 assets × 2 periods)
Author: Claude Code AI Assistant
Date: 2025-11-27

Experiment Design:
- 4 strategies: Baseline, ATR Only, Risk2Pct Only, Full Adaptive
- 5 assets: 贵州茅台, 五粮液, 招商银行, 京东方, 万科A
- 2 periods: Training (2018-2023), Testing (2024)
- Total: 40 backtests
"""

import backtrader as bt
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys

# Import strategies
from ablation_study_strategies import (
    Strategy_Baseline_Fixed,
    Strategy_ATR_Only,
    Strategy_Risk2Pct_Only,
    Strategy_Full_Adaptive
)


# =============================================================================
# Configuration
# =============================================================================

STRATEGIES = {
    'Baseline_Fixed': Strategy_Baseline_Fixed,
    'ATR_Only': Strategy_ATR_Only,
    'Risk2Pct_Only': Strategy_Risk2Pct_Only,
    'Full_Adaptive': Strategy_Full_Adaptive
}

ASSETS = {
    '600519_贵州茅台': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv',
        'volatility': 'low',
        'sector': '消费'
    },
    '000858_五粮液': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000858.csv',
        'volatility': 'medium',
        'sector': '消费'
    },
    '600036_招商银行': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600036.csv',
        'volatility': 'low',
        'sector': '金融'
    },
    '000725_京东方': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000725.csv',
        'volatility': 'high',
        'sector': '科技'
    },
    '000002_万科A': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000002.csv',
        'volatility': 'high',
        'sector': '地产'
    }
}

PERIODS = {
    'training': {'start': '2018-01-01', 'end': '2023-12-31'},
    'testing': {'start': '2024-01-01', 'end': '2024-12-31'}
}

INITIAL_CASH = 100000


# =============================================================================
# Backtest Runner
# =============================================================================

def run_single_backtest(strategy_class, data_path, start_date, end_date, initial_cash=100000):
    """
    Run a single backtest

    Returns:
        dict: {returns_pct, final_value, sharpe_ratio, max_drawdown_pct, total_trades}
    """
    try:
        # Load data
        df = pd.read_csv(data_path, parse_dates=['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        if len(df) < 50:
            return None

        # Initialize Cerebro
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.0015)

        # Create data feed
        data_feed = bt.feeds.PandasData(
            dataname=df,
            datetime='date',
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1
        )

        cerebro.adddata(data_feed)
        cerebro.addstrategy(strategy_class)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        # Run backtest
        results = cerebro.run()
        final_value = cerebro.broker.getvalue()

        # Extract metrics
        sharpe = results[0].analyzers.sharpe.get_analysis()
        drawdown = results[0].analyzers.drawdown.get_analysis()
        trades = results[0].analyzers.trades.get_analysis()

        sharpe_ratio = sharpe.get('sharperatio', 0.0)
        if sharpe_ratio is None:
            sharpe_ratio = 0.0

        max_drawdown_pct = drawdown.get('max', {}).get('drawdown', 0.0)
        total_trades = trades.get('total', {}).get('closed', 0)

        returns_pct = ((final_value - initial_cash) / initial_cash) * 100

        return {
            'returns_pct': round(returns_pct, 2),
            'final_value': round(final_value, 2),
            'sharpe_ratio': round(sharpe_ratio, 3),
            'max_drawdown_pct': round(max_drawdown_pct, 2),
            'total_trades': total_trades,
            'initial_cash': initial_cash,
            'data_points': len(df),
            'start_date': start_date,
            'end_date': end_date
        }

    except Exception as e:
        print(f"    ERROR: {str(e)}")
        return None


# =============================================================================
# Main Experiment Loop
# =============================================================================

def main():
    print("=" * 80)
    print("Ablation Study - Batch Execution")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total backtests: {len(STRATEGIES)} × {len(ASSETS)} × {len(PERIODS)} = 40")
    print("=" * 80)

    results = {}
    counter = 0
    total = len(STRATEGIES) * len(ASSETS) * len(PERIODS)

    for strategy_name, strategy_class in STRATEGIES.items():
        print(f"\n[{strategy_name}]")
        results[strategy_name] = {}

        for asset_name, asset_info in ASSETS.items():
            print(f"  - {asset_name}...")
            results[strategy_name][asset_name] = {}
            results[strategy_name][asset_name]['volatility'] = asset_info['volatility']
            results[strategy_name][asset_name]['sector'] = asset_info['sector']

            for period_name, period_dates in PERIODS.items():
                counter += 1
                print(f"    [{counter}/{total}] {period_name}...", end=' ')

                result = run_single_backtest(
                    strategy_class=strategy_class,
                    data_path=asset_info['file'],
                    start_date=period_dates['start'],
                    end_date=period_dates['end'],
                    initial_cash=INITIAL_CASH
                )

                if result:
                    results[strategy_name][asset_name][f'{period_name}_period'] = result
                    print(f"OK ({result['returns_pct']:+.2f}%)")
                else:
                    print("FAILED")

    # Save results
    output_file = '/root/autodl-tmp/outputs/ablation_study_results.json'
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        'metadata': {
            'experiment_name': 'Ablation Study - Component Contribution Analysis',
            'timestamp': datetime.now().isoformat(),
            'total_backtests': total,
            'strategies': list(STRATEGIES.keys()),
            'assets': list(ASSETS.keys()),
            'periods': list(PERIODS.keys()),
            'initial_cash': INITIAL_CASH
        },
        'results': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("Ablation Study - Execution Complete")
    print("=" * 80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output file: {output_file}")
    print(f"File size: {Path(output_file).stat().st_size / 1024:.1f} KB")
    print("=" * 80)


if __name__ == '__main__':
    main()
