#!/usr/bin/env python3
"""
Asset Adaptive Framework V1.5 - Day 26 Validated
=================================================

CRITICAL UPDATES FROM DAY 26 VALIDATION:
- All prompt styles changed to 'aggressive' (only working style with prompts_day19)
- TLT expectations lowered to match Day 26 reality (0.78% vs predicted 5-10%)
- QQQ upgraded to S-TIER (124% avg return, 100% positive rate)
- Added performance_tier classification
- Added validation_data field with experimental evidence

VERSION HISTORY:
- V1.4 (Day 23): Initial framework with conservative/balanced/aggressive styles
- V1.4 Validation (Day 24-25): FAILED - conservative/balanced generated 0% valid code
- V1.5 (Day 26): Fixed with aggressive-only, updated TLT expectations

Author: Claude AI Assistant
Date: 2025-11-17 (Day 26)
"""

class AssetAdaptiveFramework:
    """
    资产自适应参数框架 V1.5

    VALIDATED CONFIGURATION:
    - Prompt Style: 'aggressive' ONLY (Day 26 confirmed)
    - Template: prompts_day19
    - Model: Meta-Llama-3.1-8B-Instruct

    Performance Tiers:
    - S-TIER: QQQ (45-85% valid, 45-124% return, 100% positive)
    - A-TIER: SPY (90% valid, 45% return, 94% positive) [Day 16 data]
    - B-TIER: GLD (53% valid, 30% return, 94% positive) [Day 20 data]
    - C-TIER: TLT (60% valid, 0.78% return, 75% positive) [Day 26 data]
    - D-TIER: IWM (43% valid, 21% return, 62% positive) [Day 20 data]
    - F-TIER: XLE (36% valid, all negative returns) [Day 24 data - AVOID]
    """

    def __init__(self):
        self.version = "1.5"
        self.validation_date = "2025-11-17"
        self.validated_prompt_styles = ['aggressive']  # ONLY aggressive works!

        self.asset_configs = {
            'QQQ': {
                'type': 'equity_tech',
                'performance_tier': 'S-TIER',  # NEW in V1.5

                # Parameters (optimized for QQQ)
                'sma_fast': 3,
                'sma_slow': 8,
                'rsi_threshold': 30,
                'position_size': 25,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'aggressive',  # FIXED: was 'aggressive', remains best

                # Expected Performance (validated)
                'expected_return_pct': (40, 130),  # Day 17: 45.7%, Day 26: 124.1%
                'expected_sharpe': (0.8, 1.7),     # Day 17: 0.86, Day 26: 1.67
                'expected_positive_rate': (75, 100),  # Day 17: 76.5%, Day 26: 100%
                'expected_valid_rate': (45, 85),   # Day 17: 85%, Day 26: 45%

                # Validation Evidence
                'validation_data': {
                    'day17': {'valid': '17/20 (85%)', 'return': '45.7%', 'sharpe': 0.86, 'positive': '76.5%'},
                    'day26': {'valid': '9/20 (45%)', 'return': '124.1%', 'sharpe': 1.67, 'positive': '100%'}
                },

                'confidence': 'HIGH',
                'recommendation': 'PRIMARY ALLOCATION - Best performer across multiple experiments',
                'rationale': 'QQQ + aggressive style = consistent excellence. Day 26 had fewer valid but ALL exceptional (124% avg, 176% max, 100% positive). Best risk-adjusted returns.'
            },

            'SPY': {
                'type': 'equity_large',
                'performance_tier': 'A-TIER',  # NEW in V1.5

                # Parameters
                'sma_fast': 5,
                'sma_slow': 10,
                'rsi_threshold': 35,
                'position_size': 20,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'aggressive',  # CHANGED from 'balanced' in V1.4

                # Expected Performance
                'expected_return_pct': (40, 50),
                'expected_sharpe': (1.0, 1.2),
                'expected_positive_rate': (90, 95),
                'expected_valid_rate': (85, 95),

                # Validation Evidence
                'validation_data': {
                    'day16': {'valid': '18/20 (90%)', 'return': '45.36%', 'sharpe': 1.05, 'positive': '94.4%'}
                },

                'confidence': 'HIGH',
                'recommendation': 'CORE ALLOCATION - Stable and reliable',
                'rationale': 'SPY shows excellent stability. High positive rate (94.4%) and good Sharpe (1.05). Use for portfolio foundation.'
            },

            'GLD': {
                'type': 'commodity_gold',
                'performance_tier': 'B-TIER',  # NEW in V1.5

                # Parameters
                'sma_fast': 5,
                'sma_slow': 13,
                'rsi_threshold': 35,
                'position_size': 18,
                'temperature': 0.5,
                'population': 30,
                'prompt_style': 'aggressive',  # CHANGED from 'balanced' in V1.4

                # Expected Performance
                'expected_return_pct': (25, 35),
                'expected_sharpe': (0.6, 1.0),
                'expected_positive_rate': (85, 95),
                'expected_valid_rate': (50, 60),

                # Validation Evidence
                'validation_data': {
                    'day20': {'valid': '16/30 (53%)', 'return': '29.79%', 'sharpe': 0.88, 'positive': '93.8%'}
                },

                'confidence': 'MEDIUM',
                'recommendation': 'DEFENSIVE ALLOCATION - Portfolio stabilizer',
                'rationale': 'GLD provides low volatility (std 12.82%) and high positive rate (93.8%). Good for diversification and risk reduction.'
            },

            'TLT': {
                'type': 'bond_treasury',
                'performance_tier': 'C-TIER',  # NEW in V1.5

                # Parameters
                'sma_fast': 10,
                'sma_slow': 30,
                'rsi_threshold': 45,
                'position_size': 15,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'aggressive',  # CHANGED from 'conservative' in V1.4

                # Expected Performance (UPDATED based on Day 26 reality)
                'expected_return_pct': (0, 5),     # DOWNGRADED from (5, 10) in V1.4
                'expected_sharpe': (0.2, 0.4),     # DOWNGRADED from 1.2+ in V1.4
                'expected_positive_rate': (70, 80),  # DOWNGRADED from 90%+ in V1.4
                'expected_valid_rate': (55, 65),   # NEW - based on Day 26

                # Validation Evidence
                'validation_data': {
                    'day24_conservative': {'valid': '0/20 (0%)', 'return': 'N/A', 'note': 'FAILED - conservative incompatible'},
                    'day26_aggressive': {'valid': '12/20 (60%)', 'return': '0.78%', 'sharpe': 0.38, 'positive': '75%'}
                },

                'confidence': 'MEDIUM',
                'recommendation': 'MINOR ALLOCATION - Underperforms vs Day 23 predictions',
                'rationale': 'Day 26 reality (0.78% return) << Day 23 prediction (5-10%). Aggressive style enables valid code but returns modest. May need bond-specific template.',
                'warning': 'V1.4 predictions were overly optimistic. Current performance below expectations.'
            },

            'IWM': {
                'type': 'equity_small',
                'performance_tier': 'D-TIER',  # NEW in V1.5

                # Parameters
                'sma_fast': 8,
                'sma_slow': 21,
                'rsi_threshold': 40,
                'position_size': 15,
                'temperature': 0.5,
                'population': 30,
                'prompt_style': 'aggressive',  # CHANGED from 'conservative' in V1.4

                # Expected Performance
                'expected_return_pct': (15, 25),
                'expected_sharpe': (0.3, 0.5),
                'expected_positive_rate': (60, 70),
                'expected_valid_rate': (40, 50),

                # Validation Evidence
                'validation_data': {
                    'day20': {'valid': '13/30 (43%)', 'return': '20.65%', 'sharpe': 0.41, 'positive': '61.5%'}
                },

                'confidence': 'LOW',
                'recommendation': 'MINIMAL/NO ALLOCATION - Weak performer',
                'rationale': 'IWM worst performer. Low returns (20.65%), low positive rate (61.5%), lowest Sharpe (0.41). Day 21 portfolio optimization assigned 0% weight.',
                'warning': 'Consider excluding from portfolio. Training period shows -84% returns.'
            },

            'XLE': {
                'type': 'commodity_energy',
                'performance_tier': 'F-TIER',  # NEW in V1.5

                # Parameters
                'sma_fast': 3,
                'sma_slow': 10,
                'rsi_threshold': 32,
                'position_size': 20,
                'temperature': 0.5,
                'population': 25,
                'prompt_style': 'aggressive',

                # Expected Performance
                'expected_return_pct': (-30, 0),  # Based on Day 24 reality
                'expected_sharpe': (-1.5, -0.1),
                'expected_positive_rate': (0, 10),
                'expected_valid_rate': (30, 40),

                # Validation Evidence
                'validation_data': {
                    'day24': {'valid': '9/25 (36%)', 'return': '-2.75% to -26.7%', 'sharpe': -0.13, 'positive': '0%'}
                },

                'confidence': 'HIGH',  # High confidence in AVOIDANCE
                'recommendation': 'DO NOT USE - Severe overfitting detected',
                'rationale': 'XLE shows catastrophic overfitting (train +42-83%, test -2.7 to -26.7%). Train-test correlation -0.85. Market regime shift 2020-2022 (recovery) vs 2023 (stabilization).',
                'warning': '[CRITICAL] AVOID THIS ASSET - ALL strategies lost money despite valid code. Severe market regime mismatch.'
            }
        }

    def get_config(self, asset_symbol):
        """
        获取资产的自适应配置

        Args:
            asset_symbol: 资产代码 (如 'QQQ', 'SPY', 'TLT')

        Returns:
            dict: 资产配置字典
        """
        if asset_symbol in self.asset_configs:
            config = self.asset_configs[asset_symbol].copy()

            # 添加版本信息
            config['framework_version'] = self.version
            config['validation_date'] = self.validation_date

            return config
        else:
            # 默认配置 (使用aggressive作为唯一工作配置)
            return {
                'type': 'unknown',
                'performance_tier': 'UNVALIDATED',
                'sma_fast': 5,
                'sma_slow': 10,
                'rsi_threshold': 35,
                'position_size': 20,
                'temperature': 0.5,
                'population': 20,
                'prompt_style': 'aggressive',  # DEFAULT to aggressive
                'confidence': 'UNKNOWN',
                'warning': f'Asset {asset_symbol} not in framework. Using default aggressive configuration.',
                'framework_version': self.version
            }

    def generate_command(self, asset_symbol, base_path='/root/autodl-tmp'):
        """
        生成运行命令

        Args:
            asset_symbol: 资产代码
            base_path: 服务器基础路径

        Returns:
            str: 可执行的bash命令
        """
        config = self.get_config(asset_symbol)

        cmd = f"""/root/miniconda3/envs/eoh1/bin/python {base_path}/eoh/eoh_gpu_loop_fixed.py \\
    --model-dir {base_path}/models/Meta-Llama-3.1-8B-Instruct \\
    --symbol {asset_symbol} \\
    --population {config['population']} \\
    --temperature {config['temperature']} \\
    --prompt-style {config['prompt_style']} \\
    --prompt-dir {base_path}/eoh/prompts_day19 \\
    --outdir {base_path}/outputs/v15_{asset_symbol.lower()} \\
    --train-start 2020-01-01 \\
    --train-end 2022-12-31 \\
    --test-start 2023-01-01 \\
    --test-end 2023-12-31"""

        return cmd

    def print_config(self, asset_symbol):
        """打印资产配置（详细版本）"""
        config = self.get_config(asset_symbol)

        print(f"\n{'='*70}")
        print(f"Asset: {asset_symbol}")
        print(f"Type: {config.get('type', 'unknown')}")
        print(f"Performance Tier: {config.get('performance_tier', 'UNVALIDATED')}")
        print(f"Framework Version: V{config.get('framework_version', 'unknown')}")
        print(f"{'='*70}")

        print(f"\n[Parameters]")
        print(f"  SMA Fast/Slow: {config['sma_fast']}/{config['sma_slow']}")
        print(f"  RSI Threshold: {config['rsi_threshold']}")
        print(f"  Position Size: {config['position_size']}")
        print(f"  Temperature: {config['temperature']}")
        print(f"  Population: {config['population']}")
        print(f"  Prompt Style: {config['prompt_style']}")

        if 'expected_return_pct' in config:
            print(f"\n[Expected Performance]")
            ret_range = config['expected_return_pct']
            print(f"  Return: {ret_range[0]}-{ret_range[1]}%")
            sharpe_range = config['expected_sharpe']
            print(f"  Sharpe: {sharpe_range[0]:.2f}-{sharpe_range[1]:.2f}")
            pos_range = config['expected_positive_rate']
            print(f"  Positive Rate: {pos_range[0]}-{pos_range[1]}%")

        if 'validation_data' in config:
            print(f"\n[Validation Evidence]")
            for exp_name, exp_data in config['validation_data'].items():
                print(f"  {exp_name}:")
                for key, value in exp_data.items():
                    print(f"    {key}: {value}")

        print(f"\n[Assessment]")
        print(f"  Confidence: {config.get('confidence', 'UNKNOWN')}")
        print(f"  Recommendation: {config.get('recommendation', 'N/A')}")
        print(f"  Rationale: {config.get('rationale', 'N/A')}")

        if 'warning' in config:
            print(f"\n[!] WARNING: {config['warning']}")

        print(f"{'='*70}")

    def get_tier_summary(self):
        """获取性能分级汇总"""
        tiers = {}
        for symbol, config in self.asset_configs.items():
            tier = config.get('performance_tier', 'UNVALIDATED')
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(symbol)

        return tiers

    def print_tier_summary(self):
        """打印性能分级汇总"""
        print("\n" + "="*70)
        print("V1.5 Framework Performance Tier Summary")
        print("="*70)

        tiers = self.get_tier_summary()
        tier_order = ['S-TIER', 'A-TIER', 'B-TIER', 'C-TIER', 'D-TIER', 'F-TIER']

        for tier in tier_order:
            if tier in tiers:
                assets = ', '.join(tiers[tier])
                print(f"\n{tier}: {assets}")

                # 打印每个资产的简要信息
                for symbol in tiers[tier]:
                    config = self.asset_configs[symbol]
                    rec = config.get('recommendation', 'N/A')
                    print(f"  - {symbol}: {rec}")

        print("\n" + "="*70)
        print("CRITICAL V1.5 UPDATE:")
        print("  [OK] All prompt styles changed to 'aggressive' (ONLY working style)")
        print("  [!] TLT expectations lowered (0-5% vs V1.4's 5-10%)")
        print("  [BEST] QQQ upgraded to S-TIER (124% avg, 100% positive)")
        print("  [X] XLE marked F-TIER (DO NOT USE - all negative)")
        print("="*70)


def main():
    """主程序 - 展示V1.5框架"""
    framework = AssetAdaptiveFramework()

    print("=" * 80)
    print("Asset Adaptive Framework V1.5 - Day 26 Validated")
    print("=" * 80)
    print(f"Version: {framework.version}")
    print(f"Validation Date: {framework.validation_date}")
    print(f"Validated Prompt Styles: {', '.join(framework.validated_prompt_styles)}")
    print("=" * 80)

    # 打印性能分级汇总
    framework.print_tier_summary()

    # 打印所有资产详细配置
    print("\n\n" + "=" * 80)
    print("Detailed Asset Configurations")
    print("=" * 80)

    tier_order = ['S-TIER', 'A-TIER', 'B-TIER', 'C-TIER', 'D-TIER', 'F-TIER']
    tiers = framework.get_tier_summary()

    for tier in tier_order:
        if tier in tiers:
            for symbol in tiers[tier]:
                framework.print_config(symbol)
                print(f"\n[Generated Command]")
                print(framework.generate_command(symbol))
                print()


if __name__ == '__main__':
    main()
