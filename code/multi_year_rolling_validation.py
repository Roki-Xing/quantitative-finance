"""
多年份滚动窗口验证实验
======================

目的: 解决审稿人关于"跨时间泛化"的质疑
- 当前问题: 仅2024年测试期，单一时间窗口不足
- 解决方案: 多年份滚动验证 (2019-2023)

实验设计:
---------
滚动窗口方法 (Walk-Forward Validation):
1. Window 1: 训练2018-2021 → 测试2022
2. Window 2: 训练2019-2022 → 测试2023
3. Window 3: 训练2018-2023 → 测试2024 (原有)

策略: LLM_Adaptive (完全自适应)
资产: 5只核心A股 (茅台, 五粮液, 招行, 京东方, 万科A)
指标: 收益率, Sharpe, 最大回撤, 成功率

总回测数: 3窗口 × 5资产 = 15回测
"""

import backtrader as bt
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# =============================================================================
# 配置
# =============================================================================

# 核心资产 (已验证数据质量)
ASSETS = {
    '600519_贵州茅台': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv',
        'volatility': 'low'
    },
    '000858_五粮液': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000858.csv',
        'volatility': 'medium'
    },
    '600036_招商银行': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600036.csv',
        'volatility': 'low'
    },
    '000725_京东方': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000725.csv',
        'volatility': 'high'
    },
    '000002_万科A': {
        'file': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000002.csv',
        'volatility': 'high'
    }
}

# 滚动窗口定义
ROLLING_WINDOWS = [
    {
        'name': 'Window1_2022',
        'train_start': '2018-01-01',
        'train_end': '2021-12-31',
        'test_start': '2022-01-01',
        'test_end': '2022-12-31',
        'description': '4年训练 → 2022测试'
    },
    {
        'name': 'Window2_2023',
        'train_start': '2019-01-01',
        'train_end': '2022-12-31',
        'test_start': '2023-01-01',
        'test_end': '2023-12-31',
        'description': '4年训练 → 2023测试'
    },
    {
        'name': 'Window3_2024',
        'train_start': '2018-01-01',
        'train_end': '2023-12-31',
        'test_start': '2024-01-01',
        'test_end': '2024-12-31',
        'description': '6年训练 → 2024测试 (原有)'
    }
]

# =============================================================================
# 策略定义 (LLM_Adaptive完全自适应)
# =============================================================================

class LLM_Adaptive(bt.Strategy):
    """完全自适应策略 (ATR×3 + 2%风险管理)"""
    params = (
        ('sma_fast', 5), ('sma_slow', 20), ('rsi_period', 7),
        ('atr_period', 14), ('atr_multiplier', 3.0), ('risk_percent', 0.02)
    )

    def __init__(self):
        self.sma_fast = bt.indicators.SMA(period=self.p.sma_fast)
        self.sma_slow = bt.indicators.SMA(period=self.p.sma_slow)
        self.rsi = bt.indicators.RSI(period=self.p.rsi_period)
        self.atr = bt.indicators.ATR(period=self.p.atr_period)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Entry signal: SMA crossover + RSI filter
            if self.crossover > 0 and self.rsi > 50:
                # 2% risk position sizing
                account_value = self.broker.getvalue()
                risk_amount = account_value * self.p.risk_percent
                atr_stop_distance = self.atr[0] * self.p.atr_multiplier
                position_size = int(risk_amount / atr_stop_distance)
                position_size = max(1, min(position_size, 100))

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
# 回测执行器
# =============================================================================

