#!/usr/bin/env python3
"""
Experiment 1: Web Scraper Evaluator
自动化评估60个生成的Web爬虫样本

评估维度:
1. 语法正确性 (Syntax)
2. 运行时稳定性 (Runtime)
3. 功能完整性 (Functionality)
4. 安全性 (Security)
"""

import os
import sys
import json
import subprocess
import traceback
from pathlib import Path
from datetime import datetime
import numpy as np
from typing import Dict, List, Tuple

# ============================================================================
# 配置
# ============================================================================

EXPERIMENT_DIR = Path("/root/autodl-tmp/eoh/experiment1_web_scraper")
BASELINE_DIR = EXPERIMENT_DIR / "baseline"
MULTILAYER_DIR = EXPERIMENT_DIR / "multilayer"
RESULTS_DIR = EXPERIMENT_DIR / "evaluation_results"

# ============================================================================
# WebScraperEvaluator类
# ============================================================================

class WebScraperEvaluator:
    """Web爬虫代码评估器"""

    def __init__(self):
        self.test_url = "https://news.ycombinator.com"

    def test_syntax(self, code: str) -> Tuple[bool, str]:
        """
        语法检查

        Returns:
            (is_valid, error_message)
        """
        try:
            compile(code, "<string>", "exec")
            return True, None
        except SyntaxError as e:
            return False, f"SyntaxError at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def test_runtime(self, code: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        运行时测试 (不实际运行网络请求，只检查是否能执行)

        Args:
            code: Python代码
            timeout: 超时时间(秒)

        Returns:
            (is_runnable, error_message)
        """
        # 创建临时文件
        temp_file = Path("/tmp/test_scraper.py")
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                # 注入测试模式：替换实际网络请求为mock
                test_code = self._inject_test_mode(code)
                f.write(test_code)

            # 尝试执行
            result = subprocess.run(
                [sys.executable, str(temp_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return True, None
            else:
                return False, f"RuntimeError: {result.stderr[:500]}"

        except subprocess.TimeoutExpired:
            return False, "Timeout: Execution exceeded 30 seconds"
        except Exception as e:
            return False, f"Execution error: {str(e)}"
        finally:
            if temp_file.exists():
                temp_file.unlink()

    def _inject_test_mode(self, code: str) -> str:
        """
        注入测试模式：避免实际网络请求

        将requests.get()替换为返回mock HTML
        """
        mock_html = '''
<html>
<tr class="athing" id="1">
    <span class="titleline"><a href="https://example.com">Test Article</a></span>
</tr>
<tr>
    <td class="subtext">
        <span class="score">100 points</span>
        <a>10 comments</a>
    </td>
</tr>
</html>
'''

        # 在代码开头添加mock
        mock_code = f"""
# === TEST MODE: Mock网络请求 ===
import requests as _real_requests

class MockResponse:
    def __init__(self):
        self.text = '''{mock_html}'''
        self.status_code = 200

    def raise_for_status(self):
        pass

class MockRequests:
    @staticmethod
    def get(*args, **kwargs):
        import time
        time.sleep(0.1)  # 模拟网络延迟
        return MockResponse()

    exceptions = _real_requests.exceptions

# 替换requests模块
import sys
sys.modules['requests'] = MockRequests()

