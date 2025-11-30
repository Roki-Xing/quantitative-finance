# 如何查看补充材料 - 完整指南

## 📍 文件夹位置
```
C:\Users\Xing\Desktop\paper_supplementary_experiments_2025-11-27\
```

---

## 📚 推荐阅读顺序

### 方案A: 新手路线 (从零开始)
```
1. README.md (3分钟)                      - 快速了解结构
2. USAGE_GUIDE.md (30分钟) ⭐最重要       - 完整使用指导  
3. COMPREHENSIVE_SUMMARY.md (20分钟)      - 所有实验汇总
4. 具体实验报告 (按需)                     - 深入细节
```

### 方案B: 高级路线 (直接用于论文)
```
1. USAGE_GUIDE.md → "论文写作指导"        - 复制粘贴模板
2. data/*.json                             - 查看原始数据
3. charts/*.png                            - 选择图表插入
4. USAGE_GUIDE.md → "审稿人应对"          - 准备回复信
```

---

## 🔧 各类文件打开方式

### 1. Markdown文件 (.md) - 9个报告

**推荐工具:**
- **VS Code** (最佳): Ctrl+Shift+V 预览
- **Typora**: 所见即所得编辑器
- **在线查看器**: https://markdownlivepreview.com/

**关键文件:**
- `USAGE_GUIDE.md` ⭐ - 从这里开始
- `COMPREHENSIVE_SUMMARY.md` - 所有实验汇总
- `reports/statistical_report_full.md` - 基线对比详细分析

---

### 2. JSON文件 (.json) - 9个数据文件

**推荐工具:**
- **VS Code**: Alt+Shift+F 格式化
- **在线JSON查看器**: http://jsonviewer.stack.hu/

**快速查找关键数字:**

#### 示例1: 查看基线对比结果
```bash
打开: data/baseline_comparison_results.json

搜索关键字:
- "LLM_Adaptive" - 找到我们的策略结果
- "Buy_and_Hold" - 找到被动策略对比
- "total_backtests": 96 - 确认实验规模
```

#### 示例2: 查看参数敏感性
```bash
打开: data/sensitivity_A_stop_loss.json

关键数据位置:
- "600519_贵州茅台" → "training_period" → 各档止损收益
- 找到最大值和最小值，计算敏感度 (14.66 pp)
```

#### 示例3: 查看消融实验
```bash
打开: data/ablation_study_results.json

关键策略:
- "Baseline_Fixed" - 基线
- "ATR_Only" - ATR贡献
- "Full_Adaptive" - 完全自适应
- 对比 "average_return" 字段
```

---

### 3. PNG图表 (.png) - 5个高清图

**用途:**
- 直接插入论文 (300 dpi发表级质量)
- 幻灯片演示
- 投稿补充材料

**图表说明:**

| 文件名 | 用途 | 论文引用位置 |
|--------|------|-------------|
| `stop_loss_sensitivity_curves.png` | 止损参数敏感性分析 | Figure 4.1 |
| `position_size_sensitivity_curves.png` | 仓位参数敏感性分析 | Figure 4.2 |
| `training_returns_comparison.png` | 训练期收益对比 | Figure 5.1 |
| `training_returns_boxplot.png` | 训练期收益分布 | Figure 5.2 |
| `testing_returns_comparison.png` | 测试期收益对比 | Figure 5.3 |

**插入Word:**
```
插入 → 图片 → 从文件 → 选择charts/文件夹中的图
右键 → 大小和位置 → 设置宽度为15cm (适合单栏)
引用 → 插入题注 → "Figure 4.1: ..."
```

---

### 4. Python脚本 (.py) - 13个代码文件

**仅查看 (不运行):**
- **VS Code**: 代码高亮+折叠
- **Notepad++**: 轻量级查看

**如需重现实验 (高级用户):**
```bash
# SSH连接到服务器
ssh -p 18077 root@connect.westd.seetacloud.com

# 进入实验目录
cd /root/autodl-tmp/eoh

# 运行任意脚本
/root/miniconda3/bin/python run_baseline_comparison.py
```

---