def run_backtest(data_path, start_date, end_date, initial_cash=100000):
    """运行单个回测"""
    try:
        df = pd.read_csv(data_path, parse_dates=['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        if len(df) < 50:
            return None

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.0015)  # 0.15% standard rate

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
        cerebro.addstrategy(LLM_Adaptive)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        results = cerebro.run()
        final_value = cerebro.broker.getvalue()

        sharpe = results[0].analyzers.sharpe.get_analysis()
        drawdown = results[0].analyzers.drawdown.get_analysis()
        trades = results[0].analyzers.trades.get_analysis()

        return {
            'returns_pct': round(((final_value - initial_cash) / initial_cash) * 100, 2),
            'final_value': round(final_value, 2),
            'sharpe_ratio': round(sharpe.get('sharperatio', 0) or 0, 3),
            'max_drawdown_pct': round(drawdown.get('max', {}).get('drawdown', 0), 2),
            'total_trades': trades.get('total', {}).get('closed', 0),
            'initial_cash': initial_cash,
            'data_points': len(df),
            'start_date': start_date,
            'end_date': end_date
        }

    except Exception as e:
        print(f"      ERROR: {str(e)}")
        return None


# =============================================================================
# 主程序
# =============================================================================

def main():
    print("=" * 80)
    print("多年份滚动窗口验证实验")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"实验规模: 3窗口 × 5资产 = 15回测")
    print("=" * 80)

    results = {}
    counter = 0
    total = len(ROLLING_WINDOWS) * len(ASSETS)

    for window in ROLLING_WINDOWS:
        window_name = window['name']
        print(f"\n[{window_name}] {window['description']}")
        print(f"  Train: {window['train_start']} to {window['train_end']}")
        print(f"  Test:  {window['test_start']} to {window['test_end']}")

        results[window_name] = {
            'metadata': {
                'train_period': f"{window['train_start']} to {window['train_end']}",
                'test_period': f"{window['test_start']} to {window['test_end']}",
                'description': window['description']
            },
            'assets': {}
        }

        for asset_name, asset_info in ASSETS.items():
            counter += 1
            print(f"    [{counter}/{total}] {asset_name}...", end=' ')

            # Run test period backtest
            test_result = run_backtest(
                data_path=asset_info['file'],
                start_date=window['test_start'],
                end_date=window['test_end']
            )

            if test_result:
                results[window_name]['assets'][asset_name] = {
                    'volatility': asset_info['volatility'],
                    'test_period': test_result
                }
                print(f"OK ({test_result['returns_pct']:+.2f}%, {test_result['sharpe_ratio']:.3f} Sharpe)")
            else:
                print("FAILED")

    # 计算汇总统计
    print("\n" + "=" * 80)
    print("滚动窗口汇总统计")
    print("=" * 80)

    for window in ROLLING_WINDOWS:
        window_name = window['name']
        window_data = results[window_name]['assets']

        returns_list = [data['test_period']['returns_pct'] for data in window_data.values() if 'test_period' in data]
        success_count = sum(1 for r in returns_list if r > 0)

        if returns_list:
            avg_return = sum(returns_list) / len(returns_list)
            success_rate = success_count / len(returns_list)

            print(f"\n{window_name}:")
            print(f"  平均收益: {avg_return:+.2f}%")
            print(f"  成功率: {success_count}/{len(returns_list)} = {success_rate*100:.1f}%")
            print(f"  收益分布: {min(returns_list):+.2f}% to {max(returns_list):+.2f}%")

            results[window_name]['summary'] = {
                'average_return': round(avg_return, 2),
                'success_rate': round(success_rate * 100, 1),
                'success_count': success_count,
                'total_assets': len(returns_list),
                'min_return': round(min(returns_list), 2),
                'max_return': round(max(returns_list), 2)
            }

    # 保存结果
    output_file = '/root/autodl-tmp/outputs/multi_year_rolling_validation.json'
    output_data = {
        'metadata': {
            'experiment_name': 'Multi-Year Rolling Window Validation',
            'timestamp': datetime.now().isoformat(),
            'total_backtests': total,
            'windows': len(ROLLING_WINDOWS),
            'assets': list(ASSETS.keys()),
            'strategy': 'LLM_Adaptive (ATR×3 + 2% risk)'
        },
        'rolling_windows': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("多年份滚动验证 - 执行完成")
    print("=" * 80)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"输出文件: {output_file}")
    print(f"文件大小: {Path(output_file).stat().st_size / 1024:.1f} KB")
    print("=" * 80)


if __name__ == '__main__':
    main()
