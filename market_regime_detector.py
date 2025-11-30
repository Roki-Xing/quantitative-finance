#!/usr/bin/env python3
"""
市场环境识别模块
Market Regime Detector

功能: 识别当前市场环境 (牛市/熊市/震荡市)
方法: 综合趋势强度、ADX、波动率等多个指标
"""

import pandas as pd
import numpy as np


class MarketRegimeDetector:
    """市场环境识别器"""

    def __init__(self,
                 lookback_short=20,
                 lookback_long=60,
                 adx_period=14,
                 trend_bull_threshold=5.0,
                 trend_bear_threshold=-5.0,
                 adx_trend_threshold=25.0,
                 adx_sideways_threshold=20.0):
        """
        初始化市场环境识别器

        参数:
            lookback_short: 短期MA周期 (默认20)
            lookback_long: 长期MA周期 (默认60)
            adx_period: ADX计算周期 (默认14)
            trend_bull_threshold: 牛市趋势阈值 (默认5.0%)
            trend_bear_threshold: 熊市趋势阈值 (默认-5.0%)
            adx_trend_threshold: ADX趋势明确阈值 (默认25)
            adx_sideways_threshold: ADX震荡阈值 (默认20)
        """
        self.lookback_short = lookback_short
        self.lookback_long = lookback_long
        self.adx_period = adx_period
        self.trend_bull_threshold = trend_bull_threshold
        self.trend_bear_threshold = trend_bear_threshold
        self.adx_trend_threshold = adx_trend_threshold
        self.adx_sideways_threshold = adx_sideways_threshold

    def calculate_trend_strength(self, data):
        """
        计算趋势强度

        方法: (MA_short - MA_long) / MA_long * 100

        返回:
            float: 趋势强度百分比
        """
        if len(data) < self.lookback_long:
            return 0.0

        ma_short = data['close'].rolling(self.lookback_short).mean()
        ma_long = data['close'].rolling(self.lookback_long).mean()

        # 取最后一个值
        current_ma_short = ma_short.iloc[-1]
        current_ma_long = ma_long.iloc[-1]

        if current_ma_long == 0:
            return 0.0

        trend = (current_ma_short - current_ma_long) / current_ma_long * 100
        return trend

    def calculate_adx(self, data, period=None):
        """
        计算ADX (Average Directional Index)

        ADX用于衡量趋势强度，不考虑方向
        ADX > 25: 强趋势
        ADX < 20: 弱趋势/震荡

        参数:
            data: DataFrame包含high, low, close列
            period: ADX周期 (默认使用self.adx_period)

        返回:
            float: ADX值
        """
        if period is None:
            period = self.adx_period

        if len(data) < period + 1:
            return 0.0

        df = data.copy()

        # 计算True Range (TR)
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = abs(df['high'] - df['close'].shift(1))
        df['low_close'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)

        # 计算方向移动 (+DM和-DM)
        df['high_diff'] = df['high'] - df['high'].shift(1)
        df['low_diff'] = df['low'].shift(1) - df['low']

        df['plus_dm'] = np.where(
            (df['high_diff'] > df['low_diff']) & (df['high_diff'] > 0),
            df['high_diff'],
            0
        )

        df['minus_dm'] = np.where(
            (df['low_diff'] > df['high_diff']) & (df['low_diff'] > 0),
            df['low_diff'],
            0
        )

        # 平滑TR, +DM, -DM
        df['tr_smooth'] = df['tr'].rolling(period).sum()
        df['plus_dm_smooth'] = df['plus_dm'].rolling(period).sum()
        df['minus_dm_smooth'] = df['minus_dm'].rolling(period).sum()

        # 计算方向指标 (+DI和-DI)
        df['plus_di'] = 100 * df['plus_dm_smooth'] / df['tr_smooth']
        df['minus_di'] = 100 * df['minus_dm_smooth'] / df['tr_smooth']

        # 计算DX
        df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])

        # 计算ADX (DX的平滑)
        adx = df['dx'].rolling(period).mean().iloc[-1]

        return adx if not np.isnan(adx) else 0.0

    def calculate_volatility(self, data, period=20):
        """
        计算波动率

        方法: 收益率的标准差 * 100

        参数:
            data: DataFrame包含close列
            period: 计算周期 (默认20)

        返回:
            float: 波动率百分比
        """
        if len(data) < period:
            return 0.0

        returns = data['close'].pct_change()
        volatility = returns.rolling(period).std().iloc[-1] * 100

        return volatility if not np.isnan(volatility) else 0.0

    def detect(self, data):
        """
        识别市场环境

        综合考虑:
        1. 趋势强度 (MA交叉)
        2. ADX (趋势明确性)
        3. 波动率 (可选,用于辅助判断)

        参数:
            data: DataFrame包含 open, high, low, close, volume列

        返回:
            str: 'bull' (牛市), 'bear' (熊市), 'sideways' (震荡市), 'transitional' (过渡期)
        """
        # 数据验证
        if len(data) < self.lookback_long:
            return "transitional"  # 数据不足,返回过渡期

        # 计算指标
        trend_strength = self.calculate_trend_strength(data)
        adx = self.calculate_adx(data)
        volatility = self.calculate_volatility(data)

        # 判断逻辑

        # 1. 震荡市: ADX低,表明无明确趋势
        if adx < self.adx_sideways_threshold:
            return "sideways"

        # 2. 牛市: 趋势向上且ADX高
        if trend_strength > self.trend_bull_threshold and adx > self.adx_trend_threshold:
            return "bull"

        # 3. 熊市: 趋势向下且ADX高
        if trend_strength < self.trend_bear_threshold and adx > self.adx_trend_threshold:
            return "bear"

        # 4. 其他情况: 过渡期
        return "transitional"

    def detect_with_details(self, data):
        """
        识别市场环境并返回详细信息

        参数:
            data: DataFrame包含 open, high, low, close, volume列

        返回:
            dict: {
                'regime': str,
                'trend_strength': float,
                'adx': float,
                'volatility': float,
                'confidence': str  # 'high', 'medium', 'low'
            }
        """
        # 数据验证
        if len(data) < self.lookback_long:
            return {
                'regime': 'transitional',
                'trend_strength': 0.0,
                'adx': 0.0,
                'volatility': 0.0,
                'confidence': 'low'
            }

        # 计算指标
        trend_strength = self.calculate_trend_strength(data)
        adx = self.calculate_adx(data)
        volatility = self.calculate_volatility(data)

        # 识别环境
        regime = self.detect(data)

        # 评估置信度
        confidence = 'low'
        if regime in ['bull', 'bear']:
            if adx > 30 and abs(trend_strength) > 8:
                confidence = 'high'
            elif adx > 25 and abs(trend_strength) > 5:
                confidence = 'medium'
        elif regime == 'sideways':
            if adx < 15 and abs(trend_strength) < 3:
                confidence = 'high'
            elif adx < 20 and abs(trend_strength) < 5:
                confidence = 'medium'

        return {
            'regime': regime,
            'trend_strength': trend_strength,
            'adx': adx,
            'volatility': volatility,
            'confidence': confidence
        }


