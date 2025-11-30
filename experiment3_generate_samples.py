#!/usr/bin/env python3
"""
Experiment 3: Data Cleaning Script Generation
生成数据清洗/预处理脚本（基线 vs 多层次Prompt）

Task: 生成一个销售数据清洗脚本
- CSV数据加载
- 缺失值处理
- 数据类型转换
- 异常值检测
- 数据验证
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
import json
import time
from datetime import datetime

# ============================================================================
# PROMPT DEFINITIONS
# ============================================================================

BASELINE_PROMPT = """Write a Python script to clean sales data from a CSV file.

Requirements:
- Load CSV file with pandas
- Handle missing values
- Convert data types (dates, numbers)
- Detect and handle outliers
- Validate data quality
- Save cleaned data to output CSV

Input columns: date, product_id, quantity, price, customer_id, region"""

MULTILAYER_PROMPT = """# Task: Generate a Robust Data Cleaning Script for Sales Data

## Layer 1: Data Safety & Integrity Constraints (CRITICAL)

### 1.1 Data Preservation
- NEVER modify original data file
- Always create backup before processing
- Save to separate output file
- Log all transformations applied
- Enable rollback capability

### 1.2 Error Handling
- Handle malformed CSV gracefully (encoding issues, delimiters)
- Continue processing on row-level errors
- Log problematic rows for review
- Never crash on unexpected data
- Validate file exists before processing

### 1.3 Data Type Safety
- Explicit type checking before conversion
- Graceful degradation for invalid types
- Document assumptions about data formats
- Handle edge cases (empty strings, null-like values)

### 1.4 Memory Efficiency
- Process large files in chunks if needed
- Don't load entire dataset if unnecessary
- Clean up intermediate objects

## Layer 2: Functional Requirements

### 2.1 Required Operations

**Data Loading**:
```python
# Must handle:
- CSV with different encodings (utf-8, latin-1)
- Various delimiters (comma, semicolon, tab)
- Header row detection
- Date parsing
```

**Missing Value Handling**:
```python
# Strategies by column type:
- Numeric: mean/median imputation or forward-fill
- Categorical: mode or 'Unknown'
- Dates: forward-fill or drop
- Critical fields: drop row if missing
```

**Data Type Conversion**:
```python
# Required conversions:
- date: string → datetime
- product_id: string (keep as-is)
- quantity: float/int → int (handle decimals)
- price: string/float → float (handle currency symbols)
- customer_id: string (keep as-is)
- region: string → categorical
```

**Outlier Detection**:
```python
# Methods:
- IQR method for quantity and price
- Z-score for extreme values
- Business rules (quantity > 0, price > 0)
- Configurable thresholds
```

**Data Validation**:
```python
# Checks:
- Date within reasonable range (e.g., last 5 years)
- Quantity >= 0
- Price > 0
- No duplicate transactions (date + product + customer)
- Region in predefined list
```

### 2.2 Required Libraries
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path
```

### 2.3 Input/Output Specification
- Input: 'sales_data.csv' (or command-line argument)
- Output: 'sales_data_cleaned.csv'
- Log: 'data_cleaning.log'
- Report: 'cleaning_report.txt' (statistics)

## Layer 3: Code Quality Standards

### 3.1 Structure
- Separate function for each cleaning step
- Main function orchestrating the pipeline
- Configuration at top (thresholds, file paths)
- Type hints on all functions

### 3.2 Logging
- INFO: Progress updates (rows processed)
- WARNING: Suspicious data (outliers, unusual patterns)
- ERROR: Data quality issues
- DEBUG: Detailed transformation info

### 3.3 Reporting
Generate summary report with:
- Total rows processed
- Missing values filled (by column)
- Outliers detected and handled
- Invalid rows dropped
- Final data quality score

### 3.4 Documentation
- Docstrings for all functions
- Inline comments for complex logic
- README section in docstring explaining usage

## Layer 4: Complete Code Template

```python
#!/usr/bin/env python3
\"\"\"
Sales Data Cleaning Script
Handles missing values, outliers, type conversions, and validation

Usage:
    python clean_sales_data.py [input.csv] [output.csv]

Requirements:
    - pandas
    - numpy

