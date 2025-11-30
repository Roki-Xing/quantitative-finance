#!/usr/bin/env python3
"""
Experiment 1: Web Scraper Generation
生成60个Web爬虫代码样本用于跨领域验证

Days 36-37执行
"""

import os
import json
import torch
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed

# ============================================================================
# 配置
# ============================================================================

# 固定随机种子以确保可复现性
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
set_seed(SEED)

# 模型配置
MODEL_PATH = "/root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 实验配置
NUM_SAMPLES_PER_GROUP = 30  # 每组生成30个样本
OUTPUT_DIR = Path("/root/autodl-tmp/eoh/experiment1_web_scraper")

# 生成参数
GENERATION_CONFIG = {
    "max_new_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": True,
}

# ============================================================================
# Prompt模板
# ============================================================================

BASELINE_PROMPT = """Write a Python web scraper that extracts article titles, links, points, and comment counts from Hacker News (news.ycombinator.com) and saves them to a CSV file.

Use the requests and BeautifulSoup4 libraries."""

MULTILAYER_PROMPT = """# Task: Web Scraper for Hacker News

Generate a Python script that scrapes article information from Hacker News and saves to CSV.

## Layer 1: Safety & Ethics Constraints

You MUST follow these rules:
1. **Respect robots.txt**: Check and follow https://news.ycombinator.com/robots.txt
2. **Rate limiting**: Maximum 1 request per second (use time.sleep(1))
3. **User-Agent**: Set a descriptive User-Agent header
4. **Error handling**: Handle HTTP errors (404, 500, timeout) gracefully
5. **No authentication bypass**: Only scrape publicly available pages

## Layer 2: Functional Requirements

Implement the following functionality:

### Core Features:
1. **Fetch HTML**: Use `requests.get()` to fetch the front page
2. **Parse HTML**: Use `BeautifulSoup` to extract:
   - Article title (class: "titleline")
   - Article URL
   - Points (class: "score")
   - Comment count (class: "subtext")
3. **Save to CSV**: Write results to `hacker_news.csv` with headers:
   `title,url,points,comments`

### Required Libraries:
```python
import requests
from bs4 import BeautifulSoup
import csv
import time
```

### Code Structure:
```python
def fetch_page(url):
    # Fetch HTML with error handling
    pass

def parse_articles(html):
    # Parse and extract article info
    pass

def save_to_csv(articles, filename):
    # Save to CSV file
    pass

def main():
    # Main execution flow
    pass
```

## Layer 3: Quality Assurance

Your code must:
1. **Be runnable**: Execute without errors on Python 3.7+
2. **Handle edge cases**:
   - Missing points (new articles)
   - Missing comment counts
   - Network timeouts
3. **Clear logging**: Print progress messages (e.g., "Fetching page...", "Saved 30 articles")
4. **Validate data**: Check that extracted data is not empty
5. **Meaningful names**: Use descriptive variable/function names

## Layer 4: Code Template & Example

Here is the basic structure to follow:

```python
import requests
from bs4 import BeautifulSoup
import csv
import time

def fetch_page(url):
    \"\"\"
    Fetch HTML content from URL with error handling

    Args:
        url (str): Target URL

    Returns:
        str: HTML content or None if failed
    \"\"\"
    headers = {'User-Agent': 'Mozilla/5.0 (Educational Web Scraper)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for 4xx/5xx
        time.sleep(1)  # Rate limiting
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def parse_articles(html):
    \"\"\"
    Parse HTML and extract article information

    Args:
        html (str): HTML content

    Returns:
        list: List of dicts with article info
    \"\"\"
    soup = BeautifulSoup(html, 'html.parser')
    articles = []

    # Find all article rows
    rows = soup.find_all('tr', class_='athing')

    for row in rows:
        # Extract title and URL
        title_elem = row.find('span', class_='titleline')
        if title_elem:
            title = title_elem.get_text(strip=True)
            link_elem = title_elem.find('a')
            url = link_elem['href'] if link_elem else ''
        else:
            continue

        # Extract points and comments from next row
        next_row = row.find_next_sibling('tr')
        if next_row:
            subtext = next_row.find('td', class_='subtext')
            if subtext:
                # Extract points
                score_elem = subtext.find('span', class_='score')
                points = score_elem.get_text() if score_elem else '0 points'

                # Extract comments
                comment_elem = subtext.find_all('a')[-1]
                comments = comment_elem.get_text() if comment_elem else '0 comments'
            else:
                points = '0 points'
                comments = '0 comments'
        else:
            points = '0 points'
            comments = '0 comments'

        articles.append({
            'title': title,
            'url': url,
            'points': points,
            'comments': comments
        })

    return articles

def save_to_csv(articles, filename='hacker_news.csv'):
    \"\"\"
    Save articles to CSV file

    Args:
        articles (list): List of article dicts
        filename (str): Output CSV filename
    \"\"\"
    if not articles:
        print("No articles to save")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'url', 'points', 'comments'])
        writer.writeheader()
        writer.writerows(articles)

    print(f"Saved {len(articles)} articles to {filename}")

def main():
    \"\"\"Main execution function\"\"\"
    url = 'https://news.ycombinator.com'

    print("Fetching Hacker News front page...")
    html = fetch_page(url)

    if html:
        print("Parsing articles...")
        articles = parse_articles(html)

        print(f"Found {len(articles)} articles")
        save_to_csv(articles)
    else:
        print("Failed to fetch page")

if __name__ == '__main__':
    main()
```

## Parameter Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Target URL | https://news.ycombinator.com | Main page to scrape |
| Request timeout | 10 seconds | Maximum wait time |
| Rate limit | 1 second/request | Delay between requests |
| Output file | hacker_news.csv | CSV filename |
| User-Agent | Custom string | Identify your scraper |

## Expected Output

The script should:
1. Print "Fetching Hacker News front page..."
2. Print "Parsing articles..."
3. Print "Found [N] articles"
4. Print "Saved [N] articles to hacker_news.csv"
5. Create a CSV file with headers: title, url, points, comments
6. Contain 30 rows of article data (typical front page)

## Success Criteria

✅ Code runs without errors
✅ Respects rate limiting (observable 1s delay)
✅ Handles network errors gracefully
✅ CSV file is created with correct headers
✅ At least 20 articles are extracted
✅ No missing required fields

---

Now generate the complete Python script following this structure."""

