#!/usr/bin/env python3
"""
Day 21 多资产组合优化
目的: 基于Day 16-20最佳策略构建最优投资组合
作者: Claude AI Assistant
日期: 2025-11-17
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import json
from pathlib import Path

class PortfolioOptimizer:
    def __init__(self):
        self.assets = {}
        self.returns = None
        self.cov_matrix = None

    def load_strategy(self, asset, csv_path):
        """加载单个资产的最佳策略数据"""
        df = pd.read_csv(csv_path)
        # 假设CSV包含test_return列
        self.assets[asset] = df
        print(f"✅ 已加载 {asset}: {len(df)} 个策略")

    def select_best_strategies(self):
        """为每个资产选择最佳策略"""
        best_strategies = {}

        for asset, df in self.assets.items():
            # 选择test_Return_%最高的策略
            best_idx = df['test_Return_%'].idxmax()
            best = df.loc[best_idx]
            best_strategies[asset] = {
                'id': best.get('id', best_idx),
                'test_return': best['test_Return_%'],
                'test_sharpe': best.get('test_Sharpe', 0),
                'train_return': best.get('train_Return_%', 0)
            }
            print(f"  {asset}: 策略#{best.get('id', best_idx)} - 收益 {best['test_Return_%']:.2%}")

        return best_strategies

    def calculate_portfolio_metrics(self, weights, returns_df):
        """计算投资组合指标"""
        portfolio_return = np.sum(weights * returns_df.mean() * 252)  # 年化
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * 252, weights)))
        sharpe = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0

        return {
            'return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe': sharpe
        }

    def optimize_equal_weight(self, n_assets):
        """等权重配置"""
        return np.array([1.0 / n_assets] * n_assets)

    def optimize_markowitz(self, returns_df):
        """Markowitz均值-方差优化"""
        n_assets = len(returns_df.columns)

        def neg_sharpe(weights):
            portfolio_return = np.sum(weights * returns_df.mean() * 252)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * 252, weights)))
            return -portfolio_return / portfolio_vol if portfolio_vol > 0 else 0

        # 约束: 权重和=1, 每个资产 0-40%
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 0.4) for _ in range(n_assets))
        initial = np.array([1.0/n_assets] * n_assets)

        result = minimize(neg_sharpe, initial, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        return result.x

    def optimize_risk_parity(self, returns_df):
        """风险平价配置"""
        cov = returns_df.cov() * 252
        n_assets = len(returns_df.columns)

        def risk_budget_objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
            marginal_contribs = np.dot(cov, weights) / portfolio_vol
            contribs = weights * marginal_contribs
            target = portfolio_vol / n_assets
            return np.sum((contribs - target) ** 2)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial = np.array([1.0/n_assets] * n_assets)

        result = minimize(risk_budget_objective, initial, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        return result.x

    def optimize_kelly(self, returns_df):
        """Kelly准则优化 (创新方法)"""
        mean_returns = returns_df.mean() * 252
        cov = returns_df.cov() * 252

        try:
            # Kelly公式: w = Σ^(-1) * μ
            inv_cov = np.linalg.inv(cov)
            kelly_weights = np.dot(inv_cov, mean_returns)

            # 归一化并限制在0-1之间
            kelly_weights = np.maximum(kelly_weights, 0)
            kelly_weights = kelly_weights / np.sum(kelly_weights) if np.sum(kelly_weights) > 0 else np.ones(len(mean_returns)) / len(mean_returns)

            # 限制单个资产不超过40%
            kelly_weights = np.minimum(kelly_weights, 0.4)
            kelly_weights = kelly_weights / np.sum(kelly_weights)

            return kelly_weights
        except:
            # 如果协方差矩阵奇异，返回等权
            print("  ⚠️ Kelly优化失败，使用等权重")
            return self.optimize_equal_weight(len(mean_returns))

def main():
    """主程序"""
    print("="*60)
    print("Day 21 多资产组合优化")
    print("="*60)

    # 配置: 根据Day 16-20实验结果选择最佳策略文件
    strategy_files = {
        'SPY': '/root/autodl-tmp/outputs/day16_v13_crossover_spy/gen01.csv',
        'QQQ': '/root/autodl-tmp/outputs/day17_v13_cross_qqq/gen01.csv',
        'IWM': '/root/autodl-tmp/outputs/day20_diversity_iwm_v3/gen01.csv',  # Day 20 V3
        'GLD': '/root/autodl-tmp/outputs/day20_diversity_gld_v3/gen01.csv',  # Day 20 V3
    }

    print("\n1️⃣ 加载策略数据...")
    optimizer = PortfolioOptimizer()

    for asset, path in strategy_files.items():
        if Path(path).exists():
            optimizer.load_strategy(asset, path)
        else:
            print(f"  ⚠️ {asset} 文件不存在: {path}")

    print("\n2️⃣ 选择各资产最佳策略...")
    best_strategies = optimizer.select_best_strategies()

    # 构建收益率时间序列 (这里简化处理，使用策略收益率)
    # 实际应用中需要加载每个策略的日收益率序列
    print("\n3️⃣ 优化投资组合权重...")
    print("\n⚠️ 注意: 当前版本使用简化的收益率数据")
    print("   实际应用需要加载每个策略的完整日收益率序列\n")

    # 示例: 使用最佳策略的年化收益作为期望收益
    assets = list(best_strategies.keys())
    expected_returns = np.array([best_strategies[a]['test_return'] for a in assets])

    # 假设简单的协方差矩阵 (实际需要从历史数据计算)
    # 这里使用一个合理的假设值
    corr_matrix = np.array([
        [1.00, 0.85, 0.75, 0.10],  # SPY
        [0.85, 1.00, 0.70, 0.05],  # QQQ
        [0.75, 0.70, 1.00, 0.15],  # IWM
        [0.10, 0.05, 0.15, 1.00],  # GLD
    ])
    vols = np.array([0.18, 0.22, 0.25, 0.16])  # 假设的波动率
    cov_matrix = np.outer(vols, vols) * corr_matrix

    # 计算各种权重方案
    results = {}

    # 方法1: 等权重
    weights_equal = np.array([0.25, 0.25, 0.25, 0.25])
    results['Equal Weight'] = {
        'weights': dict(zip(assets, weights_equal)),
        'return': np.dot(weights_equal, expected_returns),
        'volatility': np.sqrt(np.dot(weights_equal.T, np.dot(cov_matrix, weights_equal))),
    }
    results['Equal Weight']['sharpe'] = results['Equal Weight']['return'] / results['Equal Weight']['volatility']

    # 方法2: 最大Sharpe (简化版Markowitz)
    def neg_sharpe(w):
        ret = np.dot(w, expected_returns)
        vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
        return -ret/vol if vol > 0 else 0

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 0.4) for _ in range(len(assets)))
    result_mvo = minimize(neg_sharpe, weights_equal, method='SLSQP',
                          bounds=bounds, constraints=constraints)

    weights_mvo = result_mvo.x
    results['Markowitz MVO'] = {
        'weights': dict(zip(assets, weights_mvo)),
        'return': np.dot(weights_mvo, expected_returns),
        'volatility': np.sqrt(np.dot(weights_mvo.T, np.dot(cov_matrix, weights_mvo))),
    }
    results['Markowitz MVO']['sharpe'] = results['Markowitz MVO']['return'] / results['Markowitz MVO']['volatility']

    # 方法3: Risk Parity
    def risk_parity_obj(w):
        vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
        marginal = np.dot(cov_matrix, w) / vol
        contribs = w * marginal
        target = vol / len(w)
        return np.sum((contribs - target) ** 2)

    result_rp = minimize(risk_parity_obj, weights_equal, method='SLSQP',
                        bounds=bounds, constraints=constraints)

    weights_rp = result_rp.x
    results['Risk Parity'] = {
        'weights': dict(zip(assets, weights_rp)),
        'return': np.dot(weights_rp, expected_returns),
        'volatility': np.sqrt(np.dot(weights_rp.T, np.dot(cov_matrix, weights_rp))),
    }
    results['Risk Parity']['sharpe'] = results['Risk Parity']['return'] / results['Risk Parity']['volatility']

    # 方法4: Kelly Criterion
    try:
        inv_cov = np.linalg.inv(cov_matrix)
        weights_kelly = np.dot(inv_cov, expected_returns)
        weights_kelly = np.maximum(weights_kelly, 0)
        weights_kelly = np.minimum(weights_kelly, 0.4)
        weights_kelly = weights_kelly / np.sum(weights_kelly)

        results['Kelly Criterion'] = {
            'weights': dict(zip(assets, weights_kelly)),
            'return': np.dot(weights_kelly, expected_returns),
            'volatility': np.sqrt(np.dot(weights_kelly.T, np.dot(cov_matrix, weights_kelly))),
        }
        results['Kelly Criterion']['sharpe'] = results['Kelly Criterion']['return'] / results['Kelly Criterion']['volatility']
    except:
        print("  ⚠️ Kelly优化失败")

    # 打印结果
    print("\n" + "="*80)
    print("组合优化结果对比")
    print("="*80)

    for method, metrics in results.items():
        print(f"\n📊 {method}")
        print(f"  权重:")
        for asset, weight in metrics['weights'].items():
            print(f"    {asset}: {weight:6.1%}")
        print(f"  预期年化收益: {metrics['return']:6.2%}")
        print(f"  年化波动率:   {metrics['volatility']:6.2%}")
        print(f"  Sharpe比率:   {metrics['sharpe']:6.2f}")

    # 保存结果
    output_file = '/root/autodl-tmp/outputs/day21_portfolio_optimization.json'
    with open(output_file, 'w') as f:
        # Convert numpy types to native Python types for JSON serialization
        json_results = {}
        for method, metrics in results.items():
            json_results[method] = {
                'weights': {k: float(v) for k, v in metrics['weights'].items()},
                'return': float(metrics['return']),
                'volatility': float(metrics['volatility']),
                'sharpe': float(metrics['sharpe'])
            }
        json.dump({'best_strategies': best_strategies, 'portfolios': json_results}, f, indent=2)

    print(f"\n✅ 结果已保存到: {output_file}")
    print("\n" + "="*80)

    # 推荐最优组合
    best_method = max(results.items(), key=lambda x: x[1]['sharpe'])
    print(f"\n🏆 推荐组合: {best_method[0]}")
    print(f"   Sharpe比率: {best_method[1]['sharpe']:.2f}")
    print(f"   预期收益: {best_method[1]['return']:.2%}")

if __name__ == '__main__':
    main()
