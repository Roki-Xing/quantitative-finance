#!/usr/bin/env python3
"""
扩展数据下载脚本
下载15年历史数据 (2010-2025) + 多元化股票 + 指数基准
"""

import time
from pathlib import Path
from datetime import datetime
import json

# 安装akshare
try:
    import akshare as ak
    print("✅ akshare已安装")
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "akshare", "-q"])
    import akshare as ak
    print("✅ akshare安装完成")

import pandas as pd

# 配置
DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data_extended")
DATA_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "20100101"  # 15年数据
END_DATE = "20251122"

# 多元化股票池 (按行业分类)
STOCKS = {
    # 金融
    "000001": "平安银行",
    "600036": "招商银行",
    "601318": "中国平安",
    # 消费
    "000858": "五粮液",
    "600519": "贵州茅台",
    "000651": "格力电器",
    # 科技
    "000725": "京东方A",
    "002415": "海康威视",
    "300059": "东方财富",
    # 医药
    "000538": "云南白药",
    "600276": "恒瑞医药",
    "300760": "迈瑞医疗",
    # 制造
    "000333": "美的集团",
    "600887": "伊利股份",
    "601012": "隆基绿能",
    # 地产/基建
    "000002": "万科A",
    "600048": "保利发展",
    # 能源
    "601857": "中国石油",
    "600028": "中国石化",
    # 通信
    "000063": "中兴通讯",
}

# 指数基准
INDICES = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sh000300": "沪深300",
    "sz399006": "创业板指",
}

def download_stock(symbol: str, name: str) -> dict:
    """下载单只股票数据"""
    result = {"symbol": symbol, "name": name, "success": False, "rows": 0, "error": None}

    try:
        print(f"  ⏳ {symbol} {name}...", end=" ", flush=True)

        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=START_DATE,
            end_date=END_DATE,
            adjust="qfq"  # 前复权
        )

        if df is None or len(df) == 0:
            result["error"] = "No data"
            print("❌ 无数据")
            return result

        # 标准化列名
        df.columns = ['date', 'code', 'open', 'close', 'high', 'low',
                      'volume', 'turnover', 'amplitude', 'pct_change', 'change', 'turnover_rate']
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # 保存
        save_path = DATA_DIR / f"stock_{symbol}.csv"
        df.to_csv(save_path)

        result["success"] = True
        result["rows"] = len(df)
        result["start"] = str(df.index.min().date())
        result["end"] = str(df.index.max().date())

        print(f"✅ {len(df)} 行 ({result['start']} ~ {result['end']})")

        time.sleep(0.5)  # 避免请求过快

    except Exception as e:
        result["error"] = str(e)[:100]
        print(f"❌ {str(e)[:50]}")

    return result

def download_index(code: str, name: str) -> dict:
    """下载指数数据"""
    result = {"code": code, "name": name, "success": False, "rows": 0, "error": None}

    try:
        print(f"  ⏳ {code} {name}...", end=" ", flush=True)

        # 根据代码判断市场
        if code.startswith("sh"):
            symbol = code[2:]
            df = ak.stock_zh_index_daily(symbol=f"sh{symbol}")
        else:
            symbol = code[2:]
            df = ak.stock_zh_index_daily(symbol=f"sz{symbol}")

        if df is None or len(df) == 0:
            result["error"] = "No data"
            print("❌ 无数据")
            return result

        # 标准化
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= START_DATE) & (df['date'] <= END_DATE)]
        df.set_index('date', inplace=True)

        # 保存
        save_path = DATA_DIR / f"index_{code}.csv"
        df.to_csv(save_path)

        result["success"] = True
        result["rows"] = len(df)
        result["start"] = str(df.index.min().date())
        result["end"] = str(df.index.max().date())

        print(f"✅ {len(df)} 行 ({result['start']} ~ {result['end']})")

        time.sleep(0.5)

    except Exception as e:
        result["error"] = str(e)[:100]
        print(f"❌ {str(e)[:50]}")

    return result

def main():
    print("="*80)
    print("扩展数据下载 - 15年历史数据")
    print("="*80)
    print(f"时间范围: {START_DATE} ~ {END_DATE}")
    print(f"股票数量: {len(STOCKS)}")
    print(f"指数数量: {len(INDICES)}")
    print(f"保存目录: {DATA_DIR}")
    print()

    results = {"stocks": [], "indices": [], "summary": {}}

    # 下载股票
    print("="*80)
    print("[1/2] 下载股票数据")
    print("="*80)

    for symbol, name in STOCKS.items():
        result = download_stock(symbol, name)
        results["stocks"].append(result)

    # 下载指数
    print("\n" + "="*80)
    print("[2/2] 下载指数数据")
    print("="*80)

    for code, name in INDICES.items():
        result = download_index(code, name)
        results["indices"].append(result)

    # 汇总
    stock_success = sum(1 for r in results["stocks"] if r["success"])
    index_success = sum(1 for r in results["indices"] if r["success"])
    total_rows = sum(r["rows"] for r in results["stocks"] + results["indices"])

    results["summary"] = {
        "download_time": datetime.now().isoformat(),
        "stocks_success": f"{stock_success}/{len(STOCKS)}",
        "indices_success": f"{index_success}/{len(INDICES)}",
        "total_data_points": total_rows,
        "data_directory": str(DATA_DIR)
    }

    # 保存元数据
    meta_path = DATA_DIR / "download_metadata.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 打印汇总
    print("\n" + "="*80)
    print("下载汇总")
    print("="*80)
    print(f"股票: {stock_success}/{len(STOCKS)} 成功")
    print(f"指数: {index_success}/{len(INDICES)} 成功")
    print(f"总数据点: {total_rows:,}")
    print(f"元数据: {meta_path}")

    # 列出失败的
    failed = [r for r in results["stocks"] + results["indices"] if not r["success"]]
    if failed:
        print(f"\n❌ 失败 ({len(failed)}):")
        for f in failed:
            print(f"  - {f.get('symbol', f.get('code'))}: {f['error']}")

    print("\n" + "="*80)
    print("下载完成!")
    print("="*80)

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