# ========== 测试代码 ==========

if __name__ == "__main__":
    print("市场环境识别模块测试")
    print("=" * 80)

    # 生成测试数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=200, freq='D')

    # 牛市数据 (上升趋势)
    bull_data = pd.DataFrame({
        'date': dates,
        'open': 100 + np.arange(200) * 0.5 + np.random.randn(200) * 2,
        'high': 102 + np.arange(200) * 0.5 + np.random.randn(200) * 2,
        'low': 98 + np.arange(200) * 0.5 + np.random.randn(200) * 2,
        'close': 100 + np.arange(200) * 0.5 + np.random.randn(200) * 2,
        'volume': 1000000 + np.random.randint(-100000, 100000, 200)
    })

    # 熊市数据 (下降趋势)
    bear_data = pd.DataFrame({
        'date': dates,
        'open': 200 - np.arange(200) * 0.3 + np.random.randn(200) * 2,
        'high': 202 - np.arange(200) * 0.3 + np.random.randn(200) * 2,
        'low': 198 - np.arange(200) * 0.3 + np.random.randn(200) * 2,
        'close': 200 - np.arange(200) * 0.3 + np.random.randn(200) * 2,
        'volume': 1000000 + np.random.randint(-100000, 100000, 200)
    })

    # 震荡市数据 (横盘)
    sideways_data = pd.DataFrame({
        'date': dates,
        'open': 150 + np.sin(np.arange(200) * 0.1) * 5 + np.random.randn(200) * 2,
        'high': 152 + np.sin(np.arange(200) * 0.1) * 5 + np.random.randn(200) * 2,
        'low': 148 + np.sin(np.arange(200) * 0.1) * 5 + np.random.randn(200) * 2,
        'close': 150 + np.sin(np.arange(200) * 0.1) * 5 + np.random.randn(200) * 2,
        'volume': 1000000 + np.random.randint(-100000, 100000, 200)
    })

    # 创建识别器
    detector = MarketRegimeDetector()

    # 测试牛市
    print("\n测试1: 牛市数据")
    print("-" * 80)
    result = detector.detect_with_details(bull_data)
    print(f"识别结果: {result['regime']}")
    print(f"趋势强度: {result['trend_strength']:.2f}%")
    print(f"ADX: {result['adx']:.2f}")
    print(f"波动率: {result['volatility']:.2f}%")
    print(f"置信度: {result['confidence']}")

    # 测试熊市
    print("\n测试2: 熊市数据")
    print("-" * 80)
    result = detector.detect_with_details(bear_data)
    print(f"识别结果: {result['regime']}")
    print(f"趋势强度: {result['trend_strength']:.2f}%")
    print(f"ADX: {result['adx']:.2f}")
    print(f"波动率: {result['volatility']:.2f}%")
    print(f"置信度: {result['confidence']}")

    # 测试震荡市
    print("\n测试3: 震荡市数据")
    print("-" * 80)
    result = detector.detect_with_details(sideways_data)
    print(f"识别结果: {result['regime']}")
    print(f"趋势强度: {result['trend_strength']:.2f}%")
    print(f"ADX: {result['adx']:.2f}")
    print(f"波动率: {result['volatility']:.2f}%")
    print(f"置信度: {result['confidence']}")

    print("\n" + "=" * 80)
    print("测试完成！")
