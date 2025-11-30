#!/usr/bin/env python3
"""
Experiment 4: Trading Strategy Generation (Extended Data)
扩展数据交易策略生成实验 - 使用18只股票、15年数据

对比：基线提示 vs 多层次提示
使用本地LLM模型 (Meta-Llama-3.1-8B-Instruct)
"""

import os
import json
import time
import sys
import ast
import random
import numpy as np
import torch
from pathlib import Path
from datetime import datetime
import importlib.util
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed

# ============================================================================
# 配置
# ============================================================================

# 固定随机种子以确保可复现性
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
set_seed(SEED)

# 模型配置
MODEL_PATH = "/root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 实验配置
NUM_SAMPLES_PER_GROUP = 30  # 每组生成30个样本
DATA_DIR = Path('/root/autodl-tmp/eoh/backtest_data_extended')
OUTPUT_DIR = Path('/root/autodl-tmp/eoh/experiment4_trading_extended')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 生成参数
GENERATION_CONFIG = {
    "max_new_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": True,
}

# 策略类型列表
STRATEGY_TYPES = [
    "Trend Following Strategy using Moving Averages",
    "Mean Reversion Strategy using Bollinger Bands",
    "Momentum Strategy using RSI and MACD",
    "Volatility Breakout Strategy using ATR",
    "Price-Volume Strategy",
    "Multi-Factor Comprehensive Strategy",
]

# ============================================================================
# Prompt模板
# ============================================================================

BASELINE_PROMPT = '''Write a backtrader trading strategy code.

Requirements:
1. Inherit from bt.Strategy class
2. Implement __init__ and next methods
3. Strategy type: {strategy_type}
4. Include stop-loss and take-profit logic

Output Python code directly, no explanations.
'''

MULTILAYER_PROMPT = '''You are a senior quantitative trading expert, proficient in A-share market and backtrader framework.

## Task Background
We are developing a quantitative trading system for A-shares and need to generate high-quality trading strategy code.

## Market Data Overview
- Data Range: 2010-2025 (15 years historical data)
- Stock Pool: 18 A-share blue-chip stocks across finance, consumer, tech, pharma, manufacturing, real estate, energy sectors
- Data Fields: date, open, high, low, close, volume

## Strategy Requirements
Strategy Type: {strategy_type}

### Must Implement:
1. **Indicator Calculation**: Initialize technical indicators in __init__
2. **Signal Generation**: Implement buy/sell signal logic in next
3. **Risk Management**:
   - Stop Loss: 4-5%
   - Take Profit: 8-15%
   - Position Management: Each trade no more than 30% of total capital
4. **Order Management**: Handle pending orders, avoid duplicate orders

### Code Quality Requirements:
- Complete class definition, can run directly
- Clear parameter definitions (using params tuple)
- Comprehensive logging
- Exception handling

### Output Format:
Output complete Python code directly, including necessary import statements. Do not add explanations or markdown markers.

## Example Structure:
```python
import backtrader as bt

class StrategyName(bt.Strategy):
    params = (
        ('param1', value1),
    )

    def __init__(self):
        # Initialize indicators
        self.order = None

    def next(self):
        # Trading logic
        pass
```

Now please generate the strategy code:
'''

# ============================================================================
# 模型加载
# ============================================================================

def load_model():
    """加载本地LLM模型"""
    print(f"Loading model from {MODEL_PATH}...")
    print(f"Device: {DEVICE}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        device_map="auto" if DEVICE == "cuda" else None,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("Model loaded successfully!")
    return tokenizer, model

# ============================================================================
# 代码生成
# ============================================================================

def generate_strategy(tokenizer, model, prompt: str, strategy_type: str) -> str:
    """使用本地LLM生成策略代码"""
    full_prompt = prompt.format(strategy_type=strategy_type)

    # 构建对话格式
    messages = [
        {"role": "system", "content": "You are a professional quantitative trading strategy developer."},
        {"role": "user", "content": full_prompt}
    ]

    # 应用聊天模板
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=GENERATION_CONFIG["max_new_tokens"],
            temperature=GENERATION_CONFIG["temperature"],
            top_p=GENERATION_CONFIG["top_p"],
            do_sample=GENERATION_CONFIG["do_sample"],
            pad_token_id=tokenizer.pad_token_id,
        )

    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    return response

# ============================================================================
# 代码验证
# ============================================================================

def validate_strategy(code: str) -> dict:
    """验证策略代码"""
    result = {
        'syntax_valid': False,
        'has_class': False,
        'has_init': False,
        'has_next': False,
        'errors': []
    }

    # 语法检查
    try:
        compile(code, '<string>', 'exec')
        result['syntax_valid'] = True
    except SyntaxError as e:
        result['errors'].append(f"SyntaxError: {e}")
        return result

    # 结构检查
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                result['has_class'] = True
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name == '__init__':
                            result['has_init'] = True
                        if item.name == 'next':
                            result['has_next'] = True
    except:
        pass

    return result

