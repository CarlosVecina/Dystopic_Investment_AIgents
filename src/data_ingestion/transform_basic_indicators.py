import pandas as pd


def calculate_sma(data: pd.DataFrame, window: int = 20):
    return data.rolling(window=window).mean()


def calculate_ema(data: pd.DataFrame, span: int = 20):
    return data.ewm(span=span, adjust=False).mean()


def calculate_bollinger_bands(
    data: pd.DataFrame, window: int = 20, num_std: float | int = 2
):
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, lower_band


def calculate_rsi(data: pd.DataFrame, window: int = 14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(
    data: pd.DataFrame,
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
):
    short_ema = calculate_ema(data, span=short_window)
    long_ema = calculate_ema(data, span=long_window)
    macd_line = short_ema - long_ema
    signal_line = calculate_ema(macd_line, span=signal_window)
    return macd_line, signal_line
