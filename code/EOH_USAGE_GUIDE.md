# EOH框架完整使用指南

**目的**: 在新数据上使用LLM生成策略或运行现有策略

---

## 场景1: 使用现成的Adaptive策略（推荐，无需LLM）

### 优点:
- ✅ 无需GPU
- ✅ 无需调用LLM
- ✅ 执行速度快（秒级）
- ✅ 策略已验证有效

### 步骤:

#### 1. 准备数据文件

CSV格式要求:
```csv
date,open,high,low,close,volume
2020-01-02,100.5,102.3,99.8,101.2,1000000
2020-01-03,101.5,103.1,100.5,102.8,1200000
...
```

保存为: `/root/autodl-tmp/eoh/backtest_data_extended/your_stock.csv`

#### 2. 运行脚本

```bash
cd /root/autodl-tmp/eoh
/root/miniconda3/bin/python run_strategy_on_new_data.py \
  --data /root/autodl-tmp/eoh/backtest_data_extended/your_stock.csv \
  --train-start 2020-01-01 \
  --train-end 2023-12-31 \
  --test-start 2024-01-01 \
  --test-end 2024-12-31
```

#### 3. 查看结果

输出文件: `your_stock_results.json`

```json
{
  "training": {
    "returns_pct": 15.23,
    "sharpe_ratio": 0.456,
    "max_drawdown_pct": 18.32,
    "total_trades": 12
  },
  "testing": {
    "returns_pct": 8.45,
    "sharpe_ratio": 0.382,
    "max_drawdown_pct": 12.15,
    "total_trades": 5
  }
}
```

---

## 场景2: 让LLM生成全新策略（需要GPU，较慢）

### 何时使用:
- 您想探索LLM是否能为特定数据生成更好的策略逻辑
- 您想研究不同Prompt对策略的影响
- 您在做学术实验

### 注意事项:
⚠️ **LLM生成的策略会包含固定参数，您仍需手动改为自适应参数！**

### 步骤:

#### 1. 准备数据

同场景1，准备CSV文件

#### 2. 运行EOH生成策略

```bash
cd /root/autodl-tmp/eoh

# 激活conda环境
source /root/miniconda3/bin/activate eoh1

# 运行EOH
python eoh_gpu_loop_fixed.py \
  --model-dir /root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct \
  --symbol YOUR_SYMBOL \
  --population 20 \
  --temperature 0.2 \
  --prompt-style adaptive \
  --prompt-dir /root/autodl-tmp/eoh/prompts_day51_adaptive \
  --outdir /root/autodl-tmp/outputs/new_experiment \
  --train_start 2020-01-01 \
  --train_end 2023-12-31 \
  --test_start 2024-01-01 \
  --test_end 2024-12-31
```

**参数说明**:
- `--symbol`: 股票代码（用于命名）
- `--population`: 生成策略数量（20个）
- `--temperature`: LLM温度（0.2为最优，根据Day 12实验）
- `--prompt-style`: 提示风格（adaptive为温和提示，根据Day 9实验）

#### 3. 查看LLM生成的策略

```bash
ls /root/autodl-tmp/outputs/new_experiment/
# 会看到20个生成的策略文件
```

#### 4. **关键步骤**: 手动改进参数

从生成的策略中选择最好的，然后手动修改固定参数为自适应参数：

**LLM生成的原始代码**（示例）:
```python
class Strategy:
    def next(self):
        if condition:
            # LLM生成的固定参数 ❌
            stop_loss = 200  # 固定$200
            position_size = 20  # 固定20股
            buy(size=position_size)
```

**手动改进为自适应参数** ✅:
```python
class Adaptive_Strategy:
    def __init__(self):
        self.atr = bt.indicators.ATR(period=14)

    def next(self):
        if condition:
            # 改为自适应参数
            stop_distance = self.atr[0] * 3  # ATR×3动态止损
            risk_amount = self.broker.getvalue() * 0.02  # 2%风险
            position_size = int(risk_amount / stop_distance)
            buy(size=position_size)
```

