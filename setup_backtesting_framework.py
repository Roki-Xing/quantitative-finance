#!/usr/bin/env python3
"""
Backtesting Framework Setup Script
为Phase 3策略回测准备环境和数据

功能:
1. 检查并安装必要的库（backtrader, yfinance等）
2. 下载测试数据（SPY, QQQ等ETF 2020-2025）
3. 创建回测框架目录结构
4. 测试Backtrader环境

Author: Phase 3 Setup
Date: 2025-11-22
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import json

# ============================================================================
# 配置
# ============================================================================

# 数据目录
DATA_DIR = Path("/root/autodl-tmp/eoh/backtest_data")
STRATEGY_DIR = Path("/root/autodl-tmp/eoh/strategy_library")
RESULTS_DIR = Path("/root/autodl-tmp/eoh/backtest_results")

# 测试股票/ETF列表（用于初步测试）
TEST_SYMBOLS = [
    "SPY",   # S&P 500 ETF
    "QQQ",   # NASDAQ 100 ETF
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "TSLA",  # Tesla
]

# 数据时间范围
START_DATE = "2020-01-01"
END_DATE = "2025-01-01"

# ============================================================================
# 步骤1: 检查和安装依赖
# ============================================================================

def check_and_install_dependencies():
    """检查并安装必要的Python库"""
    print("=" * 80)
    print("STEP 1: Checking and Installing Dependencies")
    print("=" * 80)

    required_packages = {
        "backtrader": "backtrader",
        "yfinance": "yfinance",
        "pandas": "pandas",
        "numpy": "numpy",
        "matplotlib": "matplotlib",
    }

    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} is already installed")
        except ImportError:
            print(f"⏳ Installing {package_name}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package_name, "-q"
                ])
                print(f"✅ {package_name} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package_name}: {e}")
                return False

    print("\n✅ All dependencies are ready!\n")
    return True

# ============================================================================
# 步骤2: 创建目录结构
# ============================================================================

def create_directory_structure():
    """创建回测框架所需的目录结构"""
    print("=" * 80)
    print("STEP 2: Creating Directory Structure")
    print("=" * 80)

    directories = {
        DATA_DIR: "Historical market data storage",
        STRATEGY_DIR: "Strategy code library",
        STRATEGY_DIR / "batch1": "First batch strategies",
        STRATEGY_DIR / "batch2": "Second batch strategies",
        RESULTS_DIR: "Backtest results and reports",
        RESULTS_DIR / "batch1": "Batch 1 results",
        RESULTS_DIR / "batch2": "Batch 2 results",
        RESULTS_DIR / "portfolio": "Portfolio results",
    }

    for directory, description in directories.items():
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
        print(f"   Purpose: {description}")

    print("\n✅ Directory structure ready!\n")
    return True

# ============================================================================
# 步骤3: 下载测试数据
# ============================================================================

def download_test_data():
    """下载测试用的历史数据"""
    print("=" * 80)
    print("STEP 3: Downloading Historical Data")
    print("=" * 80)
    print(f"Symbols: {', '.join(TEST_SYMBOLS)}")
    print(f"Date Range: {START_DATE} to {END_DATE}")
    print()

    try:
        import yfinance as yf
        import pandas as pd
    except ImportError:
        print("❌ yfinance or pandas not available. Run step 1 first.")
        return False

    successful_downloads = 0
    failed_downloads = []

    for symbol in TEST_SYMBOLS:
        try:
            print(f"⏳ Downloading {symbol}...")

            # 下载数据
            data = yf.download(
                symbol,
                start=START_DATE,
                end=END_DATE,
                progress=False
            )

            if data.empty:
                print(f"❌ {symbol}: No data returned")
                failed_downloads.append(symbol)
                continue

            # 保存为CSV
            output_file = DATA_DIR / f"{symbol}.csv"
            data.to_csv(output_file)

            print(f"✅ {symbol}: {len(data)} bars downloaded")
            print(f"   Date range: {data.index[0].date()} to {data.index[-1].date()}")
            print(f"   Saved to: {output_file}")

            successful_downloads += 1

        except Exception as e:
            print(f"❌ {symbol}: Failed - {e}")
            failed_downloads.append(symbol)

    print()
    print(f"✅ Successfully downloaded: {successful_downloads}/{len(TEST_SYMBOLS)}")
    if failed_downloads:
        print(f"❌ Failed downloads: {', '.join(failed_downloads)}")
    print()

    return successful_downloads > 0

# ============================================================================
# 步骤4: 测试Backtrader环境
# ============================================================================

def test_backtrader_setup():
    """测试Backtrader是否正常工作"""
    print("=" * 80)
    print("STEP 4: Testing Backtrader Setup")
    print("=" * 80)

    try:
        import backtrader as bt
        import pandas as pd

        # 创建简单的测试策略
        class TestStrategy(bt.Strategy):
            def __init__(self):
                self.sma = bt.indicators.SimpleMovingAverage(
                    self.data.close, period=20
                )

            def next(self):
                pass

        # 创建Cerebro引擎
        cerebro = bt.Cerebro()
        cerebro.addstrategy(TestStrategy)

        # 加载测试数据（使用第一个下载的数据）
        test_file = DATA_DIR / f"{TEST_SYMBOLS[0]}.csv"

        if not test_file.exists():
            print(f"❌ Test data file not found: {test_file}")
            return False

        # 读取数据
        data = bt.feeds.GenericCSVData(
            dataname=str(test_file),
            dtformat='%Y-%m-%d',
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            openinterest=-1
        )

        cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)

        print(f"⏳ Running test backtest on {TEST_SYMBOLS[0]}...")

        initial_value = cerebro.broker.getvalue()
        cerebro.run()
        final_value = cerebro.broker.getvalue()

        print(f"✅ Backtrader test successful!")
        print(f"   Initial Portfolio Value: ${initial_value:,.2f}")
        print(f"   Final Portfolio Value: ${final_value:,.2f}")
        print(f"   Backtrader version: {bt.__version__}")
        print()

        return True

    except Exception as e:
        print(f"❌ Backtrader test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# 步骤5: 创建配置文件
# ============================================================================

def create_configuration_file():
    """创建回测框架配置文件"""
    print("=" * 80)
    print("STEP 5: Creating Configuration File")
    print("=" * 80)

    config = {
        "framework": {
            "name": "Phase 3 Backtesting Framework",
            "version": "1.0",
            "created": datetime.now().isoformat()
        },
        "directories": {
            "data": str(DATA_DIR),
            "strategies": str(STRATEGY_DIR),
            "results": str(RESULTS_DIR)
        },
        "data_sources": {
            "provider": "yfinance",
            "symbols": TEST_SYMBOLS,
            "start_date": START_DATE,
            "end_date": END_DATE
        },
        "backtest_defaults": {
            "initial_cash": 100000.0,
            "commission": 0.001,  # 0.1%
            "slippage": 0.0005,   # 0.05%
        },
        "performance_metrics": [
            "Total Return",
            "Annual Return",
            "Sharpe Ratio",
            "Sortino Ratio",
            "Max Drawdown",
            "Win Rate",
            "Profit Factor"
        ],
        "strategy_batches": {
            "batch1": {
                "count": 10,
                "categories": [
                    "Trend Following",
                    "Mean Reversion",
                    "Momentum",
                    "Volatility"
                ]
            }
        }
    }

    config_file = Path("/root/autodl-tmp/eoh/backtest_config.json")

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuration file created: {config_file}")
    print(f"   Initial cash: ${config['backtest_defaults']['initial_cash']:,.2f}")
    print(f"   Commission: {config['backtest_defaults']['commission'] * 100:.2f}%")
    print(f"   Data symbols: {len(config['data_sources']['symbols'])}")
    print()

    return True

# ============================================================================
# 步骤6: 创建示例策略模板
# ============================================================================

def create_strategy_template():
    """创建策略代码模板文件"""
    print("=" * 80)
    print("STEP 6: Creating Strategy Template")
    print("=" * 80)

    template = '''#!/usr/bin/env python3
"""
Strategy Template for Phase 3