Author: Generated Script
Date: 2025
\"\"\"

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path
from typing import Tuple, Dict

# ============================================================================
# Configuration
# ============================================================================

# File paths
DEFAULT_INPUT = 'sales_data.csv'
DEFAULT_OUTPUT = 'sales_data_cleaned.csv'
LOG_FILE = 'data_cleaning.log'
REPORT_FILE = 'cleaning_report.txt'

# Data validation rules
VALID_REGIONS = ['North', 'South', 'East', 'West', 'Central']
MIN_DATE = datetime(2020, 1, 1)
MAX_DATE = datetime.now()
MIN_QUANTITY = 0
MAX_QUANTITY = 10000  # Outlier threshold
MIN_PRICE = 0.01
MAX_PRICE = 100000  # Outlier threshold

# Missing value strategies
NUMERIC_STRATEGY = 'median'  # or 'mean'
CATEGORICAL_STRATEGY = 'mode'  # or 'Unknown'

# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# Helper Functions
# ============================================================================

def load_data(file_path: str) -> pd.DataFrame:
    \"\"\"
    Load CSV data with error handling for encoding and format issues

    Args:
        file_path: Path to input CSV file

    Returns:
        DataFrame with raw data
    \"\"\"
    logger.info(f"Loading data from {file_path}")

    if not Path(file_path).exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1']

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"Successfully loaded with {encoding} encoding")
            logger.info(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise

    raise ValueError("Could not load file with any standard encoding")

def handle_missing_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    \"\"\"
    Handle missing values using column-appropriate strategies

    Args:
        df: Input DataFrame

    Returns:
        Tuple of (cleaned DataFrame, statistics dict)
    \"\"\"
    logger.info("Handling missing values")

    stats = {}
    initial_missing = df.isnull().sum().to_dict()

    # Date: forward fill or drop
    if 'date' in df.columns:
        missing_count = df['date'].isnull().sum()
        if missing_count > 0:
            df['date'].fillna(method='ffill', inplace=True)
            df.dropna(subset=['date'], inplace=True)
            stats['date'] = f"Dropped {missing_count} rows with missing dates"

    # Numeric columns: median/mean
    numeric_cols = ['quantity', 'price']
    for col in numeric_cols:
        if col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                fill_value = df[col].median() if NUMERIC_STRATEGY == 'median' else df[col].mean()
                df[col].fillna(fill_value, inplace=True)
                stats[col] = f"Filled {missing_count} values with {NUMERIC_STRATEGY} ({fill_value:.2f})"

    # Categorical columns: mode or 'Unknown'
    categorical_cols = ['product_id', 'customer_id', 'region']
    for col in categorical_cols:
        if col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                if CATEGORICAL_STRATEGY == 'mode' and not df[col].mode().empty:
                    fill_value = df[col].mode()[0]
                else:
                    fill_value = 'Unknown'
                df[col].fillna(fill_value, inplace=True)
                stats[col] = f"Filled {missing_count} values with '{fill_value}'"

    logger.info(f"Missing value handling complete: {len(stats)} columns processed")
    return df, stats

def convert_data_types(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    \"\"\"
    Convert columns to appropriate data types

    Args:
        df: Input DataFrame

    Returns:
        Tuple of (converted DataFrame, statistics dict)
    \"\"\"
    logger.info("Converting data types")

    stats = {}
    errors = 0

    # Date conversion
    if 'date' in df.columns:
        try:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            invalid = df['date'].isnull().sum()
            if invalid > 0:
                logger.warning(f"{invalid} invalid dates converted to NaT")
                df.dropna(subset=['date'], inplace=True)
                errors += invalid
            stats['date'] = f"Converted to datetime, dropped {invalid} invalid"
        except Exception as e:
            logger.error(f"Error converting dates: {e}")

    # Quantity: ensure integer
    if 'quantity' in df.columns:
        try:
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
            invalid = df['quantity'].isnull().sum()
            if invalid > 0:
                df.dropna(subset=['quantity'], inplace=True)
                errors += invalid
            df['quantity'] = df['quantity'].astype(int)
            stats['quantity'] = f"Converted to int, dropped {invalid} invalid"
        except Exception as e:
            logger.error(f"Error converting quantity: {e}")

    # Price: ensure float, handle currency symbols
    if 'price' in df.columns:
        try:
            # Remove currency symbols if present
            if df['price'].dtype == 'object':
                df['price'] = df['price'].astype(str).str.replace('$', '').str.replace(',', '')
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            invalid = df['price'].isnull().sum()
            if invalid > 0:
                df.dropna(subset=['price'], inplace=True)
                errors += invalid
            stats['price'] = f"Converted to float, dropped {invalid} invalid"
        except Exception as e:
            logger.error(f"Error converting price: {e}")

    logger.info(f"Data type conversion complete: {errors} total invalid rows dropped")
    return df, stats

def detect_and_handle_outliers(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    \"\"\"
    Detect and handle outliers using IQR and business rules

    Args:
        df: Input DataFrame

    Returns:
        Tuple of (cleaned DataFrame, statistics dict)
    \"\"\"
    logger.info("Detecting and handling outliers")

    stats = {}
    initial_count = len(df)

    # Quantity outliers
    if 'quantity' in df.columns:
        # Business rule: quantity must be positive
        invalid_quantity = (df['quantity'] < MIN_QUANTITY) | (df['quantity'] > MAX_QUANTITY)
        outlier_count = invalid_quantity.sum()
        if outlier_count > 0:
            logger.warning(f"Found {outlier_count} quantity outliers")
            df = df[~invalid_quantity]
            stats['quantity'] = f"Removed {outlier_count} outliers (range: {MIN_QUANTITY}-{MAX_QUANTITY})"

    # Price outliers
    if 'price' in df.columns:
        # Business rule: price must be positive
        invalid_price = (df['price'] < MIN_PRICE) | (df['price'] > MAX_PRICE)
        outlier_count = invalid_price.sum()
        if outlier_count > 0:
            logger.warning(f"Found {outlier_count} price outliers")
            df = df[~invalid_price]
            stats['price'] = f"Removed {outlier_count} outliers (range: {MIN_PRICE}-{MAX_PRICE})"

    # IQR method for additional outlier detection
    for col in ['quantity', 'price']:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR

            iqr_outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
            iqr_count = iqr_outliers.sum()
            if iqr_count > 0:
                logger.info(f"IQR outliers in {col}: {iqr_count}")
                # Note: we already removed business rule violations, so this is informational

    total_removed = initial_count - len(df)
    logger.info(f"Outlier handling complete: {total_removed} rows removed")
    return df, stats

def validate_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    \"\"\"
    Validate data quality and consistency

    Args:
        df: Input DataFrame

    Returns:
        Tuple of (validated DataFrame, statistics dict)
    \"\"\"
    logger.info("Validating data quality")

    stats = {}
    initial_count = len(df)

    # Date range validation
    if 'date' in df.columns:
        invalid_dates = (df['date'] < MIN_DATE) | (df['date'] > MAX_DATE)
        invalid_count = invalid_dates.sum()
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} dates outside valid range")
            df = df[~invalid_dates]
            stats['date_range'] = f"Removed {invalid_count} rows with invalid date range"

    # Region validation
    if 'region' in df.columns:
        invalid_regions = ~df['region'].isin(VALID_REGIONS + ['Unknown'])
        invalid_count = invalid_regions.sum()
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} invalid regions")
            # Option 1: Drop invalid regions
            df = df[~invalid_regions]
            # Option 2: Map to 'Unknown'
            # df.loc[invalid_regions, 'region'] = 'Unknown'
            stats['region'] = f"Removed {invalid_count} rows with invalid regions"

    # Remove duplicates
    duplicates = df.duplicated(subset=['date', 'product_id', 'customer_id'], keep='first')
    duplicate_count = duplicates.sum()
    if duplicate_count > 0:
        logger.warning(f"Found {duplicate_count} duplicate transactions")
        df = df[~duplicates]
        stats['duplicates'] = f"Removed {duplicate_count} duplicate rows"

    total_removed = initial_count - len(df)
    logger.info(f"Data validation complete: {total_removed} rows removed")
    return df, stats

def generate_report(original_count: int, final_count: int, all_stats: Dict) -> str:
    \"\"\"
    Generate cleaning report with statistics

    Args:
        original_count: Number of rows in original data
        final_count: Number of rows after cleaning
        all_stats: Dictionary of statistics from each step

    Returns:
        Report as string
    \"\"\"
    report = []
    report.append("=" * 80)
    report.append("DATA CLEANING REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append(f"Original rows: {original_count}")
    report.append(f"Final rows: {final_count}")
    report.append(f"Rows removed: {original_count - final_count} ({100 * (original_count - final_count) / original_count:.1f}%)")
    report.append(f"Data retention: {100 * final_count / original_count:.1f}%")
    report.append("")

    for step, stats in all_stats.items():
        report.append(f"## {step}")
        for key, value in stats.items():
            report.append(f"  - {key}: {value}")
        report.append("")

    report.append("=" * 80)
    return "\n".join(report)

def save_data(df: pd.DataFrame, output_path: str) -> None:
    \"\"\"
    Save cleaned data to CSV

    Args:
        df: Cleaned DataFrame
        output_path: Path to output file
    \"\"\"
    logger.info(f"Saving cleaned data to {output_path}")
    df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(df)} rows")

# ============================================================================
# Main Pipeline
# ============================================================================

def clean_sales_data(input_file: str, output_file: str) -> None:
    \"\"\"
    Main data cleaning pipeline

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV
    \"\"\"
    logger.info("="*80)
    logger.info("STARTING DATA CLEANING PIPELINE")
    logger.info("="*80)

    try:
        # Load data
        df = load_data(input_file)
        original_count = len(df)

        # Initialize statistics
        all_stats = {}

        # Step 1: Handle missing values
        df, stats = handle_missing_values(df)
        all_stats['Missing Values'] = stats

        # Step 2: Convert data types
        df, stats = convert_data_types(df)
        all_stats['Data Type Conversion'] = stats

        # Step 3: Handle outliers
        df, stats = detect_and_handle_outliers(df)
        all_stats['Outlier Detection'] = stats

        # Step 4: Validate data
        df, stats = validate_data(df)
        all_stats['Data Validation'] = stats

        # Save cleaned data
        save_data(df, output_file)

        # Generate and save report
        report = generate_report(original_count, len(df), all_stats)
        logger.info(f"\\n{report}")

        with open(REPORT_FILE, 'w') as f:
            f.write(report)

        logger.info("="*80)
        logger.info("DATA CLEANING COMPLETE")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    # Parse command-line arguments
    input_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    output_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

    clean_sales_data(input_file, output_file)
```

## Success Criteria Checklist

Before submitting, verify your code includes:

- [ ] CSV loading with encoding error handling
- [ ] Missing value handling (numeric: median/mean, categorical: mode/Unknown)
- [ ] Data type conversion (dates, integers, floats)
- [ ] Outlier detection (IQR method + business rules)
- [ ] Data validation (date range, value constraints, duplicates)
- [ ] Logging (INFO/WARNING/ERROR levels)
- [ ] Error handling (graceful degradation)
- [ ] Report generation (statistics summary)
- [ ] Original data preservation (separate output file)
- [ ] Documentation (docstrings, comments)

Generate a complete, robust, production-ready data cleaning script following all the above requirements."""

# ============================================================================
# CODE EXTRACTION (Fixed version - extract longest block)
# ============================================================================

def extract_code(text):
    """从LLM输出中提取Python代码（修复版：提取最长的代码块）"""
    blocks = []
    pos = 0

    # 找到所有```python代码块
    while True:
        start = text.find('```python', pos)
        if start == -1:
            break

        code_start = start + len('```python')
        code_end = text.find('```', code_start)

        if code_end == -1:
            break

        code = text[code_start:code_end].strip()
        blocks.append(code)
        pos = code_end + 3

    if blocks:
        # 返回最长的代码块（通常是最后一个完整生成的代码）
        return max(blocks, key=len)

    # Fallback: 尝试提取```之间的代码
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            return parts[1].strip()

    # 如果没有代码块标记，返回整个文本
    return text.strip()

# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_samples(num_samples_per_type=30):
    """生成数据清洗脚本样本"""

    print("=" * 80)
    print("EXPERIMENT 3: DATA CLEANING SCRIPT GENERATION")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Samples per type: {num_samples_per_type}")
    print(f"Total samples: {num_samples_per_type * 2}")

    # 设置输出目录
    output_dir = Path("/root/autodl-tmp/eoh/experiment3_data_cleaning")
    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_dir = output_dir / "baseline"
    multilayer_dir = output_dir / "multilayer"
    baseline_dir.mkdir(exist_ok=True)
    multilayer_dir.mkdir(exist_ok=True)

    # 加载模型
    print("\n[1/4] Loading model...")
    model_path = "/root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map="auto",
        local_files_only=True
    )

    print(f"Model loaded: {model_path}")
    print(f"Device: {next(model.parameters()).device}")

    # 生成参数
    gen_config = {
        "max_new_tokens": 3000,  # 数据清洗代码较长
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
        "pad_token_id": tokenizer.eos_token_id,
    }

    # 存储所有样本
    all_samples = []

    # 生成基线样本
    print(f"\n[2/4] Generating {num_samples_per_type} baseline samples...")
    for i in range(num_samples_per_type):
        torch.manual_seed(42 + i)

        messages = [
            {"role": "system", "content": "You are an expert Python developer specializing in data processing. Generate clean, working code."},
            {"role": "user", "content": BASELINE_PROMPT}
        ]

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(**inputs, **gen_config)

        full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        code = extract_code(full_output)

        # 保存
        sample_id = i
        code_file = baseline_dir / f"sample_{sample_id:03d}.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)

        all_samples.append({
            "id": sample_id,
            "prompt_type": "baseline",
            "code": code,
            "raw_output": full_output,
            "code_length": len(code),
            "lines": len(code.splitlines())
        })

        print(f"  Sample {i+1}/{num_samples_per_type}: {len(code)} chars, {len(code.splitlines())} lines")

    # 生成多层次样本
    print(f"\n[3/4] Generating {num_samples_per_type} multilayer samples...")
    for i in range(num_samples_per_type):
        torch.manual_seed(42 + i)

        messages = [
            {"role": "system", "content": "You are an expert Python developer specializing in robust data processing pipelines. Generate production-ready, well-documented code following all specified requirements."},
            {"role": "user", "content": MULTILAYER_PROMPT}
        ]

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(**inputs, **gen_config)

        full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        code = extract_code(full_output)

        # 保存
        sample_id = num_samples_per_type + i
        code_file = multilayer_dir / f"sample_{sample_id:03d}.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)

        all_samples.append({
            "id": sample_id,
            "prompt_type": "multilayer",
            "code": code,
            "raw_output": full_output,
            "code_length": len(code),
            "lines": len(code.splitlines())
        })

        print(f"  Sample {i+1}/{num_samples_per_type}: {len(code)} chars, {len(code.splitlines())} lines")

    # 保存元数据
    print("\n[4/4] Saving metadata...")
    metadata = {
        "experiment": "experiment3_data_cleaning",
        "task": "Sales Data Cleaning Script",
        "model": model_path,
        "generation_config": gen_config,
        "timestamp": datetime.now().isoformat(),
        "samples": all_samples
    }

    metadata_file = output_dir / "generation_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # 统计
    baseline_samples = [s for s in all_samples if s['prompt_type'] == 'baseline']
    multilayer_samples = [s for s in all_samples if s['prompt_type'] == 'multilayer']

    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nBaseline samples:")
    print(f"  Count: {len(baseline_samples)}")
    print(f"  Avg length: {sum(s['code_length'] for s in baseline_samples) / len(baseline_samples):.0f} chars")
    print(f"  Avg lines: {sum(s['lines'] for s in baseline_samples) / len(baseline_samples):.0f}")
    print(f"\nMultilayer samples:")
    print(f"  Count: {len(multilayer_samples)}")
    print(f"  Avg length: {sum(s['code_length'] for s in multilayer_samples) / len(multilayer_samples):.0f} chars")
    print(f"  Avg lines: {sum(s['lines'] for s in multilayer_samples) / len(multilayer_samples):.0f}")
    print(f"\nOutput directory: {output_dir}")
    print("=" * 80)

if __name__ == "__main__":
    generate_samples(num_samples_per_type=30)
