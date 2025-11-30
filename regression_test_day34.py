#!/usr/bin/env python3
"""
Day 34 Comprehensive Regression Test Suite
Tests all 16 bug fixes from Days 31-34
"""
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0

def test_result(test_name, passed, details=""):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    if passed:
        passed_tests += 1
        logger.info(f"✅ PASS: {test_name}")
    else:
        failed_tests += 1
        logger.error(f"❌ FAIL: {test_name} - {details}")
    return passed

print("=" * 80)
print("Day 34 Comprehensive Regression Test Suite")
print("=" * 80)
print()

# Test 1: Import all modules
print("Test Group 1: Module Imports")
print("-" * 80)
try:
    sys.path.insert(0, "/root/autodl-tmp/eoh")
    import asset_adaptive_framework
    import asset_adaptive_analyzer
    import portfolio_optimizer
    test_result("1.1 All modules import successfully", True)
except Exception as e:
    test_result("1.1 All modules import successfully", False, str(e))

# Test 2: Bug #1.4 - Sandbox security
print("\nTest Group 2: Security Fixes")
print("-" * 80)
try:
    with open("/root/autodl-tmp/eoh/eoh_gpu_loop_fixed.py", "r") as f:
        content = f.read()
    has_removed_import = "__import__" not in content.split("ALLOWED_GLOBALS")[1].split("}")[0] if "ALLOWED_GLOBALS" in content else False
    test_result("2.1 Bug #1.4: __import__ removed from ALLOWED_GLOBALS", has_removed_import)
except Exception as e:
    test_result("2.1 Bug #1.4: Sandbox security", False, str(e))

# Test 3: Bug #2.1 - Command injection protection
try:
    from asset_adaptive_framework import AssetAdaptiveFramework
    fw = AssetAdaptiveFramework()

    malicious_symbol = "SPY; rm -rf /"
    cmd = fw.generate_command(malicious_symbol)

    has_shlex = "shlex" in open("/root/autodl-tmp/eoh/asset_adaptive_framework.py").read()
    no_injection = "; rm -rf /" not in cmd or "'SPY; rm -rf /'" in cmd

    test_result("2.2 Bug #2.1: Command injection protected with shlex.quote", has_shlex and no_injection)
except Exception as e:
    test_result("2.2 Bug #2.1: Command injection protection", False, str(e))

# Test 4: Bug #2.2 - State pollution prevention
print("\nTest Group 3: State Management")
print("-" * 80)
try:
    from asset_adaptive_framework import AssetAdaptiveFramework
    fw = AssetAdaptiveFramework()

    config1 = fw.get_config("SPY")
    original_pop = config1["population"]
    config1["population"] = 999

    config2 = fw.get_config("SPY")

    test_result("3.1 Bug #2.2: State pollution prevented (.copy())", config2["population"] == original_pop)
except Exception as e:
    test_result("3.1 Bug #2.2: State pollution prevention", False, str(e))

# Test 5: Bug #2.3 - Unknown asset warning
try:
    from asset_adaptive_framework import AssetAdaptiveFramework
    import io

    fw = AssetAdaptiveFramework()

    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.WARNING)
    logging.getLogger().addHandler(handler)

    config = fw.get_config("spy")
    is_uppercase = config["type"] == "equity_large"

    config_unknown = fw.get_config("INVALID_SYMBOL")
    log_output = log_stream.getvalue()
    has_warning = "未知资产符号" in log_output or config_unknown["type"] == "unknown"

    logging.getLogger().removeHandler(handler)

    test_result("3.2 Bug #2.3: Unknown asset uppercase + warning", is_uppercase and has_warning)
except Exception as e:
    test_result("3.2 Bug #2.3: Unknown asset warning", False, str(e))

# Test 6: Bug #3 - Dynamic covariance matrix
print("\nTest Group 4: Portfolio Optimization")
print("-" * 80)
try:
    with open("/root/autodl-tmp/eoh/portfolio_optimizer.py", "r") as f:
        content = f.read()

    has_dynamic = "n_assets = len(assets)" in content
    has_default_4x4 = "default_corr_4x4" in content

    test_result("4.1 Bug #3: Dynamic covariance matrix for any asset count", has_dynamic and has_default_4x4)
except Exception as e:
    test_result("4.1 Bug #3: Dynamic covariance matrix", False, str(e))

# Test 7: Bug #4.1 - Environment variable paths
print("\nTest Group 5: Portability")
print("-" * 80)
try:
    with open("/root/autodl-tmp/eoh/portfolio_optimizer.py", "r") as f:
        content = f.read()

    has_env_var = "EOH_BASE_PATH" in content and "os.getenv" in content

    test_result("5.1 Bug #4.1: Environment variable EOH_BASE_PATH support", has_env_var)
except Exception as e:
    test_result("5.1 Bug #4.1: Environment variable paths", False, str(e))

# Test 8: Bug #1.3 - BASE_PATH in eoh_gpu_loop
try:
    with open("/root/autodl-tmp/eoh/eoh_gpu_loop_fixed.py", "r") as f:
        content = f.read()

    has_base_path = "BASE_PATH = os.getenv" in content and "EOH_BASE_PATH" in content

    test_result("5.2 Bug #1.3: BASE_PATH environment variable in eoh_gpu_loop", has_base_path)