# ============================================================================
# 回测
# ============================================================================

def backtest_strategy(code: str, data_file: Path) -> dict:
    """运行回测"""
    import backtrader as bt
    import pandas as pd

    result = {
        'success': False,
        'error': None,
        'return_pct': 0,
        'sharpe': None,
        'max_drawdown': 0,
        'trades': 0
    }

    try:
        # 动态加载策略
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        module_name = f"temp_strat_{int(time.time()*1000)}"
        spec = importlib.util.spec_from_file_location(module_name, temp_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # 查找策略类
        strategy_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                strategy_class = obj
                break

        if not strategy_class:
            result['error'] = "No strategy class found"
            return result

        # 加载数据
        df = pd.read_csv(data_file)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df.columns = ['open', 'high', 'low', 'close', 'volume'][:len(df.columns)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)

        # 运行回测
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class)

        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)

        cerebro.broker.setcash(100000)
        cerebro.broker.setcommission(commission=0.001)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        initial = cerebro.broker.getvalue()
        results = cerebro.run()
        final = cerebro.broker.getvalue()

        strat = results[0]
        sharpe = strat.analyzers.sharpe.get_analysis()
        dd = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()

        result['success'] = True
        result['return_pct'] = (final - initial) / initial * 100
        result['sharpe'] = sharpe.get('sharperatio')
        result['max_drawdown'] = dd.get('max', {}).get('drawdown', 0)
        result['trades'] = trades.get('total', {}).get('total', 0)

        # 清理
        os.unlink(temp_path)

    except Exception as e:
        result['error'] = str(e)[:200]

    return result

# ============================================================================
# 清理代码
# ============================================================================

def clean_code(code: str) -> str:
    """清理LLM生成的代码"""
    # 移除markdown代码块
    if '```python' in code:
        code = code.split('```python')[1].split('```')[0]
    elif '```' in code:
        parts = code.split('```')
        if len(parts) >= 2:
            code = parts[1]

    # 移除开头的解释文字（找到import或class开始）
    lines = code.split('\n')
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from ') or line.strip().startswith('class '):
            start_idx = i
            break

    code = '\n'.join(lines[start_idx:])
    return code.strip()

# ============================================================================
# 主实验函数
# ============================================================================

