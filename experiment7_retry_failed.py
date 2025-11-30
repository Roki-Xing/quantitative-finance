#!/usr/bin/env python3
"""
Experiment 7 Retry: 重新生成3个超时失败的策略
"""
import requests
import json
from pathlib import Path
from datetime import datetime

# 配置
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/experiment7_evolved_strategies")
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:7b"

# 只重试3个失败的策略,增加超时时间到300秒
RETRY_PROMPTS = [
    {
        "name": "mutation1_optimize_007",
        "description": "优化strategy_007: 改进参数和止损逻辑",
        "prompt": """You are an expert quantitative trading strategy developer.

I have a successful trend-following strategy (收益2.93%) that uses dual moving averages.

**Current Strategy Summary:**
- Dual SMA (20/50 periods)
- Dynamic position sizing (2% risk per trade)
- Stop-loss: 5%, Take-profit: 10%
- Supports both long and short positions

**Your Task:**
Create an IMPROVED version by:
1. Optimizing parameters (MA periods, risk%, stop-loss/take-profit levels)
2. Adding adaptive stop-loss based on market volatility
3. Improving exit logic to capture more profit

**Requirements:**
- Must be valid Python code using backtrader framework
- Class name: EnhancedTrendFollowing
- Include proper order management (self.order, self.entry_price, notify_order)
- Use btind.SMA, btind.ATR for indicators
- NO self.log() calls (not available in backtrader)
- Target: >3% return

Output ONLY the complete Python code, no explanations."""
    },
    {
        "name": "mutation2_enhance_022",
        "description": "增强strategy_022: 改进ATR过滤条件",
        "prompt": """You are an expert quantitative trading strategy developer.

I have a volatility breakout strategy (收益0.75%) that uses dual MA + ATR filtering.

**Current Strategy Summary:**
- Fast MA (14) / Slow MA (28)
- ATR filter: only enter when ATR is increasing
- Breakout entry on MA crossover with volatility confirmation

**Your Task:**
Create an IMPROVED version by:
1. Adding more sophisticated ATR-based entry filters
2. Implementing dynamic take-profit based on ATR multiples
3. Adding volume confirmation for breakouts
4. Optimizing MA periods for better trend capture

**Requirements:**
- Must be valid Python code using backtrader framework
- Class name: AdvancedVolatilityBreakout
- Include proper order management
- Use btind.SMA, btind.ATR, btind.Volume
- NO self.log() calls
- Target: >3% return

Output ONLY the complete Python code, no explanations."""
    },
    {
        "name": "crossover1_position_atr",
        "description": "交叉1: strategy_007仓位管理 + strategy_022的ATR过滤",
        "prompt": """You are an expert quantitative trading strategy developer.

I want to combine the best features from two successful strategies:
- Strategy A (2.93%): Dynamic position sizing (2% risk per trade)
- Strategy B (0.75%): ATR-based volatility filtering

**Your Task:**
Create a NEW strategy that combines:
1. Dynamic position sizing from Strategy A (broker.getvalue() * risk / price)
2. ATR volatility filter from Strategy B (only enter when ATR increasing)
3. Dual moving averages for trend identification
4. ATR-based stop-loss (e.g., entry_price - 2*ATR)

**Requirements:**
- Must be valid Python code using backtrader framework
- Class name: HybridTrendATR
- Include self.order, self.entry_price, notify_order()
- Use btind.SMA for trend, btind.ATR for filtering and stops
- NO self.log() calls
- Target: >3.5% return

Output ONLY the complete Python code, no explanations."""
    }
]

def call_ollama(prompt):
    """调用Ollama API生成策略代码"""
    try:
        response = requests.post(
            OLLAMA_API,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            },
            timeout=300  # 增加到300秒
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def extract_python_code(text):
    """从LLM输出中提取Python代码"""
    if "```python" in text:
        start = text.find("```python") + 9
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()

    if "import backtrader" in text:
        start = text.find("import backtrader")
        return text[start:].strip()

    return text.strip()

def main():
    print("=" * 80)
    print("Experiment 7 Retry: 重新生成3个超时失败的策略")
    print("=" * 80)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模型: {MODEL}")
    print(f"超时时间: 300秒")
    print("=" * 80)

    results = []

    for idx, evolution in enumerate(RETRY_PROMPTS, 1):
        print(f"\n[{idx}/{len(RETRY_PROMPTS)}] {evolution['name']}")
        print(f"描述: {evolution['description']}")
        print("-" * 80)

        print("⏳ 调用LLM生成策略...")
        response = call_ollama(evolution['prompt'])

        if response.startswith("Error"):
            print(f"❌ 生成失败: {response}")
            results.append({
                "name": evolution['name'],
                "success": False,
                "error": response
            })
            continue

        print("✅ LLM响应成功,提取代码...")
        code = extract_python_code(response)

        if len(code) < 100:
            print(f"❌ 代码太短,可能提取失败 (长度: {len(code)})")
            results.append({
                "name": evolution['name'],
                "success": False,
                "error": "Code too short"
            })
            continue

        # 保存策略代码
        output_file = OUTPUT_DIR / f"{evolution['name']}.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(code)

        print(f"✅ 策略已保存: {output_file}")
        print(f"   代码长度: {len(code)} 字符")

        results.append({
            "name": evolution['name'],
            "success": True,
            "file": str(output_file),
            "code_length": len(code)
        })

    # 保存结果摘要
    summary_file = OUTPUT_DIR / "retry_summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "model": MODEL,
            "total": len(RETRY_PROMPTS),
            "success": sum(1 for r in results if r.get('success')),
            "results": results
        }, f, indent=2)

    print("\n" + "=" * 80)
    print("重试完成汇总")
    print("=" * 80)
    success_count = sum(1 for r in results if r.get('success'))
    print(f"成功: {success_count}/{len(results)}")
    print(f"结果保存: {summary_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
