import logging
from dataclasses import dataclass

import numpy as np

from .definiciones import Element

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


class _CompressionValueNeeded(ValueError):
    pass


@dataclass(frozen=True)
class _CompressedElement:
    element: Element

    @property
    def h(self):
        if not self.element.section.h:
            raise _CompressionValueNeeded(
                f'Missing parameter "h" for element {self.element.section.shape}'
            )
        return self.element.section.h

    @property
    def tw(self):
        if not self.element.section.tw:
            raise _CompressionValueNeeded(
                f'Missing parameter "tw" for element {self.element.section.shape}'
            )
        return self.element.section.tw

    @property
    def bf(self):
        if not self.element.section.bf:
            raise _CompressionValueNeeded(
                f'Missing parameter "bf" for element {self.element.section.shape}'
            )
        return self.element.section.bf

    @property
    def rx(self):
        if not self.element.section.rx:
            raise _CompressionValueNeeded(
                f'Missing parameter "rx" for element {self.element.section.shape}'
            )
        return self.element.section.rx

    @property
    def ry(self):
        if not self.element.section.ry:
            raise _CompressionValueNeeded(
                f'Missing parameter "ry" for element {self.element.section.shape}'
            )
        return self.element.section.ry

    @property
    def A(self):
        if not self.element.section.a:
            raise _CompressionValueNeeded(
                f'Missing parameter "A" for element {self.element.section.shape}'
            )
        return self.element.section.a

    @property
    def tf(self):
        if not self.element.section.tf:
            raise _CompressionValueNeeded(
                f'Missing parameter "tf" for element {self.element.section.shape}'
            )
        return self.element.section.tf

    @property
    def Kx(self):
        if not self.element.Kx:
            raise _CompressionValueNeeded(
                f'Missing parameter "Kx" for element {self.element.section.shape}'
            )
        return self.element.Kx

    @property
    def Ky(self):
        if not self.element.Ky:
            raise _CompressionValueNeeded(
                f'Missing parameter "Ky" for element {self.element.section.shape}'
            )
        return self.element.Ky

    @property
    def E(self):
        if not self.element.material.E:
            raise _CompressionValueNeeded(
                f'Missing parameter "E" for element {self.element.section.shape}'
            )
        return self.element.material.E

    @property
    def Fy(self):
        if not self.element.material.Fy:
            raise _CompressionValueNeeded(
                f'Missing parameter "Fy" for element {self.element.section.shape}'
            )
        return self.element.material.Fy

    @property
    def L(self):
        if not self.element.L:
            raise _CompressionValueNeeded(
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
        lambda_web = self.h / self.tw
        lambda_flange = self.bf / (2 * self.tf)

        lambda_r_web = 1.49 * np.sqrt(self.E / self.Fy)
        lambda_r_flange = 0.56 * np.sqrt(self.E / self.Fy)

        if lambda_flange < lambda_r_flange and lambda_web < lambda_r_web:
            logging.info("El selfo no es esbelto localmente ✅.")
            return False
        else:
            logging.error("El selfo es esbelto localmente ⛔.")
            return True

    def check_global_slenderness(self) -> bool:
        global_slenderness_x = self.Kx * self.L / self.rx
        global_slenderness_y = self.Ky * self.L / self.ry

        if global_slenderness_x < 200 and global_slenderness_y < 200:
            logging.info("El selfo no es esbelto globalmente ✅.")
            return False
        else:
            logging.error("El selfo es esbelto globalmente ⛔.")
            return True

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
        if self.check_global_slenderness() and self.check_local_slenderness():
            return True
        return False


def ultimate_compression_force(compressed_element: Element) -> float:
    element = _CompressedElement(compressed_element)
    return element.compression_resistent_force()


if __name__ == "__main__":
    pass
