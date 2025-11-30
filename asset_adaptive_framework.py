#!/usr/bin/env python3
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
/root/miniconda3/envs/eoh1/bin/python {base_path}/eoh/eoh_gpu_loop_fixed.py \\
    --model-dir {base_path}/models/Meta-Llama-3.1-8B-Instruct \\
    --symbol {asset_symbol} \\
    --population {config['population']} \\
    --temperature {config['temperature']} \\
    --prompt-style {config['prompt_style']} \\
    --prompt-dir {base_path}/eoh/prompts_day19 \\
    --outdir {base_path}/outputs/day24_adaptive_{asset_symbol.lower()} \\
    --train-start 2020-01-01 \\
    --train-end 2022-12-31 \\
    --test-start 2023-01-01 \\
    --test-end 2023-12-31
"""
        return cmd.strip()

    def print_config(self, asset_symbol):
        """打印资产配置"""
        config = self.get_config(asset_symbol)
        print(f"\n{'='*60}")
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
    assets = ['SPY', 'QQQ', 'IWM', 'GLD', 'TLT', 'XLE']

    print("=" * 80)
    print("Day 24-25: 资产自适应框架 V1.4 验证")
    print("=" * 80)
    print()

    for asset in assets:
        framework.print_config(asset)
        print(f"\n运行命令:")
        print(framework.generate_command(asset))
        print()
