# 代码审查问题清单（快速参考版）

## 🔴 严重问题（需要立即修复的5个）

### 1. 过拟合风险 - 策略选择仅基于训练集
**文件**: `eoh_gpu_loop_fixed.py:327-342`
**问题**: `fit = fitness_from_stats(st_train)` 只用训练集评分
**影响**: Day 29的226%可能是过拟合，Day 31多年验证会暴露问题
**修复**:
```python
# 简单方案
if st_test['Return [%]'] < 0:  # 测试集亏损直接淘汰
    continue
fit = fitness_from_stats(st_train)
```

---

### 2. 随机种子不完整
**文件**: `eoh_gpu_loop_fixed.py:295-297`
**问题**: 缺少 `torch.manual_seed` 和 `transformers.set_seed`
**影响**: 实验不可复现，论文会被拒
**修复**:
```python
import torch
from transformers import set_seed

random.seed(args.seed)
np.random.seed(args.seed)
torch.manual_seed(args.seed)
torch.cuda.manual_seed_all(args.seed)
set_seed(args.seed)
```

---

### 3. 协方差矩阵维度不匹配
**文件**: `portfolio_optimizer.py:164`
**问题**: 硬编码4x4矩阵，但资产数量可能不是4
**影响**: Day 21投资组合构建会崩溃
**修复**:
```python
# 从实际数据计算
returns_df = pd.DataFrame({asset: returns[asset] for asset in best_strategies.keys()})
cov_matrix = returns_df.cov().values
```

---

### 4. 框架代码未保存
**文件**: `asset_adaptive_analyzer.py:254, 402-447`
**问题**: 生成了代码但没写入文件
**影响**: Day 23的成果丢失
**修复**:
```python
output_file = Path('/root/autodl-tmp/eoh/asset_adaptive_framework.py')
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, 'w') as f:
    f.write(framework_code)
```

---

### 5. 空数据除零错误
**文件**: `asset_adaptive_analyzer.py:79, 83-84`
**问题**: 没检查数组是否为空就计算均值/除法
**影响**: XLE/TLT等表现差的资产会导致崩溃
**修复**:
```python
if len(train_returns) == 0 or total_count == 0:
    logging.warning(f"{asset}数据为空，跳过")
    return None
```

---

## 🟡 中等问题（可以稍后修复）

6. **路径硬编码** - 所有`/root/autodl-tmp`路径不可移植
7. **命令注入** - `asset_adaptive_framework.py:89` 未转义参数
8. **配置污染** - `get_config`返回可变字典引用
9. **未使用参数** - `--generations`和`--cpus`存在但未实现
10. **未知资产静默降级** - 错误symbol不报警告

---

## 📋 完整报告

详细分析、修复代码和长期建议请查看:
**`CODE_REVIEW_REPORT.md`**

---

## ⚠️ 关键决策

**问题**: 修复问题#1后，QQQ的226%可能无法复现

**选项A**: 先修复再测试（推荐）
- ✅ 结果更可信
- ✅ 论文更有说服力
- ❌ 可能损失"惊人收益"的卖点

**选项B**: 保留原代码继续Day 31
- ✅ 保持226%记录
- ❌ 多年验证可能失败
- ❌ 论文被拒风险高

**建议**: 修复问题#1和#2，如果结果下降就调整叙事为"方法论创新"而非"高收益"。
