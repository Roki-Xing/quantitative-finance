"""
基线对比实验 - 统计分析脚本
=============================

功能: 分析96个回测结果,生成统计检验报告
作者: Claude Code AI Assistant
日期: 2025-11-27
Python: 3.8+

分析内容:
1. 配对t检验 (Paired t-test): LLM vs 每个基线
2. 对比表格生成
3. 显著性分析
4. 可视化图表

输入: baseline_comparison_results.json (由test_all_baselines.py生成)
输出: 统计检验报告(Markdown) + 图表(PNG)
"""

import json
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import sys

# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


# =============================================================================
# 数据加载
# =============================================================================

def load_results(json_path):
    """
    加载实验结果JSON文件

    Args:
        json_path: JSON文件路径

    Returns:
        dict: 完整的实验结果
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 成功加载结果文件: {json_path}")
        print(f"   策略数: {len(data['results'])}")
        print(f"   元数据: {data.get('metadata', {}).get('timestamp', 'N/A')}")
        return data
    except FileNotFoundError:
        print(f"❌ 文件不存在: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        sys.exit(1)


# =============================================================================
# 配对t检验
# =============================================================================

def paired_t_test(results_dict, baseline_name, ours_name='LLM_Adaptive',
                  period='training_period', metric='returns_pct'):
    """
    对两个策略进行配对t检验

    Args:
        results_dict: 完整结果字典
        baseline_name: 基线策略名称 (e.g., 'Buy_and_Hold')
        ours_name: 我们的策略名称 (default: 'LLM_Adaptive')
        period: 'training_period' 或 'testing_period'
        metric: 要比较的指标 (default: 'returns_pct')

    Returns:
        dict: 包含t统计量、p值、均值差异等
    """
    baseline_values = []
    ours_values = []
    assets = []

    # 提取所有资产的指标值
    for asset_name in results_dict[baseline_name].keys():
        baseline_result = results_dict[baseline_name][asset_name][period]
        ours_result = results_dict[ours_name][asset_name][period]

        # 跳过失败的回测 (None)
        if baseline_result is None or ours_result is None:
            continue

        baseline_val = baseline_result[metric]
        ours_val = ours_result[metric]

        baseline_values.append(baseline_val)
        ours_values.append(ours_val)
        assets.append(asset_name)

    if len(baseline_values) == 0:
        return None

    baseline_values = np.array(baseline_values)
    ours_values = np.array(ours_values)

    # 配对t检验
    t_stat, p_value = stats.ttest_rel(ours_values, baseline_values)

    # 计算差异
    differences = ours_values - baseline_values
    mean_diff = np.mean(differences)
    std_diff = np.std(differences, ddof=1)

    # 计算均值
    baseline_mean = np.mean(baseline_values)
    ours_mean = np.mean(ours_values)

    # 计算成功率 (收益>0的资产比例)
    baseline_success_rate = np.sum(baseline_values > 0) / len(baseline_values) * 100
    ours_success_rate = np.sum(ours_values > 0) / len(ours_values) * 100

    # 判定显著性
    if p_value < 0.01:
        significance = 'Highly Significant (p<0.01)'
        sig_level = '⭐⭐⭐'
    elif p_value < 0.05:
        significance = 'Significant (p<0.05)'
        sig_level = '⭐⭐'
    elif p_value < 0.10:
        significance = 'Marginally Significant (p<0.10)'
        sig_level = '⭐'
    else:
        significance = 'Not Significant (p≥0.10)'
        sig_level = '❌'

    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'mean_difference': mean_diff,
        'std_difference': std_diff,
        'baseline_mean': baseline_mean,
        'ours_mean': ours_mean,
        'baseline_success_rate': baseline_success_rate,
        'ours_success_rate': ours_success_rate,
        'sample_size': len(baseline_values),
        'significance': significance,
        'sig_level': sig_level,
        'assets': assets,
        'baseline_values': baseline_values.tolist(),
        'ours_values': ours_values.tolist(),
        'differences': differences.tolist()
    }


# =============================================================================
# 对比表格生成
# =============================================================================

def generate_comparison_table(results_dict, period='training_period',
                               metric='returns_pct'):
    """
    生成完整对比表格

    Args:
        results_dict: 完整结果字典
        period: 'training_period' 或 'testing_period'
        metric: 要显示的指标

    Returns:
        pd.DataFrame: 对比表格
    """
    strategies = list(results_dict.keys())
    assets = list(results_dict[strategies[0]].keys())

    # 创建DataFrame
    rows = []
    for asset in assets:
        row = {'Asset': asset}
        for strategy in strategies:
            result = results_dict[strategy][asset][period]
            if result is None:
                row[strategy] = 'FAILED'
            else:
                value = result[metric]
                if metric == 'returns_pct':
                    row[strategy] = f"{value:+.2f}%"
                elif metric == 'sharpe_ratio':
                    row[strategy] = f"{value:.3f}"
                elif metric == 'max_drawdown_pct':
                    row[strategy] = f"{value:.2f}%"
                else:
                    row[strategy] = str(value)
        rows.append(row)

    # 添加平均值行
    avg_row = {'Asset': '**Average**'}
    for strategy in strategies:
        values = []
        for asset in assets:
            result = results_dict[strategy][asset][period]
            if result is not None:
                values.append(result[metric])
        if values:
            avg_val = np.mean(values)
            if metric == 'returns_pct':
                avg_row[strategy] = f"**{avg_val:+.2f}%**"
            elif metric == 'sharpe_ratio':
                avg_row[strategy] = f"**{avg_val:.3f}**"
            elif metric == 'max_drawdown_pct':
                avg_row[strategy] = f"**{avg_val:.2f}%**"
            else:
                avg_row[strategy] = f"**{avg_val:.1f}**"
        else:
            avg_row[strategy] = 'N/A'
    rows.append(avg_row)

    # 添加成功率行
    success_row = {'Asset': '**Success Rate**'}
    for strategy in strategies:
        values = []
        for asset in assets:
            result = results_dict[strategy][asset][period]
            if result is not None and metric == 'returns_pct':
                values.append(result[metric])
        if values:
            success_rate = np.sum(np.array(values) > 0) / len(values) * 100
            success_row[strategy] = f"**{success_rate:.1f}%**"
        else:
            success_row[strategy] = 'N/A'
    rows.append(success_row)

    df = pd.DataFrame(rows)
    return df


# =============================================================================
# Markdown报告生成
# =============================================================================

def generate_markdown_report(data, output_path='statistical_report.md'):
    """
    生成完整的Markdown统计报告

    Args:
        data: 实验结果字典
        output_path: 输出文件路径

    Returns:
        str: 报告内容
    """
    results = data['results']
    metadata = data.get('metadata', {})

    # 确定LLM策略名称
    llm_strategy = 'LLM_Adaptive' if 'LLM_Adaptive' in results else None
    if llm_strategy is None:
        print("⚠️ 未找到LLM_Adaptive策略,无法生成对比报告")
        return None

    baselines = [s for s in results.keys() if s != llm_strategy]

    # 开始生成报告
    lines = []
    lines.append("# 基线对比实验 - 统计分析报告\n")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**实验时间**: {metadata.get('timestamp', 'N/A')}\n")
    lines.append(f"**策略数量**: {len(results)}\n")
    lines.append(f"**资产数量**: {len(list(results.values())[0])}\n")
    lines.append(f"**总回测数**: {metadata.get('total_backtests', 'N/A')}\n")
    lines.append(f"**成功率**: {metadata.get('successful_backtests', 0)}/{metadata.get('total_backtests', 0)}\n")
    lines.append("\n---\n\n")

    # 对每个时期进行分析
    for period, period_name in [('training_period', '训练期'), ('testing_period', '测试期(样本外)')]:
        lines.append(f"## {period_name} 分析\n\n")

        # 1. 收益率对比表
        lines.append(f"### 1. 收益率对比表\n\n")
        table = generate_comparison_table(results, period, 'returns_pct')
        lines.append(table.to_markdown(index=False))
        lines.append("\n\n")

        # 2. Sharpe Ratio对比表
        lines.append(f"### 2. Sharpe Ratio对比表\n\n")
        table = generate_comparison_table(results, period, 'sharpe_ratio')
        lines.append(table.to_markdown(index=False))
        lines.append("\n\n")

        # 3. 最大回撤对比表
        lines.append(f"### 3. 最大回撤对比表\n\n")
        table = generate_comparison_table(results, period, 'max_drawdown_pct')
        lines.append(table.to_markdown(index=False))
        lines.append("\n\n")

        # 4. 统计检验
        lines.append(f"### 4. 统计检验结果\n\n")

        for baseline in baselines:
            lines.append(f"#### {llm_strategy} vs {baseline}\n\n")

            test_result = paired_t_test(results, baseline, llm_strategy, period)

            if test_result is None:
                lines.append("⚠️ 数据不足,无法进行检验\n\n")
                continue

            lines.append(f"**样本量**: N = {test_result['sample_size']}\n\n")

            lines.append(f"**{baseline}**:\n")
            lines.append(f"- 平均收益: {test_result['baseline_mean']:+.2f}%\n")
            lines.append(f"- 成功率: {test_result['baseline_success_rate']:.1f}%\n\n")

            lines.append(f"**{llm_strategy}**:\n")
            lines.append(f"- 平均收益: {test_result['ours_mean']:+.2f}%\n")
            lines.append(f"- 成功率: {test_result['ours_success_rate']:.1f}%\n\n")

            lines.append(f"**差异**:\n")
            lines.append(f"- 收益差距: {test_result['mean_difference']:+.2f} percentage points\n")
            lines.append(f"- 成功率提升: {test_result['ours_success_rate'] - test_result['baseline_success_rate']:+.1f}%\n\n")

            lines.append(f"**配对t检验**:\n")
            lines.append(f"- t统计量: {test_result['t_statistic']:.3f}\n")
            lines.append(f"- p值: {test_result['p_value']:.4f}\n")
            lines.append(f"- 显著性: {test_result['significance']} {test_result['sig_level']}\n\n")

            if test_result['p_value'] < 0.05:
                lines.append(f"✅ **结论**: {llm_strategy}显著优于{baseline} (p<0.05)\n\n")
            elif test_result['p_value'] < 0.10:
                lines.append(f"⚠️ **结论**: {llm_strategy}边缘显著优于{baseline} (p<0.10)\n\n")
            else:
                lines.append(f"❌ **结论**: 差异不显著 (p={test_result['p_value']:.3f})\n\n")

            lines.append("---\n\n")

        lines.append("\n")

    # 总结
    lines.append("## 总结\n\n")
    lines.append(f"本报告基于{metadata.get('total_backtests', 'N/A')}个独立回测实验,")
    lines.append(f"对比了{len(results)}个策略在{len(list(results.values())[0])}个资产上的表现。\n\n")
    lines.append("详细统计检验结果见上文各节。\n\n")
    lines.append("---\n\n")
    lines.append("*Report generated by statistical_analysis.py*\n")

    report_content = ''.join(lines)

    # 保存报告
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"✅ 统计报告已保存: {output_path}")
    print(f"   文件大小: {Path(output_path).stat().st_size / 1024:.1f} KB")

    return report_content


# =============================================================================
# 可视化图表
# =============================================================================

def plot_comparison_charts(data, output_dir='charts'):
    """
    生成对比图表

    Args:
        data: 实验结果字典
        output_dir: 图表输出目录

    Returns:
        list: 生成的图表文件路径列表
    """
    results = data['results']
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    chart_files = []

    # 1. 训练期收益率对比柱状图
    fig, ax = plt.subplots(figsize=(14, 8))

    strategies = list(results.keys())
    assets = list(results[strategies[0]].keys())

    returns_data = []
    for strategy in strategies:
        strategy_returns = []
        for asset in assets:
            result = results[strategy][asset]['training_period']
            if result is not None:
                strategy_returns.append(result['returns_pct'])
            else:
                strategy_returns.append(0)
        returns_data.append(strategy_returns)

    x = np.arange(len(assets))
    width = 0.2
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']

    for i, (strategy, returns) in enumerate(zip(strategies, returns_data)):
        offset = width * (i - len(strategies)/2 + 0.5)
        ax.bar(x + offset, returns, width, label=strategy, color=colors[i % len(colors)])

    ax.set_xlabel('Assets', fontsize=12)
    ax.set_ylabel('Returns (%)', fontsize=12)
    ax.set_title('Training Period Returns Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([a.split('_')[0] for a in assets], rotation=45, ha='right')
    ax.legend(loc='upper left')
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    chart_path = output_dir / 'training_returns_comparison.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    chart_files.append(str(chart_path))
    print(f"✅ 图表已保存: {chart_path}")

    # 2. 测试期收益率对比柱状图
    fig, ax = plt.subplots(figsize=(14, 8))

    returns_data_test = []
    for strategy in strategies:
        strategy_returns = []
        for asset in assets:
            result = results[strategy][asset]['testing_period']
            if result is not None:
                strategy_returns.append(result['returns_pct'])
            else:
                strategy_returns.append(0)
        returns_data_test.append(strategy_returns)

    for i, (strategy, returns) in enumerate(zip(strategies, returns_data_test)):
        offset = width * (i - len(strategies)/2 + 0.5)
        ax.bar(x + offset, returns, width, label=strategy, color=colors[i % len(colors)])

    ax.set_xlabel('Assets', fontsize=12)
    ax.set_ylabel('Returns (%)', fontsize=12)
    ax.set_title('Testing Period Returns Comparison (Out-of-Sample)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([a.split('_')[0] for a in assets], rotation=45, ha='right')
    ax.legend(loc='upper left')
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    chart_path = output_dir / 'testing_returns_comparison.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    chart_files.append(str(chart_path))
    print(f"✅ 图表已保存: {chart_path}")

    # 3. 箱线图 (训练期)
    fig, ax = plt.subplots(figsize=(10, 6))

    box_data = []
    box_labels = []
    for strategy in strategies:
        strategy_returns = []
        for asset in assets:
            result = results[strategy][asset]['training_period']
            if result is not None:
                strategy_returns.append(result['returns_pct'])
        if strategy_returns:
            box_data.append(strategy_returns)
            box_labels.append(strategy)

    bp = ax.boxplot(box_data, labels=box_labels, patch_artist=True,
                     showmeans=True, meanline=True)

    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.set_ylabel('Returns (%)', fontsize=12)
    ax.set_title('Training Period Returns Distribution', fontsize=14, fontweight='bold')
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    chart_path = output_dir / 'training_returns_boxplot.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    chart_files.append(str(chart_path))
    print(f"✅ 图表已保存: {chart_path}")

    return chart_files


# =============================================================================
# 主程序入口
# =============================================================================

def main():
    """完整统计分析流程"""
    import argparse

    parser = argparse.ArgumentParser(description='基线对比实验统计分析')
    parser.add_argument('--input', type=str,
                        default='/root/autodl-tmp/outputs/baseline_comparison_results.json',
                        help='输入JSON文件路径')
    parser.add_argument('--output', type=str,
                        default='/root/autodl-tmp/outputs/statistical_report.md',
                        help='输出Markdown报告路径')
    parser.add_argument('--charts-dir', type=str,
                        default='/root/autodl-tmp/outputs/charts',
                        help='图表输出目录')
    parser.add_argument('--no-charts', action='store_true',
                        help='不生成图表 (仅报告)')

    args = parser.parse_args()

    print("=" * 80)
    print("基线对比实验 - 统计分析")
    print("=" * 80)

    # 1. 加载数据
    print("\n📂 加载实验结果...")
    data = load_results(args.input)

    # 2. 生成Markdown报告
    print("\n📊 生成统计报告...")
    report = generate_markdown_report(data, args.output)

    if report is None:
        print("❌ 报告生成失败")
        return

    # 3. 生成图表
    if not args.no_charts:
        print("\n📈 生成对比图表...")
        try:
            chart_files = plot_comparison_charts(data, args.charts_dir)
            print(f"\n✅ 共生成{len(chart_files)}个图表")
        except Exception as e:
            print(f"⚠️ 图表生成失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("分析完成!")
    print("=" * 80)
    print(f"📄 统计报告: {args.output}")
    if not args.no_charts:
        print(f"📊 图表目录: {args.charts_dir}")
    print("=" * 80)


if __name__ == '__main__':
    main()
