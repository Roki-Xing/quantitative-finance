"""
参数敏感性分析 - 批量测试脚本
============================

功能: 运行完整的150个回测实验
作者: Claude Code AI Assistant
日期: 2025-11-27
Python: 3.8+

实验矩阵:
- 实验A: 止损参数扫描 (6固定+1自适应) × 5资产 × 2期 = 70回测
- 实验B: 仓位参数扫描 (6固定+1自适应) × 5资产 × 2期 = 70回测
- 实验C: 完全自适应 × 5资产 × 2期 = 10回测
- 总计: 150个独立回测

预计运行时间: 3-4小时
"""

import backtrader as bt
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import sys
import traceback

from parameter_sensitivity_strategies import (
    Strategy13_FixedStopLoss,
    Strategy13_FixedPositionSize,
    Strategy13_ATR_Adaptive,
    Strategy13_Risk2Pct,
    Strategy13_FullyAdaptive
)


# =============================================================================
# 资产配置 (5只代表性A股)
# =============================================================================

ASSETS = {
    '600519_贵州茅台': {
        'path': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600519.csv',
        'train_start': '2018-01-01',
        'train_end': '2023-12-31',
        'test_start': '2024-01-01',
        'test_end': '2024-12-31',
        'volatility': 'low',
        'price_level': 'high',
        'sector': '消费'
    },
    '000858_五粮液': {
        'path': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000858.csv',
        'train_start': '2018-01-01',
        'train_end': '2023-12-31',
        'test_start': '2024-01-01',
        'test_end': '2024-12-31',
        'volatility': 'medium',
        'price_level': 'medium',
        'sector': '消费'
    },
    '600036_招商银行': {
        'path': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sh_600036.csv',
        'train_start': '2018-01-01',
        'train_end': '2023-12-31',
        'test_start': '2024-01-01',
        'test_end': '2024-12-31',
        'volatility': 'low',
        'price_level': 'medium',
        'sector': '金融'
    },
    '000725_京东方': {
        'path': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000725.csv',
        'train_start': '2018-01-01',
        'train_end': '2023-12-31',
        'test_start': '2024-01-01',
        'test_end': '2024-12-31',
        'volatility': 'high',
        'price_level': 'low',
        'sector': '科技'
    },
    '000002_万科A': {
        'path': '/root/autodl-tmp/eoh/backtest_data_extended/stock_sz_000002.csv',
        'train_start': '2018-01-01',
        'train_end': '2023-12-31',
        'test_start': '2024-01-01',
        'test_end': '2024-12-31',
        'volatility': 'high',
        'price_level': 'medium',
        'sector': '地产'
    }
}


# =============================================================================
# 参数扫描配置
# =============================================================================

STOP_LOSS_PARAMS = [50, 100, 150, 200, 250, 300]  # 6个固定止损值
POSITION_SIZE_PARAMS = [5, 10, 15, 20, 25, 30]    # 6个固定仓位值


# =============================================================================
# 核心回测函数
# =============================================================================

