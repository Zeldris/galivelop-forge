"""Ports of gforge. Without an implementation, every operation fails closed (invariant 10).

Nothing here fakes a measurement or a lock: an unavailable port always raises PortUnavailable.
"""
from __future__ import annotations

import abc
from typing import Any, ContextManager, Dict


class PortUnavailable(RuntimeError):
    """Raised when a port has no implementation; says what is missing and how to fix it."""

    def __init__(self, port: str, missing: str, remedy: str) -> None:
        self.port = port
        self.missing = missing
        self.remedy = remedy
        super().__init__(str(self))

    def __str__(self) -> str:
        return "{} unavailable: {} is missing; {}".format(self.port, self.missing, self.remedy)


class MachinePort(abc.ABC):
    """Model catalogue and machine profile (gmod = galivelop-models)."""

    @abc.abstractmethod
    def base_models(self, target: Any) -> Any:
        """Return the base models that fit the target."""

    @abc.abstractmethod
    def register(self, model: Any) -> Any:
        """Register a trained model in the catalogue."""


class QueuePort(abc.ABC):
    """Local job queue and lock (grun = galivelop-runtime)."""

    @abc.abstractmethod
    def lock(self, job: Any) -> ContextManager[Any]:
        """Return a context manager that holds the machine lock for the job."""


class MeasurePort(abc.ABC):
    """Measurement (GVE = galivelop-evaluator)."""

    @abc.abstractmethod
    def baseline(self, target: Any, model: Any) -> Any:
        """Measure the baseline of a model on a target."""

    @abc.abstractmethod
    def measure(self, target: Any, model: Any) -> Any:
        """Measure a model on a target."""


class TrainerPort(abc.ABC):
    """Trainer (optional extra)."""

    @abc.abstractmethod
    def train(self, recipe: Any) -> Any:
        """Run the training described by the recipe."""


class PublishPort(abc.ABC):
    """Publication (Hugging Face)."""

    @abc.abstractmethod
    def publish(self, card: Any) -> Any:
        """Publish a card."""


class UnavailableMachinePort(MachinePort):
    def _fail(self) -> PortUnavailable:
        return PortUnavailable(
            "MachinePort", "galivelop-models (gmod)", "provide a MachinePort from galivelop-models"
        )

    def base_models(self, target: Any) -> Any:
        raise self._fail()

    def register(self, model: Any) -> Any:
        raise self._fail()


class UnavailableQueuePort(QueuePort):
    def lock(self, job: Any) -> ContextManager[Any]:
        raise PortUnavailable(
            "QueuePort", "galivelop-runtime (grun)", "provide a QueuePort from galivelop-runtime"
        )


class UnavailableMeasurePort(MeasurePort):
    def _fail(self) -> PortUnavailable:
        return PortUnavailable(
            "MeasurePort",
            "galivelop-evaluator (GVE)",
            "provide a MeasurePort from galivelop-evaluator",
        )

    def baseline(self, target: Any, model: Any) -> Any:
        raise self._fail()

    def measure(self, target: Any, model: Any) -> Any:
        raise self._fail()


class UnavailableTrainerPort(TrainerPort):
    def train(self, recipe: Any) -> Any:
        raise PortUnavailable(
            "TrainerPort", "a trainer", 'pip install "galivelop-forge[unsloth]"'
        )


class UnavailablePublishPort(PublishPort):
    def publish(self, card: Any) -> Any:
        raise PortUnavailable("PublishPort", "a Hugging Face credential", "set HF_TOKEN")


def default_ports() -> Dict[str, Any]:
    """Return every port in its unavailable form, by name."""
    return {
        "MachinePort": UnavailableMachinePort(),
        "QueuePort": UnavailableQueuePort(),
        "MeasurePort": UnavailableMeasurePort(),
        "TrainerPort": UnavailableTrainerPort(),
        "PublishPort": UnavailablePublishPort(),
    }
