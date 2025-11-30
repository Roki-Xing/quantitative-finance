# 实验1: Web爬虫生成 - Prompt模板

**实验日期**: 2025-11-22 (Day 35-37)
**目标**: 验证多层次Prompt结构在Web爬虫代码生成中的有效性
**对照**: 基线Prompt vs 多层次Prompt

---

## 实验设计

### 任务描述

生成一个Python爬虫，用于抓取新闻网站的文章信息。

**目标网站**: https://news.ycombinator.com (Hacker News)

**需抓取内容**:
- 文章标题
- 文章链接
- 评分 (points)
- 评论数

**输出格式**: CSV文件

**基本要求**:
- 使用 requests + BeautifulSoup4
- 遵守 robots.txt
- 错误处理
- 限速 (1请求/秒)

---

## Prompt模板对比

### 版本A: 基线Prompt (Control Group)

```markdown
Write a Python web scraper that extracts article titles, links, points, and comment counts from Hacker News (news.ycombinator.com) and saves them to a CSV file.

Use the requests and BeautifulSoup4 libraries.
```

**特点**:
- 简单直接
- 无结构化
- 无安全约束
- 无示例代码

---

### 版本B: 多层次Prompt (Treatment Group)

```markdown
# Task: Web Scraper for Hacker News

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
    """
    Fetch HTML content from URL with error handling

    Args:
        url (str): Target URL

    Returns:
        str: HTML content or None if failed
    """
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
    """
    Parse HTML and extract article information

    Args:
        html (str): HTML content

    Returns:
        list: List of dicts with article info
    """
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
    """
    Save articles to CSV file

    Args:
        articles (list): List of article dicts
        filename (str): Output CSV filename
    """
    if not articles:
        print("No articles to save")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'url', 'points', 'comments'])
        writer.writeheader()
        writer.writerows(articles)

    print(f"Saved {len(articles)} articles to {filename}")

def main():
    """Main execution function"""
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

Now generate the complete Python script following this structure.
```

**特点**:
- ✅ 多层次结构 (4层)
- ✅ 明确的安全约束
- ✅ 详细的功能需求
- ✅ 完整的代码模板
- ✅ 表格化参数说明
- ✅ 明确的成功标准

---

## 实验流程

### Step 1: 数据生成

```python
# 使用两种Prompt各生成30个样本
samples = {
    "baseline": [],     # 基线Prompt生成
    "multilayer": []    # 多层次Prompt生成
}

for i in range(30):
    # 生成基线版本
    code_baseline = llm.generate(prompt_baseline)
    samples["baseline"].append({
        "id": i,
        "code": code_baseline,
        "prompt_type": "baseline"
    })

    # 生成多层次版本
    code_multilayer = llm.generate(prompt_multilayer)
    samples["multilayer"].append({
        "id": i,
        "code": code_multilayer,
        "prompt_type": "multilayer"
    })
```

### Step 2: 自动化测试

```python
class WebScraperEvaluator:
    def __init__(self):
        self.test_url = "https://news.ycombinator.com"

    def test_syntax(self, code):
        """语法检查"""
        try:
            compile(code, "<string>", "exec")
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def test_runtime(self, code):
        """运行时测试"""
        try:
            # 在隔离环境中执行
            exec(code, {"__name__": "__main__"})
            return True, None
        except Exception as e:
            return False, str(e)

    def test_functionality(self, code):
        """功能性测试"""
        checks = {
            "has_requests": "import requests" in code,
            "has_beautifulsoup": "from bs4 import BeautifulSoup" in code or "import bs4" in code,
            "has_csv": "import csv" in code,
            "has_rate_limit": "time.sleep" in code or "sleep(" in code,
            "has_error_handling": "try:" in code and "except" in code,
            "has_user_agent": "User-Agent" in code or "headers" in code,
            "saves_to_csv": ".csv" in code and "open(" in code
        }
        score = sum(checks.values()) / len(checks) * 100
        return score, checks

    def test_security(self, code):
        """安全性测试"""
        issues = []

        # 检查危险操作
        if "os.system" in code or "subprocess" in code:
            issues.append("Dangerous system call")

        if "eval(" in code or "exec(" in code:
            issues.append("Dangerous eval/exec")

        # 检查rate limiting
        if "sleep" not in code:
            issues.append("No rate limiting")

        # 检查error handling
        if "try:" not in code:
            issues.append("No error handling")

        score = max(0, 100 - len(issues) * 25)
        return score, issues

    def comprehensive_eval(self, code):
        """综合评估"""
        results = {}

        # 1. 语法检查
        syntax_ok, syntax_error = self.test_syntax(code)
        results["syntax"] = {
            "pass": syntax_ok,
            "error": syntax_error
        }

        # 2. 运行时测试
        if syntax_ok:
            runtime_ok, runtime_error = self.test_runtime(code)
            results["runtime"] = {
                "pass": runtime_ok,
                "error": runtime_error
            }
        else:
            results["runtime"] = {"pass": False, "error": "Skipped due to syntax error"}

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
        elif not runtime_ok:
            total_score = 25  # 语法正确得25分
        else:
            total_score = (25 +  # 语法
                          25 +  # 运行
                          func_score * 0.3 +  # 功能30%
                          sec_score * 0.2)    # 安全20%

        results["total_score"] = total_score

        return results
```

