from dataclasses import dataclass
from typing import Dict


@dataclass
class CombinacionCarga:
    D: float = 0
    L: float = 0
    Lr: float = 0
    W: float = 0
    S: float = 0
    E: float = 0
    R: float = 0
    special_case: bool = False

    @property
    def _L_corr(self) -> float:
        # Accompanying live load per E.060
        return self.L if self.special_case else 0.5 * self.L

    # ---------------- LRFD (E.060) ----------------

    def combinations(self) -> Dict[str, float]:
        combinations: Dict[str, float] = {}

        # Combinación 1: 1.4D
        combinations["1"] = 1.4 * self.D

        # Combinación 2: 1.2D * 1.6L + 0.5(Lr ó S ó R)
        for name, x in zip(("Lr", "S", "R"), (self.Lr, self.S, self.R)):
            combinations[f"2-{name}"] = 1.2 * self.D + 1.6 * self.L + 0.5 * x

        # Combinación 3: 1.2D + 1.6(Lr ó S ó R) + (0,5L ó 0.8W)
        for name, x in zip(("Lr", "S", "R"), (self.Lr, self.S, self.R)):
            combinations[f"3-{name}-L"] = 1.2 * self.D + 1.6 * x + self._L_corr
            combinations[f"3-{name}-W"] = 1.2 * self.D + 1.6 * x + 0.8 * self.W

        # Combinación 4: 1.2D ∓ 1.3W + 0.5L + 0.5(Lr ó S ó R)
        for name, x in zip(("Lr", "S", "R"), (self.Lr, self.S, self.R)):
            combinations[f"4-{name}"] = (
                1.2 * self.D + 1.3 * self.W + self._L_corr + 0.5 * x
            )

        # Combinación 5: 1.2D ∓ 1.0E + 0.5L + 0.2S
        combinations["5-E+"] = 1.2 * self.D + self.E + self._L_corr + 0.2 * self.S
        combinations["5-E-"] = 1.2 * self.D - self.E + self._L_corr + 0.2 * self.S

        # Combinación 6: 0.9D ∓ (1.3W ó 1.0E)
        combinations["6-W+"] = 0.9 * self.D + 1.3 * self.W
        combinations["6-W-"] = 0.9 * self.D - 1.3 * self.W
        combinations["6-E+"] = 0.9 * self.D + 1.0 * self.E
        combinations["6-E-"] = 0.9 * self.D - 1.0 * self.E

        return combinations

    # ---------------- ENVELOPES ----------------

    @property
    def envelope_max(self):
        combos = self.combinations()
        tag = max(combos, key=lambda k: combos[k])
        return tag, combos[tag]

    @property
    def envelope_min(self):
        combos = self.combinations()
        tag = min(combos, key=lambda k: combos[k])
        return tag, combos[tag]
