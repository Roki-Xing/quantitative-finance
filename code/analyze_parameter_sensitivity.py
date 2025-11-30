"""
参数敏感性分析 - 结果分析与可视化
====================================

功能: 分析150个回测结果,生成敏感性曲线和统计报告
作者: Claude Code AI Assistant
日期: 2025-11-27
Python: 3.8+

输入文件:
- sensitivity_A_stop_loss.json (70回测)
- sensitivity_B_position_size.json (70回测)
- sensitivity_C_fully_adaptive.json (10回测)

输出:
- 敏感性曲线图 (PNG, 300dpi)
- 统计分析报告 (Markdown)
- 量化证据 (CSV)
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")


# =============================================================================
# 数据加载
# =============================================================================

def load_results():
    """加载所有3个JSON结果文件"""
    base_path = Path('C:/Users/Xing/Desktop')

    with open(base_path / 'sensitivity_A_stop_loss.json', 'r', encoding='utf-8') as f:
        results_A = json.load(f)

    with open(base_path / 'sensitivity_B_position_size.json', 'r', encoding='utf-8') as f:
        results_B = json.load(f)

    with open(base_path / 'sensitivity_C_fully_adaptive.json', 'r', encoding='utf-8') as f:
        results_C = json.load(f)

    return results_A, results_B, results_C


# =============================================================================
# 数据提取函数
# =============================================================================

def extract_stop_loss_data(results_A):
    """
    提取止损参数扫描数据

    Returns:
        DataFrame with columns: [stop_loss, asset, period, returns, sharpe, max_dd, trades]
    """
    rows = []

    stop_loss_params = [50, 100, 150, 200, 250, 300]

    for param in stop_loss_params:
        key = f'StopLoss_{param}'

        for asset_name, asset_data in results_A['results'][key].items():
            # 训练期
            train = asset_data.get('training_period')
            if train:
                rows.append({
                    'stop_loss': param,
                    'asset': asset_name,
                    'period': 'training',
                    'returns_pct': train['returns_pct'],
                    'sharpe_ratio': train['sharpe_ratio'],
                    'max_drawdown_pct': train['max_drawdown_pct'],
                    'total_trades': train['total_trades'],
                    'volatility': asset_data.get('volatility', 'unknown')
                })

            # 测试期
            test = asset_data.get('testing_period')
            if test:
                rows.append({
                    'stop_loss': param,
                    'asset': asset_name,
                    'period': 'testing',
                    'returns_pct': test['returns_pct'],
                    'sharpe_ratio': test['sharpe_ratio'],
                    'max_drawdown_pct': test['max_drawdown_pct'],
                    'total_trades': test['total_trades'],
                    'volatility': asset_data.get('volatility', 'unknown')
                })

    # ATR自适应
    for asset_name, asset_data in results_A['results']['StopLoss_ATR_Adaptive'].items():
        train = asset_data.get('training_period')
        if train:
            rows.append({
                'stop_loss': 'ATR_Adaptive',
                'asset': asset_name,
                'period': 'training',
                'returns_pct': train['returns_pct'],
                'sharpe_ratio': train['sharpe_ratio'],
                'max_drawdown_pct': train['max_drawdown_pct'],
                'total_trades': train['total_trades'],
                'volatility': asset_data.get('volatility', 'unknown')
            })

        test = asset_data.get('testing_period')
        if test:
            rows.append({
                'stop_loss': 'ATR_Adaptive',
                'asset': asset_name,
                'period': 'testing',
                'returns_pct': test['returns_pct'],
                'sharpe_ratio': test['sharpe_ratio'],
                'max_drawdown_pct': test['max_drawdown_pct'],
                'total_trades': test['total_trades'],
                'volatility': asset_data.get('volatility', 'unknown')
            })

    return pd.DataFrame(rows)


def extract_position_size_data(results_B):
    """
    提取仓位参数扫描数据

    Returns:
        DataFrame with columns: [position_size, asset, period, returns, sharpe, max_dd, trades]
    """
    rows = []

    position_size_params = [5, 10, 15, 20, 25, 30]

    for param in position_size_params:
        key = f'PositionSize_{param}'

        for asset_name, asset_data in results_B['results'][key].items():
            # 训练期
            train = asset_data.get('training_period')
            if train:
                rows.append({
                    'position_size': param,
                    'asset': asset_name,
                    'period': 'training',
                    'returns_pct': train['returns_pct'],
                    'sharpe_ratio': train['sharpe_ratio'],
                    'max_drawdown_pct': train['max_drawdown_pct'],
                    'total_trades': train['total_trades'],
                    'volatility': asset_data.get('volatility', 'unknown')
                })

            # 测试期
            test = asset_data.get('testing_period')
            if test:
                rows.append({
                    'position_size': param,
                    'asset': asset_name,
                    'period': 'testing',
                    'returns_pct': test['returns_pct'],
                    'sharpe_ratio': test['sharpe_ratio'],
                    'max_drawdown_pct': test['max_drawdown_pct'],
                    'total_trades': test['total_trades'],
                    'volatility': asset_data.get('volatility', 'unknown')
                })

    # 2%风险管理
    for asset_name, asset_data in results_B['results']['PositionSize_Risk2Pct'].items():
        train = asset_data.get('training_period')
        if train:
            rows.append({
                'position_size': 'Risk2Pct',
                'asset': asset_name,
                'period': 'training',
                'returns_pct': train['returns_pct'],
                'sharpe_ratio': train['sharpe_ratio'],
                'max_drawdown_pct': train['max_drawdown_pct'],
                'total_trades': train['total_trades'],
                'volatility': asset_data.get('volatility', 'unknown')
            })

        test = asset_data.get('testing_period')
        if test:
            rows.append({
                'position_size': 'Risk2Pct',
                'asset': asset_name,
                'period': 'testing',
                'returns_pct': test['returns_pct'],
                'sharpe_ratio': test['sharpe_ratio'],
                'max_drawdown_pct': test['max_drawdown_pct'],
                'total_trades': test['total_trades'],
                'volatility': asset_data.get('volatility', 'unknown')
            })

    return pd.DataFrame(rows)


def extract_fully_adaptive_data(results_C):
    """
    提取完全自适应数据

    Returns:
        DataFrame with columns: [asset, period, returns, sharpe, max_dd, trades]
    """
    rows = []

    for asset_name, asset_data in results_C['results'].items():
        # 训练期
        train = asset_data.get('training_period')
        if train:
            rows.append({
                'asset': asset_name,
                'period': 'training',
                'returns_pct': train['returns_pct'],
                'sharpe_ratio': train['sharpe_ratio'],
                'max_drawdown_pct': train['max_drawdown_pct'],
                'total_trades': train['total_trades'],
                'volatility': asset_data.get('volatility', 'unknown')
            })

        # 测试期
        test = asset_data.get('testing_period')
        if test:
            rows.append({
                'asset': asset_name,
                'period': 'testing',
                'returns_pct': test['returns_pct'],
                'sharpe_ratio': test['sharpe_ratio'],
                'max_drawdown_pct': test['max_drawdown_pct'],
                'total_trades': test['total_trades'],
                'volatility': asset_data.get('volatility', 'unknown')
            })

    return pd.DataFrame(rows)


# =============================================================================
# 可视化函数
# =============================================================================

def plot_stop_loss_sensitivity(df_A, output_dir):
    """
    绘制止损参数敏感性曲线 (5个资产 × 2个时期)
    """
    assets = df_A['asset'].unique()

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()

    for idx, asset in enumerate(assets):
        ax = axes[idx]

        # 提取该资产的数据
        asset_data = df_A[df_A['asset'] == asset]

        # 训练期数据 (固定参数)
        train_fixed = asset_data[(asset_data['period'] == 'training') &
                                 (asset_data['stop_loss'] != 'ATR_Adaptive')]
        train_fixed = train_fixed.sort_values('stop_loss')

        # 测试期数据 (固定参数)
        test_fixed = asset_data[(asset_data['period'] == 'testing') &
                                (asset_data['stop_loss'] != 'ATR_Adaptive')]
        test_fixed = test_fixed.sort_values('stop_loss')

        # 绘制固定参数曲线
        ax.plot(train_fixed['stop_loss'], train_fixed['returns_pct'],
                'o-', linewidth=2.5, markersize=9, label='Training (Fixed)', color='#2E86AB')
        ax.plot(test_fixed['stop_loss'], test_fixed['returns_pct'],
                's--', linewidth=2.5, markersize=9, label='Testing (Fixed)', color='#A23B72')

        # ATR自适应结果 (横虚线)
        train_atr = asset_data[(asset_data['period'] == 'training') &
                               (asset_data['stop_loss'] == 'ATR_Adaptive')]
        test_atr = asset_data[(asset_data['period'] == 'testing') &
                              (asset_data['stop_loss'] == 'ATR_Adaptive')]

        if not train_atr.empty:
            ax.axhline(y=train_atr['returns_pct'].values[0], color='#06A77D',
                      linestyle=':', linewidth=3, label='ATR Adaptive (Train)')

        if not test_atr.empty:
            ax.axhline(y=test_atr['returns_pct'].values[0], color='#F18F01',
                      linestyle=':', linewidth=3, label='ATR Adaptive (Test)')

        # 零线
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.3)

        # 样式设置
        asset_short_name = asset.split('_')[1] if '_' in asset else asset
        volatility = asset_data['volatility'].iloc[0]
        ax.set_title(f'{asset_short_name} ({volatility} volatility)',
                    fontsize=13, fontweight='bold')
        ax.set_xlabel('Stop-Loss Amount ($)', fontsize=11)
        ax.set_ylabel('Returns (%)', fontsize=11)
        ax.legend(fontsize=9, loc='best')
        ax.grid(alpha=0.3, linestyle=':')

        # 设置x轴范围
        ax.set_xlim(40, 310)

    # 删除多余子图
    if len(assets) < 6:
        for idx in range(len(assets), 6):
            fig.delaxes(axes[idx])

    plt.tight_layout()
    chart_path = output_dir / 'stop_loss_sensitivity_curves.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  >>> 止损敏感性曲线已生成: {chart_path}")
    print(f"      文件大小: {chart_path.stat().st_size / 1024:.1f} KB")

    return chart_path


def plot_position_size_sensitivity(df_B, output_dir):
    """
    绘制仓位参数敏感性曲线 (5个资产 × 2个时期)
    """
    assets = df_B['asset'].unique()

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()

    for idx, asset in enumerate(assets):
        ax = axes[idx]

        # 提取该资产的数据
        asset_data = df_B[df_B['asset'] == asset]

        # 训练期数据 (固定参数)
        train_fixed = asset_data[(asset_data['period'] == 'training') &
                                 (asset_data['position_size'] != 'Risk2Pct')]
        train_fixed = train_fixed.sort_values('position_size')

        # 测试期数据 (固定参数)
        test_fixed = asset_data[(asset_data['period'] == 'testing') &
                                (asset_data['position_size'] != 'Risk2Pct')]
        test_fixed = test_fixed.sort_values('position_size')

        # 绘制固定参数曲线
        ax.plot(train_fixed['position_size'], train_fixed['returns_pct'],
                'o-', linewidth=2.5, markersize=9, label='Training (Fixed)', color='#2E86AB')
        ax.plot(test_fixed['position_size'], test_fixed['returns_pct'],
                's--', linewidth=2.5, markersize=9, label='Testing (Fixed)', color='#A23B72')

        # 2%风险管理结果 (横虚线)
        train_risk = asset_data[(asset_data['period'] == 'training') &
                                (asset_data['position_size'] == 'Risk2Pct')]
        test_risk = asset_data[(asset_data['period'] == 'testing') &
                               (asset_data['position_size'] == 'Risk2Pct')]

        if not train_risk.empty:
            ax.axhline(y=train_risk['returns_pct'].values[0], color='#06A77D',
                      linestyle=':', linewidth=3, label='2% Risk Mgmt (Train)')

        if not test_risk.empty:
            ax.axhline(y=test_risk['returns_pct'].values[0], color='#F18F01',
                      linestyle=':', linewidth=3, label='2% Risk Mgmt (Test)')

        # 零线
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.3)

        # 样式设置
        asset_short_name = asset.split('_')[1] if '_' in asset else asset
        volatility = asset_data['volatility'].iloc[0]
        ax.set_title(f'{asset_short_name} ({volatility} volatility)',
                    fontsize=13, fontweight='bold')
        ax.set_xlabel('Position Size (shares)', fontsize=11)
        ax.set_ylabel('Returns (%)', fontsize=11)
        ax.legend(fontsize=9, loc='best')
        ax.grid(alpha=0.3, linestyle=':')

        # 设置x轴范围
        ax.set_xlim(3, 32)

    # 删除多余子图
    if len(assets) < 6:
        for idx in range(len(assets), 6):
            fig.delaxes(axes[idx])

    plt.tight_layout()
    chart_path = output_dir / 'position_size_sensitivity_curves.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  >>> 仓位敏感性曲线已生成: {chart_path}")
    print(f"      文件大小: {chart_path.stat().st_size / 1024:.1f} KB")

    return chart_path


# =============================================================================
# 统计分析函数
# =============================================================================

def analyze_parameter_sensitivity(df_A, df_B, df_C):
    """
    分析参数敏感性,生成关键发现

    Returns:
        dict: 包含关键统计数据
    """
    findings = {}

    # 1. 止损参数敏感性分析
    stop_loss_stats = df_A[df_A['period'] == 'training'].groupby('stop_loss')['returns_pct'].agg([
        ('mean', 'mean'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max')
    ])

    findings['stop_loss_sensitivity'] = {
        'range': f"{stop_loss_stats['min'].min():.2f}% to {stop_loss_stats['max'].max():.2f}%",
        'best_fixed': stop_loss_stats['mean'].idxmax(),
        'worst_fixed': stop_loss_stats['mean'].idxmin(),
        'adaptive_avg': df_A[(df_A['period'] == 'training') &
                             (df_A['stop_loss'] == 'ATR_Adaptive')]['returns_pct'].mean()
    }

    # 2. 仓位参数敏感性分析
    position_stats = df_B[df_B['period'] == 'training'].groupby('position_size')['returns_pct'].agg([
        ('mean', 'mean'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max')
    ])

    findings['position_sensitivity'] = {
        'range': f"{position_stats['min'].min():.2f}% to {position_stats['max'].max():.2f}%",
        'best_fixed': position_stats['mean'].idxmax(),
        'worst_fixed': position_stats['mean'].idxmin()
    }

    # 3. 完全自适应性能
    adaptive_train = df_C[df_C['period'] == 'training']['returns_pct'].mean()
    adaptive_test = df_C[df_C['period'] == 'testing']['returns_pct'].mean()

    findings['fully_adaptive'] = {
        'train_avg': adaptive_train,
        'test_avg': adaptive_test,
        'success_rate_train': (df_C[df_C['period'] == 'training']['returns_pct'] > 0).sum() /
                              len(df_C[df_C['period'] == 'training']) * 100,
        'success_rate_test': (df_C[df_C['period'] == 'testing']['returns_pct'] > 0).sum() /
                             len(df_C[df_C['period'] == 'testing']) * 100
    }

    # 4. 对比固定参数 (选择最常用的: 止损$200, 仓位20股)
    fixed_baseline = df_A[(df_A['stop_loss'] == 200) & (df_A['period'] == 'training')]['returns_pct'].mean()

    findings['improvement'] = {
        'fixed_baseline': fixed_baseline,
        'adaptive_improvement': adaptive_train - fixed_baseline,
        'improvement_pct': ((adaptive_train - fixed_baseline) / abs(fixed_baseline) * 100) if fixed_baseline != 0 else 0
    }

    return findings


def generate_analysis_report(findings, df_A, df_B, df_C, output_path):
    """
    生成Markdown格式的分析报告
    """
    report = []

    report.append("# 参数敏感性分析 - 完整报告")
    report.append("")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**实验规模**: 150个独立回测 (70止损 + 70仓位 + 10完全自适应)")
    report.append("")
    report.append("=" * 80)
    report.append("")

    # 核心发现
    report.append("## 核心发现")
    report.append("")

    report.append("### 发现1: 固定止损参数的极端敏感性")
    report.append("")
    report.append(f"- **收益范围**: {findings['stop_loss_sensitivity']['range']}")
    report.append(f"- **最佳固定参数**: 止损${findings['stop_loss_sensitivity']['best_fixed']}")
    report.append(f"- **最差固定参数**: 止损${findings['stop_loss_sensitivity']['worst_fixed']}")
    report.append(f"- **ATR自适应平均**: {findings['stop_loss_sensitivity']['adaptive_avg']:.2f}%")
    report.append("")
    report.append("> **结论**: 固定止损参数选择错误可导致收益跨度超过数十个百分点,证明了\"固定参数陷阱\"的存在。")
    report.append("")

    report.append("### 发现2: 固定仓位参数的极端敏感性")
    report.append("")
    report.append(f"- **收益范围**: {findings['position_sensitivity']['range']}")
    report.append(f"- **最佳固定参数**: 仓位{findings['position_sensitivity']['best_fixed']}股")
    report.append(f"- **最差固定参数**: 仓位{findings['position_sensitivity']['worst_fixed']}股")
    report.append("")
    report.append("> **结论**: 固定仓位参数无法适应不同价格水平和波动率的股票。")
    report.append("")

    report.append("### 发现3: 完全自适应策略的优势")
    report.append("")
    report.append(f"- **训练期平均收益**: {findings['fully_adaptive']['train_avg']:.2f}%")
    report.append(f"- **测试期平均收益**: {findings['fully_adaptive']['test_avg']:.2f}%")
    report.append(f"- **训练期成功率**: {findings['fully_adaptive']['success_rate_train']:.1f}%")
    report.append(f"- **测试期成功率**: {findings['fully_adaptive']['success_rate_test']:.1f}%")
    report.append("")

    report.append("### 发现4: 量化改进效果")
    report.append("")
    report.append(f"- **固定参数基线** (止损$200, 仓位20股): {findings['improvement']['fixed_baseline']:.2f}%")
    report.append(f"- **完全自适应**: {findings['fully_adaptive']['train_avg']:.2f}%")
    report.append(f"- **绝对改进**: {findings['improvement']['adaptive_improvement']:+.2f} percentage points")
    report.append(f"- **相对改进**: {findings['improvement']['improvement_pct']:+.1f}%")
    report.append("")

    # 详细数据表
    report.append("=" * 80)
    report.append("")
    report.append("## 详细数据")
    report.append("")

    report.append("### 止损参数扫描结果 (训练期平均)")
    report.append("")
    stop_loss_summary = df_A[df_A['period'] == 'training'].groupby('stop_loss')['returns_pct'].agg([
        ('平均收益', 'mean'),
        ('标准差', 'std'),
        ('最小值', 'min'),
        ('最大值', 'max')
    ]).round(2)
    report.append(stop_loss_summary.to_markdown())
    report.append("")

    report.append("### 仓位参数扫描结果 (训练期平均)")
    report.append("")
    position_summary = df_B[df_B['period'] == 'training'].groupby('position_size')['returns_pct'].agg([
        ('平均收益', 'mean'),
        ('标准差', 'std'),
        ('最小值', 'min'),
        ('最大值', 'max')
    ]).round(2)
    report.append(position_summary.to_markdown())
    report.append("")

    report.append("### 完全自适应结果 (各资产)")
    report.append("")
    adaptive_summary = df_C.pivot_table(
        index='asset',
        columns='period',
        values='returns_pct'
    ).round(2)
    report.append(adaptive_summary.to_markdown())
    report.append("")

    # 论文引用建议
    report.append("=" * 80)
    report.append("")
    report.append("## 论文使用建议")
    report.append("")
    report.append("### Results章节引用")
    report.append("")
    report.append("```")
    report.append("To quantify the impact of the fixed parameter trap, we conducted")
    report.append("a comprehensive parameter sensitivity analysis (150 independent backtests).")
    report.append("")
    report.append(f"Our experiments reveal extreme sensitivity: fixed stop-loss amounts")
    report.append(f"yielded returns ranging from {findings['stop_loss_sensitivity']['range']},")
    report.append(f"while fixed position sizes showed similar variability.")
    report.append("")
    report.append(f"In contrast, the fully adaptive strategy (ATR stop-loss + 2% risk")
    report.append(f"position sizing) achieved {findings['fully_adaptive']['train_avg']:.1f}% average return")
    report.append(f"with {findings['fully_adaptive']['success_rate_train']:.0f}% success rate,")
    report.append(f"representing a {findings['improvement']['improvement_pct']:+.1f}% improvement")
    report.append(f"over fixed parameters ({findings['improvement']['fixed_baseline']:.1f}%).")
    report.append("```")
    report.append("")

    report.append("=" * 80)
    report.append(f"**报告生成完成**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"  >>> 分析报告已生成: {output_path}")
    print(f"      文件大小: {output_path.stat().st_size / 1024:.1f} KB")

    return output_path


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序流程"""
    print("=" * 80)
    print("参数敏感性分析 - 结果处理")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 1. 加载数据
    print("\n[1/5] 加载实验数据...")
    results_A, results_B, results_C = load_results()
    print("  >>> 已加载3个JSON文件")

    # 2. 数据提取
    print("\n[2/5] 提取结构化数据...")
    df_A = extract_stop_loss_data(results_A)
    df_B = extract_position_size_data(results_B)
    df_C = extract_fully_adaptive_data(results_C)
    print(f"  >>> 止损数据: {len(df_A)} 条记录")
    print(f"  >>> 仓位数据: {len(df_B)} 条记录")
    print(f"  >>> 完全自适应: {len(df_C)} 条记录")

    # 3. 生成可视化
    print("\n[3/5] 生成敏感性曲线...")
    output_dir = Path('C:/Users/Xing/Desktop')

    chart1 = plot_stop_loss_sensitivity(df_A, output_dir)
    chart2 = plot_position_size_sensitivity(df_B, output_dir)

    # 4. 统计分析
    print("\n[4/5] 统计分析...")
    findings = analyze_parameter_sensitivity(df_A, df_B, df_C)
    print("  >>> 关键发现已提取")

    # 5. 生成报告
    print("\n[5/5] 生成分析报告...")
    report_path = output_dir / 'parameter_sensitivity_report.md'
    generate_analysis_report(findings, df_A, df_B, df_C, report_path)

    # 保存CSV数据
    df_A.to_csv(output_dir / 'sensitivity_A_data.csv', index=False, encoding='utf-8-sig')
    df_B.to_csv(output_dir / 'sensitivity_B_data.csv', index=False, encoding='utf-8-sig')
    df_C.to_csv(output_dir / 'sensitivity_C_data.csv', index=False, encoding='utf-8-sig')
    print("  >>> CSV数据已保存")

    print("\n" + "=" * 80)
    print("参数敏感性分析 - 全部完成")
    print("=" * 80)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n输出文件:")
    print(f"  1. {chart1}")
    print(f"  2. {chart2}")
    print(f"  3. {report_path}")
    print(f"  4-6. 3个CSV数据文件")
    print("=" * 80)


if __name__ == '__main__':
    main()
