#!/usr/bin/env python3
"""
扩展数据交易策略生成实验
使用18只股票、15年数据生成和评估交易策略

对比：基线提示 vs 多层次提示
"""

import os
import json
import time
import sys
from pathlib import Path
from datetime import datetime
import importlib.util

# 配置
DATA_DIR = Path('/root/autodl-tmp/eoh/backtest_data_extended')
OUTPUT_DIR = Path('/root/autodl-tmp/eoh/experiment_trading_extended')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 样本数量
NUM_SAMPLES = 30  # 每组30个策略

# 策略类型列表
STRATEGY_TYPES = [
    "趋势跟踪策略 (使用移动平均线)",
    "均值回归策略 (使用布林带)",
    "动量策略 (使用RSI和MACD)",
    "波动率突破策略 (使用ATR)",
    "价量配合策略",
    "多因子综合策略",
]

# 基线提示模板
BASELINE_PROMPT = '''请生成一个backtrader交易策略代码。

要求:
1. 继承bt.Strategy类
2. 实现__init__和next方法
3. 策略类型: {strategy_type}
4. 包含止损和止盈逻辑

直接输出Python代码,不要解释。
'''

# 多层次提示模板
MULTILAYER_PROMPT = '''你是一位资深量化交易专家,精通A股市场和backtrader框架。

## 任务背景
我们正在开发一套A股量化交易系统,需要生成高质量的交易策略代码。

## 市场数据概况
- 数据范围: 2010-2025年 (15年历史数据)
- 股票池: 18只A股蓝筹股,覆盖金融、消费、科技、医药、制造、地产、能源等行业
- 数据字段: date, open, high, low, close, volume

## 策略要求
策略类型: {strategy_type}

### 必须实现的功能:
1. **指标计算**: 在__init__中初始化所需技术指标
2. **信号生成**: 在next中实现买卖信号逻辑
3. **风险管理**:
   - 止损: 4-5%
   - 止盈: 8-15%
   - 仓位管理: 每次交易不超过总资金的30%
4. **订单管理**: 处理pending订单,避免重复下单

### 代码质量要求:
- 完整的类定义,可直接运行
- 清晰的参数定义(使用params元组)
- 完善的日志记录
- 异常处理

### 输出格式:
直接输出完整的Python代码,包含必要的import语句。不要添加解释或markdown标记。

## 示例结构:
```python
import backtrader as bt

class StrategyName(bt.Strategy):
    params = (
        ('param1', value1),
    )

    def __init__(self):
        # 初始化指标
        self.order = None

    def next(self):
        # 交易逻辑
        pass
```

现在请生成策略代码:
'''


def setup_llm():
    """初始化LLM客户端"""
    from openai import OpenAI

    # 尝试不同的API配置
    api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('DASHSCOPE_API_KEY')
    base_url = os.environ.get('OPENAI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')

    if not api_key:
        # 尝试从配置文件读取
        config_path = Path('/root/autodl-tmp/eoh/.env')
        if config_path.exists():
            with open(config_path) as f:
                for line in f:
                    if 'API_KEY' in line:
                        api_key = line.split('=')[1].strip()
                        break

    client = OpenAI(api_key=api_key, base_url=base_url)
    return client


