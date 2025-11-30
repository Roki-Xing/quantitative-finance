"""
数据一致性检查
================

目的: 对比今日5股实验 vs Day 52的10股数据
- 今日完全自适应 (2024): 0%成功率, -1.00%收益
- Day 52数据 (2024): 70%成功率, +5.68%收益

检查项:
1. 股票列表是否一致
2. 参数配置是否一致 (ATR倍数, 风险百分比)
3. 时间段是否一致
4. 数据源是否一致
"""

import json
from pathlib import Path
import pandas as pd

print("=" * 80)
print("数据一致性检查")
print("=" * 80)

# 读取今日实验数据
today_file = Path('C:/Users/Xing/Desktop/sensitivity_C_fully_adaptive.json')
with open(today_file, 'r', encoding='utf-8') as f:
    today_data = json.load(f)

# 读取Day 52数据 (从你的existing materials中)
day52_file = Path('C:/Users/Xing/Desktop/paper_supporting_materials/[核心数据汇总]_DATA_SUMMARY_所有关键数字_JSON格式.json')
with open(day52_file, 'r', encoding='utf-8') as f:
    day52_data = json.load(f)

print("\n[1] 今日实验 (sensitivity_C_fully_adaptive.json)")
print("-" * 80)
print(f"实验名称: {today_data['metadata']['experiment_name']}")
print(f"时间戳: {today_data['metadata']['timestamp']}")
print(f"策略: {today_data['metadata']['strategy']}")
print(f"\n资产列表 ({len(today_data['metadata']['assets'])}只):")
for asset in today_data['metadata']['assets']:
    print(f"  - {asset}")

print("\n训练期结果:")
train_results = []
for asset_name, asset_data in today_data['results'].items():
    train = asset_data.get('training_period', {})
    train_results.append({
        'asset': asset_name,
        'returns_pct': train.get('returns_pct', 0),
        'volatility': asset_data.get('volatility', 'N/A')
    })
    print(f"  {asset_name}: {train.get('returns_pct', 0):+.2f}%")

train_avg = sum(r['returns_pct'] for r in train_results) / len(train_results)
train_success = sum(1 for r in train_results if r['returns_pct'] > 0)
print(f"\n  平均收益: {train_avg:+.2f}%")
print(f"  成功率: {train_success}/{len(train_results)} = {train_success/len(train_results)*100:.1f}%")

print("\n测试期结果 (2024):")
test_results = []
for asset_name, asset_data in today_data['results'].items():
    test = asset_data.get('testing_period', {})
    test_results.append({
        'asset': asset_name,
        'returns_pct': test.get('returns_pct', 0)
    })
    print(f"  {asset_name}: {test.get('returns_pct', 0):+.2f}%")

test_avg = sum(r['returns_pct'] for r in test_results) / len(test_results)
test_success = sum(1 for r in test_results if r['returns_pct'] > 0)
print(f"\n  平均收益: {test_avg:+.2f}%")
print(f"  成功率: {test_success}/{len(test_results)} = {test_success/len(test_results)*100:.1f}%")

print("\n" + "=" * 80)
print("\n[2] Day 52数据 (DATA_SUMMARY.json)")
print("-" * 80)

# 提取Day 52的自适应策略2024测试期数据
# 需要找到对应的实验部分
print("正在解析Day 52数据结构...")

# 检查Day 52数据结构
if 'experiments' in day52_data:
    print(f"找到 {len(day52_data['experiments'])} 个实验")

    # 查找自适应策略的2024测试结果
    for exp_name, exp_data in day52_data['experiments'].items():
        if 'adaptive' in exp_name.lower() or 'strategy13' in exp_name.lower():
            print(f"\n实验: {exp_name}")
            if 'testing_2024' in exp_data or 'out_of_sample' in exp_data:
                print("  找到2024测试期数据!")
                # 提取详细信息

elif 'Day52_18_stocks' in day52_data or 'comprehensive_results' in day52_data:
    print("找到综合结果数据")

# 如果数据结构不同，先展示顶层结构
print("\nDay 52数据顶层键:")
for key in day52_data.keys():
    print(f"  - {key}")

print("\n" + "=" * 80)
print("\n[3] 对比分析")
print("-" * 80)

print("\n关键差异:")
print(f"1. 资产数量: 今日 {len(today_data['metadata']['assets'])} vs Day 52 (待确认)")
print(f"2. 今日5只股票: {', '.join(today_data['metadata']['assets'])}")
print(f"3. 今日2024成功率: {test_success}/{len(test_results)} = {test_success/len(test_results)*100:.1f}%")
print(f"4. Day 52声称2024成功率: 70% (7/10)")
print(f"5. 今日2024平均收益: {test_avg:+.2f}%")
print(f"6. Day 52声称2024平均收益: +5.68%")

print("\n可能原因:")
print("  A. 股票选择不同 (今日5只 ≠ Day 52的10只)")
print("  B. 参数配置微调 (ATR倍数/风险百分比不同)")
print("  C. 数据源更新 (2024数据有新的交易日)")
print("  D. 策略实现细节差异")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
print("\n建议: 需要查看Day 52的原始实验代码和数据，明确10只股票身份")