def run_experiment():
    """运行完整实验"""
    print("="*80)
    print("Experiment 4: Trading Strategy Generation (Extended Data)")
    print("="*80)
    print(f"Time: {datetime.now()}")
    print(f"Samples: {NUM_SAMPLES_PER_GROUP} per group")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print()

    # 加载模型
    print("[1/4] Loading LLM model...")
    tokenizer, model = load_model()
    print("  OK")

    # 获取测试数据文件
    data_files = sorted(DATA_DIR.glob('stock_*.csv'))[:5]  # 使用5只股票测试
    print(f"[2/4] Test data: {len(data_files)} stocks")
    for df in data_files:
        print(f"  - {df.name}")

    # 创建输出目录
    baseline_dir = OUTPUT_DIR / 'baseline'
    multilayer_dir = OUTPUT_DIR / 'multilayer'
    baseline_dir.mkdir(exist_ok=True)
    multilayer_dir.mkdir(exist_ok=True)

    results = {
        'baseline': [],
        'multilayer': [],
        'meta': {
            'start_time': datetime.now().isoformat(),
            'num_samples': NUM_SAMPLES_PER_GROUP,
            'model': MODEL_PATH,
            'data_files': [f.name for f in data_files]
        }
    }

    # 生成策略
    print(f"\n[3/4] Generating strategies ({NUM_SAMPLES_PER_GROUP * 2} total)...")

    for i in range(NUM_SAMPLES_PER_GROUP):
        strategy_type = STRATEGY_TYPES[i % len(STRATEGY_TYPES)]

        # 基线组
        print(f"\n--- Baseline #{i+1}: {strategy_type[:30]}...")
        try:
            code = generate_strategy(tokenizer, model, BASELINE_PROMPT, strategy_type)
            code = clean_code(code)

            # 保存
            save_path = baseline_dir / f'strategy_{i+1:03d}.py'
            with open(save_path, 'w') as f:
                f.write(code)

            # 验证
            validation = validate_strategy(code)

            # 回测 (使用第一个数据文件)
            backtest = backtest_strategy(code, data_files[0]) if validation['syntax_valid'] else {'success': False}

            results['baseline'].append({
                'id': i+1,
                'strategy_type': strategy_type,
                'validation': validation,
                'backtest': backtest,
                'code_length': len(code)
            })

            status = "OK" if backtest.get('success') else "FAIL"
            print(f"  [{status}] {len(code)} chars, Return: {backtest.get('return_pct', 0):.2f}%")
        except Exception as e:
            print(f"  [ERROR] {str(e)[:50]}")
            results['baseline'].append({
                'id': i+1,
                'strategy_type': strategy_type,
                'error': str(e)[:100]
            })

        # 多层次组
        print(f"--- Multilayer #{i+1}: {strategy_type[:30]}...")
        try:
            code = generate_strategy(tokenizer, model, MULTILAYER_PROMPT, strategy_type)
            code = clean_code(code)

            # 保存
            save_path = multilayer_dir / f'strategy_{i+1:03d}.py'
            with open(save_path, 'w') as f:
                f.write(code)

            # 验证
            validation = validate_strategy(code)

            # 回测
            backtest = backtest_strategy(code, data_files[0]) if validation['syntax_valid'] else {'success': False}

            results['multilayer'].append({
                'id': i+1,
                'strategy_type': strategy_type,
                'validation': validation,
                'backtest': backtest,
                'code_length': len(code)
            })

            status = "OK" if backtest.get('success') else "FAIL"
            print(f"  [{status}] {len(code)} chars, Return: {backtest.get('return_pct', 0):.2f}%")
        except Exception as e:
            print(f"  [ERROR] {str(e)[:50]}")
            results['multilayer'].append({
                'id': i+1,
                'strategy_type': strategy_type,
                'error': str(e)[:100]
            })

    # 汇总统计
    print("\n[4/4] Statistics summary...")

    results['meta']['end_time'] = datetime.now().isoformat()

    # 基线组统计
    baseline_valid = sum(1 for r in results['baseline'] if r.get('validation', {}).get('syntax_valid'))
    baseline_runnable = sum(1 for r in results['baseline'] if r.get('backtest', {}).get('success'))
    baseline_returns = [r['backtest']['return_pct'] for r in results['baseline'] if r.get('backtest', {}).get('success')]

    # 多层次组统计
    multi_valid = sum(1 for r in results['multilayer'] if r.get('validation', {}).get('syntax_valid'))
    multi_runnable = sum(1 for r in results['multilayer'] if r.get('backtest', {}).get('success'))
    multi_returns = [r['backtest']['return_pct'] for r in results['multilayer'] if r.get('backtest', {}).get('success')]

    results['summary'] = {
        'baseline': {
            'total': len(results['baseline']),
            'syntax_valid': baseline_valid,
            'runnable': baseline_runnable,
            'avg_return': sum(baseline_returns) / len(baseline_returns) if baseline_returns else 0,
            'avg_code_length': sum(r.get('code_length', 0) for r in results['baseline']) / len(results['baseline']) if results['baseline'] else 0
        },
        'multilayer': {
            'total': len(results['multilayer']),
            'syntax_valid': multi_valid,
            'runnable': multi_runnable,
            'avg_return': sum(multi_returns) / len(multi_returns) if multi_returns else 0,
            'avg_code_length': sum(r.get('code_length', 0) for r in results['multilayer']) / len(results['multilayer']) if results['multilayer'] else 0
        }
    }

    # 保存结果
    results_file = OUTPUT_DIR / 'experiment_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    # 打印汇总
    print("\n" + "="*80)
    print("EXPERIMENT RESULTS SUMMARY")
    print("="*80)
    print(f"\nBaseline Group:")
    print(f"  Syntax Valid: {baseline_valid}/{NUM_SAMPLES_PER_GROUP} ({baseline_valid/NUM_SAMPLES_PER_GROUP*100:.1f}%)")
    print(f"  Runnable: {baseline_runnable}/{NUM_SAMPLES_PER_GROUP} ({baseline_runnable/NUM_SAMPLES_PER_GROUP*100:.1f}%)")
    print(f"  Avg Return: {results['summary']['baseline']['avg_return']:.2f}%")
    print(f"  Avg Code Length: {results['summary']['baseline']['avg_code_length']:.0f} chars")

    print(f"\nMultilayer Group:")
    print(f"  Syntax Valid: {multi_valid}/{NUM_SAMPLES_PER_GROUP} ({multi_valid/NUM_SAMPLES_PER_GROUP*100:.1f}%)")
    print(f"  Runnable: {multi_runnable}/{NUM_SAMPLES_PER_GROUP} ({multi_runnable/NUM_SAMPLES_PER_GROUP*100:.1f}%)")
    print(f"  Avg Return: {results['summary']['multilayer']['avg_return']:.2f}%")
    print(f"  Avg Code Length: {results['summary']['multilayer']['avg_code_length']:.0f} chars")

    print(f"\nResults saved: {results_file}")
    print("="*80)

    return results


if __name__ == '__main__':
    run_experiment()
