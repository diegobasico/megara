import logging
from dataclasses import dataclass

import numpy as np

from .definiciones import Element

logger = logging.getLogger(__name__)


class CompressionValueNeeded(ValueError):
    pass


@dataclass(frozen=True)
class _CompressedElement:
    element: Element

    @property
    def t(self) -> float:
        if not self.element.section.t:
            raise CompressionValueNeeded(
                f'Missing parameter "t" for element {self.element.section.shape}'
            )
        return self.element.section.t

    @property
    def tw(self) -> float:
        if not self.element.section.tw:
            raise CompressionValueNeeded(
                f'Missing parameter "tw" for element {self.element.section.shape}'
            )
        return self.element.section.tw

    @property
    def bf(self) -> float:
        if not self.element.section.bf:
            raise CompressionValueNeeded(
                f'Missing parameter "bf" for element {self.element.section.shape}'
            )
        return self.element.section.bf

    @property
    def rx(self) -> float:
        if not self.element.section.rx:
            raise CompressionValueNeeded(
                f'Missing parameter "rx" for element {self.element.section.shape}'
            )
        return self.element.section.rx

    @property
    def ry(self) -> float:
        if not self.element.section.ry:
            raise CompressionValueNeeded(
                f'Missing parameter "ry" for element {self.element.section.shape}'
            )
        return self.element.section.ry

    @property
    def A(self) -> float:
        if not self.element.section.a:
            raise CompressionValueNeeded(
                f'Missing parameter "A" for element {self.element.section.shape}'
            )
        return self.element.section.a

    @property
    def tf(self) -> float:
        if not self.element.section.tf:
            raise CompressionValueNeeded(
                f'Missing parameter "tf" for element {self.element.section.shape}'
            )
        return self.element.section.tf

    @property
    def Kx(self) -> float:
        if not self.element.Kx:
            raise CompressionValueNeeded(
                f'Missing parameter "Kx" for element {self.element.section.shape}'
            )
        return self.element.Kx

    @property
    def Ky(self) -> float:
        if not self.element.Ky:
            raise CompressionValueNeeded(
                f'Missing parameter "Ky" for element {self.element.section.shape}'
            )
        return self.element.Ky

    @property
    def E(self) -> float:
        if not self.element.material.E:
            raise CompressionValueNeeded(
                f'Missing parameter "E" for element {self.element.section.shape}'
            )
        return self.element.material.E

    @property
    def Fy(self) -> float:
        if not self.element.material.Fy:
            raise CompressionValueNeeded(
                f'Missing parameter "Fy" for element {self.element.section.shape}'
            )
        return self.element.material.Fy

    @property
    def L(self) -> float:
        if not self.element.L:
            raise CompressionValueNeeded(
                f'Missing parameter "L" for element {self.element.section.shape}'
            )
        return self.element.L

    # ----------------
    # Slenderness
    # ----------------

    def check_local_slenderness(self) -> bool:
        # Table B4.1a, AISC 360 - 16
        # web    : λ = h / tw = d - 2k_des / tw
        # flange : λ = b / t = 0.5 * bf / tf = bf/(2 * tf)
        lambda_web = self.t / self.tw
        lambda_flange = self.bf / (2 * self.tf)

        lambda_r_web = 1.49 * np.sqrt(self.E / self.Fy)
        lambda_r_flange = 0.56 * np.sqrt(self.E / self.Fy)

        if lambda_flange < lambda_r_flange and lambda_web < lambda_r_web:
            logging.info("El elemento no es esbelto localmente ✅.")
            return True
        else:
            logging.warning("El elemento es esbelto localmente ⛔.")
            return False

    def check_global_slenderness(self) -> bool:
        global_slenderness_x = self.Kx * self.L / self.rx
        global_slenderness_y = self.Ky * self.L / self.ry

        if global_slenderness_x < 200 and global_slenderness_y < 200:
            logging.info("El elemento no es esbelto globalmente ✅.")
            return True
        else:
            logging.error("El elemento es esbelto globalmente ⛔.")
            return False

    # ----------------
    # Buckling
    # ----------------

    def buckling_limit(self) -> float:
        value = 4.71 * np.sqrt(self.E / self.Fy)
        return value

    def slenderness_x(self):
        value = self.Kx * self.L / self.rx
        return value

    def slenderness_y(self):
        value = self.Ky * self.L / self.ry
        return value

    def euler_buckling_x(self) -> float:
        value = np.pi**2 * self.E / self.slenderness_x() ** 2
        return value

    def euler_buckling_y(self) -> float:
        value = np.pi**2 * self.E / self.slenderness_y() ** 2
        return value

    def aisc_buckling_x(self) -> float:
        if self.slenderness_x() <= self.buckling_limit():
            Fcr = (0.658 ** (self.Fy / self.euler_buckling_x())) * self.Fy
        else:
            Fcr = 0.877 * self.euler_buckling_x()
        return Fcr

    def aisc_buckling_y(self) -> float:
        if self.slenderness_y() <= self.buckling_limit():
            Fcr = (0.658 ** (self.Fy / self.euler_buckling_y())) * self.Fy
        else:
            Fcr = 0.877 * self.euler_buckling_y()
        return Fcr

    def critical_buckling_stress(self) -> float:
        return min(self.aisc_buckling_x(), self.aisc_buckling_y())

    def compression_resistent_force(self) -> float:
        "Outputs force un kips."
        phi = 0.90  # compression
        Pu = phi * self.A * self.critical_buckling_stress()
        return Pu

    def check_slenderness(self) -> float:
        not_slender = self.check_global_slenderness() and self.check_local_slenderness()
        if not_slender:
            return True
        return False


def ultimate_compression_force(compressed_element: Element) -> float:
    element = _CompressedElement(compressed_element)
    return element.compression_resistent_force()


def check_slenderness(compressed_element: Element) -> float:
    element = _CompressedElement(compressed_element)
    not_slender = (
        element.check_global_slenderness() and element.check_local_slenderness()
    )
    if not_slender:
        return True
    logger.info("Element is not slender")
    return False


if __name__ == "__main__":
    pass