---

## 场景对比

| 维度 | 场景1 (现成策略) | 场景2 (LLM生成) |
|------|----------------|----------------|
| **需要GPU** | ❌ 否 | ✅ 是 |
| **执行时间** | ~1秒 | ~10-30分钟 |
| **策略质量** | ✅ 已验证 | ❓ 需要手动改进参数 |
| **适用情况** | 测试新数据 | 学术研究/探索 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐☆☆☆ |

---

## 实际使用建议

### 如果您只是想测试新股票数据:
→ **使用场景1**（现成Adaptive策略）

### 如果您在做以下研究:
- 研究不同Prompt对LLM策略生成的影响
- 对比不同LLM模型（Llama vs GPT vs Qwen）
- 探索策略多样性
→ **使用场景2**（EOH生成新策略）

---

## 常见问题 (FAQ)

### Q1: 为什么不直接用LLM生成的策略？

**A**: LLM生成的固定参数（如$200止损）无法跨市场泛化:
- US市场: +1.49% (勉强可用)
- A股市场: -65.10% (灾难性失败)

改为自适应参数后:
- US市场: +5.41% (263%提升)
- A股市场: +204.88% (+292.81pp提升)

### Q2: Adaptive策略在我的新数据上一定有效吗？

**A**: 不保证。策略效果取决于:
1. 数据质量（是否有缺失/异常值）
2. 市场状态（趋势市 vs 震荡市）
3. 资产特性（高波动 vs 低波动）

但自适应参数框架至少保证:
- ✅ 止损会根据波动率自动调整
- ✅ 仓位会根据账户规模和风险自动调整
- ✅ 不会出现固定参数的灾难性失败

### Q3: 我能否修改Adaptive策略的参数？

**A**: 可以！您可以调整:
- `atr_multiplier`: ATR倍数（默认3.0，可调2.0-5.0）
- `risk_per_trade`: 单笔风险（默认2%，可调1%-5%）
- `sma_fast/slow`: SMA周期（默认20/50）
- `rsi_period`: RSI周期（默认14）

修改方法: 编辑`run_strategy_on_new_data.py`中的`params`部分

### Q4: 如何批量测试多只股票？

**A**: 创建循环脚本:

```bash
#!/bin/bash
# batch_test.sh

for stock in stock_600000.csv stock_600001.csv stock_600002.csv
do
  echo "Testing $stock..."
  python run_strategy_on_new_data.py \
    --data /root/autodl-tmp/eoh/backtest_data_extended/$stock \
    --train-start 2020-01-01 \
    --train-end 2023-12-31 \
    --test-start 2024-01-01 \
    --test-end 2024-12-31
done
```

---

## 技术架构总结

```
┌─────────────────────────────────────────────────┐
│  您的位置: 已完成策略开发,现在要测试新数据      │
└─────────────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  选择: 使用现成策略 or 重新生成? │
        └───────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌──────────────────┐          ┌─────────────────────┐
│ 场景1: 现成策略   │          │ 场景2: LLM重新生成   │
│ (推荐)           │          │ (学术研究用)         │
├──────────────────┤          ├─────────────────────┤
│ 1. 准备CSV       │          │ 1. 准备CSV          │
│ 2. 运行Python    │          │ 2. 运行EOH生成      │
│ 3. 查看结果      │          │ 3. 手动改进参数     │
│                  │          │ 4. 运行回测         │
│ 时间: ~1秒       │          │ 时间: ~30分钟       │
└──────────────────┘          └─────────────────────┘
```

---

**推荐流程**: 场景1 → 如果效果不理想 → 考虑场景2

**关键理念**: EOH的价值在于策略逻辑生成,参数框架需要人工优化!

---

**文档版本**: v1.0
**更新时间**: 2025-11-28
**联系**: 见论文补充材料
