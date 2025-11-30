#!/usr/bin/env python3
"""
Phase 3 - Batch 1 Strategy Generation
生成第一批10个量化交易策略

使用Phase 1验证的多层次Prompt方法（HPDT）
每个策略包含4层结构：Safety → Functional → Quality → Template

Author: Phase 3 Day 40
Date: 2025-11-22
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
import json
import time
from datetime import datetime
import ast

# ============================================================================
# 配置
# ============================================================================

MODEL_PATH = "/root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct"
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/strategy_library/batch1")
METADATA_FILE = Path("/root/autodl-tmp/eoh/strategy_generation_batch1_metadata.json")

# 生成参数（基于Phase 2经验）
GEN_CONFIG = {
    "max_new_tokens": 2500,  # 策略代码约200-250行
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": True,
    "pad_token_id": None,  # 将在加载tokenizer后设置
}

# ============================================================================
# 策略定义（10个策略的完整Prompt）
# ============================================================================

# 由于每个策略的完整Prompt太长（包含250行代码模板），这里只包含关键部分
# 完整的Layer 4模板会在实际使用时插入

STRATEGIES = [
    {
        "id": 1,
        "name": "dual_ma_crossover",
        "display_name": "双均线交叉策略",
        "category": "趋势跟踪",
        "description": "20日均线上穿50日均线做多，下穿平仓",
        "prompt_layers": {
            "layer1_safety": """## Layer 1: Safety & Risk Constraints (CRITICAL)

### Data Integrity
- NEVER use future data in calculations (no lookahead bias)
- NEVER modify historical price data
- Use only OHLCV data available at the time of each bar
- Implement proper data alignment

### Risk Management (MANDATORY)
- Stop-loss: 5% from entry price
- Take-profit: 15% from entry price
- Maximum position size: 100% of capital
- No overlapping positions
- Log every entry and exit with reasons

### Error Handling
- Handle missing data gracefully
- Validate indicator calculations
- Ensure position exists before exit
- Log errors without crashing""",

            "layer2_functional": """## Layer 2: Functional Requirements

### Strategy Logic

**Entry Signal**:
- Fast MA (20-day SMA) crosses above Slow MA (50-day SMA)
- Confirm with closing price > Fast MA
- Enter at next bar's open price

**Exit Signal**:
- Fast MA crosses below Slow MA (normal exit)
- Stop-loss: Price falls 5% below entry
- Take-profit: Price rises 15% above entry
- Exit at next bar's open price

### Required Indicators
- Simple Moving Average (SMA) 20
- Simple Moving Average (SMA) 50
- Crossover detection

### Parameters (Configurable)
```python
fast_period = 20    # Fast MA period
slow_period = 50    # Slow MA period
stop_loss = 0.05    # 5% stop loss
take_profit = 0.15  # 15% take profit
```

### Required Libraries
```python
import backtrader as bt
import datetime
import logging
from typing import Optional
```""",

            "layer3_quality": """## Layer 3: Code Quality Standards

### Structure
- Inherit from bt.Strategy
- Separate parameter definition
- Clear method organization: __init__, next, notify_order, notify_trade
- Modular helper methods if needed

### Documentation
- Class docstring explaining strategy logic, rules, expected performance
- Method docstrings for all functions
- Inline comments for complex logic
- Parameter descriptions

### Logging
- INFO: Entry and exit signals
- WARNING: Stop-loss or take-profit triggered
- ERROR: Data issues or calculation errors
- Include timestamp, price, and reason for all trades

### Type Hints
- Type hints on all method parameters
- Return type annotations

### Best Practices
- Use bt.indicators for calculations
- Store entry price for stop-loss/take-profit tracking
- Use self.buy() and self.sell() for orders
- Track order status in notify_order()""",

            "layer4_template": """## Layer 4: Complete Backtrader Strategy Template

Generate a complete, production-ready Backtrader strategy class following this structure:

