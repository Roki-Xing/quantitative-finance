#!/usr/bin/env python3
"""
Day 23 资产特征分析器
目的: 分析不同资产类别的策略表现特征，为自适应框架提供依据
作者: Claude AI Assistant
日期: 2025-11-17
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

class AssetFeatureAnalyzer:
    def __init__(self):
        self.asset_data = {}
        self.asset_classes = {
            'SPY': 'equity_large',
            'QQQ': 'equity_tech',
            'IWM': 'equity_small',
            'GLD': 'commodity_gold',
            'TLT': 'bond_treasury',
            'XLE': 'commodity_energy'
        }

    def load_strategy_results(self, base_path='/root/autodl-tmp/outputs'):
        """加载各资产的策略结果"""
        print("="*80)
        print("📊 加载策略结果数据")
        print("="*80)

        # FIX 3.3: 定义要加载的实验结果（包含所有资产类型）
        # 注意：TLT和XLE可能还没有实验数据，会通过try-except优雅处理
        experiments = {
            'SPY': 'day16_v13_crossover_spy/gen01.csv',
            'QQQ': 'day17_v13_cross_qqq/gen01.csv',
            'IWM': 'day20_diversity_iwm_v3/gen01.csv',
            'GLD': 'day20_diversity_gld_v3/gen01.csv',
            'TLT': 'day*_tlt*/gen*.csv',  # 未来实验数据
            'XLE': 'day*_xle*/gen*.csv',  # 未来实验数据
        }

        for asset, file_path in experiments.items():
            full_path = f"{base_path}/{file_path}"
            try:
                df = pd.read_csv(full_path)
                # 过滤有效策略
                valid_df = df[df['test_Return_%'].notna()].copy()
                self.asset_data[asset] = valid_df
                print(f"✅ {asset}: {len(valid_df)} 个有效策略 (来源: {file_path.split('/')[0]})")
            except Exception as e:
                print(f"⚠️  {asset}: 文件不存在或读取失败 - {e}")

        print()

    def analyze_asset_characteristics(self):
        """分析各资产的策略特征"""
        print("="*80)
        print("🔍 资产特征分析")
        print("="*80)

        features = {}

        for asset, df in self.asset_data.items():
            asset_class = self.asset_classes.get(asset, 'unknown')

            # 基础统计
            test_returns = df['test_Return_%'].values
            train_returns = df['train_Return_%'].values if 'train_Return_%' in df.columns else np.zeros(len(df))
            test_sharpes = df['test_Sharpe'].values if 'test_Sharpe' in df.columns else np.zeros(len(df))

            # 过滤掉异常值
            test_returns = test_returns[~np.isnan(test_returns)]
            train_returns = train_returns[~np.isnan(train_returns)]
            test_sharpes = test_sharpes[~np.isnan(test_sharpes)]

            # FIX #5: Add empty data validation
            features[asset] = {
                'asset_class': asset_class,
                'n_strategies': len(df),
                'test_return': {
                    'mean': float(np.mean(test_returns)) if len(test_returns) > 0 else 0.0,
                    'median': float(np.median(test_returns)) if len(test_returns) > 0 else 0.0,
                    'std': float(np.std(test_returns)) if len(test_returns) > 0 else 0.0,
                    'max': float(np.max(test_returns)) if len(test_returns) > 0 else 0.0,
                    'min': float(np.min(test_returns)) if len(test_returns) > 0 else 0.0,
                    'positive_rate': float(np.sum(test_returns > 0) / len(test_returns)) if len(test_returns) > 0 else 0.0
                },
                'train_return': {
                    'mean': float(np.mean(train_returns)) if len(train_returns) > 0 else 0.0,
                    'median': float(np.median(train_returns)) if len(train_returns) > 0 else 0.0,
                    'std': float(np.std(train_returns)) if len(train_returns) > 0 else 0.0
                },
                'sharpe': {
                    'mean': float(np.mean(test_sharpes)) if len(test_sharpes) > 0 else 0,
                    'median': float(np.median(test_sharpes)) if len(test_sharpes) > 0 else 0,
                    'max': float(np.max(test_sharpes)) if len(test_sharpes) > 0 else 0
                }
            }

            print(f"\n📈 {asset} ({asset_class})")
            print(f"  策略数: {features[asset]['n_strategies']}")
            print(f"  测试收益:")
            print(f"    平均: {features[asset]['test_return']['mean']:>8.2%}")
            print(f"    中位数: {features[asset]['test_return']['median']:>8.2%}")
            print(f"    最大: {features[asset]['test_return']['max']:>8.2%}")
            print(f"    阳性率: {features[asset]['test_return']['positive_rate']:>8.1%}")
            print(f"  测试Sharpe:")
            print(f"    平均: {features[asset]['sharpe']['mean']:>8.2f}")
            print(f"    最大: {features[asset]['sharpe']['max']:>8.2f}")

        self.features = features
        return features

    def identify_asset_class_patterns(self):
        """识别资产类别的共同模式"""
        print("\n" + "="*80)
        print("🎯 资产类别模式识别")
        print("="*80)

        # 按资产类别分组
        class_groups = {}
        for asset, feat in self.features.items():
            asset_class = feat['asset_class']
            class_type = asset_class.split('_')[0]  # equity, commodity, bond

            if class_type not in class_groups:
                class_groups[class_type] = []
            class_groups[class_type].append((asset, feat))

        patterns = {}
        for class_type, assets in class_groups.items():
            # 计算该类别的平均特征
            avg_return = np.mean([feat['test_return']['mean'] for _, feat in assets])
            avg_sharpe = np.mean([feat['sharpe']['mean'] for _, feat in assets])
            avg_positive_rate = np.mean([feat['test_return']['positive_rate'] for _, feat in assets])

            patterns[class_type] = {
                'assets': [asset for asset, _ in assets],
                'avg_test_return': float(avg_return),
                'avg_sharpe': float(avg_sharpe),
                'avg_positive_rate': float(avg_positive_rate)
            }

            print(f"\n📊 {class_type.upper()} 类别")
            print(f"  资产: {', '.join(patterns[class_type]['assets'])}")
            print(f"  平均测试收益: {patterns[class_type]['avg_test_return']:>8.2%}")
            print(f"  平均Sharpe: {patterns[class_type]['avg_sharpe']:>8.2f}")
            print(f"  平均阳性率: {patterns[class_type]['avg_positive_rate']:>8.1%}")

        self.patterns = patterns
        return patterns

    def recommend_parameters(self):
        """基于分析推荐各资产类别的参数配置"""
        print("\n" + "="*80)
        print("💡 自适应参数推荐")
        print("="*80)

        recommendations = {}

        # Equity (股票) - 基于SPY, QQQ, IWM的表现
        if 'equity' in self.patterns:
            # QQQ表现最好，使用其参数作为科技股基准
            # SPY作为大盘基准
            # IWM作为小盘基准
            recommendations['equity_large'] = {
                'description': '大盘股票 (如SPY)',
                'sma_fast': 5,
                'sma_slow': 10,
                'rsi_threshold': 35,
                'position_size': 20,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'balanced',
                'rationale': 'SPY表现稳定，使用标准参数'
            }

            recommendations['equity_tech'] = {
                'description': '科技股 (如QQQ)',
                'sma_fast': 3,
                'sma_slow': 8,
                'rsi_threshold': 30,
                'position_size': 25,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'aggressive',
                'rationale': 'QQQ高收益，使用更敏捷参数捕捉快速趋势'
            }

            recommendations['equity_small'] = {
                'description': '小盘股 (如IWM)',
                'sma_fast': 8,
                'sma_slow': 21,
                'rsi_threshold': 40,
                'position_size': 15,
                'temperature': 0.5,
                'population': 30,
                'prompt_style': 'conservative',
                'rationale': 'IWM波动大，使用更保守参数+更多样本'
            }

        # Commodity (商品) - 基于GLD的表现
        if 'commodity' in self.patterns:
            recommendations['commodity_gold'] = {
                'description': '黄金商品 (如GLD)',
                'sma_fast': 5,
                'sma_slow': 13,
                'rsi_threshold': 35,
                'position_size': 18,
                'temperature': 0.5,
                'population': 30,
                'prompt_style': 'balanced',
                'rationale': 'GLD趋势性强，需要更多样本捕捉多样策略'
            }

            recommendations['commodity_energy'] = {
                'description': '能源商品 (如XLE, USO)',
                'sma_fast': 3,
                'sma_slow': 10,
                'rsi_threshold': 32,
                'position_size': 20,
                'temperature': 0.5,
                'population': 25,
                'prompt_style': 'aggressive',
                'rationale': '能源波动极大，需要快速响应参数'
            }

        # Bond (债券) - 理论推荐
        recommendations['bond_treasury'] = {
            'description': '国债 (如TLT)',
            'sma_fast': 10,
            'sma_slow': 30,
            'rsi_threshold': 45,
            'position_size': 15,
            'temperature': 0.5,
            'population': 20,
            'prompt_style': 'conservative',
            'rationale': '债券波动小，使用长周期参数'
        }

        # 输出推荐
        for asset_type, config in recommendations.items():
            print(f"\n🎯 {asset_type.upper()}")
            print(f"  描述: {config['description']}")
            print(f"  参数配置:")
            print(f"    SMA: ({config['sma_fast']}, {config['sma_slow']})")
            print(f"    RSI阈值: {config['rsi_threshold']}")
            print(f"    仓位: {config['position_size']}")
            print(f"    Population: {config['population']}")
            print(f"    风格: {config['prompt_style']}")
            print(f"  理由: {config['rationale']}")

        self.recommendations = recommendations
        return recommendations

    def generate_adaptive_framework_code(self):
        """生成自适应框架代码"""
        print("\n" + "="*80)
        print("🔧 生成自适应框架代码")
        print("="*80)

        framework_code = '''#!/usr/bin/env python3
"""
Day 23 资产自适应框架 V1.4
自动根据资产类型选择最优参数配置
"""

class AssetAdaptiveFramework:
    """资产自适应参数框架"""

    def __init__(self):
        self.asset_configs = {
            'SPY': {
                'type': 'equity_large',
                'sma_fast': 5,
                'sma_slow': 10,
                'rsi_threshold': 35,
                'position_size': 20,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'balanced'
            },
            'QQQ': {
                'type': 'equity_tech',
                'sma_fast': 3,
                'sma_slow': 8,
                'rsi_threshold': 30,
                'position_size': 25,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'aggressive'
            },
            'IWM': {
                'type': 'equity_small',
                'sma_fast': 8,
                'sma_slow': 21,
                'rsi_threshold': 40,
                'position_size': 15,
                'temperature': 0.5,
                'population': 30,
                'prompt_style': 'conservative'
            },
            'GLD': {
                'type': 'commodity_gold',
                'sma_fast': 5,
                'sma_slow': 13,
                'rsi_threshold': 35,
                'position_size': 18,
                'temperature': 0.5,
                'population': 30,
                'prompt_style': 'balanced'
            },
            'TLT': {
                'type': 'bond_treasury',
                'sma_fast': 10,
                'sma_slow': 30,
                'rsi_threshold': 45,
                'position_size': 15,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'conservative'
            },
            'XLE': {
                'type': 'commodity_energy',
                'sma_fast': 3,
                'sma_slow': 10,
                'rsi_threshold': 32,
                'position_size': 20,
                'temperature': 0.5,
                'population': 25,
                'prompt_style': 'aggressive'
            }
        }

    def get_config(self, asset_symbol):
        """获取资产的自适应配置"""
        if asset_symbol in self.asset_configs:
            return self.asset_configs[asset_symbol]
        else:
            # 默认配置
            return {
                'type': 'unknown',
                'sma_fast': 5,
                'sma_slow': 10,
                'rsi_threshold': 35,
                'position_size': 20,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'balanced'
            }

    def generate_command(self, asset_symbol, base_path='/root/autodl-tmp'):
        """生成运行命令"""
        config = self.get_config(asset_symbol)

        cmd = f"""