def run_single_backtest(strategy_class, params, data_path, start_date, end_date,
                        initial_cash=100000, commission=0.0005):
    """
    运行单个回测

    Args:
        strategy_class: 策略类
        params: 策略参数字典
        data_path: 数据文件路径
        start_date: 开始日期 (str, YYYY-MM-DD)
        end_date: 结束日期 (str, YYYY-MM-DD)
        initial_cash: 初始资金 (default: $100,000)
        commission: 单边手续费率 (default: 0.05%)

    Returns:
        dict: 包含Returns, Sharpe, Max DD, Trades等指标
              如果失败返回None
    """
    try:
        # 1. 加载数据
        df = pd.read_csv(data_path, parse_dates=['date'], index_col='date')

        # 2. 筛选日期范围
        df = df[(df.index >= start_date) & (df.index <= end_date)]

        if len(df) < 10:
            return None

        # 3. 创建backtrader数据对象
        data = bt.feeds.PandasData(dataname=df)

        # 4. 创建Cerebro引擎
        cerebro = bt.Cerebro()
        cerebro.adddata(data)

        # 5. 添加策略with参数
        cerebro.addstrategy(strategy_class, **params)

        # 6. 设置初始资金和手续费
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission)

        # 7. 添加分析器
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        # 8. 运行回测
        results = cerebro.run()
        final_value = cerebro.broker.getvalue()

        # 9. 提取结果
        strat = results[0]

        # Returns
        returns_pct = (final_value - initial_cash) / initial_cash * 100

        # Sharpe Ratio
        sharpe_analyzer = strat.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe_analyzer.get('sharperatio', None)
        if sharpe_ratio is None:
            sharpe_ratio = 0.0

        # Maximum Drawdown
        drawdown_analyzer = strat.analyzers.drawdown.get_analysis()
        max_drawdown_pct = drawdown_analyzer.get('max', {}).get('drawdown', 0.0)

        # Trades
        trades_analyzer = strat.analyzers.trades.get_analysis()
        total_trades = trades_analyzer.get('total', {}).get('closed', 0)

        return {
            'returns_pct': round(returns_pct, 2),
            'final_value': round(final_value, 2),
            'sharpe_ratio': round(sharpe_ratio, 3) if sharpe_ratio else 0.0,
            'max_drawdown_pct': round(max_drawdown_pct, 2),
            'total_trades': total_trades,
            'initial_cash': initial_cash,
            'data_points': len(df),
            'start_date': start_date,
            'end_date': end_date
        }

    except FileNotFoundError:
        print(f"      ❌ 数据文件不存在: {data_path}")
        return None
    except Exception as e:
        print(f"      ❌ 回测失败: {str(e)}")
        return None


# =============================================================================
# 实验A: 止损参数扫描
# =============================================================================