# === 原始代码 ===
{code}
"""
        return mock_code

    def test_functionality(self, code: str) -> Tuple[float, Dict]:
        """
        功能性测试

        检查代码是否包含必要的功能元素

        Returns:
            (score, checks_dict)
        """
        checks = {
            "has_requests": "import requests" in code,
            "has_beautifulsoup": ("from bs4 import BeautifulSoup" in code or
                                 "import bs4" in code),
            "has_csv": "import csv" in code,
            "has_rate_limit": ("time.sleep" in code or "sleep(" in code),
            "has_error_handling": ("try:" in code and "except" in code),
            "has_user_agent": ("User-Agent" in code or "headers" in code),
            "saves_to_csv": (".csv" in code and "open(" in code),
            "has_functions": ("def " in code),
            "has_main": ("if __name__" in code or "def main" in code),
        }

        score = sum(checks.values()) / len(checks) * 100
        return score, checks

    def test_security(self, code: str) -> Tuple[float, List[str]]:
        """
        安全性测试

        检查潜在的安全隐患

        Returns:
            (score, issues_list)
        """
        issues = []

        # 检查危险操作
        if "os.system" in code or "subprocess.call" in code:
            issues.append("Dangerous system call detected")

        if "eval(" in code or "exec(" in code:
            issues.append("Dangerous eval/exec detected")

        # 检查SQL注入风险 (虽然爬虫不常见，但检查一下)
        if "execute(" in code and ("%" in code or ".format(" in code):
            issues.append("Potential SQL injection pattern")

        # 检查rate limiting
        if "sleep" not in code and "time.sleep" not in code:
            issues.append("Missing rate limiting")

        # 检查error handling
        if "try:" not in code:
            issues.append("Missing error handling")

        # 检查User-Agent (礼貌爬虫)
        if "User-Agent" not in code and "headers" not in code:
            issues.append("Missing User-Agent header")

        # 评分: 每个问题-15分
        score = max(0, 100 - len(issues) * 15)
        return score, issues

    def comprehensive_eval(self, code: str, sample_id: int, group: str) -> Dict:
        """
        综合评估

        Returns:
            完整的评估结果字典
        """
        print(f"  🔍 评估样本 #{sample_id} ({group})...")

        results = {
            "sample_id": sample_id,
            "group": group,
            "timestamp": datetime.now().isoformat(),
        }

        # 1. 语法检查
        syntax_ok, syntax_error = self.test_syntax(code)
        results["syntax"] = {
            "pass": syntax_ok,
            "error": syntax_error
        }

        # 2. 运行时测试 (仅在语法正确时运行)
        if syntax_ok:
            runtime_ok, runtime_error = self.test_runtime(code)
            results["runtime"] = {
                "pass": runtime_ok,
                "error": runtime_error
            }
        else:
            results["runtime"] = {
                "pass": False,
                "error": "Skipped due to syntax error"
            }

        # 3. 功能性测试
        func_score, func_checks = self.test_functionality(code)
        results["functionality"] = {
            "score": func_score,
            "checks": func_checks
        }

        # 4. 安全性测试
        sec_score, sec_issues = self.test_security(code)
        results["security"] = {
            "score": sec_score,
            "issues": sec_issues
        }

        # 综合评分
        if not syntax_ok:
            total_score = 0
        elif not results["runtime"]["pass"]:
            total_score = 25  # 语法正确得25分
        else:
            total_score = (
                25 +  # 语法正确
                25 +  # 运行时正确
                func_score * 0.3 +  # 功能性30%
                sec_score * 0.2     # 安全性20%
            )

        results["total_score"] = round(total_score, 2)

        return results


# ============================================================================
# 主评估流程
# ============================================================================

def evaluate_all_samples():
    """评估所有样本"""

    print("="*80)
    print("Experiment 1: Web Scraper Evaluation - Day 36")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 创建结果目录
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    evaluator = WebScraperEvaluator()

    all_results = {
        "baseline": [],
        "multilayer": []
    }

    # ========================================================================
    # 评估基线组 (30个样本)
    # ========================================================================

    print("📊 评估基线组 (Baseline Prompt)...")
    baseline_files = sorted(BASELINE_DIR.glob("sample_*.py"))

    for i, code_file in enumerate(baseline_files, 1):
        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                code = f.read()

            result = evaluator.comprehensive_eval(code, i, "baseline")
            result["code_file"] = str(code_file)
            all_results["baseline"].append(result)

            print(f"    ✅ #{i}: {result['total_score']:.1f}/100 "
                  f"(语法: {result['syntax']['pass']}, "
                  f"运行: {result['runtime']['pass']}, "
                  f"功能: {result['functionality']['score']:.1f}, "
                  f"安全: {result['security']['score']:.1f})")

        except Exception as e:
            print(f"    ❌ #{i}: 评估失败 - {str(e)}")
            all_results["baseline"].append({
                "sample_id": i,
                "group": "baseline",
                "code_file": str(code_file),
                "error": str(e),
                "total_score": 0
            })

    # ========================================================================
    # 评估多层次组 (30个样本)
    # ========================================================================

    print("\n📊 评估多层次组 (Multilayer Prompt)...")
    multilayer_files = sorted(MULTILAYER_DIR.glob("sample_*.py"))

    for i, code_file in enumerate(multilayer_files, 1):
        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                code = f.read()

            result = evaluator.comprehensive_eval(code, i, "multilayer")
            result["code_file"] = str(code_file)
            all_results["multilayer"].append(result)

            print(f"    ✅ #{i}: {result['total_score']:.1f}/100 "
                  f"(语法: {result['syntax']['pass']}, "
                  f"运行: {result['runtime']['pass']}, "
                  f"功能: {result['functionality']['score']:.1f}, "
                  f"安全: {result['security']['score']:.1f})")

        except Exception as e:
            print(f"    ❌ #{i}: 评估失败 - {str(e)}")
            all_results["multilayer"].append({
                "sample_id": i,
                "group": "multilayer",
                "code_file": str(code_file),
                "error": str(e),
                "total_score": 0
            })

    # ========================================================================
    # 保存结果
    # ========================================================================

    # 保存原始结果
    baseline_results_file = RESULTS_DIR / "baseline_results.json"
    with open(baseline_results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results["baseline"], f, indent=2, ensure_ascii=False)

    multilayer_results_file = RESULTS_DIR / "multilayer_results.json"
    with open(multilayer_results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results["multilayer"], f, indent=2, ensure_ascii=False)

    # ========================================================================
    # 统计分析
    # ========================================================================

    print("\n" + "="*80)
    print("📈 统计分析")
    print("="*80)

    stats = compute_statistics(all_results)

    # 保存统计结果
    stats_file = RESULTS_DIR / "comparison_statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    # 打印对比表
    print_comparison_table(stats)

    # ========================================================================
    # 完成
    # ========================================================================

    print("\n" + "="*80)
    print("✅ 评估完成")
    print("="*80)
    print(f"基线组结果: {baseline_results_file}")
    print(f"多层次组结果: {multilayer_results_file}")
    print(f"统计分析: {stats_file}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("下一步: 运行 experiment1_analyze_results.py 进行深度分析")


def compute_statistics(all_results: Dict) -> Dict:
    """计算统计指标"""

    def extract_scores(results_list):
        """从结果列表提取各项指标"""
        scores = {
            "total_scores": [],
            "syntax_pass": [],
            "runtime_pass": [],
            "functionality_scores": [],
            "security_scores": []
        }

        for r in results_list:
            if "error" in r:
                continue

            scores["total_scores"].append(r["total_score"])
            scores["syntax_pass"].append(1 if r["syntax"]["pass"] else 0)
            scores["runtime_pass"].append(1 if r["runtime"]["pass"] else 0)
            scores["functionality_scores"].append(r["functionality"]["score"])
            scores["security_scores"].append(r["security"]["score"])

        return scores

    baseline_scores = extract_scores(all_results["baseline"])
    multilayer_scores = extract_scores(all_results["multilayer"])

    stats = {
        "baseline": {
            "sample_count": len(all_results["baseline"]),
            "avg_total_score": float(np.mean(baseline_scores["total_scores"])) if baseline_scores["total_scores"] else 0,
            "syntax_pass_rate": float(np.mean(baseline_scores["syntax_pass"]) * 100) if baseline_scores["syntax_pass"] else 0,
            "runtime_pass_rate": float(np.mean(baseline_scores["runtime_pass"]) * 100) if baseline_scores["runtime_pass"] else 0,
            "avg_functionality_score": float(np.mean(baseline_scores["functionality_scores"])) if baseline_scores["functionality_scores"] else 0,
            "avg_security_score": float(np.mean(baseline_scores["security_scores"])) if baseline_scores["security_scores"] else 0,
        },
        "multilayer": {
            "sample_count": len(all_results["multilayer"]),
            "avg_total_score": float(np.mean(multilayer_scores["total_scores"])) if multilayer_scores["total_scores"] else 0,
            "syntax_pass_rate": float(np.mean(multilayer_scores["syntax_pass"]) * 100) if multilayer_scores["syntax_pass"] else 0,
            "runtime_pass_rate": float(np.mean(multilayer_scores["runtime_pass"]) * 100) if multilayer_scores["runtime_pass"] else 0,
            "avg_functionality_score": float(np.mean(multilayer_scores["functionality_scores"])) if multilayer_scores["functionality_scores"] else 0,
            "avg_security_score": float(np.mean(multilayer_scores["security_scores"])) if multilayer_scores["security_scores"] else 0,
        }
    }

    # 计算改进
    stats["improvement"] = {
        "total_score": stats["multilayer"]["avg_total_score"] - stats["baseline"]["avg_total_score"],
        "syntax_pass_rate": stats["multilayer"]["syntax_pass_rate"] - stats["baseline"]["syntax_pass_rate"],
        "runtime_pass_rate": stats["multilayer"]["runtime_pass_rate"] - stats["baseline"]["runtime_pass_rate"],
        "functionality_score": stats["multilayer"]["avg_functionality_score"] - stats["baseline"]["avg_functionality_score"],
        "security_score": stats["multilayer"]["avg_security_score"] - stats["baseline"]["avg_security_score"],
    }

    return stats


def print_comparison_table(stats: Dict):
    """打印对比表"""

    print("\n" + "="*80)
    print("对比结果")
    print("="*80)
    print()

    print(f"{'指标':<30} {'基线组':<15} {'多层次组':<15} {'改进':<15}")
    print("-" * 80)

    metrics = [
        ("样本数量", "sample_count", ""),
        ("平均总分", "avg_total_score", "{:.2f}"),
        ("语法通过率 (%)", "syntax_pass_rate", "{:.1f}%"),
        ("运行通过率 (%)", "runtime_pass_rate", "{:.1f}%"),
        ("功能评分", "avg_functionality_score", "{:.2f}"),
        ("安全评分", "avg_security_score", "{:.2f}"),
    ]

    for label, key, fmt in metrics:
        baseline_val = stats["baseline"][key]
        multilayer_val = stats["multilayer"][key]

        if fmt:
            baseline_str = fmt.format(baseline_val)
            multilayer_str = fmt.format(multilayer_val)
            if key != "sample_count":
                improvement = multilayer_val - baseline_val
                if "%" in fmt:
                    improvement_str = f"{improvement:+.1f}%"
                else:
                    improvement_str = f"{improvement:+.2f}"
            else:
                improvement_str = "-"
        else:
            baseline_str = str(baseline_val)
            multilayer_str = str(multilayer_val)
            improvement_str = "-"

        print(f"{label:<30} {baseline_str:<15} {multilayer_str:<15} {improvement_str:<15}")

    print()


if __name__ == "__main__":
    evaluate_all_samples()