def generate_strategy(client, prompt: str, strategy_type: str) -> str:
    """调用LLM生成策略代码"""
    full_prompt = prompt.format(strategy_type=strategy_type)

    try:
        response = client.chat.completions.create(
            model="qwen-plus",  # 或 qwen-turbo
            messages=[
                {"role": "system", "content": "你是一位专业的量化交易策略开发专家。"},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"  [ERROR] LLM调用失败: {e}")
        return None


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
    import ast
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


def run_experiment():
    """运行完整实验"""
    print("="*80)
    print("扩展数据交易策略生成实验")
    print("="*80)
    print(f"时间: {datetime.now()}")
    print(f"样本数: 每组 {NUM_SAMPLES} 个")
    print(f"数据目录: {DATA_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print()

    # 初始化LLM
    print("[1/4] 初始化LLM...")
    client = setup_llm()
    print("  OK")

    # 获取测试数据文件
    data_files = list(DATA_DIR.glob('stock_*.csv'))[:5]  # 使用5只股票测试
    print(f"[2/4] 测试数据: {len(data_files)} 只股票")

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
            'num_samples': NUM_SAMPLES,
            'data_files': [f.name for f in data_files]
        }
    }

    # 生成策略
    print(f"\n[3/4] 生成策略 (共 {NUM_SAMPLES * 2} 个)...")

    for i in range(NUM_SAMPLES):
        strategy_type = STRATEGY_TYPES[i % len(STRATEGY_TYPES)]

        # 基线组
        print(f"\n--- 基线 #{i+1}: {strategy_type[:20]}...")
        code = generate_strategy(client, BASELINE_PROMPT, strategy_type)
        if code:
            # 清理代码
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0]
            elif '```' in code:
                code = code.split('```')[1].split('```')[0]

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

        time.sleep(1)  # 避免API限流

        # 多层次组
        print(f"--- 多层次 #{i+1}: {strategy_type[:20]}...")
        code = generate_strategy(client, MULTILAYER_PROMPT, strategy_type)
        if code:
            # 清理代码
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0]
            elif '```' in code:
                code = code.split('```')[1].split('```')[0]

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

        time.sleep(1)

    # 汇总统计
    print("\n[4/4] 统计汇总...")

    results['meta']['end_time'] = datetime.now().isoformat()

    # 基线组统计
    baseline_valid = sum(1 for r in results['baseline'] if r['validation']['syntax_valid'])
    baseline_runnable = sum(1 for r in results['baseline'] if r['backtest'].get('success'))
    baseline_returns = [r['backtest']['return_pct'] for r in results['baseline'] if r['backtest'].get('success')]

    # 多层次组统计
    multi_valid = sum(1 for r in results['multilayer'] if r['validation']['syntax_valid'])
    multi_runnable = sum(1 for r in results['multilayer'] if r['backtest'].get('success'))
    multi_returns = [r['backtest']['return_pct'] for r in results['multilayer'] if r['backtest'].get('success')]

    results['summary'] = {
        'baseline': {
            'total': len(results['baseline']),
            'syntax_valid': baseline_valid,
            'runnable': baseline_runnable,
            'avg_return': sum(baseline_returns) / len(baseline_returns) if baseline_returns else 0,
            'avg_code_length': sum(r['code_length'] for r in results['baseline']) / len(results['baseline']) if results['baseline'] else 0
        },
        'multilayer': {
            'total': len(results['multilayer']),
            'syntax_valid': multi_valid,
            'runnable': multi_runnable,
            'avg_return': sum(multi_returns) / len(multi_returns) if multi_returns else 0,
            'avg_code_length': sum(r['code_length'] for r in results['multilayer']) / len(results['multilayer']) if results['multilayer'] else 0
        }
    }

    # 保存结果
    results_file = OUTPUT_DIR / 'experiment_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    # 打印汇总
    print("\n" + "="*80)
    print("实验结果汇总")
    print("="*80)
    print(f"\n基线组 (Baseline):")
    print(f"  语法正确: {baseline_valid}/{NUM_SAMPLES} ({baseline_valid/NUM_SAMPLES*100:.1f}%)")
    print(f"  可执行: {baseline_runnable}/{NUM_SAMPLES} ({baseline_runnable/NUM_SAMPLES*100:.1f}%)")
    print(f"  平均收益: {results['summary']['baseline']['avg_return']:.2f}%")
    print(f"  平均代码长度: {results['summary']['baseline']['avg_code_length']:.0f} chars")

    print(f"\n多层次组 (Multilayer):")
    print(f"  语法正确: {multi_valid}/{NUM_SAMPLES} ({multi_valid/NUM_SAMPLES*100:.1f}%)")
    print(f"  可执行: {multi_runnable}/{NUM_SAMPLES} ({multi_runnable/NUM_SAMPLES*100:.1f}%)")
    print(f"  平均收益: {results['summary']['multilayer']['avg_return']:.2f}%")
    print(f"  平均代码长度: {results['summary']['multilayer']['avg_code_length']:.0f} chars")

    print(f"\n结果保存: {results_file}")
    print("="*80)

    return results


if __name__ == '__main__':
    run_experiment()
