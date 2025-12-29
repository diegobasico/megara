import logging
from dataclasses import dataclass
from functools import cached_property

import numpy as np
import matplotlib.pyplot as plt

from megara.flexión import Slenderness

from .definiciones import Element
from etc.paths import local_paths

logger = logging.getLogger(__name__)


class CompressionValueNeeded(ValueError):
    pass


@dataclass(frozen=True)
class CompressedElement:
    element: Element

    # ----------------
    # Section geometry
    # ----------------

    def __post_init__(self):
        logger.info(
            f"\n\n:: Applying compression to element {self.element.name}...\n"
            + "-" * 45
            + "\n"
        )

    @cached_property
    def phi(self) -> float:
        logger.info("flexure ɸ : 0.9")
        return 0.9

    @cached_property
    def t(self) -> float:
        if not self.element.section.t:
            logger.error("Missing t")
            raise CompressionValueNeeded(
                f'Missing parameter "t" for element {self.element.section.shape}'
            )
        logger.info(f"t : {self.element.section.t}")
        return self.element.section.t

    @cached_property
    def tw(self) -> float:
        if not self.element.section.tw:
            logger.error("Missing tw")
            raise CompressionValueNeeded(
                f'Missing parameter "tw" for element {self.element.section.shape}'
            )
        logger.info(f"tw : {self.element.section.tw}")
        return self.element.section.tw

    @cached_property
    def bf(self) -> float:
        if not self.element.section.bf:
            logger.error("Missing bf")
            raise CompressionValueNeeded(
                f'Missing parameter "bf" for element {self.element.section.shape}'
            )
        logger.info(f"bf : {self.element.section.bf}")
        return self.element.section.bf

    @cached_property
    def tf(self) -> float:
        if not self.element.section.tf:
            logger.error("Missing tf")
            raise CompressionValueNeeded(
                f'Missing parameter "tf" for element {self.element.section.shape}'
            )
        logger.info(f"tf : {self.element.section.tf}")
        return self.element.section.tf

    @cached_property
    def rx(self) -> float:
        if not self.element.section.rx:
            logger.error("Missing rx")
            raise CompressionValueNeeded(
                f'Missing parameter "rx" for element {self.element.section.shape}'
            )
        logger.info(f"rx : {self.element.section.rx}")
        return self.element.section.rx

    @cached_property
    def ry(self) -> float:
        if not self.element.section.ry:
            logger.error("Missing ry")
            raise CompressionValueNeeded(
                f'Missing parameter "ry" for element {self.element.section.shape}'
            )
        logger.info(f"ry : {self.element.section.ry}")
        return self.element.section.ry

    @cached_property
    def A(self) -> float:
        if not self.element.section.a:
            logger.error("Missing A")
            raise CompressionValueNeeded(
                f'Missing parameter "A" for element {self.element.section.shape}'
            )
        logger.info(f"A : {self.element.section.a}")
        return self.element.section.a

    # ----------------
    # Element / material
    # ----------------

    @cached_property
    def Kx(self) -> float:
        if not self.element.Kx:
            logger.error("Missing Kx")
            raise CompressionValueNeeded(
                f'Missing parameter "Kx" for element {self.element.section.shape}'
            )
        logger.info(f"Kx : {self.element.Kx}")
        return self.element.Kx

    @cached_property
    def Ky(self) -> float:
        if not self.element.Ky:
            logger.error("Missing Ky")
            raise CompressionValueNeeded(
                f'Missing parameter "Ky" for element {self.element.section.shape}'
            )
        logger.info(f"Ky : {self.element.Ky}")
        return self.element.Ky

    @cached_property
    def L(self) -> float:
        if not self.element.L:
            logger.error("Missing L")
            raise CompressionValueNeeded(
                f'Missing parameter "L" for element {self.element.section.shape}'
            )
        logger.info(f"L : {self.element.L}")
        return self.element.L

    @cached_property
    def E(self) -> float:
        if not self.element.material.E:
            logger.error("Missing E")
            raise CompressionValueNeeded(
                f'Missing parameter "E" for element {self.element.section.shape}'
            )
        logger.info(f"E : {self.element.material.E}")
        return self.element.material.E

    @cached_property
    def Fy(self) -> float:
        if not self.element.material.Fy:
            logger.error("Missing Fy")
            raise CompressionValueNeeded(
                f'Missing parameter "Fy" for element {self.element.section.shape}'
            )
        logger.info(f"Fy : {self.element.material.Fy}")
        return self.element.material.Fy

    # ----------------
    # Slenderness
    # ----------------

    @cached_property
    def lambda_web(self) -> float:
        value = self.t / self.tw
        logger.info(f"λ_web : {value}")
        return value

    @cached_property
    def lambda_flange(self) -> float:
        value = self.bf / (2 * self.tf)
        logger.info(f"λ_flange : {value}")
        return value

    @cached_property
    def lambda_r_web(self) -> float:
        value = 1.49 * np.sqrt(self.E / self.Fy)
        logger.info(f"λ_r_web : {value}")
        return value

    @cached_property
    def lambda_r_flange(self) -> float:
        value = 0.56 * np.sqrt(self.E / self.Fy)
        logger.info(f"λ_r_flange : {value}")
        return value

    @cached_property
    def local_slenderness(self) -> Slenderness:
        if (
            self.lambda_flange < self.lambda_r_flange
            and self.lambda_web < self.lambda_r_web
        ):
            slenderness = Slenderness.compact
        else:
            slenderness = Slenderness.slender
        logger.info(f"Local slenderness : {slenderness}")
        return slenderness

    @cached_property
    def slenderness_x(self) -> float:
        value = self.Kx * self.L / self.rx
        logger.info(f"KL/rx : {value}")
        return value

    @cached_property
    def slenderness_y(self) -> float:
        value = self.Ky * self.L / self.ry
        logger.info(f"KL/ry : {value}")
        return value

    @cached_property
    def global_slenderness(self) -> Slenderness:
        if self.slenderness_x < 200 and self.slenderness_y < 200:
            slenderness = Slenderness.compact
        else:
            slenderness = Slenderness.slender
        logger.info(f"Global slenderness : {slenderness}")
        return slenderness

    # ----------------
    # Buckling
    # ----------------

    @cached_property
    def buckling_limit(self) -> float:
        value = 4.71 * np.sqrt(self.E / self.Fy)
        logger.info(f"buckling limit : {value}")
        return value

    def euler_buckling_stress(self, slenderness: float) -> float:
        value = np.pi**2 * self.E / slenderness**2
        logger.debug(f"Euler buckling stress for {slenderness} : {value}")
        return value

    def critical_buckling_stress(self, slenderness: float) -> float:
        if slenderness <= self.buckling_limit:
            value = (
                0.658 ** (self.Fy / self.euler_buckling_stress(slenderness))
            ) * self.Fy
        else:
            value = 0.877 * self.euler_buckling_stress(slenderness)
        logger.debug(f"Critical buckling stress for {slenderness} : {value}")
        return value

    @cached_property
    def Fcr(self) -> float:
        if (
            self.local_slenderness == Slenderness.compact
            and self.global_slenderness == Slenderness.compact
        ):
            value = min(
                self.critical_buckling_stress(self.slenderness_x),
                self.critical_buckling_stress(self.slenderness_y),
            )
            logger.info(f"Fcr : {value}")
            return value
        else:
            raise ValueError("Check local or global slenderness.")

    @cached_property
    def phi_Fcr(self) -> float:
        value = self.phi * self.Fcr
        logger.info(f"ɸFcr : {value}")
        return value

    @cached_property
    def phi_Pn(self) -> float:
        value = self.A * self.phi_Fcr
        logger.info(f"ɸPn : {value}")
        return value

    # ----------------
    # Plot
    # ----------------

    @property
    def _phi_Pn_figure(self):
        slenderness = np.linspace(1, 200, 400)
        phi_Pn_vals = np.array(
            [self.phi * self.A * self.critical_buckling_stress(s) for s in slenderness]
        )

        fig, ax = plt.subplots()

        ax.plot(
            slenderness, phi_Pn_vals, color="black", linewidth=2, label="_nolegend_"
        )

        ax.axvline(
            self.slenderness_x, linestyle="--", color="tab:red", label="_nolegend_"
        )
        ax.axvline(
            self.slenderness_y, linestyle="--", color="tab:blue", label="_nolegend_"
        )

        # ---- Points
        phi_Pn_x = self.A * self.phi * self.critical_buckling_stress(self.slenderness_x)
        phi_Pn_y = self.A * self.phi * self.critical_buckling_stress(self.slenderness_y)

        ax.scatter(self.slenderness_x, phi_Pn_x, zorder=5, color="tab:red")
        ax.scatter(self.slenderness_y, phi_Pn_y, zorder=5, color="tab:blue")

        # ---- Annotations
        ax.annotate(
            f"KL/rx: {self.slenderness_x:.2f}",
            xy=(self.slenderness_x, 0),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )
        ax.annotate(
            f"ɸFcr_x * A: {phi_Pn_x:.2f}",
            xy=(self.slenderness_x, phi_Pn_x),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

        ax.annotate(
            f"KL/ry: {self.slenderness_y:.2f}",
            xy=(self.slenderness_y, 0),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )
        ax.annotate(
            f"ɸFcr_y * A: {phi_Pn_y:.2f}",
            xy=(self.slenderness_y, phi_Pn_y),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

        # ---- Governing point (boxed callout, like ɸMn)
        slenderness_gov = (
            self.slenderness_x if phi_Pn_x <= phi_Pn_y else self.slenderness_y
        )
        phi_Pn_gov = min(phi_Pn_x, phi_Pn_y)

        ax.scatter(slenderness_gov, phi_Pn_gov, zorder=6, color="black")

        ax.annotate(
            f"ɸPn:  {phi_Pn_gov:.3f}\nKL/r: {slenderness_gov:.2f}",
            xy=(slenderness_gov, phi_Pn_gov),
            textcoords="offset points",
            xytext=(-75, -45),
            arrowprops=dict(arrowstyle="->", linewidth=1.5, relpos=(1, 1)),
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.5),
            fontsize=9,
            ha="left",
            va="bottom",
        )

        # ---- Axes
        ax.set_xlim(0, 200)
        ax.set_ylim(bottom=0)
        ax.set_xlabel("Slenderness, KL/r")
        ax.set_ylabel("Design Force, ɸPn (kip)")
        ax.grid(True)

        fig.suptitle(
            f"Compression Buckling Curve: Available Force (ɸPn)\nvs Column Slenderness (KL/r) for {self.element.name} ({self.element.section.shape})"
        )

        return fig, ax

    def show_phi_Pn_curve(self):
        _, _ = self._phi_Pn_figure
        plt.show()

    def save_phi_Pn_curve(self, dpi: int = 300):
        fig, _ = self._phi_Pn_figure
        path = local_paths.cache / f"{self.element.name}_compression.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
