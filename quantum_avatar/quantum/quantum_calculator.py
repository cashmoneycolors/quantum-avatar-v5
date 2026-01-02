from __future__ import annotations

from typing import Any

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    from qiskit import QuantumCircuit, transpile  # type: ignore
except ImportError:  # pragma: no cover
    QuantumCircuit = None
    transpile = None

try:
    from qiskit_aer import AerSimulator  # type: ignore
except ImportError:  # pragma: no cover
    AerSimulator = None


class QuantumCalculator:
    def __init__(self):
        self.simulator = AerSimulator() if AerSimulator is not None else None

    def optimize_produce_display(self, products, weather_temp, max_slots=10):
        # Quantum-inspired optimization for minimizing spoilage
        # Products: list of dicts with 'name', 'spoil_rate', 'freshness_index'
        # Keep this deterministic and lightweight for local runs/tests.
        def score(product: dict[str, Any]) -> float:
            spoil_rate = float(product.get("spoil_rate", 0.0))
            freshness_index = float(product.get("freshness_index", 0.0))
            temp_factor = 1.0 + (float(weather_temp) / 10.0)
            return freshness_index - (spoil_rate * temp_factor)

        ranked = sorted(list(products), key=score, reverse=True)
        return ranked[: int(max_slots)]

    def calculate_quantum_probability(self, states=None):
        # Simple quantum state simulation (fallback if qiskit isn't available).
        missing = self.simulator is None or QuantumCircuit is None or transpile is None
        if missing:
            return {"00": 512, "11": 512}

        assert self.simulator is not None
        assert QuantumCircuit is not None
        assert transpile is not None

        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        job = self.simulator.run(transpile(qc, self.simulator), shots=1024)
        result = job.result()
        return result.get_counts()
