#!/usr/bin/env python3
"""
Day 48: 批量下载高潜力策略进行手动修复
"""

import subprocess
import json
from pathlib import Path

# 高潜力策略列表（基于修复报告）
HIGH_POTENTIAL_STRATEGIES = {
    'baseline': [
        'strategy_007.py',  # ✅ SUCCESS - 已经可运行
        'strategy_026.py',  # ✅ SUCCESS - 已经可运行
        'strategy_015.py',  # ⏭️  NO CHANGES - 语法正确但可能有运行时错误
        'strategy_022.py',  # ⏭️  NO CHANGES
    ],
    'multilayer': [
        # 9个 NO CHANGES策略 - 从multilayer报告中识别
        'strategy_002.py',
        'strategy_004.py',
        'strategy_006.py',
        'strategy_009.py',
        'strategy_010.py',
        'strategy_012.py',
        'strategy_018.py',
        'strategy_020.py',
        'strategy_025.py',
    ]
}

# 服务器配置
SERVER = "root@connect.westd.seetacloud.com"
PORT = 18077
REMOTE_BASE = "/root/autodl-tmp/eoh/experiment4_trading_extended"

# 本地目录
LOCAL_DIR = Path("C:/Users/Xing/Desktop/day31_code_review/manual_fix")
LOCAL_DIR.mkdir(exist_ok=True)

def download_strategies():
    """下载所有高潜力策略"""
    print("="*80)
    print("下载高潜力策略进行手动修复")
    print("="*80)

    total = sum(len(strategies) for strategies in HIGH_POTENTIAL_STRATEGIES.values())
    downloaded = 0

    for group, strategies in HIGH_POTENTIAL_STRATEGIES.items():
        group_dir = LOCAL_DIR / group
        group_dir.mkdir(exist_ok=True)

        print(f"\n[{group.upper()}] 下载 {len(strategies)} 个策略...")

        for strategy in strategies:
            remote_path = f"{REMOTE_BASE}/{group}/{strategy}"
            local_path = group_dir / strategy

            cmd = f'scp -P {PORT} {SERVER}:{remote_path} {local_path}'
            try:
                subprocess.run(cmd, shell=True, check=True, capture_output=True)
                downloaded += 1
                print(f"  ✅ {strategy}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ {strategy}: {e}")

    print(f"\n下载完成: {downloaded}/{total}")
    print(f"保存到: {LOCAL_DIR}")

    # 生成修复清单
    checklist = {
        'total': total,
        'downloaded': downloaded,
        'strategies': HIGH_POTENTIAL_STRATEGIES,
        'next_steps': [
            "1. 检查每个策略的语法错误和不完整代码块",
            "2. 修复incomplete elif/else blocks",
            "3. 添加缺失的imports（如 import backtrader.indicators as btind）",
            "4. 完善交易逻辑",
            "5. 重新上传到服务器",
            "6. 运行回测验证"
        ]
    }

    checklist_file = LOCAL_DIR / 'fix_checklist.json'
    with open(checklist_file, 'w') as f:
        json.dump(checklist, f, indent=2)

    print(f"\n修复清单已生成: {checklist_file}")
    return downloaded

if __name__ == '__main__':
    download_strategies()
