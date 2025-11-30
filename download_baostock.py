#!/usr/bin/env python3
"""使用baostock下载A股历史数据"""

import baostock as bs
import pandas as pd
from pathlib import Path
import time

DATA_DIR = Path('/root/autodl-tmp/eoh/backtest_data_extended')
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 登录
lg = bs.login()
print(f'Login: {lg.error_code} - {lg.error_msg}')

# 股票列表 (baostock格式: sh.代码 或 sz.代码)
symbols = {
    'sh.600036': '招商银行',
    'sh.601318': '中国平安',
    'sz.000858': '五粮液',
    'sh.600519': '贵州茅台',
    'sz.000651': '格力电器',
    'sz.000725': '京东方A',
    'sz.002415': '海康威视',
    'sz.300059': '东方财富',
    'sz.000538': '云南白药',
    'sh.600276': '恒瑞医药',
    'sz.000333': '美的集团',
    'sh.600887': '伊利股份',
    'sz.000002': '万科A',
    'sh.600048': '保利发展',
    'sh.601857': '中国石油',
    'sh.600028': '中国石化',
    'sz.000063': '中兴通讯',
    'sz.000001': '平安银行',
}

success = 0
failed = 0

for code, name in symbols.items():
    print(f'{code} {name}...', end=' ', flush=True)
    try:
        rs = bs.query_history_k_data_plus(
            code,
            'date,open,high,low,close,volume',
            start_date='2010-01-01',
            end_date='2025-11-22',
            frequency='d',
            adjustflag='2'  # 前复权
        )
        if rs.error_code == '0':
            data = []
            while rs.next():
                data.append(rs.get_row_data())
            df = pd.DataFrame(data, columns=rs.fields)

            # 保存 - 替换.为_
            filename = f'stock_{code.replace(".", "_")}.csv'
            df.to_csv(DATA_DIR / filename, index=False)
            print(f'OK {len(df)} rows')
            success += 1
        else:
            print(f'Error: {rs.error_msg}')
            failed += 1
    except Exception as e:
        print(f'Exception: {str(e)[:50]}')
        failed += 1

    time.sleep(0.5)

bs.logout()

print(f'\n=== Summary ===')
print(f'Success: {success}')
print(f'Failed: {failed}')
print(f'Data saved to: {DATA_DIR}')
