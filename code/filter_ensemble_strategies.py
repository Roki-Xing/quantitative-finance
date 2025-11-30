"""
Strategy Quality Filter
=======================

Purpose: Select high-quality strategies from the ensemble pool based on training metrics.

Usage:
    python filter_ensemble_strategies.py

Output:
    - Console summary of filtered strategies
    - top_strategies.json: List of top strategy IDs
    - strategy_correlation_matrix.csv: Diversity analysis (optional)

Quality Criteria:
    - Training return > 0% (profitability)
    - Sharpe ratio > 0.5 (risk-adjusted performance)
    - Max drawdown < 30% (risk control)
    - Total trades >= 10 (sufficient activity)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import sys

class StrategyFilter:
    """Filter and rank strategies from ensemble pool."""

    def __init__(self, pool_dir: str):
        self.pool_dir = Path(pool_dir)
        self.strategies = []

    def load_strategies(self) -> int:
        """
        Load all strategy results from pool directory.

        Returns:
            Number of strategies loaded successfully
        """
        print("Loading strategies from ensemble pool...")
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

                    # Extract training metrics
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
                          f"Return={strategy_data['training_return']:.2f}%, "
                          f"Sharpe={strategy_data['training_sharpe']:.3f}, "
                          f"DD={strategy_data['training_drawdown']:.2f}%, "
                          f"Trades={strategy_data['training_trades']}")

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
                          min_trades: int = 10) -> List[Dict]:
        """
        Filter strategies by quality criteria.

        Args:
            min_return: Minimum training return (%)
            min_sharpe: Minimum Sharpe ratio
            max_drawdown: Maximum acceptable drawdown (%)
            min_trades: Minimum number of trades

        Returns:
            List of filtered strategy dictionaries
        """
        print("Applying quality filters...")
        print(f"  Min Return: {min_return}%")
        print(f"  Min Sharpe: {min_sharpe}")
        print(f"  Max Drawdown: {max_drawdown}%")
        print(f"  Min Trades: {min_trades}")
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
                # Show reason for failure
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

    def rank_strategies(self, strategies: List[Dict] = None,
                       metric: str = 'training_sharpe') -> pd.DataFrame:
        """
        Rank strategies by specified metric.

        Args:
            strategies: List of strategies to rank (default: all loaded)
            metric: Metric to rank by (default: training_sharpe)

        Returns:
            DataFrame with ranked strategies
        """
        if strategies is None:
            strategies = self.strategies

        df = pd.DataFrame(strategies)

        if df.empty:
            print("⚠ Warning: No strategies to rank")
            return df

        # Sort by metric (descending)
        df = df.sort_values(by=metric, ascending=False).reset_index(drop=True)

        return df

    def select_top_n(self, n: int = 10,
                    metric: str = 'training_sharpe',
                    filtered_only: bool = True) -> Tuple[List[Dict], pd.DataFrame]:
        """
        Select top N strategies by metric.

        Args:
            n: Number of top strategies to select
            metric: Metric to rank by
            filtered_only: Only select from quality-filtered strategies

        Returns:
            Tuple of (top_strategies_list, ranking_dataframe)
        """
        if filtered_only:
            # Apply default quality filter first
            candidates = self.filter_by_criteria()
        else:
            candidates = self.strategies

        if len(candidates) == 0:
            print("❌ Error: No strategies available after filtering")
            return [], pd.DataFrame()

        # Rank candidates
        df = self.rank_strategies(candidates, metric)

        # Select top N
        top_n = min(n, len(df))
        df_top = df.head(top_n)

        top_strategies = df_top.to_dict('records')

        print(f"Top {top_n} Strategies (ranked by {metric}):")
        print("=" * 80)
        for i, strategy in enumerate(top_strategies, 1):
            print(f"{i:2d}. {strategy['id']:15s} | "
                  f"Sharpe: {strategy['training_sharpe']:6.3f} | "
                  f"Return: {strategy['training_return']:7.2f}% | "
                  f"DD: {strategy['training_drawdown']:6.2f}% | "
                  f"Trades: {strategy['training_trades']:3d}")
        print("=" * 80)
        print()

        return top_strategies, df_top

    def analyze_diversity(self, strategies: List[Dict]) -> pd.DataFrame:
        """
        Analyze strategy diversity through correlation analysis.

        Note: This requires return time series data, which is not available
        from the current backtest results format. This is a placeholder for
        future implementation.

        Args:
            strategies: List of strategies to analyze

        Returns:
            Correlation matrix DataFrame (placeholder)
        """
        print("Strategy diversity analysis...")
        print("⚠ Note: Full correlation analysis requires time series data")
        print("   This feature will be implemented in future version")
        print()

        # Placeholder: Analyze metric correlation as proxy for diversity
        df = pd.DataFrame(strategies)

        if len(df) < 2:
            print("⚠ Need at least 2 strategies for diversity analysis")
            return pd.DataFrame()

        # Calculate correlation between metrics
        metrics = ['training_return', 'training_sharpe', 'training_drawdown', 'training_trades']
        corr_matrix = df[metrics].corr()

        print("Metric Correlation Matrix:")
        print(corr_matrix.round(3))
        print()

        return corr_matrix

    def save_top_strategies(self, strategies: List[Dict], output_file: str):
        """Save top strategy IDs to JSON file."""
        top_ids = [s['id'] for s in strategies]

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(top_ids, f, indent=2)

        print(f"✓ Top {len(top_ids)} strategies saved to: {output_file}")
        print()

    def generate_summary_report(self, output_file: str):
        """Generate human-readable summary report."""
        with open(output_file, 'w') as f:
            f.write("Strategy Pool Quality Summary\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Total Strategies Generated: {len(self.strategies)}\n\n")

            if len(self.strategies) == 0:
                f.write("No strategies loaded.\n")
                return

            # Summary statistics
            df = pd.DataFrame(self.strategies)

            f.write("Performance Statistics:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Average Return:   {df['training_return'].mean():7.2f}%  "
                   f"(σ={df['training_return'].std():6.2f}%)\n")
            f.write(f"  Average Sharpe:   {df['training_sharpe'].mean():7.3f}   "
                   f"(σ={df['training_sharpe'].std():6.3f})\n")
            f.write(f"  Average Drawdown: {df['training_drawdown'].mean():7.2f}%  "
                   f"(σ={df['training_drawdown'].std():6.2f}%)\n")
            f.write(f"  Average Trades:   {df['training_trades'].mean():7.1f}   "
                   f"(σ={df['training_trades'].std():6.1f})\n\n")

            f.write("Performance Distribution:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Min Return:    {df['training_return'].min():7.2f}%\n")
            f.write(f"  25th Pctl:     {df['training_return'].quantile(0.25):7.2f}%\n")
            f.write(f"  Median:        {df['training_return'].median():7.2f}%\n")
            f.write(f"  75th Pctl:     {df['training_return'].quantile(0.75):7.2f}%\n")
            f.write(f"  Max Return:    {df['training_return'].max():7.2f}%\n\n")

            f.write("Quality Filter Results:\n")
            f.write("-" * 70 + "\n")
            filtered = self.filter_by_criteria()
            f.write(f"  Strategies Passing Filter: {len(filtered)} / {len(self.strategies)}\n")
            f.write(f"  Success Rate: {len(filtered) / len(self.strategies) * 100:.1f}%\n\n")

            f.write("Individual Strategy Results:\n")
            f.write("-" * 70 + "\n")
            df_sorted = df.sort_values('training_sharpe', ascending=False)
            for i, row in df_sorted.iterrows():
                f.write(f"  {row['id']:15s} | "
                       f"Sharpe: {row['training_sharpe']:6.3f} | "
                       f"Return: {row['training_return']:7.2f}% | "
                       f"DD: {row['training_drawdown']:6.2f}% | "
                       f"Trades: {row['training_trades']:3.0f}\n")

        print(f"✓ Summary report saved to: {output_file}")
        print()


def main():
    """Main execution function."""
    print("=" * 80)
    print("Strategy Quality Filter")
    print("=" * 80)
    print()

    # Configuration
    POOL_DIR = "/root/autodl-tmp/outputs/ensemble_pool"
    TOP_N = 10
    OUTPUT_TOP_FILE = "/root/autodl-tmp/outputs/ensemble_pool/top_strategies.json"
    OUTPUT_SUMMARY = "/root/autodl-tmp/outputs/ensemble_pool/filter_summary.txt"

    # Initialize filter
    filter_obj = StrategyFilter(POOL_DIR)

    # Load strategies
    num_loaded = filter_obj.load_strategies()

    if num_loaded == 0:
        print("❌ No strategies loaded. Exiting.")
        sys.exit(1)

    # Select top strategies
    top_strategies, df_top = filter_obj.select_top_n(
        n=TOP_N,
        metric='training_sharpe',
        filtered_only=True
    )

    if len(top_strategies) == 0:
        print("❌ No strategies passed quality filter. Consider relaxing criteria.")
        sys.exit(1)

    # Analyze diversity (placeholder)
    filter_obj.analyze_diversity(top_strategies)

    # Save results
    filter_obj.save_top_strategies(top_strategies, OUTPUT_TOP_FILE)
    filter_obj.generate_summary_report(OUTPUT_SUMMARY)

    # Final summary
    print("=" * 80)
    print("Filter Process Complete")
    print("=" * 80)
    print(f"Total Strategies: {num_loaded}")
    print(f"Top Strategies Selected: {len(top_strategies)}")
    print(f"Selection Rate: {len(top_strategies) / num_loaded * 100:.1f}%")
    print()
    print("Next Steps:")
    print("  1. Review filter_summary.txt for detailed analysis")
    print("  2. Inspect top strategy code in strategy_XX directories")
    print("  3. Proceed with ensemble backtesting using run_ensemble_backtest.py")
    print("=" * 80)


if __name__ == '__main__':
    main()