# ============================================================================
# 主函数
# ============================================================================

def load_model():
    """加载LLM模型"""
    print(f"🔧 加载模型: {MODEL_PATH}")
    print(f"🔧 设备: {DEVICE}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        device_map="auto" if DEVICE == "cuda" else None,
    )

    if DEVICE == "cpu":
        model = model.to(DEVICE)

    print(f"✅ 模型加载完成")
    print(f"✅ GPU可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✅ GPU设备: {torch.cuda.get_device_name(0)}")
        print(f"✅ GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    return tokenizer, model


def generate_code_sample(tokenizer, model, prompt, sample_id, group_name):
    """生成单个代码样本"""
    print(f"\n{'='*80}")
    print(f"🚀 生成样本 #{sample_id} ({group_name})")
    print(f"{'='*80}")

    # 构建完整prompt
    messages = [
        {"role": "user", "content": prompt}
    ]

    # Tokenize
    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(DEVICE)

    print(f"📊 输入长度: {input_ids.shape[1]} tokens")

    # 生成
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_new_tokens=GENERATION_CONFIG["max_new_tokens"],
            temperature=GENERATION_CONFIG["temperature"],
            top_p=GENERATION_CONFIG["top_p"],
            do_sample=GENERATION_CONFIG["do_sample"],
            pad_token_id=tokenizer.eos_token_id,
        )

    # 解码
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 提取代码部分
    # LLM通常会在```python和```之间生成代码
    code = extract_code(generated_text)

    print(f"✅ 生成完成: {len(code)} 字符")

    return {
        "id": sample_id,
        "group": group_name,
        "prompt_type": "baseline" if group_name == "baseline" else "multilayer",
        "code": code,
        "raw_output": generated_text,
        "timestamp": datetime.now().isoformat(),
    }


def extract_code(text):
    """从LLM输出中提取Python代码"""
    # 尝试提取```python ... ```之间的代码
    if "```python" in text:
        start = text.find("```python") + len("```python")
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()

    # 尝试提取```之间的代码
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            return parts[1].strip()

    # 如果没有代码块标记，返回整个文本
    return text.strip()


def main():
    """主执行函数"""
    print("="*80)
    print("Experiment 1: Web Scraper Generation - Day 36")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"随机种子: {SEED}")
    print(f"每组样本数: {NUM_SAMPLES_PER_GROUP}")
    print(f"总样本数: {NUM_SAMPLES_PER_GROUP * 2}")
    print()

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    baseline_dir = OUTPUT_DIR / "baseline"
    multilayer_dir = OUTPUT_DIR / "multilayer"
    baseline_dir.mkdir(exist_ok=True)
    multilayer_dir.mkdir(exist_ok=True)

    # 加载模型
    tokenizer, model = load_model()

    all_samples = []

    # ========================================================================
    # 第一组: 基线Prompt (30个样本)
    # ========================================================================

    print("\n" + "="*80)
    print("📋 第一组: 基线Prompt (简单指令)")
    print("="*80)

    for i in range(NUM_SAMPLES_PER_GROUP):
        sample_id = i + 1

        sample = generate_code_sample(
            tokenizer, model,
            BASELINE_PROMPT,
            sample_id,
            "baseline"
        )

        # 保存代码到文件
        code_file = baseline_dir / f"sample_{sample_id:03d}.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(sample["code"])

        # 保存完整样本信息
        sample["code_file"] = str(code_file)
        all_samples.append(sample)

        print(f"💾 已保存: {code_file}")

    # ========================================================================
    # 第二组: 多层次Prompt (30个样本)
    # ========================================================================

    print("\n" + "="*80)
    print("📋 第二组: 多层次Prompt (4层结构)")
    print("="*80)

    for i in range(NUM_SAMPLES_PER_GROUP):
        sample_id = i + 1

        sample = generate_code_sample(
            tokenizer, model,
            MULTILAYER_PROMPT,
            sample_id,
            "multilayer"
        )

        # 保存代码到文件
        code_file = multilayer_dir / f"sample_{sample_id:03d}.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(sample["code"])

        # 保存完整样本信息
        sample["code_file"] = str(code_file)
        all_samples.append(sample)

        print(f"💾 已保存: {code_file}")

    # ========================================================================
    # 保存元数据
    # ========================================================================

    metadata = {
        "experiment": "experiment1_web_scraper",
        "date": datetime.now().isoformat(),
        "seed": SEED,
        "model": MODEL_PATH,
        "device": DEVICE,
        "num_samples_per_group": NUM_SAMPLES_PER_GROUP,
        "total_samples": len(all_samples),
        "generation_config": GENERATION_CONFIG,
        "samples": all_samples
    }

    metadata_file = OUTPUT_DIR / "generation_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print("✅ Experiment 1 - 代码生成完成")
    print("="*80)
    print(f"总样本数: {len(all_samples)}")
    print(f"基线组: {NUM_SAMPLES_PER_GROUP} 个")
    print(f"多层次组: {NUM_SAMPLES_PER_GROUP} 个")
    print(f"元数据保存: {metadata_file}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("下一步: 运行 experiment1_evaluate_samples.py 进行自动化评估")


if __name__ == "__main__":
    main()