def experiment_A_stop_loss_sweep():
    """
    实验A: 止损参数敏感性分析

    测试固定止损金额: $50, $100, $150, $200, $250, $300
    + ATR自适应止损

    仓位固定: 20股
    """
    print("="*80)
    print("实验A: 止损参数敏感性分析")
    print("="*80)
    print(f"测试止损参数: {STOP_LOSS_PARAMS} + ATR自适应")
    print(f"仓位固定: 20股")
    print(f"预计回测数: {(len(STOP_LOSS_PARAMS) + 1) * len(ASSETS) * 2}")
    print("="*80)

    results = {}
    total_tests = (len(STOP_LOSS_PARAMS) + 1) * len(ASSETS) * 2
    completed = 0

    # 测试固定止损
    for stop_loss in STOP_LOSS_PARAMS:
        print(f"\n{'─'*80}")
        print(f"📊 测试止损参数: ${stop_loss}")
        print(f"{'─'*80}")

        results[f'StopLoss_{stop_loss}'] = {}

        for asset_name, asset_info in ASSETS.items():
            print(f"\n  资产: {asset_name} ({asset_info['sector']}, {asset_info['volatility']}波动)")

            # 训练期
            train_result = run_single_backtest(
                Strategy13_FixedStopLoss,
                {'stop_loss_amount': stop_loss, 'position_size': 20},
                asset_info['path'],
                asset_info['train_start'],
                asset_info['train_end']
            )
            completed += 1

            if train_result:
                print(f"    🔵 训练期: {train_result['returns_pct']:+7.2f}% "
                      f"(Sharpe={train_result['sharpe_ratio']:.2f}, "
                      f"Trades={train_result['total_trades']}) "
                      f"[{completed}/{total_tests}]")
            else:
                print(f"    ❌ 训练期失败 [{completed}/{total_tests}]")

            # 测试期
            test_result = run_single_backtest(
                Strategy13_FixedStopLoss,
                {'stop_loss_amount': stop_loss, 'position_size': 20},
                asset_info['path'],
                asset_info['test_start'],
                asset_info['test_end']
            )
            completed += 1

            if test_result:
                print(f"    🟢 测试期: {test_result['returns_pct']:+7.2f}% "
                      f"(Sharpe={test_result['sharpe_ratio']:.2f}, "
                      f"Trades={test_result['total_trades']}) "
                      f"[{completed}/{total_tests}]")
            else:
                print(f"    ❌ 测试期失败 [{completed}/{total_tests}]")

            results[f'StopLoss_{stop_loss}'][asset_name] = {
                'training_period': train_result,
                'testing_period': test_result,
                'volatility': asset_info['volatility'],
                'sector': asset_info['sector']
            }

    # ATR自适应测试
    print(f"\n{'─'*80}")
    print(f"📊 测试自适应止损: ATR×2.0")
    print(f"{'─'*80}")

    results['StopLoss_ATR_Adaptive'] = {}

    for asset_name, asset_info in ASSETS.items():
        print(f"\n  资产: {asset_name}")

        train_result = run_single_backtest(
            Strategy13_ATR_Adaptive,
            {'position_size': 20},
            asset_info['path'],
            asset_info['train_start'],
            asset_info['train_end']
        )
        completed += 1

        if train_result:
            print(f"    🔵 训练期: {train_result['returns_pct']:+7.2f}% [{completed}/{total_tests}]")
        else:
            print(f"    ❌ 训练期失败 [{completed}/{total_tests}]")

        test_result = run_single_backtest(
            Strategy13_ATR_Adaptive,
            {'position_size': 20},
            asset_info['path'],
            asset_info['test_start'],
            asset_info['test_end']
        )
        completed += 1

        if test_result:
            print(f"    🟢 测试期: {test_result['returns_pct']:+7.2f}% [{completed}/{total_tests}]")
        else:
            print(f"    ❌ 测试期失败 [{completed}/{total_tests}]")

        results['StopLoss_ATR_Adaptive'][asset_name] = {
            'training_period': train_result,
            'testing_period': test_result
        }

    print(f"\n{'='*80}")
    print(f"实验A完成: {completed}/{total_tests} 回测")
    print(f"{'='*80}")

    return results


# =============================================================================
# 实验B: 仓位参数扫描
# =============================================================================