/root/miniconda3/envs/eoh1/bin/python {base_path}/eoh/eoh_gpu_loop_fixed.py \\\\
    --model-dir {base_path}/models/Meta-Llama-3.1-8B-Instruct \\\\
    --symbol {asset_symbol} \\\\
    --population {config['population']} \\\\
    --temperature {config['temperature']} \\\\
    --prompt-style {config['prompt_style']} \\\\
    --prompt-dir {base_path}/eoh/prompts_day19 \\\\
    --outdir {base_path}/outputs/day23_adaptive_{asset_symbol.lower()} \\\\
    --train-start 2020-01-01 \\\\
    --train-end 2022-12-31 \\\\
    --test-start 2023-01-01 \\\\
    --test-end 2023-12-31
"""
        return cmd.strip()

    def print_config(self, asset_symbol):
        """打印资产配置"""
        config = self.get_config(asset_symbol)
        print(f"\\n{'='*60}")
        print(f"Asset: {asset_symbol}")
        print(f"Type: {config['type']}")
        print(f"{'='*60}")
        print(f"SMA Fast/Slow: {config['sma_fast']}/{config['sma_slow']}")
        print(f"RSI Threshold: {config['rsi_threshold']}")
        print(f"Position Size: {config['position_size']}")
        print(f"Temperature: {config['temperature']}")
        print(f"Population: {config['population']}")
        print(f"Prompt Style: {config['prompt_style']}")
        print(f"{'='*60}")


if __name__ == '__main__':
    framework = AssetAdaptiveFramework()

    # 示例：为所有资产生成配置
    assets = ['SPY', 'QQQ', 'IWM', 'GLD', 'TLT', 'XLE']

    print("Day 23 资产自适应框架 V1.4")
    print("="*60)

    for asset in assets:
        framework.print_config(asset)
        print(f"\\n运行命令:")
        print(framework.generate_command(asset))
        print()
'''

        output_file = '/root/autodl-tmp/eoh/asset_adaptive_framework.py'
        
        # FIX #4: Actually write the generated code to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(framework_code)
        
        print(f"✅ 框架代码已生成并保存: {output_file}")

        return framework_code

    def save_results(self, output_dir='/root/autodl-tmp/outputs'):
        """保存分析结果"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'asset_features': self.features,
            'asset_class_patterns': self.patterns,
            'parameter_recommendations': self.recommendations
        }

        output_file = f'{output_dir}/day23_asset_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ 分析结果已保存: {output_file}")


def main():
    """主程序"""
    print("="*80)
    print("Day 23: 资产特征分析与自适应框架开发")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    analyzer = AssetFeatureAnalyzer()

    # 1. 加载数据
    analyzer.load_strategy_results()

    # 2. 分析特征
    analyzer.analyze_asset_characteristics()

    # 3. 识别模式
    analyzer.identify_asset_class_patterns()

    # 4. 推荐参数
    analyzer.recommend_parameters()

    # 5. 生成框架代码
    framework_code = analyzer.generate_adaptive_framework_code()

    # 6. 保存结果
    analyzer.save_results()

    print("\n" + "="*80)
    print("✅ Day 23 资产分析完成！")
    print("="*80)
    print("\n下一步:")
    print("1. 使用生成的自适应框架运行新资产测试")
    print("2. 对比自适应策略 vs 统一策略的表现")
    print("3. 验证框架有效性")


if __name__ == '__main__':
    main()
