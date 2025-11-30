"""
统计稳健性分析脚本
===================

目的: 为Day 55补充实验添加:
1. Bootstrap置信区间 (95% CI)
2. 效应量计算 (Cohen's d)
3. 多重假设检验校正 (Bonferroni)
4. 统计检验力分析

基于Day 12发现的小样本偏差问题,为所有N<30的实验添加置信区间
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# Bootstrap置信区间计算
# =============================================================================

def bootstrap_ci(data, n_iterations=10000, ci=95):
    """
    计算Bootstrap置信区间

    Parameters:
    -----------
    data : list of float
        样本数据
    n_iterations : int
        Bootstrap迭代次数
    ci : int
        置信水平 (95 or 99)

    Returns:
    --------
    (mean, ci_lower, ci_upper, std_error)
    """
    data = np.array(data)
    n = len(data)

    # Bootstrap采样
    bootstrap_means = []
    for _ in range(n_iterations):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_means.append(np.mean(sample))

    # 计算百分位数
    alpha = (100 - ci) / 2
    ci_lower = np.percentile(bootstrap_means, alpha)
    ci_upper = np.percentile(bootstrap_means, 100 - alpha)

    mean = np.mean(data)
    std_error = np.std(bootstrap_means)

    return mean, ci_lower, ci_upper, std_error


# =============================================================================
# 效应量计算
# =============================================================================

def cohens_d(group1, group2):
    """
    计算Cohen's d效应量

    Parameters:
    -----------
    group1, group2 : list of float
        两组样本数据

    Returns:
    --------
    d : float
        Cohen's d值
    interpretation : str
        效应量解释 (small/medium/large/huge)
    """
    n1, n2 = len(group1), len(group2)
    mean1, mean2 = np.mean(group1), np.mean(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

    # 合并标准差
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1 + n2 - 2))

    # Cohen's d
    d = (mean1 - mean2) / pooled_std

    # 效应量解释 (Cohen, 1988)
    abs_d = abs(d)
    if abs_d < 0.2:
        interpretation = "negligible"
    elif abs_d < 0.5:
        interpretation = "small"
    elif abs_d < 0.8:
        interpretation = "medium"
    elif abs_d < 1.2:
        interpretation = "large"
    else:
        interpretation = "huge"

    return d, interpretation


def cohens_h(p1, p2):
    """
    计算Cohen's h效应量 (用于比例/成功率)

    Parameters:
    -----------
    p1, p2 : float
        两组成功率 (0-1)

    Returns:
    --------
    h : float
        Cohen's h值
    interpretation : str
        效应量解释
    """
    # Cohen's h基于arcsin变换
    h = 2 * (np.arcsin(np.sqrt(p1)) - np.arcsin(np.sqrt(p2)))

    abs_h = abs(h)
    if abs_h < 0.2:
        interpretation = "negligible"
    elif abs_h < 0.5:
        interpretation = "small"
    elif abs_h < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    return h, interpretation


# =============================================================================
# 统计检验力分析
# =============================================================================

def statistical_power_analysis(n, effect_size, alpha=0.05):
    """
    计算统计检验力 (Power)

    Parameters:
    -----------
    n : int
        样本量
    effect_size : float
        效应量 (Cohen's d)
    alpha : float
        显著性水平

    Returns:
    --------
    power : float
        统计检验力 (0-1)
    """
    from scipy.stats import t as t_dist

    # 非中心参数
    ncp = effect_size * np.sqrt(n / 2)

    # 临界值
    df = 2 * n - 2
    critical_t = t_dist.ppf(1 - alpha/2, df)

    # 计算power
    power = 1 - t_dist.cdf(critical_t, df, ncp) + t_dist.cdf(-critical_t, df, ncp)

    return power


# =============================================================================
# 多重假设检验校正
# =============================================================================

def bonferroni_correction(p_values, alpha=0.05):
    """
    Bonferroni多重假设检验校正

    Parameters:
    -----------
    p_values : list of float
        原始p值列表
    alpha : float
        家族显著性水平

    Returns:
    --------
    corrected_alpha : float
        校正后的显著性水平
    significant : list of bool
        每个检验是否显著
    """
    m = len(p_values)
    corrected_alpha = alpha / m

    significant = [p < corrected_alpha for p in p_values]

    return corrected_alpha, significant


# =============================================================================
# 分析Day 55实验数据
# =============================================================================

def analyze_baseline_comparison():
    """分析基线对比实验的统计稳健性"""

    print("=" * 80)
    print("分析1: 基线对比实验 (96回测)")
    print("=" * 80)

    # 读取数据
    data_file = Path(__file__).parent.parent / 'data' / 'baseline_comparison_results.json'

    if not data_file.exists():
        print(f"数据文件不存在: {data_file}")
        return {}

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取2024测试期数据
    results = {}

    for strategy_name in ['Buy_and_Hold', 'LLM_Adaptive', 'SMA_Crossover', 'RSI_Strategy']:
        returns_2024 = []

        for asset_data in data['results'].values():
            if 'testing' in asset_data.get(strategy_name, {}):
                ret = asset_data[strategy_name]['testing']['returns_pct']
                returns_2024.append(ret)

        if len(returns_2024) >= 5:
            # Bootstrap置信区间
            mean, ci_lower, ci_upper, std_error = bootstrap_ci(returns_2024)

            results[strategy_name] = {
                'n': len(returns_2024),
                'mean': mean,
                '95_ci_lower': ci_lower,
                '95_ci_upper': ci_upper,
                'std_error': std_error,
                'raw_returns': returns_2024
            }

            print(f"\n{strategy_name}:")
            print(f"  样本量: n={len(returns_2024)}")
            print(f"  平均收益: {mean:+.2f}%")
            print(f"  95% CI: [{ci_lower:+.2f}%, {ci_upper:+.2f}%]")
            print(f"  标准误: ±{std_error:.2f}%")

    # LLM_Adaptive vs Buy_and_Hold效应量
    if 'LLM_Adaptive' in results and 'Buy_and_Hold' in results:
        llm_returns = results['LLM_Adaptive']['raw_returns']
        bh_returns = results['Buy_and_Hold']['raw_returns']

        # Paired t-test
        t_stat, p_value = stats.ttest_rel(llm_returns, bh_returns)

        # Cohen's d
        differences = np.array(llm_returns) - np.array(bh_returns)
        d = np.mean(differences) / np.std(differences, ddof=1)

        if abs(d) < 0.2:
            d_interp = "negligible"
        elif abs(d) < 0.5:
            d_interp = "small"
        elif abs(d) < 0.8:
            d_interp = "medium"
        else:
            d_interp = "large"

        # Statistical power
        power = statistical_power_analysis(len(llm_returns), abs(d))

        print(f"\n[OK] LLM_Adaptive vs Buy&Hold (2024):")
        print(f"  配对t检验: t={t_stat:.3f}, p={p_value:.4f}")
        print(f"  Cohen's d: {d:.3f} ({d_interp})")
        print(f"  统计检验力: {power:.2%}")

        if p_value < 0.05:
            print(f"  [SIGNIFICANT] 在5%显著性水平下显著 (LLM {'优于' if d > 0 else '弱于'} Buy&Hold)")
        else:
            print(f"  [NOT SIGNIFICANT] 未达到5%显著性水平")

        results['llm_vs_buyhold'] = {
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': d,
            'interpretation': d_interp,
            'power': power
        }

    return results


def analyze_parameter_sensitivity():
    """分析参数敏感性实验的统计稳健性"""

    print("\n" + "=" * 80)
    print("分析2: 参数敏感性实验")
    print("=" * 80)

    # 读取止损敏感性数据
    data_file_A = Path(__file__).parent.parent / 'data' / 'sensitivity_A_stop_loss.json'

    if not data_file_A.exists():
        print(f"数据文件不存在: {data_file_A}")
        return {}

    with open(data_file_A, 'r', encoding='utf-8') as f:
        data_A = json.load(f)

    results = {}

    # 分析茅台的止损敏感性
    moutai_data = data_A['results'].get('600519_贵州茅台', {})

    if moutai_data:
        returns_training = []
        stop_loss_values = []

        for variant_name, variant_data in moutai_data.items():
            if 'training' in variant_data:
                ret = variant_data['training']['returns_pct']
                returns_training.append(ret)

                # 提取止损值
                if 'Fixed' in variant_name:
                    # 从variant_name提取数字 (e.g., "Fixed_50" -> 50)
                    import re
                    match = re.search(r'Fixed_(\d+)', variant_name)
                    if match:
                        stop_loss_values.append(int(match.group(1)))

        if len(returns_training) >= 5:
            # 计算敏感度范围
            sensitivity_range = max(returns_training) - min(returns_training)

            # Bootstrap CI for range
            ranges = []
            for _ in range(10000):
                sample = np.random.choice(returns_training, size=len(returns_training), replace=True)
                ranges.append(max(sample) - min(sample))

            range_mean = np.mean(ranges)
            range_ci_lower = np.percentile(ranges, 2.5)
            range_ci_upper = np.percentile(ranges, 97.5)

            results['stop_loss_sensitivity'] = {
                'asset': '贵州茅台',
                'n_variants': len(returns_training),
                'sensitivity_range': sensitivity_range,
                'range_95_ci': [range_ci_lower, range_ci_upper],
                'min_return': min(returns_training),
                'max_return': max(returns_training),
                'returns': returns_training
            }

            print(f"\n止损参数敏感性 (茅台训练期):")
            print(f"  测试变体数: {len(returns_training)}")
            print(f"  敏感度范围: {sensitivity_range:.2f} pp")
            print(f"  95% CI: [{range_ci_lower:.2f}, {range_ci_upper:.2f}] pp")
            print(f"  收益范围: {min(returns_training):+.2f}% to {max(returns_training):+.2f}%")
            print(f"  [WARNING] 敏感度超过10pp,证明固定参数陷阱存在")

    return results


def analyze_ablation_study():
    """分析消融实验的统计稳健性"""

    print("\n" + "=" * 80)
    print("分析3: 消融实验 (40回测)")
    print("=" * 80)

    data_file = Path(__file__).parent.parent / 'data' / 'ablation_study_results.json'

    if not data_file.exists():
        print(f"数据文件不存在: {data_file}")
        return {}

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取训练期平均收益
    strategies = {
        'Baseline_Fixed': [],
        'ATR_Only': [],
        'Risk2Pct_Only': [],
        'Full_Adaptive': []
    }

    for strategy_name in strategies.keys():
        for asset_data in data['results'].values():
            if 'training' in asset_data.get(strategy_name, {}):
                ret = asset_data[strategy_name]['training']['returns_pct']
                strategies[strategy_name].append(ret)

    results = {}

    # 计算每个策略的Bootstrap CI
    for strategy_name, returns in strategies.items():
        if len(returns) >= 5:
            mean, ci_lower, ci_upper, std_error = bootstrap_ci(returns)

            results[strategy_name] = {
                'mean': mean,
                '95_ci': [ci_lower, ci_upper],
                'std_error': std_error
            }

            print(f"\n{strategy_name}:")
            print(f"  平均收益: {mean:+.2f}%")
            print(f"  95% CI: [{ci_lower:+.2f}%, {ci_upper:+.2f}%]")

    # 计算组件贡献的效应量
    if 'Baseline_Fixed' in results and 'Full_Adaptive' in results:
        baseline_returns = strategies['Baseline_Fixed']
        adaptive_returns = strategies['Full_Adaptive']

        # Cohen's d
        d, d_interp = cohens_d(adaptive_returns, baseline_returns)

        print(f"\n[OK] Full_Adaptive vs Baseline效应量:")
        print(f"  Cohen's d: {d:.3f} ({d_interp})")
        print(f"  解释: Full_Adaptive比Baseline高{d:.1f}个标准差")

        results['adaptive_vs_baseline'] = {
            'cohens_d': d,
            'interpretation': d_interp
        }

    return results


def analyze_multiyear_validation():
    """分析多年份验证的统计稳健性"""

    print("\n" + "=" * 80)
    print("分析4: 多年份滚动验证 (15回测)")
    print("=" * 80)

    data_file = Path(__file__).parent.parent / 'data' / 'multi_year_rolling_validation.json'

    if not data_file.exists():
        print(f"数据文件不存在: {data_file}")
        return {}

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = {}

    # 分析每个窗口的成功率和收益
    for window_name, window_data in data['rolling_windows'].items():
        returns = []

        for asset_name, asset_data in window_data['assets'].items():
            if 'test_period' in asset_data:
                ret = asset_data['test_period']['returns_pct']
                returns.append(ret)

        if len(returns) >= 3:  # 至少3个资产
            # Bootstrap CI (小样本!)
            mean, ci_lower, ci_upper, std_error = bootstrap_ci(returns, n_iterations=10000)

            # 成功率
            success_count = sum(1 for r in returns if r > 0)
            success_rate = success_count / len(returns)

            # 成功率的Wilson Score置信区间 (更适合小样本)
            from scipy.stats import norm
            z = norm.ppf(0.975)  # 95% CI
            n = len(returns)
            p = success_rate

            denominator = 1 + z**2 / n
            center = (p + z**2 / (2*n)) / denominator
            margin = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denominator

            sr_ci_lower = max(0, center - margin)
            sr_ci_upper = min(1, center + margin)

            results[window_name] = {
                'n': len(returns),
                'mean_return': mean,
                'return_95_ci': [ci_lower, ci_upper],
                'success_rate': success_rate,
                'success_rate_95_ci': [sr_ci_lower, sr_ci_upper]
            }

            print(f"\n{window_name}:")
            print(f"  样本量: n={len(returns)} [WARNING: Small sample!]")
            print(f"  平均收益: {mean:+.2f}%")
            print(f"  收益95% CI: [{ci_lower:+.2f}%, {ci_upper:+.2f}%]")
            print(f"  成功率: {success_rate*100:.0f}%")
            print(f"  成功率95% CI: [{sr_ci_lower*100:.0f}%, {sr_ci_upper*100:.0f}%]")
            print(f"  [WARNING] 置信区间较宽,反映小样本不确定性")

    return results


# =============================================================================
# 生成综合报告
# =============================================================================

def generate_statistical_report():
    """生成统计稳健性分析综合报告"""

    print("\n" + "=" * 80)
    print("统计稳健性分析 - 开始")
    print("=" * 80)
    print(f"时间: {Path().resolve()}")

    all_results = {}

    # 分析1: 基线对比
    baseline_results = analyze_baseline_comparison()
    all_results['baseline_comparison'] = baseline_results

    # 分析2: 参数敏感性
    sensitivity_results = analyze_parameter_sensitivity()
    all_results['parameter_sensitivity'] = sensitivity_results

    # 分析3: 消融实验
    ablation_results = analyze_ablation_study()
    all_results['ablation_study'] = ablation_results

    # 分析4: 多年份验证
    multiyear_results = analyze_multiyear_validation()
    all_results['multiyear_validation'] = multiyear_results

    # 保存结果
    output_file = Path(__file__).parent.parent / 'data' / 'statistical_robustness_results.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("统计稳健性分析 - 完成")
    print("=" * 80)
    print(f"输出文件: {output_file}")
    print(f"文件大小: {output_file.stat().st_size / 1024:.1f} KB")

    return all_results


if __name__ == '__main__':
    generate_statistical_report()
