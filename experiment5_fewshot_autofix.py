#!/usr/bin/env python3
"""
Experiment 5: Few-shot Auto-fix
用3个修复示例教LLM自动修复剩余的broken策略
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# Configuration - 使用Ollama本地模型
client = OpenAI(
    api_key="ollama",  # Ollama不需要真实API key
    base_url="http://localhost:11434/v1"
)

BASE_DIR = Path("/root/autodl-tmp/eoh/experiment4_trading_extended/baseline")
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/experiment5_autofix")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 3个修复示例 (简化版展示关键修复模式)
FIX_EXAMPLES = """
## Example 1: MACD API修复
错误代码:
```python
self.macd = btind.MACD(self.data.close, fast=12, slow=26, signal=9)
```
修复后:
```python
self.macd = btind.MACD(self.data.close, period_me1=12, period_me2=26, period_signal=9)
```

## Example 2: 缩进错误修复
错误代码:
```python
if not self.position:
    if condition:
        self.buy()
else:
if self.data.close[0] > self.entry_price:  # 错误：else后面没有缩进
    self.close()
```
修复后:
```python
if not self.position:
    if condition:
        self.buy()
else:
    if self.data.close[0] > self.entry_price:  # 正确缩进
        self.close()
```

## Example 3: 不存在的API修复
错误代码:
```python
self.broker.set_stop_loss(0.05)  # 不存在的API
self.broker.set_take_profit(0.10)  # 不存在的API
```
修复后:
```python
# 删除不存在的API调用，手动实现止损止盈逻辑
if self.position.size > 0:
    if self.data.close[0] >= self.entry_price * (1 + self.p.take_profit):
        self.order = self.close()
    elif self.data.close[0] <= self.entry_price * (1 - self.p.stop_loss):
        self.order = self.close()
```

## Example 4: 订单管理修复
错误代码:
```python
def __init__(self):
    self.sma = btind.SMA(...)
    # 缺少order和entry_price追踪

def next(self):
    if not self.position:
        self.buy()
        self.buy()  # 重复调用
```
修复后:
```python
def __init__(self):
    self.sma = btind.SMA(...)
    self.order = None
    self.entry_price = None

def next(self):
    if self.order:
        return
    if not self.position:
        self.order = self.buy()
        self.entry_price = self.data.close[0]

def notify_order(self, order):
    if order.status in [order.Completed]:
        self.order = None
```
"""

SYSTEM_PROMPT = f"""你是一个backtrader策略修复专家。你的任务是修复有语法或API错误的策略代码。

常见错误模式和修复方法:
{FIX_EXAMPLES}

修复要求:
1. 保持策略的原始逻辑意图
2. 修复所有语法错误、缩进错误、API错误
3. 确保有完整的订单管理(self.order, self.entry_price)
4. 确保有notify_order方法
5. 只返回修复后的完整Python代码，不要解释

输出格式: 只返回修复后的Python代码，用```python和```包裹。
"""

def fix_strategy(broken_code: str, strategy_name: str) -> str:
    """用few-shot方式修复策略"""
    try:
        response = client.chat.completions.create(
            model="qwen2.5-coder:7b",  # Ollama本地模型
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"请修复以下策略代码 ({strategy_name}):\n\n```python\n{broken_code}\n```"}
            ],
            temperature=0.1,
            max_tokens=2000
        )

        content = response.choices[0].message.content

        # 提取代码
        if "```python" in content:
            code = content.split("```python")[1].split("```")[0].strip()
        elif "```" in content:
            code = content.split("```")[1].split("```")[0].strip()
        else:
            code = content.strip()

        return code
    except Exception as e:
        return f"# ERROR: {str(e)}"

def main():
    print("="*80)
    print("Experiment 5: Few-shot Auto-fix")
    print("="*80)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 需要修复的策略 (排除已修复的13个)
    fixed_strategies = {1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 15, 22}
    all_strategies = set(range(1, 31))
    broken_strategies = all_strategies - fixed_strategies

    print(f"\n待修复策略: {sorted(broken_strategies)}")
    print(f"共 {len(broken_strategies)} 个\n")

    results = []

    for idx in sorted(broken_strategies):
        strategy_file = BASE_DIR / f"strategy_{idx:03d}.py"

        if not strategy_file.exists():
            print(f"[strategy_{idx:03d}] 文件不存在，跳过")
            continue

        print(f"[strategy_{idx:03d}] 修复中...", end=" ")

        # 读取原始代码
        broken_code = strategy_file.read_text(encoding='utf-8')

        # 调用LLM修复
        start_time = time.time()
        fixed_code = fix_strategy(broken_code, f"strategy_{idx:03d}")
        elapsed = time.time() - start_time

        # 保存修复后的代码
        output_file = OUTPUT_DIR / f"strategy_{idx:03d}_autofix.py"
        output_file.write_text(fixed_code, encoding='utf-8')

        result = {
            "strategy": f"strategy_{idx:03d}",
            "time": elapsed,
            "output_file": str(output_file),
            "has_error": fixed_code.startswith("# ERROR:")
        }
        results.append(result)

        if result["has_error"]:
            print(f"❌ 错误 ({elapsed:.1f}s)")
        else:
            print(f"✅ 完成 ({elapsed:.1f}s)")

        time.sleep(0.5)  # Rate limiting

    # 保存结果
    results_file = OUTPUT_DIR / "autofix_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "total": len(results),
            "success": len([r for r in results if not r["has_error"]]),
            "results": results
        }, f, indent=2)

    print("\n" + "="*80)
    print("修复完成")
    print("="*80)
    print(f"成功: {len([r for r in results if not r['has_error']])}/{len(results)}")
    print(f"结果保存: {results_file}")
    print(f"修复文件: {OUTPUT_DIR}")
    print("\n下一步: 运行验证脚本测试修复后的策略")

if __name__ == "__main__":
    main()