```python
#!/usr/bin/env python3
\"\"\"
Dual Moving Average Crossover Strategy

Strategy Rules:
- Entry: 20-day SMA crosses above 50-day SMA
- Exit: 20-day SMA crosses below 50-day SMA, or stop-loss/take-profit
- Stop-loss: 5% below entry
- Take-profit: 15% above entry

Expected Performance:
- Win rate: ~45%
- Profit factor: ~2:1
- Best for: Trending markets
\"\"\"

import backtrader as bt
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DualMAStrategy(bt.Strategy):
    \"\"\"Dual Moving Average Crossover - Classic Trend Following\"\"\"

    params = (
        ('fast_period', 20),
        ('slow_period', 50),
        ('stop_loss', 0.05),
        ('take_profit', 0.15),
    )

    def __init__(self):
        # Indicators
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

        # State tracking
        self.order = None
        self.entry_price = 0.0

    def notify_order(self, order):
        # Handle order notifications
        if order.status in [order.Completed]:
            if order.isbuy():
                logger.info(f"BUY at {order.executed.price:.2f}")
                self.entry_price = order.executed.price
            elif order.issell():
                logger.info(f"SELL at {order.executed.price:.2f}")
            self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            logger.info(f"TRADE CLOSED - PnL: {trade.pnl:.2f}")

    def next(self):
        if self.order:
            return

        if not self.position:
            # Entry logic
            if self.crossover > 0:
                size = self.broker.get_cash() / self.data.close[0]
                self.order = self.buy(size=size)
        else:
            # Exit logic
            current = self.data.close[0]
            if current <= self.entry_price * (1 - self.params.stop_loss):
                self.order = self.sell(size=self.position.size)
            elif current >= self.entry_price * (1 + self.params.take_profit):
                self.order = self.sell(size=self.position.size)
            elif self.crossover < 0:
                self.order = self.sell(size=self.position.size)
```

Generate the complete strategy code with all methods properly implemented, comprehensive docstrings, type hints, and logging."""
        }
    },

    # 策略2-10的定义会在实际生成时根据STRATEGY_BATCH1_PLAN.md补充
    # 这里先包含策略2作为示例

    {
        "id": 2,
        "name": "macd_zero_cross",
        "display_name": "MACD零轴穿越",
        "category": "趋势跟踪",
        "description": "MACD线上穿0轴做多，下穿平仓",
        "prompt_layers": {
            "layer1_safety": """## Layer 1: Safety & Risk Constraints (CRITICAL)

### Data Integrity
- No lookahead bias
- No data modification
- Only use OHLCV data

### Risk Management
- Stop-loss: 4% from entry
- Take-profit: 12% from entry
- Max position: 100%
- Log all trades

### Error Handling
- Handle missing data
- Validate MACD calculations
- Prevent position errors""",

            "layer2_functional": """## Layer 2: Functional Requirements

### Strategy Logic

**Entry Signal**:
- MACD line crosses above 0
- Enter at next bar open

**Exit Signal**:
- MACD line crosses below 0
- Stop-loss: -4%
- Take-profit: +12%

### Required Indicators
- MACD (12, 26, 9)
- Signal line

### Parameters
```python
macd_fast = 12
macd_slow = 26
macd_signal = 9
stop_loss = 0.04
take_profit = 0.12
```""",

            "layer3_quality": """## Layer 3: Code Quality Standards

- Inherit from bt.Strategy
- Comprehensive docstrings
- Type hints
- Logging (INFO/WARNING)
- Parameter configuration""",

            "layer4_template": """## Layer 4: Template

