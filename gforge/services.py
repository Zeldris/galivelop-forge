"""Services of gforge. Each one goes through a port and fails closed without it."""
from __future__ import annotations

from typing import Any, Optional

from gforge.ports import MeasurePort, TrainerPort, UnavailableMeasurePort, UnavailableTrainerPort


def baseline(target: Any, model: Any, measure: Optional[MeasurePort] = None) -> Any:
    """Measure the baseline of a model through MeasurePort."""
    port = UnavailableMeasurePort() if measure is None else measure
    return port.baseline(target, model)


def train(recipe: Any, trainer: Optional[TrainerPort] = None) -> Any:
    """Train a recipe through TrainerPort."""
    port = UnavailableTrainerPort() if trainer is None else trainer
    return port.train(recipe)
