import logging
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from functools import cached_property

import numpy as np
import matplotlib.pyplot as plt

from .definiciones import Element
from etc.paths import local_paths


logger = logging.getLogger(__name__)


class FlexureValueNeeded(ValueError):
    pass


class Slenderness(Enum):
    slender = "slender"
    compact = "compact"
    noncompact = "noncompact"


@dataclass(frozen=True)
class FlexedElement:
    element: Element
    Lb: float
    cb: float

    # ----------------
    # Section geometry
    # ----------------

    def __post_init__(self):
        logger.info(
            f"\n\n:: Applying flexure to element {self.element.name}...\n"
            + "-" * 45
            + "\n"
        )

    @cached_property
    def shape(self) -> str:
        if not self.element.section.shape:
            logger.error("Missing shape")
            raise FlexureValueNeeded(
                f'Missing parameter "shape" for element {self.element.section.shape}.'
            )
        logger.info(f"shape : {self.element.section.shape}")
        return self.element.section.shape

    @cached_property
    def d(self) -> float:
        if not self.element.section.d:
            logger.error("Missing d")
            raise FlexureValueNeeded(
                f'Missing parameter "d" for element {self.element.section.shape}.'
            )
        logger.info(f"d : {self.element.section.d}")
        return self.element.section.d

    @cached_property
    def h(self) -> float:
        if not self.element.section.t:
            logger.error("Missing h = t")
            raise FlexureValueNeeded(
                f'Missing parameter "h = t" for element {self.element.section.shape}.'
            )
        logger.info(f"d : {self.element.section.t}")
        return self.element.section.t

    @cached_property
    def tf(self) -> float:
        if not self.element.section.tf:
            logger.error("Missing tf")
            raise FlexureValueNeeded(
                f'Missing parameter "tf" for element {self.element.section.shape}.'
            )
        logger.info(f"tf : {self.element.section.tf}")
        return self.element.section.tf

    @cached_property
    def tw(self) -> float:
        if not self.element.section.tw:
            logger.error("Missing tw")
            raise FlexureValueNeeded(
                f'Missing parameter "tw" for element {self.element.section.shape}.'
            )
        logger.info(f"tw : {self.element.section.tw}")
        return self.element.section.tw

    @cached_property
    def bf(self) -> float:
        if not self.element.section.bf:
            logger.error("Missing bf")
            raise FlexureValueNeeded(
                f'Missing parameter "bf" for element {self.element.section.shape}.'
            )
        logger.info(f"bf : {self.element.section.bf}")
        return self.element.section.bf

    @cached_property
    def ry(self) -> float:
        if not self.element.section.ry:
            logger.error("Missing ry")
            raise FlexureValueNeeded(
                f'Missing parameter "ry" for element {self.element.section.shape}.'
            )
        logger.info(f"ry : {self.element.section.ry}")
        return self.element.section.ry

    @cached_property
    def sx(self) -> float:
        if not self.element.section.sx:
            logger.error("Missing sx")
            raise FlexureValueNeeded(
                f'Missing parameter "sx" for element {self.element.section.shape}.'
            )
        logger.info(f"sx : {self.element.section.sx}")
        return self.element.section.sx

    @cached_property
    def j(self) -> float:
        if not self.element.section.j:
            logger.error("Missing j")
            raise FlexureValueNeeded(
                f'Missing parameter "j" for element {self.element.section.shape}.'
            )
        logger.info(f"j : {self.element.section.j}")
        return self.element.section.j

    @cached_property
    def iy(self) -> float:
        if not self.element.section.iy:
            logger.error("Missing iy")
            raise FlexureValueNeeded(
                f'Missing parameter "iy" for element {self.element.section.shape}.'
            )
        logger.info(f"iy : {self.element.section.iy}")
        return self.element.section.iy

    @cached_property
    def cw(self) -> float:
        if not self.element.section.cw:
            logger.error("Missing cw")
            raise FlexureValueNeeded(
                f'Missing parameter "cw" for element {self.element.section.shape}.'
            )
        logger.info(f"cw : {self.element.section.cw}")
        return self.element.section.cw

    @cached_property
    def zx(self) -> float:
        if not self.element.section.zx:
            logger.error("Missing zx")
            raise FlexureValueNeeded(
                f'Missing parameter "zx" for element {self.element.section.shape}.'
            )
        logger.info(f"zx : {self.element.section.zx}")
        return self.element.section.zx

    @cached_property
    def rts(self) -> float:
        value = np.sqrt(np.sqrt(self.iy * self.cw) / self.sx)
        logger.info(f"rts : {value}")
        return value

    @cached_property
    def ho(self) -> float:
        value = self.d - self.tf
        logger.info(f"ho : {value}")
        return value

    # ----------------
    # Material
    # ----------------

    @cached_property
    def E(self) -> float:
        if not self.element.material.E:
            logger.error("Missing E")
            raise FlexureValueNeeded(
                f'Missing parameter "E" for element {self.element.section.shape}.'
            )
        logger.info(f"E : {self.element.material.E}")
        return self.element.material.E

    @cached_property
    def Fy(self) -> float:
        if not self.element.material.Fy:
            logger.error("Missing Fy")
            raise FlexureValueNeeded(
                f'Missing parameter "Fy" for element {self.element.section.shape}.'
            )
        logger.info(f"Fy : {self.element.material.Fy}")
        return self.element.material.Fy

    @cached_property
    def L(self) -> float:
        if not self.element.L:
            logger.error("Missing L")
            raise FlexureValueNeeded(
                f'Missing parameter "L" for element {self.element.section.shape}.'
            )
        logger.info(f"L : {self.element.L}")
        return self.element.L

    # ----------------
    # Slenderness
    # ----------------

    @cached_property
    def _lambda(self) -> float:
        _lambda = self.bf / (2 * self.tf)
        logger.info(f"λ_f : {_lambda}")
        return _lambda

    @cached_property
    def lambda_pf(self) -> float:
        lambda_pf = 0.38 * np.sqrt(self.E / self.Fy)
        logger.info(f"λ_pf : {lambda_pf}")
        return lambda_pf

    @cached_property
    def lambda_rf(self) -> float:
        lambda_rf = np.sqrt(self.E / self.Fy)
        logger.info(f"λ_rf : {lambda_rf}")
        return lambda_rf

    @cached_property
    def slenderness(self) -> Slenderness:
        if self._lambda <= self.lambda_pf:
            logger.info("slenderness : compact")
            return Slenderness.compact
        elif self._lambda <= self.lambda_rf:
            logger.info("slenderness : non-compact")
            return Slenderness.noncompact
        else:
            logger.info("slenderness : slender")
            return Slenderness.slender

    # if compact, go to design by flexure

    @cached_property
    def noncompact_Mn(self) -> float:
        value = self.Mp - (self.Mp - 0.7 * self.Fy * self.sx) * (
            self._lambda - self.lambda_pf
        ) / (self.lambda_rf - self.lambda_pf)
        return value

    @cached_property
    def kc(self) -> float:
        value = 4 / np.sqrt(self.h / self.tw)
        logger.info(f"kc : {value}")
        return value

    @cached_property
    def slender_Mn(self) -> float:
        return 0.9 * self.E * self.kc * self.sx / (self._lambda**2)

    # ----------------
    # Flexure
    # ----------------

    @cached_property
    def Lp(self) -> float:
        value = 1.76 * self.ry * np.sqrt(self.E / self.Fy)
        logger.info(f"Lp : {value}")
        return value

    @cached_property
    def c(self) -> float:
        if self.shape[0] == "W":
            # HACK: to match excel, comment out the W case, since it
            # always uses c > 1 from channels, ignoring 1 for W.
            #     logger.info("c[Section W]: 1.00")
            #     return 1
            # elif self.shape[0] == "C":
            value = (self.ho / 2) * np.sqrt(self.iy / self.cw)
            logger.info(f"c[Section C] : {value}")
            return value
        else:
            logger.error("Invalid section shape for c")
            raise FlexureValueNeeded("Section is not W nor C.")

    @cached_property
    def Lr(self) -> float:
        term1 = np.sqrt(self.j * self.c / (self.sx * self.ho))
        term2 = np.sqrt(
            1
            + np.sqrt(
                1
                + 6.76
                * (0.7 * self.Fy * self.sx * self.ho / (self.E * self.j * self.c)) ** 2
            )
        )
        value = 1.95 * self.rts * self.E / (0.7 * self.Fy) * term1 * term2
        logger.info(f"Lr : {value}")
        return value

    @cached_property
    def Mp(self) -> float:
        value = self.Fy * self.zx
        logger.info(f"Mp : {value}")
        return value

    def plastic_Mn(self, Lb: float) -> float:
        logger.debug(f"plastic_Mn(Lb={Lb}) : {self.Mp}")
        return self.Mp

    def inelastic_Mn(self, Lb) -> float:
        value = self.cb * (
            self.Mp
            - (self.Mp - 0.7 * self.Fy * self.sx)
            * ((Lb - self.Lp) / (self.Lr - self.Lp))
        )

        logger.debug(f"inelastic_Mn(Lb={Lb}) : {value}")
        return value

    def elastic_Mn(self, Lb: float) -> float:
        value = (
            ((self.cb * np.pi**2 * self.E) / (Lb / self.rts) ** 2)
            * np.sqrt(
                (
                    1
                    + 0.078
                    * (self.j * self.c / (self.sx * self.ho))
                    * (Lb / self.rts) ** 2
                )
            )
            * self.sx
        )
        logger.debug(f"elastic_Mn(Lb={Lb}) : {value}")
        return value

    @cached_property
    def Mr(self) -> float:
        value = self.inelastic_Mn(self.Lr)
        logger.info(f"Mr : {value}")
        return value

    @cached_property
    def Mn(self) -> float:
        if self.slenderness == Slenderness.compact:
            if self.Lb <= self.Lp:
                return self.Mp
            elif self.Lb <= self.Lr:
                return self.inelastic_Mn(self.Lb)
            else:
                value = min(self.elastic_Mn(self.Lb), self.Mp)
                return value
        elif self.slenderness == Slenderness.noncompact:
            return self.noncompact_Mn
        else:  # if self.slenderness == Slenderness.slender
            return self.slender_Mn

    @cached_property
    def phi_Mn(self) -> float:
        phi = 0.90
        value = self.Mn * phi
        logger.info(f"ɸMn : {value}")
        return value

    # ----------------
    # Plot
    # ----------------

    @property
    def _Mn_figure(self):
        Lb_max = 30
        n = 360
        Lb_vals = np.linspace(0.01, Lb_max, n)
        Mn_vals = np.zeros_like(Lb_vals)

        for i, Lb in enumerate(Lb_vals):
            if Lb * 12 <= self.Lp:
                Mn_vals[i] = 0.9 * self.Mp / 12
            elif Lb * 12 <= self.Lr:
                Mn_vals[i] = 0.9 * self.inelastic_Mn(Lb * 12) / 12
            else:
                Mn_vals[i] = 0.9 * self.elastic_Mn(Lb * 12) / 12

        fig, ax = plt.subplots()

        # ---- Regions
        ax.axvspan(0, self.Lp / 12, alpha=0.15, color="tab:green", label="Plastic")
        ax.axvspan(
            self.Lp / 12,
            self.Lr / 12,
            alpha=0.15,
            color="tab:orange",
            label="Inelastic",
        )
        ax.axvspan(self.Lr / 12, Lb_max, alpha=0.15, color="tab:red", label="Elastic")

        # ---- Curve
        ax.plot(Lb_vals, Mn_vals, color="purple", linewidth=2, label="_nolegend_")

        # ---- Markers
        ax.axvline(self.Lp / 12, linestyle="--", color="tab:gray", label="_nolegend_")
        ax.axvline(self.Lr / 12, linestyle="--", color="tab:gray", label="_nolegend_")
        ax.axvline(self.Lb / 12, linestyle=":", color="tab:red", label="_nolegend_")

        # ---- Annotations (unchanged)
        ax.scatter(self.Lp / 12, 0.9 * self.Mp / 12, zorder=5)
        ax.annotate(
            f"ɸMp: {0.9 * self.Mp / 12:.2f}",
            xy=(self.Lp / 12, 0.9 * self.Mp / 12),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )
        ax.annotate(
            f"Lp: {self.Lp / 12:.2f}",
            xy=(self.Lp / 12, 0),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

        ax.scatter(self.Lr / 12, 0.9 * self.Mr / 12, zorder=5)
        ax.annotate(
            f"ɸMr: {0.9 * self.Mr / 12:.2f}",
            xy=(self.Lr / 12, 0.9 * self.Mr / 12),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )
        ax.annotate(
            f"Lr: {self.Lr / 12:.2f}",
            xy=(self.Lr / 12, 0),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

        ax.scatter(self.Lb / 12, 0.9 * self.Mn / 12, zorder=6, color="tab:red")
        ax.annotate(
            f"Lb   : {self.Lb / 12:.2f}\nɸMn: {0.9 * self.Mn / 12:.2f}",
            xy=(self.Lb / 12, 0.9 * self.Mn / 12),
            textcoords="offset points",
            xytext=(-60, -45),
            arrowprops=dict(arrowstyle="->", linewidth=1.5, relpos=(1, 1)),
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.5),
            fontsize=9,
            ha="left",
            va="bottom",
        )

        ax.set_xlim(0, 30)
        ax.set_ylim(0, 80)
        ax.set_xlabel("Unbraced Length, Lb (ft)")
        ax.set_ylabel("Available Moment, ɸMn (kip-ft)")
        ax.grid(True)
        ax.legend()

        fig.suptitle(
            f"Plot of Available Moment (ɸMn) vs\nUnbraced Length (Lb) for {self.element.name} ({self.shape})"
        )

        return fig, ax

    def show_Mn_curve(self):
        _, _ = self._Mn_figure
        plt.show()

    def save_Mn_curve(
        self,
        dpi: int = 300,
    ):
        fig, _ = self._Mn_figure
        path = local_paths.cache / self.element.name
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    pass