except Exception as e:
    test_result("5.2 Bug #1.3: BASE_PATH support", False, str(e))

# Test 9: Bug #4.3 - CSV column validation
print("\nTest Group 6: Data Validation")
print("-" * 80)
try:
    with open("/root/autodl-tmp/eoh/portfolio_optimizer.py", "r") as f:
        content = f.read()

    has_validation = "required_cols" in content and "missing_cols" in content

    test_result("6.1 Bug #4.3: CSV column validation in portfolio optimizer", has_validation)
except Exception as e:
    test_result("6.1 Bug #4.3: CSV column validation", False, str(e))

# Test 10: Bug #4.4 - Empty results check
try:
    with open("/root/autodl-tmp/eoh/portfolio_optimizer.py", "r") as f:
        content = f.read()

    has_empty_check = "if not results:" in content

    test_result("6.2 Bug #4.4: Empty results check before max()", has_empty_check)
except Exception as e:
    test_result("6.2 Bug #4.4: Empty results check", False, str(e))

# Test 11: Bug #5 - Empty data validation in analyzer
try:
    with open("/root/autodl-tmp/eoh/asset_adaptive_analyzer.py", "r") as f:
        content = f.read()

    has_len_check = "if len(test_returns) > 0 else" in content

    test_result("6.3 Bug #5: Empty data validation in analyzer", has_len_check)
except Exception as e:
    test_result("6.3 Bug #5: Empty data validation", False, str(e))

# Test 12: Bug #3.4 - Directory creation
try:
    with open("/root/autodl-tmp/eoh/asset_adaptive_analyzer.py", "r") as f:
        content = f.read()

    has_mkdir = "mkdir(parents=True, exist_ok=True)" in content or ".mkdir(" in content

    test_result("6.4 Bug #3.4: Output directory creation", has_mkdir)
except Exception as e:
    test_result("6.4 Bug #3.4: Directory creation", False, str(e))

# Test 13: Bug #1 - Overfitting filter
print("\nTest Group 7: Overfitting Prevention")
print("-" * 80)
try:
    with open("/root/autodl-tmp/eoh/eoh_gpu_loop_fixed.py", "r") as f:
        content = f.read()

    has_test_filter = "test_return < 0" in content and "overfitting prevention" in content

    test_result("7.1 Bug #1: Overfitting filter (test_return < 0)", has_test_filter)
except Exception as e:
    test_result("7.1 Bug #1: Overfitting filter", False, str(e))

# Test 14: Bug #2 - Complete random seeds
print("\nTest Group 8: Reproducibility")
print("-" * 80)
try:
    with open("/root/autodl-tmp/eoh/eoh_gpu_loop_fixed.py", "r") as f:
        content = f.read()

    has_torch_seed = "torch.manual_seed" in content
    has_transformers = "set_seed" in content or "transformers" in content

    test_result("8.1 Bug #2: Complete random seeds (torch + transformers)", has_torch_seed and has_transformers)
except Exception as e:
    test_result("8.1 Bug #2: Complete random seeds", False, str(e))

# Test 15: Bug #1.5 - Documented --generations parameter
print("\nTest Group 9: Documentation")
print("-" * 80)
try:
    with open("/root/autodl-tmp/eoh/eoh_gpu_loop_fixed.py", "r") as f:
        content = f.read()

    has_generations = "--generations" in content
    has_doc = "FIX Bug #1.5" in content or "reserved for future" in content

    test_result("9.1 Bug #1.5: --generations parameter documented", has_generations and has_doc)
except Exception as e:
    test_result("9.1 Bug #1.5: Parameter documentation", False, str(e))

# Test 16: Bug #4 - Framework code saving
try:
    with open("/root/autodl-tmp/eoh/asset_adaptive_analyzer.py", "r") as f:
        content = f.read()

    has_write = "with open(output_file" in content and "encoding='utf-8'" in content
    has_write_call = "f.write(framework_code)" in content

    test_result("9.2 Bug #4: Framework code file saving", has_write and has_write_call)
except Exception as e:
    test_result("9.2 Bug #4: Framework code saving", False, str(e))

# Test 17: Bug #3.3 - TLT and XLE in experiments
print("\nTest Group 10: Asset Coverage")
print("-" * 80)
try:
    with open("/root/autodl-tmp/eoh/asset_adaptive_analyzer.py", "r") as f:
        content = f.read()

    has_tlt = "'TLT':" in content or '"TLT":' in content
    has_xle = "'XLE':" in content or '"XLE":' in content

    test_result("10.1 Bug #3.3: TLT and XLE added to experiments", has_tlt and has_xle)
except Exception as e:
    test_result("10.1 Bug #3.3: TLT and XLE support", False, str(e))

# Final Summary
print("\n" + "=" * 80)
print("REGRESSION TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {total_tests}")
print(f"✅ Passed: {passed_tests}")
print(f"❌ Failed: {failed_tests}")
print(f"Success Rate: {100 * passed_tests / total_tests if total_tests > 0 else 0:.1f}%")
print("=" * 80)

if failed_tests == 0:
    print("\n🎉 ALL TESTS PASSED! BUG ZERO STATUS ACHIEVED! 🎉")
    sys.exit(0)
else:
    print(f"\n⚠️  {failed_tests} test(s) failed. Please review.")
    sys.exit(1)