Generate a complete Backtrader strategy for MACD zero-cross with:
- MACD indicator (12, 26, 9)
- Zero-line crossover detection
- 4% stop-loss, 12% take-profit
- Full logging and error handling
- Class name: MACDZeroCrossStrategy"""
        }
    },
]

# 后续会添加策略3-10...

# ============================================================================
# 代码提取函数
# ============================================================================

def extract_code(text: str) -> str:
    """从LLM输出中提取Python代码（提取最长代码块）"""
    blocks = []
    pos = 0

    # 查找所有```python代码块
    while True:
        start = text.find('```python', pos)
        if start == -1:
            break

        code_start = start + len('```python')
        code_end = text.find('```', code_start)

        if code_end == -1:
            break

        code = text[code_start:code_end].strip()
        blocks.append(code)
        pos = code_end + 3

    if blocks:
        # 返回最长的代码块
        return max(blocks, key=len)

    # Fallback: 尝试提取```之间的代码
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            return parts[1].strip()

    # 如果没有代码块标记，返回整个文本
    return text.strip()

# ============================================================================
# 代码验证函数
# ============================================================================

def validate_strategy_code(code: str, strategy_name: str) -> dict:
    """验证生成的策略代码"""
    result = {
        "valid": False,
        "syntax_ok": False,
        "has_class": False,
        "has_init": False,
        "has_next": False,
        "has_notify_order": False,
        "has_logging": False,
        "has_docstring": False,
        "line_count": 0,
        "char_count": 0,
        "issues": []
    }

    # 基本检查
    result["line_count"] = len(code.splitlines())
    result["char_count"] = len(code)

    # 语法检查
    try:
        tree = ast.parse(code)
        result["syntax_ok"] = True
    except SyntaxError as e:
        result["issues"].append(f"Syntax error: {e}")
        return result

    # 检查必需元素
    if "class " in code and "bt.Strategy" in code:
        result["has_class"] = True
    else:
        result["issues"].append("Missing strategy class")

    if "def __init__" in code:
        result["has_init"] = True
    else:
        result["issues"].append("Missing __init__ method")

    if "def next" in code:
        result["has_next"] = True
    else:
        result["issues"].append("Missing next method")

    if "def notify_order" in code or "notify_order" in code:
        result["has_notify_order"] = True

    if "logging" in code or "logger" in code:
        result["has_logging"] = True
    else:
        result["issues"].append("Missing logging")

    if '"""' in code or "'''" in code:
        result["has_docstring"] = True
    else:
        result["issues"].append("Missing docstrings")

    # 检查代码长度
    if result["line_count"] < 50:
        result["issues"].append(f"Code too short ({result['line_count']} lines)")
    elif result["line_count"] > 350:
        result["issues"].append(f"Code too long ({result['line_count']} lines - Template Threshold risk!)")

    # 总体验证
    result["valid"] = (
        result["syntax_ok"] and
        result["has_class"] and
        result["has_init"] and
        result["has_next"] and
        50 <= result["line_count"] <= 350
    )

    return result

# ============================================================================
# 主生成函数
# ============================================================================

