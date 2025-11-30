"""
基线对比实验 - 简化统计分析 (无scipy依赖)
==========================================

功能: 分析baseline_results.json,生成初步统计报告
无需scipy,使用numpy手动计算t检验
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

# 手动实现配对t检验
def paired_t_test_manual(sample1, sample2):
    """
    手动计算配对t检验

    Args:
        sample1, sample2: 两组配对样本

    Returns:
        dict: t统计量, p值(近似), 均值差异等
    """
    sample1 = np.array(sample1)
    sample2 = np.array(sample2)

    # 计算差异
    differences = sample1 - sample2
    n = len(differences)

    if n < 2:
        return None

    # 均值和标准差
    mean_diff = np.mean(differences)
    std_diff = np.std(differences, ddof=1)

    # t统计量
    if std_diff == 0:
        t_stat = 0
    else:
        t_stat = mean_diff / (std_diff / np.sqrt(n))

    # 自由度
    df = n - 1

    # p值近似 (使用简化的t分布表)
    # 对于df>=10, 临界值约: p=0.05->t=2.0, p=0.01->t=2.7
    abs_t = abs(t_stat)
    if abs_t < 1.5:
        p_approx = ">0.10"
        sig_level = "Not Significant"
    elif abs_t < 2.0:
        p_approx = "0.05-0.10"
        sig_level = "Marginally Significant"
    elif abs_t < 2.7:
        p_approx = "<0.05"
        sig_level = "** Significant"
    else:
        p_approx = "<0.01"
        sig_level = "*** Highly Significant"

    return {
        't_statistic': t_stat,
        'p_value_approx': p_approx,
        'mean_difference': mean_diff,
        'std_difference': std_diff,
        'sample1_mean': np.mean(sample1),
        'sample2_mean': np.mean(sample2),
        'sample_size': n,
        'significance': sig_level
    }


def analyze_baseline_results(json_path):
    """分析baseline_results.json"""

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']
    metadata = data.get('metadata', {})

    print("="*80)
    print("基线对比实验 - 统计分析报告 (简化版)")
    print("="*80)
    print(f"生成时间: 2025-11-27")
    print(f"实验时间: {metadata.get('timestamp', 'N/A')}")
    print(f"总回测数: {metadata.get('total_backtests', 'N/A')}")
    print(f"成功率: {metadata.get('successful_backtests', 0)}/{metadata.get('total_backtests', 0)}")
    print("="*80)

    # 提取LLM策略和基线策略
    llm_strategy = 'LLM_Adaptive'
    baselines = [s for s in results.keys() if s != llm_strategy]

    # 分析训练期
    print("\n## 训练期 (2018-2023) 分析\n")

    for period_name, period_key in [('训练期', 'training_period'), ('测试期', 'testing_period')]:
        print(f"\n{'='*80}")
        print(f"## {period_name} 分析")
        print(f"{'='*80}\n")

        # 1. 收益率对比表
        print(f"### 1. 平均收益率对比\n")

        strategy_stats = {}
        for strategy in [llm_strategy] + baselines:
            returns_list = []
            for asset in results[strategy]:
                result = results[strategy][asset][period_key]
                if result is not None:
                    returns_list.append(result['returns_pct'])

            if returns_list:
                avg_return = np.mean(returns_list)
                success_rate = sum(1 for r in returns_list if r > 0) / len(returns_list) * 100
                strategy_stats[strategy] = {
                    'avg_return': avg_return,
                    'success_rate': success_rate,
                    'returns_list': returns_list
                }

        # 打印表格
        print(f"| 策略                | 平均收益 | 成功率 | 样本量 |")
        print(f"|---------------------|----------|--------|--------|")
        for strategy, stats in strategy_stats.items():
            marker = " *" if strategy == llm_strategy else "  "
            print(f"| {strategy:19s}{marker}| {stats['avg_return']:+7.2f}% | {stats['success_rate']:5.1f}% | {len(stats['returns_list']):6d} |")

        print()

        # 2. 配对t检验
        print(f"### 2. 统计检验结果\n")

        for baseline in baselines:
            print(f"#### {llm_strategy} vs {baseline}\n")

            # 提取配对数据
            llm_returns = []
            baseline_returns = []

            for asset in results[llm_strategy]:
                llm_result = results[llm_strategy][asset][period_key]
                baseline_result = results[baseline][asset][period_key]

                if llm_result is not None and baseline_result is not None:
                    llm_returns.append(llm_result['returns_pct'])
                    baseline_returns.append(baseline_result['returns_pct'])

            if len(llm_returns) >= 2:
                test_result = paired_t_test_manual(llm_returns, baseline_returns)

                print(f"**样本量**: N = {test_result['sample_size']}\n")
                print(f"**{baseline}**: 平均收益 {test_result['sample2_mean']:+.2f}%")
                print(f"**{llm_strategy}**: 平均收益 {test_result['sample1_mean']:+.2f}%\n")
                print(f"**差异**: {test_result['mean_difference']:+.2f} percentage points\n")
                print(f"**配对t检验**:")
                print(f"- t统计量: {test_result['t_statistic']:.3f}")
                print(f"- p值(近似): {test_result['p_value_approx']}")
                print(f"- 显著性: {test_result['significance']}\n")

                if "Significant" in test_result['significance'] and "Not" not in test_result['significance']:
                    print(f">>> **结论**: {llm_strategy}显著优于{baseline}\n")
                else:
                    print(f">>> **结论**: 差异不显著\n")
            else:
                print(f">>> 数据不足,无法进行检验\n")

            print("---\n")

    print("\n" + "="*80)
    print("分析完成")
    print("="*80)
    print("\n**注意**: 此为简化版分析,p值为近似值。")
    print("完整版统计分析需要scipy库支持。")
    print("="*80)


if __name__ == '__main__':
    # 分析baseline_results.json
    json_path = Path('C:/Users/Xing/Desktop/baseline_results.json')

    if not json_path.exists():
        print(f"ERROR: 文件不存在: {json_path}")
    else:
        analyze_baseline_results(json_path)
