import numpy as np

class NaiveForecaster:
    """Persistence model: predicts the last observed value."""
    def __init__(self):
        self.last_val = None

    def fit(self, y):
        self.last_val = y.iloc[-1] if hasattr(y, 'iloc') else y[-1]
        return self

    def predict(self, horizon: int):
        return np.full(horizon, self.last_val)

class SeasonalNaiveForecaster:
    """Seasonal Naive model: predicts the value from 24 steps prior."""
    def __init__(self, season_length: int = 24):
        self.season_length = season_length
        self.last_season = None

    def fit(self, y):
        values = y.values if hasattr(y, 'values') else y
        if len(values) >= self.season_length:
            self.last_season = values[-self.season_length:]
        else:
            self.last_season = np.pad(values, (self.season_length - len(values), 0), mode='edge')
        return self

    def predict(self, horizon: int):
        reps = (horizon // self.season_length) + 1
        forecast = np.tile(self.last_season, reps)[:horizon]
        return forecast
