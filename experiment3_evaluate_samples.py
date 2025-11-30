#!/usr/bin/env python3
"""
Experiment 3: Data Cleaning Script Evaluation
评估数据清洗脚本的语法、安全性、功能完整性

重点评估维度：
1. 语法正确性 - AST解析
2. 数据安全性 - 原始数据保护、错误处理
3. 功能完整性 - 缺失值、类型转换、异常值、验证
4. 代码质量 - 日志、文档、结构
"""

import ast
import json
import re
from pathlib import Path
from datetime import datetime

class DataCleaningEvaluator:
    """数据清洗脚本评估器"""

    def __init__(self):
        self.results = []

    def evaluate_sample(self, code: str, sample_id: int, prompt_type: str) -> dict:
        """评估单个样本"""
        result = {
            "id": sample_id,
            "prompt_type": prompt_type,
            "syntax_valid": False,
            "safety_score": 0,
            "functionality_score": 0,
            "quality_score": 0,
            "total_score": 0,
            "safety_details": {},
            "functionality_details": {},
            "quality_details": {},
            "issues": []
        }

        # 1. 语法检查
        try:
            ast.parse(code)
            result["syntax_valid"] = True
        except SyntaxError as e:
            result["issues"].append(f"Syntax error: {e}")
            return result

        # 2. 数据安全性检查 (30分)
        safety = self.check_safety(code)
        result["safety_details"] = safety
        result["safety_score"] = safety["score"]

        # 3. 功能完整性检查 (50分)
        functionality = self.check_functionality(code)
        result["functionality_details"] = functionality
        result["functionality_score"] = functionality["score"]

        # 4. 代码质量检查 (20分)
        quality = self.check_quality(code)
        result["quality_details"] = quality
        result["quality_score"] = quality["score"]

        # 总分
        result["total_score"] = (
            result["safety_score"] +
            result["functionality_score"] +
            result["quality_score"]
        )

        return result

    def check_safety(self, code: str) -> dict:
        """数据安全性检查 (30分)"""
        checks = {
            "separate_output_file": False,     # 10分 - 不修改原始文件
            "error_handling": False,            # 10分 - try-except
            "file_exists_check": False,         # 5分 - 检查文件存在
            "encoding_handling": False,         # 5分 - 处理编码问题
        }

        code_lower = code.lower()

        # 检查是否使用独立的输出文件
        if any(x in code for x in ['output', 'cleaned', 'to_csv']):
            # 确保不是直接覆盖输入文件
            if 'to_csv' in code and 'output' in code_lower:
                checks["separate_output_file"] = True

        # 错误处理
        if 'try:' in code and 'except' in code:
            checks["error_handling"] = True
        if any(x in code for x in ['Exception', 'Error', 'ValueError', 'FileNotFoundError']):
            checks["error_handling"] = True

        # 文件存在检查
        if any(x in code for x in ['exists(', 'isfile(', 'Path(', 'os.path.exists']):
            checks["file_exists_check"] = True
        if 'FileNotFoundError' in code:
            checks["file_exists_check"] = True

        # 编码处理
        if any(x in code for x in ["encoding='", 'encoding="', 'utf-8', 'latin-1']):
            checks["encoding_handling"] = True

        # 计算分数
        scores = {
            "separate_output_file": 10,
            "error_handling": 10,
            "file_exists_check": 5,
            "encoding_handling": 5,
        }

        total = sum(scores[k] for k, v in checks.items() if v)

        return {
            "checks": checks,
            "score": total,
            "max_score": 30
        }

    def check_functionality(self, code: str) -> dict:
        """功能完整性检查 (50分)"""
        checks = {
            "csv_loading": False,               # 8分 - pandas read_csv
            "missing_value_handling": False,    # 12分 - fillna/dropna
            "type_conversion": False,           # 12分 - to_datetime/astype
            "outlier_detection": False,         # 10分 - IQR/quantile/业务规则
            "data_validation": False,           # 8分 - 数据范围/重复检查
        }

        code_lower = code.lower()

        # CSV加载
        if 'read_csv' in code or 'pandas' in code:
            checks["csv_loading"] = True

        # 缺失值处理
        missing_patterns = [
            'fillna', 'dropna', 'isnull', 'isna', 'notnull', 'notna',
            'missing', 'nan', 'null'
        ]
        if any(pattern in code_lower for pattern in missing_patterns):
            checks["missing_value_handling"] = True

        # 类型转换
        type_patterns = [
            'to_datetime', 'astype', 'pd.to_numeric', 'to_numeric',
            'int(', 'float(', 'str(', 'datetime'
        ]
        if any(pattern in code_lower for pattern in type_patterns):
            checks["type_conversion"] = True

        # 异常值检测
        outlier_patterns = [
            'quantile', 'iqr', 'outlier', 'z-score', 'zscore',
            'std()', 'mean()', 'median()'
        ]
        # 业务规则
        if any(pattern in code_lower for pattern in outlier_patterns):
            checks["outlier_detection"] = True
        # 或者检查范围验证
        if re.search(r'(>|<|>=|<=)\s*\d+', code):
            checks["outlier_detection"] = True

        # 数据验证
        validation_patterns = [
            'duplicated', 'duplicate', 'drop_duplicates',
            'validate', 'check', 'assert', 'range'
        ]
        if any(pattern in code_lower for pattern in validation_patterns):
            checks["data_validation"] = True
        # 或者检查范围检查逻辑
        if re.search(r'(min_|max_|valid_)', code_lower):
            checks["data_validation"] = True

        # 计算分数
        scores = {
            "csv_loading": 8,
            "missing_value_handling": 12,
            "type_conversion": 12,
            "outlier_detection": 10,
            "data_validation": 8,
        }

        total = sum(scores[k] for k, v in checks.items() if v)

        return {
            "checks": checks,
            "score": total,
            "max_score": 50
        }

    def check_quality(self, code: str) -> dict:
        """代码质量检查 (20分)"""
        checks = {
            "has_logging": False,           # 6分 - logging
            "has_docstrings": False,        # 5分 - docstrings
            "has_functions": False,         # 5分 - 模块化
            "has_main_function": False,     # 4分 - main函数
        }

        # Logging
        if 'logging' in code or 'logger' in code:
            checks["has_logging"] = True
        if any(x in code for x in ['logger.info', 'logger.warning', 'logger.error']):
            checks["has_logging"] = True

        # Docstrings
        if '"""' in code or "'''" in code:
            # 检查是否是真正的docstring（不仅仅是注释）
            if re.search(r'def\s+\w+.*:\s*\n\s*["\']', code):
                checks["has_docstrings"] = True

        # 函数定义
        tree = ast.parse(code)
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        if len(functions) >= 3:  # 至少3个函数
            checks["has_functions"] = True

        # Main函数
        if 'def main' in code or "if __name__ == '__main__'" in code:
            checks["has_main_function"] = True

        # 计算分数
        scores = {
            "has_logging": 6,
            "has_docstrings": 5,
            "has_functions": 5,
            "has_main_function": 4,
        }

        total = sum(scores[k] for k, v in checks.items() if v)

        return {
            "checks": checks,
            "score": total,
            "max_score": 20
        }

    def evaluate_all(self, data_dir: Path) -> dict:
        """评估所有样本"""
        print("=" * 80)
        print("EXPERIMENT 3: DATA CLEANING SCRIPT EVALUATION")
        print("=" * 80)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        baseline_dir = data_dir / "baseline"
        multilayer_dir = data_dir / "multilayer"

        all_results = []

        # 评估基线样本
        print("\n[1/3] Evaluating baseline samples...")
        for code_file in sorted(baseline_dir.glob("*.py")):
            sample_id = int(code_file.stem.split("_")[1])
            with open(code_file, 'r', encoding='utf-8') as f:
                code = f.read()

            result = self.evaluate_sample(code, sample_id, "baseline")
            all_results.append(result)
            print(f"  Sample {sample_id:03d}: Safety={result['safety_score']}/30, "
                  f"Func={result['functionality_score']}/50, "
                  f"Quality={result['quality_score']}/20, "
                  f"Total={result['total_score']}/100")

        # 评估多层次样本
        print("\n[2/3] Evaluating multilayer samples...")
        for code_file in sorted(multilayer_dir.glob("*.py")):
            sample_id = int(code_file.stem.split("_")[1])
            with open(code_file, 'r', encoding='utf-8') as f:
                code = f.read()

            result = self.evaluate_sample(code, sample_id, "multilayer")
            all_results.append(result)
            print(f"  Sample {sample_id:03d}: Safety={result['safety_score']}/30, "
                  f"Func={result['functionality_score']}/50, "
                  f"Quality={result['quality_score']}/20, "
                  f"Total={result['total_score']}/100")

        # 保存结果
        print("\n[3/3] Saving results...")
        results_dir = data_dir / "evaluation_results"
        results_dir.mkdir(exist_ok=True)

        baseline_results = [r for r in all_results if r['prompt_type'] == 'baseline']
        multilayer_results = [r for r in all_results if r['prompt_type'] == 'multilayer']

        with open(results_dir / "baseline_results.json", 'w') as f:
            json.dump(baseline_results, f, indent=2)

        with open(results_dir / "multilayer_results.json", 'w') as f:
            json.dump(multilayer_results, f, indent=2)

        # 统计
        stats = self.calculate_statistics(baseline_results, multilayer_results)
        with open(results_dir / "comparison_statistics.json", 'w') as f:
            json.dump(stats, f, indent=2)

        # 打印结果
        print("\n" + "=" * 80)
        print("EVALUATION RESULTS")
        print("=" * 80)

        print("\n📊 BASELINE GROUP:")
        print(f"  Syntax valid: {stats['baseline']['syntax_valid_count']}/{stats['baseline']['total']}")
        print(f"  Avg Safety Score: {stats['baseline']['avg_safety']:.2f}/30")
        print(f"  Avg Functionality Score: {stats['baseline']['avg_functionality']:.2f}/50")
        print(f"  Avg Quality Score: {stats['baseline']['avg_quality']:.2f}/20")
        print(f"  Avg Total Score: {stats['baseline']['avg_total']:.2f}/100")

        print("\n📊 MULTILAYER GROUP:")
        print(f"  Syntax valid: {stats['multilayer']['syntax_valid_count']}/{stats['multilayer']['total']}")
        print(f"  Avg Safety Score: {stats['multilayer']['avg_safety']:.2f}/30")
        print(f"  Avg Functionality Score: {stats['multilayer']['avg_functionality']:.2f}/50")
        print(f"  Avg Quality Score: {stats['multilayer']['avg_quality']:.2f}/20")
        print(f"  Avg Total Score: {stats['multilayer']['avg_total']:.2f}/100")

        print("\n📈 IMPROVEMENT:")
        print(f"  Safety: +{stats['improvement']['safety']:.2f} points")
        print(f"  Functionality: +{stats['improvement']['functionality']:.2f} points")
        print(f"  Quality: +{stats['improvement']['quality']:.2f} points")
        print(f"  Total: +{stats['improvement']['total']:.2f} points")

        print("\n" + "=" * 80)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Results saved to: {results_dir}")
        print("=" * 80)

        return stats

    def calculate_statistics(self, baseline: list, multilayer: list) -> dict:
        """计算统计数据"""
        def calc_group_stats(results):
            valid = [r for r in results if r['syntax_valid']]
            return {
                "total": len(results),
                "syntax_valid_count": len(valid),
                "syntax_valid_rate": len(valid) / len(results) if results else 0,
                "avg_safety": sum(r['safety_score'] for r in valid) / len(valid) if valid else 0,
                "avg_functionality": sum(r['functionality_score'] for r in valid) / len(valid) if valid else 0,
                "avg_quality": sum(r['quality_score'] for r in valid) / len(valid) if valid else 0,
                "avg_total": sum(r['total_score'] for r in valid) / len(valid) if valid else 0,
            }

        baseline_stats = calc_group_stats(baseline)
        multilayer_stats = calc_group_stats(multilayer)

        return {
            "baseline": baseline_stats,
            "multilayer": multilayer_stats,
            "improvement": {
                "safety": multilayer_stats['avg_safety'] - baseline_stats['avg_safety'],
                "functionality": multilayer_stats['avg_functionality'] - baseline_stats['avg_functionality'],
                "quality": multilayer_stats['avg_quality'] - baseline_stats['avg_quality'],
                "total": multilayer_stats['avg_total'] - baseline_stats['avg_total'],
            }
        }


if __name__ == "__main__":
    evaluator = DataCleaningEvaluator()
    data_dir = Path("/root/autodl-tmp/eoh/experiment3_data_cleaning")
    evaluator.evaluate_all(data_dir)