## 🎯 常见使用场景

### 场景1: 我要写论文Chapter 5 (结果)

**步骤:**
1. 打开 `USAGE_GUIDE.md`
2. 搜索 "Chapter 5" 或跳转到第436行
3. 复制以下段落模板:
   ```markdown
   5.1 Training Performance (2018-2023)
   LLM_Adaptive achieves +4.36% average return...
   
   5.2 Out-of-Sample Testing (2024)
   LLM_Adaptive: +5.68% vs Buy&Hold: +27.24% (p=0.017)
   ```
4. 根据您的论文结构调整格式
5. 引用对应的JSON文件作为证据

---

### 场景2: 审稿人质疑"参数调优是常识"

**步骤:**
1. 打开 `USAGE_GUIDE.md`
2. 搜索 "质疑2" 或跳转到第695行
3. 使用预制回应模板:
   ```markdown
   "We quantify the fixed parameter trap: 14.66pp sensitivity
   (data: sensitivity_A_stop_loss.json, Figure 4.1)."
   ```
4. 附上图表 `charts/stop_loss_sensitivity_curves.png`

---

### 场景3: 我需要验证某个数字是否正确

**示例: 验证 "ATR贡献+1.87pp"**

1. 打开 `data/ablation_study_results.json`
2. 搜索 `"ATR_Only"`
3. 找到 `"average_return"` (假设是 +3.85%)
4. 搜索 `"Baseline_Fixed"`
5. 找到 `"average_return"` (假设是 +1.98%)
6. 计算: 3.85 - 1.98 = 1.87 pp ✅

或者直接查看报告:
```bash
打开: reports/ablation_study_report.md
搜索: "ATR contribution"
找到: "+1.87 pp" 已计算好
```

---

### 场景4: 我需要所有关键数字的速查表

**最快方式:**
1. 打开 `COMPREHENSIVE_SUMMARY.md`
2. 搜索 "关键数字速查表" 或跳转到第257行
3. 直接复制表格到论文

或者查看:
```bash
打开: USAGE_GUIDE.md
搜索: "核心数字速查表" (第752行)
```

---

## 📊 数据文件详细索引

### 核心实验数据 (必看)

| JSON文件 | 大小 | 回测数 | 关键内容 |
|---------|------|--------|----------|
| `baseline_comparison_results.json` | 36 KB | 96 | 4策略对比, p值检验 |
| `ablation_study_results.json` | 16 KB | 40 | 组件贡献分解 |
| `sensitivity_A_stop_loss.json` | 28 KB | 70 | 止损敏感性 (14.66pp) |
| `sensitivity_B_position_size.json` | 26 KB | 70 | 仓位敏感性 (13.98pp) |
| `multi_year_rolling_validation.json` | 7.6 KB | 15 | 3年滚动验证 |

### 补充实验数据 (可选)

| JSON文件 | 大小 | 用途 |
|---------|------|------|
| `extended_baseline_results.json` | 34 KB | 10股扩展验证 |
| `transaction_cost_sensitivity.json` | 14 KB | 交易成本稳健性 |
| `sensitivity_C_fully_adaptive.json` | 4 KB | 完全自适应验证 |

---

## 🔍 如何搜索特定信息

### 在Markdown文件中搜索

**VS Code:**
```
Ctrl+F: 搜索当前文件
Ctrl+Shift+F: 搜索所有文件
```

**常用搜索关键词:**
- `14.66` - 找到止损敏感度
- `p=0.017` - 找到统计显著性
- `ATR` - 找到自适应止损相关
- `2023` - 找到熊市失败案例
- `Figure` - 找到图表引用位置
- `Chapter` - 找到论文章节模板

---

### 在JSON文件中搜索

**搜索技巧:**
```json
"LLM_Adaptive"     - 找到我们的策略
"returns_pct"      - 找到收益率数据
"sharpe_ratio"     - 找到Sharpe比率
"max_drawdown"     - 找到最大回撤
"total_backtests"  - 找到实验规模
"timestamp"        - 找到执行时间
```

---

## 💡 高级技巧