This is a template for creating Backtrader strategies.
Copy and modify for new strategies.
"""

import backtrader as bt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateStrategy(bt.Strategy):
    """
    Strategy Description:
    - [Describe your strategy logic here]

    Entry Rules:
    - [Entry conditions]

    Exit Rules:
    - [Exit conditions]

    Risk Management:
    - Stop-loss: [percentage]
    - Take-profit: [percentage]
    - Position size: [percentage of capital]
    """

    params = (
        ('period', 20),          # Example parameter
        ('stop_loss', 0.05),     # 5% stop loss
        ('take_profit', 0.15),   # 15% take profit
    )

    def __init__(self):
        """Initialize indicators and variables"""
        # Example indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=self.params.period
        )

        # Track orders and positions
        self.order = None
        self.entry_price = 0.0

        logger.info(f"Strategy initialized with period={self.params.period}")

    def notify_order(self, order):
        """Handle order notifications"""
        if order.status in [order.Completed]:
            if order.isbuy():
                logger.info(f"BUY EXECUTED at {order.executed.price:.2f}")
                self.entry_price = order.executed.price
            elif order.issell():
                logger.info(f"SELL EXECUTED at {order.executed.price:.2f}")

            self.order = None

    def notify_trade(self, trade):
        """Handle trade close notifications"""
        if trade.isclosed:
            logger.info(f"TRADE CLOSED - PnL: {trade.pnl:.2f}")

    def next(self):
        """Main strategy logic - called on each bar"""
        if self.order:
            return

        current_price = self.data.close[0]

        # Entry logic
        if not self.position:
            # Example: Buy when price crosses above SMA
            if current_price > self.sma[0]:
                size = self.broker.get_cash() / current_price
                self.order = self.buy(size=size)
                logger.info(f"BUY SIGNAL at {current_price:.2f}")

        # Exit logic
        else:
            # Stop-loss
            if current_price <= self.entry_price * (1 - self.params.stop_loss):
                self.order = self.sell(size=self.position.size)
                logger.warning(f"STOP-LOSS at {current_price:.2f}")

            # Take-profit
            elif current_price >= self.entry_price * (1 + self.params.take_profit):
                self.order = self.sell(size=self.position.size)
                logger.info(f"TAKE-PROFIT at {current_price:.2f}")

            # Example: Sell when price crosses below SMA
            elif current_price < self.sma[0]:
                self.order = self.sell(size=self.position.size)
                logger.info(f"SELL SIGNAL at {current_price:.2f}")


if __name__ == '__main__':
    # Example usage
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TemplateStrategy)

    # Load data (replace with actual data file)
    # data = bt.feeds.GenericCSVData(dataname='data.csv', ...)
    # cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    cerebro.run()
    print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')
'''

    template_file = STRATEGY_DIR / "strategy_template.py"

    with open(template_file, 'w') as f:
        f.write(template)

    print(f"✅ Strategy template created: {template_file}")
    print(f"   Use this as a starting point for new strategies")
    print()

    return True

# ============================================================================
# 主执行流程
# ============================================================================

def main():
    """运行所有设置步骤"""
    print("\n" + "=" * 80)
    print("PHASE 3 BACKTESTING FRAMEWORK SETUP")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    steps = [
        ("Dependencies Check & Install", check_and_install_dependencies),
        ("Directory Structure", create_directory_structure),
        ("Download Test Data", download_test_data),
        ("Test Backtrader", test_backtrader_setup),
        ("Create Configuration", create_configuration_file),
        ("Create Strategy Template", create_strategy_template),
    ]

    results = []

    for step_name, step_func in steps:
        try:
            success = step_func()
            results.append((step_name, success))

            if not success:
                print(f"\n⚠️  Step '{step_name}' failed or had issues")
                print("   Continuing with remaining steps...\n")

        except Exception as e:
            print(f"\n❌ Step '{step_name}' encountered an error: {e}")
            import traceback
            traceback.print_exc()
            results.append((step_name, False))

    # 总结
    print("=" * 80)
    print("SETUP SUMMARY")
    print("=" * 80)

    for step_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {step_name}")

    successful_steps = sum(1 for _, success in results if success)
    print()
    print(f"Completed: {successful_steps}/{len(steps)} steps")

    if successful_steps == len(steps):
        print("\n🎉 All setup steps completed successfully!")
        print("   You are ready to start generating and backtesting strategies!")
    else:
        print("\n⚠️  Some steps failed. Please review the errors above.")

    print("=" * 80)

    return successful_steps == len(steps)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