def experiment_B_position_size_sweep():
    """
    实验B: 仓位参数敏感性分析

    测试固定仓位: 5股, 10股, 15股, 20股, 25股, 30股
    + 2%风险管理

    止损固定: $200
    """
    print("="*80)
    print("实验B: 仓位参数敏感性分析")
    print("="*80)
    print(f"测试仓位参数: {POSITION_SIZE_PARAMS} + 2%风险管理")
    print(f"止损固定: $200")
    print(f"预计回测数: {(len(POSITION_SIZE_PARAMS) + 1) * len(ASSETS) * 2}")
    print("="*80)

    results = {}
    total_tests = (len(POSITION_SIZE_PARAMS) + 1) * len(ASSETS) * 2
    completed = 0

    # 测试固定仓位
    for position_size in POSITION_SIZE_PARAMS:
        print(f"\n{'─'*80}")
        print(f"📊 测试仓位大小: {position_size}股")
        print(f"{'─'*80}")

        results[f'PositionSize_{position_size}'] = {}

        for asset_name, asset_info in ASSETS.items():
            print(f"\n  资产: {asset_name}")

            train_result = run_single_backtest(
                Strategy13_FixedPositionSize,
                {'stop_loss_amount': 200, 'position_size': position_size},
                asset_info['path'],
                asset_info['train_start'],
                asset_info['train_end']
            )
            completed += 1

            if train_result:
                print(f"    🔵 训练期: {train_result['returns_pct']:+7.2f}% [{completed}/{total_tests}]")
            else:
                print(f"    ❌ 训练期失败 [{completed}/{total_tests}]")

            test_result = run_single_backtest(
                Strategy13_FixedPositionSize,
                {'stop_loss_amount': 200, 'position_size': position_size},
                asset_info['path'],
                asset_info['test_start'],
                asset_info['test_end']
            )
            completed += 1

            if test_result:
                print(f"    🟢 测试期: {test_result['returns_pct']:+7.2f}% [{completed}/{total_tests}]")
            else:
                print(f"    ❌ 测试期失败 [{completed}/{total_tests}]")

            results[f'PositionSize_{position_size}'][asset_name] = {
                'training_period': train_result,
                'testing_period': test_result
            }

    # 2%风险管理测试
    print(f"\n{'─'*80}")
    print(f"📊 测试自适应仓位: 2%风险管理")
    print(f"{'─'*80}")

    results['PositionSize_Risk2Pct'] = {}

    for asset_name, asset_info in ASSETS.items():
        print(f"\n  资产: {asset_name}")

        train_result = run_single_backtest(
            Strategy13_Risk2Pct,
            {},
            asset_info['path'],
            asset_info['train_start'],
            asset_info['train_end']
        )
        completed += 1

        if train_result:
            print(f"    🔵 训练期: {train_result['returns_pct']:+7.2f}% [{completed}/{total_tests}]")
        else:
            print(f"    ❌ 训练期失败 [{completed}/{total_tests}]")

        test_result = run_single_backtest(
            Strategy13_Risk2Pct,
            {},
            asset_info['path'],
            asset_info['test_start'],
            asset_info['test_end']
        )
        completed += 1

        if test_result:
            print(f"    🟢 测试期: {test_result['returns_pct']:+7.2f}% [{completed}/{total_tests}]")
        else:
            print(f"    ❌ 测试期失败 [{completed}/{total_tests}]")

        results['PositionSize_Risk2Pct'][asset_name] = {
            'training_period': train_result,
            'testing_period': test_result
        }

    print(f"\n{'='*80}")
    print(f"实验B完成: {completed}/{total_tests} 回测")
    print(f"{'='*80}")

    return results


# =============================================================================
# 实验C: 完全自适应
# =============================================================================

def experiment_C_fully_adaptive():
    """
    实验C: 完全自适应 (ATR止损 + 2%风险仓位)

    这是论文核心创新的完整实现
    """
    print("="*80)
    print("实验C: 完全自适应 (ATR止损 + 2%风险仓位)")
    print("="*80)
    print(f"预计回测数: {len(ASSETS) * 2}")
    print("="*80)

    results = {}
    total_tests = len(ASSETS) * 2
    completed = 0

    for asset_name, asset_info in ASSETS.items():
        print(f"\n{'─'*80}")
        print(f"📊 资产: {asset_name}")
        print(f"{'─'*80}")

        train_result = run_single_backtest(
            Strategy13_FullyAdaptive,
            {},
            asset_info['path'],
            asset_info['train_start'],
            asset_info['train_end']
        )
        completed += 1

        if train_result:
            print(f"  🔵 训练期: {train_result['returns_pct']:+7.2f}% "
                  f"(Sharpe={train_result['sharpe_ratio']:.2f}, "
                  f"MaxDD={train_result['max_drawdown_pct']:.2f}%, "
                  f"Trades={train_result['total_trades']}) "
                  f"[{completed}/{total_tests}]")
        else:
            print(f"  ❌ 训练期失败 [{completed}/{total_tests}]")

        test_result = run_single_backtest(
            Strategy13_FullyAdaptive,
            {},
            asset_info['path'],
            asset_info['test_start'],
            asset_info['test_end']
        )
        completed += 1

        if test_result:
            print(f"  🟢 测试期: {test_result['returns_pct']:+7.2f}% "
                  f"(Sharpe={test_result['sharpe_ratio']:.2f}, "
                  f"MaxDD={test_result['max_drawdown_pct']:.2f}%, "
                  f"Trades={test_result['total_trades']}) "
                  f"[{completed}/{total_tests}]")
        else:
            print(f"  ❌ 测试期失败 [{completed}/{total_tests}]")

        results[asset_name] = {
            'training_period': train_result,
            'testing_period': test_result,
            'volatility': asset_info['volatility'],
            'sector': asset_info['sector']
        }

    print(f"\n{'='*80}")
    print(f"实验C完成: {completed}/{total_tests} 回测")
    print(f"{'='*80}")

    return results