### Step 3: 数据分析

```python
# 对比两组结果
baseline_results = [evaluator.comprehensive_eval(s["code"]) for s in samples["baseline"]]
multilayer_results = [evaluator.comprehensive_eval(s["code"]) for s in samples["multilayer"]]

# 统计指标
metrics = {
    "baseline": {
        "avg_score": np.mean([r["total_score"] for r in baseline_results]),
        "syntax_pass_rate": sum([r["syntax"]["pass"] for r in baseline_results]) / 30 * 100,
        "runtime_pass_rate": sum([r["runtime"]["pass"] for r in baseline_results]) / 30 * 100,
        "avg_func_score": np.mean([r["functionality"]["score"] for r in baseline_results]),
        "avg_sec_score": np.mean([r["security"]["score"] for r in baseline_results])
    },
    "multilayer": {
        "avg_score": np.mean([r["total_score"] for r in multilayer_results]),
        "syntax_pass_rate": sum([r["syntax"]["pass"] for r in multilayer_results]) / 30 * 100,
        "runtime_pass_rate": sum([r["runtime"]["pass"] for r in multilayer_results]) / 30 * 100,
        "avg_func_score": np.mean([r["functionality"]["score"] for r in multilayer_results]),
        "avg_sec_score": np.mean([r["security"]["score"] for r in multilayer_results])
    }
}
```

---

## 预期结果

### 假设H1: 多层次Prompt提高成功率

**预期**:
```
基线版本 vs 多层次版本:
- 语法通过率: 80% vs 95% (+15%)
- 运行通过率: 60% vs 85% (+25%)
- 功能评分: 65 vs 85 (+20)
- 安全评分: 50 vs 80 (+30)
```

### 假设H2: 安全约束层效果显著

**预期**: 多层次版本中：
- 95%包含rate limiting
- 90%包含error handling
- 85%包含User-Agent设置
- 基线版本中仅30-50%

### 假设H3: 代码模板提升质量

**预期**: 多层次版本：
- 更完整的函数结构
- 更好的变量命名
- 更多的注释
- 更健壮的错误处理

---

## 数据输出

### 实验数据文件结构

```
experiment1_web_scraper/
├── prompts/
│   ├── baseline_prompt.md
│   └── multilayer_prompt.md
├── generated_code/
│   ├── baseline/
│   │   ├── sample_001.py
│   │   ├── sample_002.py
│   │   └── ... (30 files)
│   └── multilayer/
│       ├── sample_001.py
│       ├── sample_002.py
│       └── ... (30 files)
├── evaluation_results/
│   ├── baseline_results.json
│   ├── multilayer_results.json
│   └── comparison.json
├── analysis/
│   ├── statistical_analysis.ipynb
│   ├── error_analysis.md
│   └── visualization.png
└── report/
    └── experiment1_report.md
```

---

## 成功标准

✅ **数据收集**: 60个样本 (30 baseline + 30 multilayer)
✅ **评估完成**: 所有样本自动化测试
✅ **统计显著**: p-value < 0.05 (t-test)
✅ **效果明显**: 多层次版本至少+20%提升
✅ **文档完整**: 完整的实验报告

---

**下一步**: 运行实验，生成60个Web爬虫代码样本

**预计时间**: 2-3天 (Day 36-37)
