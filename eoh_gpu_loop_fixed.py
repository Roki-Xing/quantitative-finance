import os
import json
import textwrap
import argparse
import random
import re
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any, Tuple

import numpy as np
import pandas as pd
import requests

from backtesting import Backtest, Strategy
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from eoh_core.prompts import PromptLibrary, PromptStyle
from eoh_core.llm import LocalHFClient, extract_code_blocks
from eoh_core.utils import ensure_dir, log

try:
    import yfinance as yf
    _HAS_YF = True
except Exception:
    _HAS_YF = False


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--symbol", default="SPY")
    ap.add_argument("--train_start", required=True)
    ap.add_argument("--train_end", required=True)
    ap.add_argument("--test_start", required=True)
    ap.add_argument("--test_end", required=True)
    ap.add_argument("--generations", type=int, default=1)
    ap.add_argument("--population", type=int, default=8)
    ap.add_argument("--commission", type=float, default=0.0005)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--max_new_tokens", type=int, default=320)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--prompt-style", default="normal")
    ap.add_argument("--prompt-dir", default="prompts")
    return ap.parse_args()


def save_text(path: Path, txt: str):
    path.write_text(txt, encoding="utf-8")


def load_local_csv(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    # 优先尝试通用数据文件（Day 15 手动上传的固定范围数据）
    generic_fp = Path(f"/root/autodl-tmp/data/{symbol}_2020_2023.csv")
    if generic_fp.exists():
        # yfinance CSV 有多级表头，需要特殊处理
        df = pd.read_csv(generic_fp, header=[0, 1], index_col=0, parse_dates=True).sort_index()
        # 展平多级列名
        df.columns = [col[0] for col in df.columns]
        # 过滤到所需日期范围
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
        df = df.loc[(df.index >= start_dt) & (df.index <= end_dt)]
        log(f"[INFO] loaded from generic CSV: {generic_fp} rows={len(df)}")
        if len(df) > 0:
            return df
    
    # 回退到原始 cache 方式（保持向后兼容）
    cache_fp = Path(f"./price_cache/{symbol}_{start}_{end}.csv")
    if cache_fp.exists():
        df = pd.read_csv(cache_fp, index_col=0, parse_dates=True).sort_index()
        log(f"[INFO] local CSV hit: {cache_fp} rows={len(df)}")
        return df
    
    return None


def load_yf(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    if not _HAS_YF:
        return None
    try:
        df = yf.download(symbol, start=start, end=end, auto_adjust=False)
        if df is not None and len(df):
            df.index.name = "Date"
            return df
    except Exception as e:
        log(f"[WARN] yfinance error: {e}")
    return None


def load_prices(symbol: str, start: str, end: str) -> pd.DataFrame:
    for fn in (load_local_csv, load_yf):
        df = fn(symbol, start, end)
        if df is not None and len(df):
            return df
    raise RuntimeError("no price data")


def slice_df(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    df = df.loc[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))].copy()
    # Fix column names for Backtesting.py
    df.columns = [col.capitalize() for col in df.columns]
    return df


def SMA(series, n=10):
    s = pd.Series(series, copy=False)
    return s.rolling(int(n)).mean().to_numpy()


def RSI(series, n=14):
    s = pd.Series(series, copy=False).astype(float)
    delta = s.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    roll_up = up.rolling(int(n)).mean()
    roll_down = down.rolling(int(n)).mean()
    rs = roll_up / (roll_down.replace(0, np.nan) + 1e-12)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0).to_numpy()


