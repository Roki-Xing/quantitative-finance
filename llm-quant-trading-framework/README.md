# LLM-Driven Quantitative Trading Framework

## Abstract
This repository presents a novel framework for generating quantitative trading strategies using Large Language Models (LLMs). Our approach leverages Meta-Llama-3.1-8B-Instruct to automatically generate trading algorithms through prompt engineering and genetic programming techniques.

## Key Achievements
- **127% Average Return** on QQQ (NASDAQ-100) with 100% positive rate
- **112% Average Return** on SPY (S&P 500) with 100% positive rate
- **V1.5 Asset-Adaptive Framework** with performance-tiered asset classification
- **28-Day Experimental Validation** across 6 major asset classes

## Repository Structure
```
llm-quant-trading-framework/
├── src/           # Core framework code
├── data/          # Experimental results (CSV files)
├── results/       # Performance analysis and reports
├── docs/          # Documentation and methodology
└── figures/       # Visualizations for presentation
```

## Performance Tiers
- **S-TIER**: QQQ (45-85% valid, 127% avg return)
- **A-TIER**: SPY (40% valid, 112% avg return)
- **B-TIER**: GLD (60% valid, 33% avg return)
- **C-TIER**: TLT (60% valid, 0.78% avg return)
- **D-TIER**: IWM (40-50% valid, 20% avg return)
- **F-TIER**: XLE (36% valid, negative returns - AVOID)

## Methodology
1. **Prompt Engineering**: Aggressive prompt style with asset-specific parameters
2. **Genetic Programming**: Population-based strategy evolution
3. **Validation Framework**: Train (2020-2022) / Test (2023) split
4. **Risk Management**: Sharpe ratio optimization and positive rate tracking

## Technical Stack
- **LLM**: Meta-Llama-3.1-8B-Instruct
- **GPU**: NVIDIA vGPU-48GB
- **Framework Version**: V1.5 (Day 26 validated)
- **Language**: Python 3.x

## Authors
- Roki Xing (18957444596@163.com)
- Claude AI Assistant (Co-author)

## Citation
If you use this framework in your research, please cite:
```
@misc{xing2025llmquant,
  title={LLM-Driven Quantitative Trading Framework},
  author={Xing, Roki and Claude},
  year={2025},
  publisher={GitHub},
  url={https://github.com/Roki-Xing/llm-quant-trading-framework}
}
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For questions and collaboration opportunities, please contact:
- Email: 18957444596@163.com
- GitHub: Roki-Xing
