import logging
from dataclasses import dataclass
from functools import cached_property

import numpy as np
import matplotlib.pyplot as plt

from .definiciones import Element
from etc.paths import local_paths


logger = logging.getLogger(__name__)


class ShearValueNeeded(ValueError):
    pass


@dataclass(frozen=True)
class ShearedElement:
    """
    Element to be sheared.
        - element: beam to be checked for shear strength
        - a: distance between transverse stiffeners (in mm)
    """

    element: Element
    a: float | None = None

    # ----------------
    # Section geometry
    # ----------------

    def __post_init__(self):
        logger.info(
            f"\n\n:: Applying shear to element {self.element.name}...\n"
            + "-" * 45
            + "\n"
        )

    @cached_property
    def shape(self) -> str:
        if not self.element.section.shape:
            logger.error("Missing shape")
            raise ShearValueNeeded(
                f'Missing parameter "shape" for element {self.element.section.shape}.'
            )
        logger.info(f"shape : {self.element.section.shape}")
        return self.element.section.shape

    @cached_property
    def d(self) -> float:
        if not self.element.section.d:
            logger.error("Missing d")
            raise ShearValueNeeded(
                f'Missing parameter "d" for element {self.element.section.shape}.'
            )
        logger.info(f"d : {self.element.section.d}")
        return self.element.section.d

    @cached_property
    def h(self) -> float:
        if not self.element.section.t:
            logger.error("Missing h = t")
            raise ShearValueNeeded(
                f'Missing parameter "h = t" for element {self.element.section.shape}.'
            )
        logger.info(f"h : {self.element.section.t}")
        return self.element.section.t

    @cached_property
    def tw(self) -> float:
        if not self.element.section.tw:
            logger.error("Missing tw")
            raise ShearValueNeeded(
                f'Missing parameter "tw" for element {self.element.section.shape}.'
            )
        logger.info(f"tw : {self.element.section.tw}")
        return self.element.section.tw

    # ----------------
    # Material
    # ----------------

    @cached_property
    def E(self) -> float:
        if not self.element.material.E:
            logger.error("Missing E")
            raise ShearValueNeeded(
                f'Missing parameter "E" for element {self.element.section.shape}.'
            )
        logger.info(f"E : {self.element.material.E}")
        return self.element.material.E

    @cached_property
    def Fy(self) -> float:
        if not self.element.material.Fy:
            logger.error("Missing Fy")
            raise ShearValueNeeded(
                f'Missing parameter "Fy" for element {self.element.section.shape}.'
            )
        logger.info(f"Fy : {self.element.material.Fy}")
        return self.element.material.Fy

    # ----------------
    # Slenderness
    # ----------------

    @cached_property
    def _lambda_w(self) -> float:
        _lambda = self.h / self.tw
        logger.info(f"λ_w : {_lambda}")
        return _lambda

    @cached_property
    def _lambda_r(self) -> float:
        if self.shape[0] in ("W", "S", "M", "H"):
            value = 2.24 * np.sqrt(self.E / self.Fy)
            # HACK: the correct formula should be:
            # value = 1.10 * np.sqrt(self.kv * self.E / self.Fy)
            # but AISC changed it to 2.24, which is higer,
            # for some reason that I haven't understood yet;
            # this draws a non-continuous function with a peak
            # on the edge case h/wt = lambda_r
        elif self.shape[0] in ("C"):
            value = 1.10 * np.sqrt(self.kv * self.E / self.Fy)
        else:
            raise ShearValueNeeded("Unsupported shape for shear")
        logger.info(f"λr : {value}")
        return value

    # ----------------
    # Shear
    # ----------------

    @cached_property
    def Aw(self) -> float:
        value = self.d * self.tw
        logger.info(f"Aw : {value}")
        return value

    @cached_property
    def kv(self) -> float:
        if self.a is None or self.a / self.h > 3:
            value = 5.34
        else:
            value = 5 + 5 / (self.a / self.h) ** 2
        logger.info(f"Kv : {value}")
        return value

    @cached_property
    def cv(self) -> float:
        if self._lambda_w < self._lambda_r:
            value = 1
        else:
            value = 1.10 * np.sqrt(self.kv * self.E / self.Fy) / (self._lambda_w)
        logger.info(f"Cv : {value}")
        return value

    @cached_property
    def Vn(self) -> float:
        if self.a is not None and self.a / self.h <= 3:
            raise NotImplementedError(
                "Tension field action (AISC G2.2) not implemented"
            )

        value = 0.6 * self.Fy * self.Aw * self.cv
        logger.info(f"Vn : {value}")
        return value

    @cached_property
    def phi(self) -> float:
        if self.shape[0] in ("W", "S", "M", "H"):
            value = 1
        elif self.shape[0] in ("C"):
            value = 0.9
        else:
            raise ShearValueNeeded("Unsupported shape for shear")
        logger.info(f"ɸ_v : {value}")
        return value

    @cached_property
    def phi_Vn(self) -> float:
        return self.Vn * self.phi

    # ----------------
    # Plot
    # ----------------

    def _cv_from_lambda(self, lambda_w: float) -> float:
        if lambda_w <= self._lambda_r:
            return 1.0
        return 1.10 * np.sqrt(self.kv * self.E / self.Fy) / lambda_w

    @property
    def _phi_Vn_figure(self):
        # ---- Slenderness range
        lambda_vals = np.linspace(1, 250, 500)

        Vn_vals = np.array(
            [
                self.phi * 0.6 * self.Fy * self.Aw * self._cv_from_lambda(lw)
                for lw in lambda_vals
            ]
        )

        fig, ax = plt.subplots()

        # ---- Curve
        ax.plot(lambda_vals, Vn_vals, color="black", linewidth=2, label="_nolegend_")

        # ---- Limit line λr
        ax.axvline(
            self._lambda_r,
            linestyle="--",
            color="tab:red",
            label="_nolegend_",
        )

        # ---- Actual section point
        lambda_w = self._lambda_w
        Vn_w = self.phi * 0.6 * self.Fy * self.Aw * self.cv

        ax.scatter(lambda_w, Vn_w, zorder=5, color="black")

        # ---- Annotations
        ax.annotate(
            f"$\\lambda_r = {self._lambda_r:.2f}$",
            xy=(self._lambda_r, 0),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

        # ax.annotate(
        #     f"Vn = {Vn_w:.2f}",
        #     xy=(lambda_w, Vn_w),
        #     textcoords="offset points",
        #     xytext=(5, 5),
        #     fontsize=9,
        # )

        # ---- Governing callout (boxed)
        ax.annotate(
            f"$V_n$:  {Vn_w:.3f}\n$\\lambda_w$: {lambda_w:.2f}",
            xy=(lambda_w, Vn_w),
            textcoords="offset points",
            xytext=(40, 60),
            arrowprops=dict(
                arrowstyle="->",
                linewidth=1.5,
            ),
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.5),
            fontsize=9,
            ha="left",
            va="center",
        )

        # ---- Axes
        ax.set_xlim(0, 250)
        ax.set_ylim(0, 80)
        ax.set_xlabel(r"Web slenderness, $\lambda_w$ $(h/t_w)$")
        ax.set_ylabel(r"Nominal Shear Strength, $\phi V_n$ $(kip)$")
        ax.grid(True)

        fig.suptitle(
            r"Plot of Available Shear Strength ($\phi V_n$) vs"
            "\n"
            rf"Web Slenderness ($\lambda_w$) for {self.element.name} ({self.element.section.shape})"
        )

        return fig, ax

    def show_Vn_curve(self):
        _, _ = self._phi_Vn_figure
        plt.show()

    def save_Vn_curve(
        self,
        dpi: int = 300,
    ):
        fig, _ = self._phi_Vn_figure
        path = local_paths.cache / f"{self.element.name}_shear.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    pass