def crossover(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    if len(a) < 2 or len(b) < 2:
        return False
    return (a[-2] < b[-2]) and (a[-1] > b[-1])


ALLOWED_GLOBALS = {
    "__builtins__": {
        "__name__": "__main__",
        "__import__": __import__,
        "__build_class__": __build_class__,
        "abs": abs,
        "min": min,
        "max": max,
        "range": range,
        "len": len,
        "sum": sum,
        "any": any,
        "all": all,
        "round": round,
        "enumerate": enumerate,
        "zip": zip,
    },
    "Strategy": Strategy,
    "SMA": SMA,
    "RSI": RSI,
    "crossover": crossover,
}


def sanitize_code(code: str) -> str:
    code = code.encode("ascii", errors="ignore").decode()
    code = code.replace("```python", "```").replace("```py", "```").replace("```", "")
    match = re.search(r"class\s+Strat\s*\(\s*Strategy\s*\)", code)
    if match:
        code = code[match.start():]
    
    code = code.replace("__init__", "init")

    replacements = {
        "self.I(SMA, 'SPY'": "self.I(SMA, self.data.Close",
        "self.I(SMA, \"SPY\"": "self.I(SMA, self.data.Close",
        "self.I(SMA, 'close'": "self.I(SMA, self.data.Close",
        "self.I(SMA, \"close\"": "self.I(SMA, self.data.Close",
        "self.I(RSI, 'SPY'": "self.I(RSI, self.data.Close",
        "self.I(RSI, \"SPY\"": "self.I(RSI, self.data.Close",
        "self.I(RSI, 'close'": "self.I(RSI, self.data.Close",
        "self.I(RSI, \"close\"": "self.I(RSI, self.data.Close",
        "self.data('SPY')": "self.data",
        "self.data(\"SPY\")": "self.data",
        "self.buy('SPY', 1)": "self.buy()",
        "self.sell('SPY', 1)": "self.sell()",
        "self.buy(\"SPY\", 1)": "self.buy()",
        "self.sell(\"SPY\", 1)": "self.sell()",
        "self.position.is_long == True": "self.position",
        "self.position.is_long == False": "not self.position",
        "self.position.is_long": "self.position",
    }
    for key, val in replacements.items():
        code = code.replace(key, val)

    code = re.sub(r"self\.I\(SMA,\s*(\d+)\)", r"self.I(SMA, self.data.Close, \1)", code)
    code = re.sub(r"self\.I\(RSI,\s*(\d+)\)", r"self.I(RSI, self.data.Close, \1)", code)
    code = re.sub(r"(self\.I\([A-Za-z_]+,\s*self\.data\.Close,\s*\d+)\s*,\s*'[^']+'\)", r"\1)", code)
    code = re.sub(r"(self\.I\([A-Za-z_]+,\s*self\.data\.Close,\s*\d+)\s*,\s*\"[^\"]+\"\)", r"\1)", code)

    banned = ("np.", "numpy(", "pd.", "pandas(", " ta.", "zipline", "symbol(", 
              "order_target_value", "order_target_percent")
    lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped.startswith("import ") or stripped.startswith("from "):
            continue
        if any(tok in stripped for tok in banned):
            continue
        lines.append(line.rstrip())

    cleaned = "\n".join(lines).strip()
    
#     if "class Strat(Strategy):" not in cleaned:
#         return "" 
    
    if not cleaned.endswith("\n"):
        cleaned += "\n"
        
    return cleaned


def safe_exec_strategy(code: str) -> Optional[Callable]:
    try:
        loc: Dict[str, Any] = {}
        exec(compile(code, "<llm_code>", "exec"), ALLOWED_GLOBALS, loc)
        Strat = loc.get("Strat")
        if Strat is None or not hasattr(Strat, "init") or not hasattr(Strat, "next"):
            return None
        return Strat
    except Exception as e:
        log(f"[WARN] exec failed: {e}")
        return None


def run_bt(df: pd.DataFrame, StratCls: Strategy, commission: float) -> Tuple[pd.Series, Backtest]:
    bt = Backtest(df, StratCls, cash=100_000, commission=commission, exclusive_orders=True)
    stats = bt.run()
    return stats, bt


def fitness_from_stats(st: pd.Series) -> float:
    r = float(st.get("Return [%]", 0.0))
    dd = float(st.get("Max. Drawdown [%]", 1.0))
    sharpe = float(st.get("Sharpe Ratio", 0.0))
    return r - 0.5 * max(0.0, dd) + 10.0 * max(0.0, sharpe)


def main():
    args = get_args()
    random.seed(args.seed)
    np.random.seed(args.seed)

    outdir = ensure_dir(args.outdir)
    prompt_dir = Path(args.prompt_dir).expanduser()
    if not prompt_dir.exists():
        prompt_dir = None

    prompt_library = PromptLibrary(base_dir=prompt_dir)
    style_tokens = [token.strip().lower() for token in args.prompt_style.split(",") if token.strip()]
    if not style_tokens:
        style_tokens = ["normal"]

    resolved_styles: List[PromptStyle] = []
    for token in style_tokens:
        try:
            resolved_styles.append(PromptStyle(token))
        except ValueError:
            log(f"[WARN] unknown prompt style '{token}', fallback to normal")
            resolved_styles.append(PromptStyle.NORMAL)

    templates = {style: prompt_library.get(style) for style in resolved_styles}
    default_template = templates[resolved_styles[0]]

    prompt_specs = []
    for idx in range(args.population):
        style = resolved_styles[idx % len(resolved_styles)]
        tmpl = templates[style]
        prompt_specs.append(
            {
                "index": idx + 1,
                "style": style,
                "template": tmpl,
                "prompt": tmpl.user.format(symbol=args.symbol),
            }
        )

    span_start = min(args.train_start, args.test_start)
    span_end = max(args.train_end, args.test_end)
    df_all = load_prices(args.symbol, span_start, span_end)
    
    df_train = slice_df(df_all, args.train_start, args.train_end)
    df_test = slice_df(df_all, args.test_start, args.test_end)
    log(f"[INFO] split: train={len(df_train)} test={len(df_test)}")

    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, use_fast=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_dir,
        device_map="auto",
        dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    log(f"[INFO] model loaded on {model.device}")
    client = LocalHFClient(tokenizer=tokenizer, model=model, system_prompt=default_template.system)

    gen_dir = ensure_dir(outdir / "gen01_codes")
    rows: List[Dict[str, Any]] = []

    for spec in prompt_specs:
        idx = spec["index"]
        template = spec["template"]
        prompt_text = spec["prompt"]
        log(f"[GEN] {idx}/{len(prompt_specs)} style={template.name}")

        raw = client.generate(
            prompt_text,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            system_prompt=template.system,
        )
        save_text(gen_dir / f"raw_{idx:03d}.txt", raw)

        code = extract_code_blocks(raw)
        if not code:
            log("[WARN] no code extracted")
            continue
            
        code = sanitize_code(code)
        if not code:
            log("[WARN] code discarded after sanitization")
            continue

        Strat = safe_exec_strategy(code)
        if Strat is None:
            log("[WARN] no valid Strat class")
            continue

        try:
            st_train, _ = run_bt(df_train, Strat, args.commission)
            st_test, _ = run_bt(df_test, Strat, args.commission)
            fit = fitness_from_stats(st_train)
            code_path = gen_dir / f"strat_{idx:03d}.py"
            save_text(code_path, code)
            rows.append(
                {
                    "id": idx,
                    "prompt_style": template.name,
                    "fitness": fit,
                    "train_Return_%": float(st_train.get("Return [%]", float("nan"))),
                    "train_Sharpe": float(st_train.get("Sharpe Ratio", float("nan"))),
                    "train_MaxDD_%": float(st_train.get("Max. Drawdown [%]", float("nan"))),
                    "test_Return_%": float(st_test.get("Return [%]", float("nan"))),
                    "test_Sharpe": float(st_test.get("Sharpe Ratio", float("nan"))),
                    "test_MaxDD_%": float(st_test.get("Max. Drawdown [%]", float("nan"))),
                    "code_path": str(code_path),
                }
            )
            log(
                "[OK] id={id} style={style} fit={fit:.2f} trainR={train:.2f} testR={test:.2f}".format(
                    id=idx,
                    style=template.name,
                    fit=fit,
                    train=rows[-1]["train_Return_%"],
                    test=rows[-1]["test_Return_%"],
                )
            )
        except Exception as exc:
            log(f"[WARN] backtest failed: {exc}")
            continue

    if not rows:
        log("[INFO] generation 1 done, valid=0")
        return

    df_res = pd.DataFrame(rows).sort_values("fitness", ascending=False)
    df_res.to_csv(outdir / "gen01.csv", index=False)
    best = df_res.iloc[0].to_dict()

    best_code = Path(best["code_path"]).read_text(encoding="utf-8")
    save_text(outdir / "best_strategy.py", best_code)
    save_text(outdir / "best_metrics.json", json.dumps(best, indent=2, ensure_ascii=False))
    readme = textwrap.dedent(
        f"""
        symbol: {args.symbol}
        train: {args.train_start} ~ {args.train_end}
        test : {args.test_start} ~ {args.test_end}
        population: {args.population}
        temperature: {args.temperature}
        commission: {args.commission}
        model_dir: {args.model_dir}
        prompt_styles: {", ".join(style.value for style in resolved_styles)}
        prompt_dir: {prompt_dir or 'built-ins'}
        """
    ).strip()
    save_text(outdir / "README.txt", readme + "\n")
    log(f"[INFO] generation 1 done, valid={len(rows)}, best id={int(best['id'])}")
    log(f"[INFO] results -> {outdir}")


if __name__ == "__main__":
    main()