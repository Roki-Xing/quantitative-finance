#!/usr/bin/env python3
"""
扩展数据批量回测 - 多股票多时期测试
测试策略在不同股票、不同市场环境下的表现
"""

import backtrader as bt
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import importlib.util
import warnings
warnings.filterwarnings('ignore')

# 配置
DATA_DIR = Path('/root/autodl-tmp/eoh/backtest_data_extended')
STRATEGY_DIR = Path('/root/autodl-tmp/eoh/strategy_library/batch1')
RESULTS_DIR = Path('/root/autodl-tmp/eoh/backtest_results/extended')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 时间段划分
PERIODS = {
    'full': ('2010-01-01', '2025-11-21'),      # 全周期
    '2010-2015': ('2010-01-01', '2015-12-31'), # 牛熊转换
    '2015-2020': ('2016-01-01', '2020-12-31'), # 震荡+疫情
    '2020-2025': ('2021-01-01', '2025-11-21'), # 近期
}

def load_data(csv_path: Path, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """加载并预处理数据"""
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # 筛选时间段
    if start_date:
        df = df[df.index >= start_date]
    if end_date:
        df = df[df.index <= end_date]

    # 确保列名正确
    df.columns = ['open', 'high', 'low', 'close', 'volume'][:len(df.columns)]

    # 转换数值类型
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)
    return df

def load_strategy(strategy_path: Path):
    """动态加载策略类 - 跳过有语法错误的"""
    import sys
    try:
        # 使用唯一的模块名避免冲突
        module_name = f"strat_{strategy_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, strategy_path)
        module = importlib.util.module_from_spec(spec)
        # 关键：注册到sys.modules，否则backtrader无法找到模块
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                return obj
        return None
    except SyntaxError as e:
        print(f'    [SYNTAX ERROR] {strategy_path.name}: {e}')
        return None
    except Exception as e:
        print(f'    [LOAD ERROR] {strategy_path.name}: {e}')
        return None

def run_single_backtest(strategy_class, df: pd.DataFrame, initial_cash: float = 100000) -> dict:
    """运行单次回测"""
    try:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class)

        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)

        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

        results = cerebro.run()
        strat = results[0]

        final = cerebro.broker.getvalue()
        sharpe = strat.analyzers.sharpe.get_analysis()
        dd = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        returns = strat.analyzers.returns.get_analysis()

        return {
            'success': True,
            'initial': initial_cash,
            'final': final,
            'return_pct': (final - initial_cash) / initial_cash * 100,
            'sharpe': sharpe.get('sharperatio'),
            'max_drawdown': dd.get('max', {}).get('drawdown', 0),
            'total_trades': trades.get('total', {}).get('total', 0),
            'annual_return': returns.get('rnorm100', 0),
        }
    except Exception as e:
        return {'success': False, 'error': str(e)[:100]}

def main():
    print('='*80)
    print('扩展数据批量回测 - 多股票多时期')
    print('='*80)

    # 获取所有数据文件和策略
    stock_files = sorted(DATA_DIR.glob('stock_*.csv'))
    strategy_files = sorted(STRATEGY_DIR.glob('*.py'))

    print(f'股票数据: {len(stock_files)} 个')
    print(f'策略文件: {len(strategy_files)} 个')
    print(f'时间段: {len(PERIODS)} 个')
    print()

    # 预加载策略
    strategies = {}
    for sf in strategy_files:
        strat_class = load_strategy(sf)
        if strat_class:
            strategies[sf.stem] = strat_class
            print(f'  [OK] {sf.stem}')
        else:
            print(f'  [SKIP] {sf.stem} - 无策略类')

    print(f'\n有效策略: {len(strategies)} 个')

    # 存储所有结果
    all_results = {
        'meta': {
            'date': datetime.now().isoformat(),
            'stocks': len(stock_files),
            'strategies': len(strategies),
            'periods': list(PERIODS.keys()),
        },
        'results': [],
        'summary': {}
    }

    # 批量回测
    total_tests = len(strategies) * len(stock_files) * len(PERIODS)
    completed = 0

    print(f'\n开始回测 (总计 {total_tests} 次)...\n')

    for period_name, (start, end) in PERIODS.items():
        print(f'\n{"="*80}')
        print(f'时期: {period_name} ({start} ~ {end})')
        print('='*80)

        period_results = []

        for stock_file in stock_files[:5]:  # 先测试5只股票
            stock_name = stock_file.stem.replace('stock_', '')

            try:
                df = load_data(stock_file, start, end)
                if len(df) < 100:
                    print(f'  {stock_name}: 数据不足 ({len(df)} rows), 跳过')
                    continue
            except Exception as e:
                print(f'  {stock_name}: 加载失败 - {e}')
                continue

            print(f'\n  [{stock_name}] {len(df)} rows')

            for strat_name, strat_class in strategies.items():
                result = run_single_backtest(strat_class, df)
                result['stock'] = stock_name
                result['strategy'] = strat_name
                result['period'] = period_name

                period_results.append(result)
                completed += 1

                if result['success']:
                    status = f"Return: {result['return_pct']:+.1f}%"
                else:
                    status = f"Error: {result.get('error', 'Unknown')[:30]}"
                print(f'    {strat_name}: {status}')

        all_results['results'].extend(period_results)

        # 时期汇总
        success_results = [r for r in period_results if r.get('success')]
        if success_results:
            avg_return = sum(r['return_pct'] for r in success_results) / len(success_results)
            sharpes = [r['sharpe'] for r in success_results if r['sharpe']]
            avg_sharpe = sum(sharpes) / len(sharpes) if sharpes else None

            all_results['summary'][period_name] = {
                'total_tests': len(period_results),
                'success': len(success_results),
                'avg_return': avg_return,
                'avg_sharpe': avg_sharpe,
            }
            print(f'\n  [{period_name}] 平均收益: {avg_return:.2f}%, Sharpe: {avg_sharpe}')

    # 保存结果
    results_file = RESULTS_DIR / 'extended_backtest_results.json'
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    # 打印总结
    print('\n' + '='*80)
    print('回测汇总')
    print('='*80)

    for period, summary in all_results['summary'].items():
        print(f"\n{period}:")
        print(f"  测试次数: {summary['total_tests']}")
        print(f"  成功: {summary['success']}")
        print(f"  平均收益: {summary['avg_return']:.2f}%")
        print(f"  平均Sharpe: {summary['avg_sharpe']}")

    print(f'\n结果保存: {results_file}')
    print('='*80)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