def generate_strategies():
    """生成所有策略"""
    print("=" * 80)
    print("PHASE 3 - BATCH 1 STRATEGY GENERATION")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Strategies to generate: {len(STRATEGIES)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 加载模型
    print("[1/4] Loading model...")
    print(f"Model path: {MODEL_PATH}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token
    GEN_CONFIG["pad_token_id"] = tokenizer.eos_token_id

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,
        device_map="auto",
        local_files_only=True
    )

    print(f"✅ Model loaded: {next(model.parameters()).device}")
    print()

    # 生成策略
    print(f"[2/4] Generating strategies...")
    print()

    all_results = []

    for idx, strategy in enumerate(STRATEGIES, 1):
        print(f"--- Strategy {idx}/{len(STRATEGIES)}: {strategy['display_name']} ---")

        # 构建完整Prompt
        full_prompt = f"""# Task: Generate a {strategy['display_name']} Backtrader Strategy

{strategy['prompt_layers']['layer1_safety']}

{strategy['prompt_layers']['layer2_functional']}

{strategy['prompt_layers']['layer3_quality']}

{strategy['prompt_layers']['layer4_template']}

## Success Criteria Checklist

Before submitting, verify the code includes:
- [ ] No lookahead bias
- [ ] Stop-loss and take-profit mechanisms
- [ ] Proper indicator calculations
- [ ] Entry and exit logging
- [ ] Type hints on methods
- [ ] Comprehensive docstrings
- [ ] Backtrader compatible structure
- [ ] Error handling

Generate the complete, production-ready strategy code now."""

        # 准备消息
        messages = [
            {
                "role": "system",
                "content": "You are an expert quantitative trading strategy developer specializing in Backtrader. Generate clean, production-ready, well-documented trading strategies."
            },
            {
                "role": "user",
                "content": full_prompt
            }
        ]

        # 生成
        try:
            torch.manual_seed(42)  # 固定seed确保可重复性

            prompt_text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

            print(f"  Generating code (max_tokens={GEN_CONFIG['max_new_tokens']})...")
            start_time = time.time()

            with torch.no_grad():
                outputs = model.generate(**inputs, **GEN_CONFIG)

            generation_time = time.time() - start_time

            full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
            code = extract_code(full_output)

            # 验证代码
            validation = validate_strategy_code(code, strategy['name'])

            print(f"  ✅ Generated: {validation['line_count']} lines, {validation['char_count']} chars")
            print(f"  ⏱️  Time: {generation_time:.1f}s")
            print(f"  Validation: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")

            if not validation['valid']:
                print(f"  Issues: {', '.join(validation['issues'])}")

            # 保存代码
            output_file = OUTPUT_DIR / f"{idx:02d}_{strategy['name']}.py"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)

            print(f"  💾 Saved to: {output_file.name}")
            print()

            # 记录结果
            all_results.append({
                "id": strategy["id"],
                "name": strategy["name"],
                "display_name": strategy["display_name"],
                "category": strategy["category"],
                "file": str(output_file),
                "generation_time": generation_time,
                "validation": validation,
                "code_length": validation["char_count"],
                "line_count": validation["line_count"],
            })

        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            print()

    # 保存元数据
    print("[3/4] Saving metadata...")

    metadata = {
        "experiment": "Phase 3 - Batch 1 Strategy Generation",
        "date": datetime.now().isoformat(),
        "model": MODEL_PATH,
        "generation_config": GEN_CONFIG,
        "total_strategies": len(STRATEGIES),
        "successful": sum(1 for r in all_results if r['validation']['valid']),
        "failed": sum(1 for r in all_results if not r['validation']['valid']),
        "strategies": all_results
    }

    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Metadata saved: {METADATA_FILE}")
    print()

    # 统计
    print("[4/4] Generation Summary")
    print("=" * 80)

    valid_count = sum(1 for r in all_results if r['validation']['valid'])
    invalid_count = len(all_results) - valid_count

    print(f"Total strategies: {len(all_results)}")
    print(f"Valid (passed checks): {valid_count}")
    print(f"Invalid (need review): {invalid_count}")
    print()

    if valid_count > 0:
        avg_lines = sum(r['line_count'] for r in all_results if r['validation']['valid']) / valid_count
        avg_time = sum(r['generation_time'] for r in all_results if r['validation']['valid']) / valid_count
        print(f"Average code length: {avg_lines:.0f} lines")
        print(f"Average generation time: {avg_time:.1f}s")
        print()

    # 列出有问题的策略
    if invalid_count > 0:
        print("⚠️ Strategies needing review:")
        for r in all_results:
            if not r['validation']['valid']:
                print(f"  - {r['display_name']}: {', '.join(r['validation']['issues'])}")
        print()

    print("=" * 80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 80)

    return metadata


if __name__ == "__main__":
    metadata = generate_strategies()

    # 打印最终统计
    print("\n🎉 Batch 1 generation complete!")
    print(f"📁 Check {OUTPUT_DIR} for generated strategies")
    print(f"📊 Success rate: {metadata['successful']}/{metadata['total_strategies']} "
          f"({100*metadata['successful']/metadata['total_strategies']:.0f}%)")