# =============================================================================
# 主程序入口
# =============================================================================

def main():
    """完整参数敏感性分析流程"""
    print("="*80)
    print("参数敏感性分析实验 - 开始")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"实验设计: ")
    print(f"  - 实验A: 止损参数扫描 (7个参数 × 5资产 × 2期 = 70回测)")
    print(f"  - 实验B: 仓位参数扫描 (7个参数 × 5资产 × 2期 = 70回测)")
    print(f"  - 实验C: 完全自适应 (1个策略 × 5资产 × 2期 = 10回测)")
    print(f"  - 总计: 150个独立回测")
    print(f"预计时间: 3-4小时")
    print("="*80)

    try:
        # 实验A: 止损参数扫描
        print("\n" + "🚀 开始实验A")
        results_A = experiment_A_stop_loss_sweep()

        # 保存中间结果
        output_path_A = Path('/root/autodl-tmp/outputs/sensitivity_A_stop_loss.json')
        output_path_A.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path_A, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'experiment_name': 'Parameter Sensitivity Analysis - Stop Loss',
                    'timestamp': datetime.now().isoformat(),
                    'parameters_tested': STOP_LOSS_PARAMS + ['ATR_Adaptive'],
                    'fixed_position_size': 20,
                    'assets': list(ASSETS.keys())
                },
                'results': results_A
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 实验A结果已保存: {output_path_A}")
        print(f"   文件大小: {output_path_A.stat().st_size / 1024:.1f} KB")

        # 实验B: 仓位参数扫描
        print("\n" + "🚀 开始实验B")
        results_B = experiment_B_position_size_sweep()

        output_path_B = Path('/root/autodl-tmp/outputs/sensitivity_B_position_size.json')
        with open(output_path_B, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'experiment_name': 'Parameter Sensitivity Analysis - Position Size',
                    'timestamp': datetime.now().isoformat(),
                    'parameters_tested': POSITION_SIZE_PARAMS + ['Risk2Pct'],
                    'fixed_stop_loss': 200,
                    'assets': list(ASSETS.keys())
                },
                'results': results_B
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 实验B结果已保存: {output_path_B}")
        print(f"   文件大小: {output_path_B.stat().st_size / 1024:.1f} KB")

        # 实验C: 完全自适应
        print("\n" + "🚀 开始实验C")
        results_C = experiment_C_fully_adaptive()

        output_path_C = Path('/root/autodl-tmp/outputs/sensitivity_C_fully_adaptive.json')
        with open(output_path_C, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'experiment_name': 'Parameter Sensitivity Analysis - Fully Adaptive',
                    'timestamp': datetime.now().isoformat(),
                    'strategy': 'ATR Stop Loss + 2% Risk Position Sizing',
                    'assets': list(ASSETS.keys())
                },
                'results': results_C
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 实验C结果已保存: {output_path_C}")
        print(f"   文件大小: {output_path_C.stat().st_size / 1024:.1f} KB")

        print("\n" + "="*80)
        print("参数敏感性分析实验 - 全部完成")
        print("="*80)
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n输出文件:")
        print(f"  1. {output_path_A}")
        print(f"  2. {output_path_B}")
        print(f"  3. {output_path_C}")
        print("="*80)

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n\n❌ 程序异常: {str(e)}")
        traceback.print_exc()


if __name__ == '__main__':
    main()
