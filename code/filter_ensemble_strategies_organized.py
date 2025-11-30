"""
Strategy Quality Filter (Organized Version)
===========================================

Purpose: Select high-quality strategies from the ensemble pool

Input:  /root/autodl-tmp/eoh_ensemble_experiment/01_strategy_pool/
Output: /root/autodl-tmp/eoh_ensemble_experiment/03_filtered_strategies/

Usage:
    python filter_ensemble_strategies_organized.py
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

class StrategyFilter:
    """Filter and rank strategies from ensemble pool."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.pool_dir = self.base_dir / "01_strategy_pool"
        self.output_dir = self.base_dir / "03_filtered_strategies"
        self.strategies = []

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_strategies(self) -> int:
        """Load all strategy results from pool directory."""
        print("=" * 80)
        print("Loading Strategies from Pool")
        print("=" * 80)
        print(f"Pool directory: {self.pool_dir}")
        print()

        if not self.pool_dir.exists():
            print(f"❌ Error: Pool directory not found: {self.pool_dir}")
            return 0

        count = 0
        for strategy_dir in sorted(self.pool_dir.glob("strategy_*")):
            results_file = strategy_dir / "backtest_results.json"

            if results_file.exists():
                try:
                    with open(results_file, 'r') as f:
                        results = json.load(f)

                    training = results.get('training', {})

                    strategy_data = {
                        'id': strategy_dir.name,
                        'path': str(strategy_dir),
                        'training_return': training.get('returns_pct', 0.0),
                        'training_sharpe': training.get('sharpe_ratio', 0.0),
                        'training_drawdown': abs(training.get('max_drawdown_pct', 0.0)),
                        'training_trades': training.get('total_trades', 0),
                        'final_value': training.get('final_value', 100000.0),
                    }

                    self.strategies.append(strategy_data)
                    count += 1

                    print(f"  ✓ {strategy_dir.name}: "
                          f"Return={strategy_data['training_return']:7.2f}%, "
                          f"Sharpe={strategy_data['training_sharpe']:.3f}, "
                          f"DD={strategy_data['training_drawdown']:6.2f}%, "
                          f"Trades={strategy_data['training_trades']:3d}")

                except Exception as e:
                    print(f"  ✗ {strategy_dir.name}: Failed to load - {e}")
            else:
                print(f"  ⚠ {strategy_dir.name}: No backtest results found")

        print()
        print(f"Total strategies loaded: {count}")
        print()

        return count

    def filter_by_criteria(self,
                          min_return: float = 0.0,
                          min_sharpe: float = 0.5,
                          max_drawdown: float = 30.0,
                          min_trades: int = 10) -> list:
        """Filter strategies by quality criteria."""
        print("=" * 80)
        print("Applying Quality Filters")
        print("=" * 80)
        print(f"  Min Return:    {min_return:7.2f}%")
        print(f"  Min Sharpe:    {min_sharpe:7.3f}")
        print(f"  Max Drawdown:  {max_drawdown:7.2f}%")
        print(f"  Min Trades:    {min_trades:3d}")
        print()

        filtered = []
        for strategy in self.strategies:
            passes = (
                strategy['training_return'] >= min_return and
                strategy['training_sharpe'] >= min_sharpe and
                strategy['training_drawdown'] <= max_drawdown and
                strategy['training_trades'] >= min_trades
            )

            if passes:
                filtered.append(strategy)
                print(f"  ✓ {strategy['id']} passed filter")
            else:
                reasons = []
                if strategy['training_return'] < min_return:
                    reasons.append(f"return={strategy['training_return']:.2f}%")
                if strategy['training_sharpe'] < min_sharpe:
                    reasons.append(f"sharpe={strategy['training_sharpe']:.3f}")
                if strategy['training_drawdown'] > max_drawdown:
                    reasons.append(f"DD={strategy['training_drawdown']:.2f}%")
                if strategy['training_trades'] < min_trades:
                    reasons.append(f"trades={strategy['training_trades']}")

                print(f"  ✗ {strategy['id']} failed: {', '.join(reasons)}")

        print()
        print(f"Strategies passing filter: {len(filtered)} / {len(self.strategies)}")
        print()

        return filtered

    def select_top_n(self, n: int = 10,
                    metric: str = 'training_sharpe',
                    filtered_only: bool = True) -> tuple:
        """Select top N strategies by metric."""
        print("=" * 80)
        print(f"Selecting Top {n} Strategies")
        print("=" * 80)
        print(f"Ranking metric: {metric}")
        print()

        if filtered_only:
            candidates = self.filter_by_criteria()
        else:
            candidates = self.strategies

        if len(candidates) == 0:
            print("❌ Error: No strategies available after filtering")
            return [], pd.DataFrame()

        df = pd.DataFrame(candidates)
        df = df.sort_values(by=metric, ascending=False).reset_index(drop=True)

        top_n = min(n, len(df))
        df_top = df.head(top_n)

        top_strategies = df_top.to_dict('records')

        print(f"Top {top_n} Strategies:")
        print("-" * 80)
        for i, strategy in enumerate(top_strategies, 1):
            print(f"{i:2d}. {strategy['id']:15s} | "
                  f"Sharpe: {strategy['training_sharpe']:6.3f} | "
                  f"Return: {strategy['training_return']:7.2f}% | "
                  f"DD: {strategy['training_drawdown']:6.2f}% | "
                  f"Trades: {strategy['training_trades']:3.0f}")
        print("-" * 80)
        print()

        return top_strategies, df_top

    def save_results(self, top_strategies: list, df_all: pd.DataFrame):
        """Save filtering results to output directory."""
        print("=" * 80)
        print("Saving Results")
        print("=" * 80)

        # 1. Save top strategy IDs (JSON)
        top_ids = [s['id'] for s in top_strategies]
        output_json = self.output_dir / "top_strategies.json"

        with open(output_json, 'w') as f:
            json.dump(top_ids, f, indent=2)

        print(f"✓ Top strategies list: {output_json}")

        # 2. Save strategy rankings (CSV)
        df_all_sorted = df_all.sort_values('training_sharpe', ascending=False)
        output_csv = self.output_dir / "strategy_rankings.csv"

        df_all_sorted.to_csv(output_csv, index=False)

        print(f"✓ Strategy rankings: {output_csv}")

        # 3. Save filter summary (TXT)
        output_txt = self.output_dir / "filter_summary.txt"

        with open(output_txt, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("Strategy Quality Filter Summary\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Filter Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Base Directory: {self.base_dir}\n\n")

            f.write(f"Total Strategies Loaded: {len(self.strategies)}\n")
            f.write(f"Strategies Passing Filter: {len(top_strategies)}\n")
            f.write(f"Success Rate: {len(top_strategies) / len(self.strategies) * 100:.1f}%\n\n")

            f.write("Performance Statistics (All Strategies):\n")
            f.write("-" * 70 + "\n")

            df_stats = pd.DataFrame(self.strategies)
            f.write(f"  Mean Return:   {df_stats['training_return'].mean():7.2f}%  "
                   f"(σ={df_stats['training_return'].std():6.2f}%)\n")
            f.write(f"  Mean Sharpe:   {df_stats['training_sharpe'].mean():7.3f}   "
                   f"(σ={df_stats['training_sharpe'].std():6.3f})\n")
            f.write(f"  Mean Drawdown: {df_stats['training_drawdown'].mean():7.2f}%  "
                   f"(σ={df_stats['training_drawdown'].std():6.2f}%)\n")
            f.write(f"  Mean Trades:   {df_stats['training_trades'].mean():7.1f}   "
                   f"(σ={df_stats['training_trades'].std():6.1f})\n\n")

            f.write("Performance Distribution (All Strategies):\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Min Return:    {df_stats['training_return'].min():7.2f}%\n")
            f.write(f"  25th Pctl:     {df_stats['training_return'].quantile(0.25):7.2f}%\n")
            f.write(f"  Median:        {df_stats['training_return'].median():7.2f}%\n")
            f.write(f"  75th Pctl:     {df_stats['training_return'].quantile(0.75):7.2f}%\n")
            f.write(f"  Max Return:    {df_stats['training_return'].max():7.2f}%\n\n")

            f.write("Top {len(top_strategies)} Strategies (Ranked by Sharpe):\n")
            f.write("-" * 70 + "\n")
            for i, strategy in enumerate(top_strategies, 1):
                f.write(f"{i:2d}. {strategy['id']:15s} | "
                       f"Sharpe: {strategy['training_sharpe']:6.3f} | "
                       f"Return: {strategy['training_return']:7.2f}% | "
                       f"DD: {strategy['training_drawdown']:6.2f}% | "
                       f"Trades: {strategy['training_trades']:3.0f}\n")

            f.write("\n" + "=" * 70 + "\n")

        print(f"✓ Filter summary: {output_txt}")
        print()

    def update_readme(self, top_count: int):
        """Update experiment README with filter results."""
        readme_path = self.base_dir / "README_EXPERIMENT.md"

        if readme_path.exists():
            # Read current content
            with open(readme_path, 'r') as f:
                content = f.read()

            # Update progress
            content = content.replace(
                '- [ ] Step 3: 质量筛选（Top 10）',
                '- [x] Step 3: 质量筛选（Top 10）'
            )

            # Append filter results
            if '## 筛选结果' not in content:
                content += f"\n\n## 筛选结果\n\n"
                content += f"**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                content += f"**Top策略数量**: {top_count}\n"
                content += f"**筛选标准**: Return>0%, Sharpe>0.5, DD<30%, Trades≥10\n\n"
                content += f"详细结果见: `03_filtered_strategies/filter_summary.txt`\n"

            # Write back
            with open(readme_path, 'w') as f:
                f.write(content)

            print(f"✓ Updated: {readme_path}")


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("Strategy Quality Filter (Organized Version)")
    print("=" * 80)
    print()

    # Configuration
    BASE_DIR = "/root/autodl-tmp/eoh_ensemble_experiment"
    TOP_N = 10

    # Initialize filter
    filter_obj = StrategyFilter(BASE_DIR)

    # Load strategies
    num_loaded = filter_obj.load_strategies()

    if num_loaded == 0:
        print("❌ No strategies loaded. Exiting.")
        sys.exit(1)

    # Select top strategies
    top_strategies, df_all = filter_obj.select_top_n(
        n=TOP_N,
        metric='training_sharpe',
        filtered_only=True
    )

    if len(top_strategies) == 0:
        print("❌ No strategies passed quality filter.")
        print("   Consider relaxing filter criteria.")
        sys.exit(1)

    # Save results
    filter_obj.save_results(top_strategies, pd.DataFrame(filter_obj.strategies))

    # Update README
    filter_obj.update_readme(len(top_strategies))

    # Final summary
    print("=" * 80)
    print("Filter Process Complete")
    print("=" * 80)
    print(f"Total Strategies Loaded: {num_loaded}")
    print(f"Top Strategies Selected: {len(top_strategies)}")
    print(f"Selection Rate: {len(top_strategies) / num_loaded * 100:.1f}%")
    print()
    print("Output Files:")
    print(f"  - {filter_obj.output_dir / 'top_strategies.json'}")
    print(f"  - {filter_obj.output_dir / 'strategy_rankings.csv'}")
    print(f"  - {filter_obj.output_dir / 'filter_summary.txt'}")
    print()
    print("Next Steps:")
    print("  1. Review filter_summary.txt for detailed analysis")
    print("  2. Inspect top strategy code in 01_strategy_pool/strategy_XX/")
    print("  3. Proceed with individual backtesting")
    print("=" * 80)


if __name__ == '__main__':
    main()
