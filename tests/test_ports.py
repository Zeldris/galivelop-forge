"""Invariant 10: ports fail closed."""
import unittest

from gforge import (
    MeasurePort,
    PortUnavailable,
    UnavailableMachinePort,
    UnavailableMeasurePort,
    UnavailablePublishPort,
    UnavailableQueuePort,
    UnavailableTrainerPort,
    baseline,
    default_ports,
)


class FakeMeasure(MeasurePort):
    def baseline(self, target, model):
        return ("measured", target, model)

    def measure(self, target, model):
        return ("m", target, model)


class PortsFailClosed(unittest.TestCase):
    def test_baseline_without_port_names_the_repo(self):
        with self.assertRaises(PortUnavailable) as cm:
            baseline("t", "m")
        self.assertEqual(cm.exception.port, "MeasurePort")
        self.assertIn("galivelop-evaluator", str(cm.exception))

    def test_every_unavailable_method_raises_with_port_name(self):
        calls = [
            ("MachinePort", lambda: UnavailableMachinePort().base_models("t")),
            ("MachinePort", lambda: UnavailableMachinePort().register("m")),
            ("QueuePort", lambda: UnavailableQueuePort().lock("j")),
            ("MeasurePort", lambda: UnavailableMeasurePort().baseline("t", "m")),
            ("MeasurePort", lambda: UnavailableMeasurePort().measure("t", "m")),
            ("TrainerPort", lambda: UnavailableTrainerPort().train({})),
            ("PublishPort", lambda: UnavailablePublishPort().publish({})),
        ]
        for name, call in calls:
            with self.subTest(port=name):
                with self.assertRaises(PortUnavailable) as cm:
                    call()
                self.assertEqual(cm.exception.port, name)
                self.assertTrue(str(cm.exception).startswith(name + " unavailable: "))
                self.assertTrue(cm.exception.missing)
                self.assertTrue(cm.exception.remedy)

    def test_lock_raises_instead_of_returning_a_fake(self):
        with self.assertRaises(PortUnavailable) as cm:
            UnavailableQueuePort().lock("job")
        self.assertIn("galivelop-runtime", str(cm.exception))

    def test_publish_names_credential(self):
        with self.assertRaises(PortUnavailable) as cm:
            UnavailablePublishPort().publish({})
        self.assertIn("Hugging Face credential", str(cm.exception))
        self.assertIn("HF_TOKEN", str(cm.exception))

    def test_injected_port_is_used(self):
        self.assertEqual(baseline("t", "m", measure=FakeMeasure()), ("measured", "t", "m"))

    def test_default_ports_are_all_unavailable(self):
        ports = default_ports()
        self.assertEqual(
            sorted(ports),
            ["MachinePort", "MeasurePort", "PublishPort", "QueuePort", "TrainerPort"],
        )


if __name__ == "__main__":
    unittest.main()