### 技巧1: 批量验证数据一致性

**检查所有JSON的回测总数:**
```bash
# Windows PowerShell
cd data/
Get-ChildItem *.json | ForEach-Object {
    $content = Get-Content $_.Name | ConvertFrom-Json
    Write-Host "$($_.Name): $($content.metadata.total_backtests) backtests"
}
```

**预期输出:**
```
baseline_comparison: 96 backtests
ablation_study: 40 backtests
sensitivity_A: 70 backtests
...
总计: 425 backtests
```

---

### 技巧2: 快速提取关键数字到Excel

1. 打开任意JSON文件
2. 复制需要的数据段
3. 访问 https://www.convertcsv.com/json-to-csv.htm
4. 粘贴JSON → 转换为CSV
5. 在Excel中打开CSV → 制作自定义表格

---

### 技巧3: 生成论文引用列表

**Markdown报告 → BibTeX:**
```bibtex
@misc{supplementary2025,
  title={Supplementary Experiments for LLM-based Trading Strategy},
  author={[Your Name]},
  year={2025},
  note={425 backtests across 6 experiments},
  howpublished={Available in supplementary materials}
}
```

---

## 📞 常见问题

### Q1: 我应该从哪个文件开始看?

**A:** 按顺序阅读:
1. `README.md` (3分钟快速了解)
2. `USAGE_GUIDE.md` (30分钟完整指导) ⭐
3. `COMPREHENSIVE_SUMMARY.md` (20分钟汇总)

---

### Q2: JSON文件太大，打不开怎么办?

**A:** 最大的文件只有36 KB，任何文本编辑器都能打开。如果卡顿:
- 使用VS Code (性能更好)
- 在线查看器: http://jsonviewer.stack.hu/
- 或者只看对应的Markdown报告 (已经分析好了)

---

### Q3: 如何引用这些数据到论文?

**A:** 参考模板:
```markdown
Parameter sensitivity analysis (150 backtests) reveals 14.66pp 
range across stop-loss values (data: sensitivity_A_stop_loss.json, 
Figure 4.1).
```

---

### Q4: 图表分辨率够用吗?

**A:** 所有图表都是300 dpi，符合以下期刊要求:
- ESWA: 最低300 dpi ✅
- EAAI: 最低300 dpi ✅
- Nature系列: 推荐300-600 dpi ✅

---

### Q5: 我可以修改这些文件吗?

**A:** 可以！建议:
- **只读模式**: 直接查看原始文件
- **编辑模式**: 复制一份再修改
- **版本控制**: 用Git追踪改动

---

## 🎯 论文写作快速通道

### 30分钟快速上手

**时间分配:**
```
00:00 - 00:05  打开USAGE_GUIDE.md，浏览目录
00:05 - 00:15  阅读"论文写作指导"章节
00:15 - 00:25  复制Chapter 4/5/6 模板到论文
00:25 - 00:30  选择2-3张图表插入论文
```

**产出:**
- Chapter 4 实验设计初稿
- Chapter 5 结果汇报初稿
- Chapter 6 局限性讨论
- 3张高质量图表

---

## 📖 推荐学习资源

### Markdown学习
- **10分钟教程**: https://www.markdowntutorial.com/
- **语法速查**: https://www.markdownguide.org/cheat-sheet/

### JSON数据处理
- **在线工具**: https://jsonformatter.org/
- **Python处理**: https://realpython.com/python-json/

### 科学绘图
- **Matplotlib教程**: https://matplotlib.org/stable/tutorials/
- **期刊图表标准**: https://www.elsevier.com/authors/policies-and-guidelines/artwork-and-media-instructions

---

## 📬 需要帮助?

如果遇到任何问题:
1. 先查看 `USAGE_GUIDE.md` 中的FAQ章节
2. 检查 `COMPREHENSIVE_SUMMARY.md` 中的详细说明
3. 查看具体实验的报告文件

---

**最后更新**: 2025-11-28  
**版本**: v1.0 Final  
**总文件数**: 42个  
**总大小**: 2.2 MB

**祝您论文写作顺利！** 📝🎉
