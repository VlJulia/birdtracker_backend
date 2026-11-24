from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.utils import calculate_avg_distance, calculate_avg_speed, haversine

KM_PER_DEGREE = 111.19  # один градус широты
START = datetime(2025, 6, 1, 12, 0)


def point(latitude: float, hours: float = 0) -> SimpleNamespace:
    return SimpleNamespace(
        latitude=latitude, longitude=30.0, timestamp=START + timedelta(hours=hours)
    )


def test_haversine_moscow_to_saint_petersburg():
    assert haversine(55.7558, 37.6173, 59.9343, 30.3351) == pytest.approx(634, abs=2)


def test_avg_speed_is_total_distance_over_total_time():
    track = [point(50, hours=0), point(51, hours=1), point(53, hours=4)]

    assert calculate_avg_speed(track) == pytest.approx(3 * KM_PER_DEGREE / 4, abs=0.01)


def test_avg_distance_is_mean_step_between_points():
    track = [point(50), point(51), point(53)]

    assert calculate_avg_distance(track) == pytest.approx(1.5 * KM_PER_DEGREE, abs=0.01)


@pytest.mark.parametrize("track", [[], [point(50)]])
def test_single_point_gives_zero(track):
    assert calculate_avg_speed(track) == 0
    assert calculate_avg_distance(track) == 0
