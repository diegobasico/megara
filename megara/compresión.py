import logging

import numpy as np

from .definiciones import Element

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


class CompressionException(Exception):
    pass


# ----------------
# Slenderness
# ----------------


def check_local_slenderness(element: Element) -> bool:
    # Table B4.1a, AISC 360 - 16
    # web    : λ = h / tw = d - 2k_des / tw
    # flange : λ = b / t = 0.5 * bf / tf = bf/(2 * tf)
    lambda_web = element.h / element.tw
    lambda_flange = element.bf / (2 * element.tf)

    lambda_r_web = 1.49 * np.sqrt(element.E / element.Fy)
    lambda_r_flange = 0.56 * np.sqrt(element.E / element.Fy)

    if lambda_flange < lambda_r_flange and lambda_web < lambda_r_web:
        logging.info("El elemento no es esbelto localmente ✅.")
        return False
    else:
        logging.error("El elemento es esbelto localmente ⛔.")
        return True


def check_global_slenderness(element: Element) -> bool:
    if not element.Kx or not element.Ky:
        raise CompressionException("Must specify Kx and Ky for compression check")
    global_slenderness_x = element.Kx * element.L / element.rx
    global_slenderness_y = element.Ky * element.L / element.ry

    if global_slenderness_x < 200 and global_slenderness_y < 200:
        logging.info("El elemento no es esbelto globalmente ✅.")
        return False
    else:
        logging.error("El elemento es esbelto globalmente ⛔.")
        return True


# ----------------
# Buckling
# ----------------


def buckling_limit(element: Element) -> float:
    value = 4.71 * np.sqrt(element.E / element.Fy)
    return value


def slenderness_x(element: Element):
    if not element.Kx or not element.Ky:
        raise CompressionException("Must specify Kx and Ky for compression check")

    value = element.Kx * element.L / element.rx
    return value


def slenderness_y(element: Element):
    if not element.Kx or not element.Ky:
        raise CompressionException("Must specify Kx and Ky for compression check")

    value = element.Ky * element.L / element.ry
    return value


def euler_buckling_x(element: Element) -> float:
    value = np.pi**2 * element.E / slenderness_x(element) ** 2
    return value


def euler_buckling_y(element: Element) -> float:
    value = np.pi**2 * element.E / slenderness_y(element) ** 2
    return value


def aisc_buckling_x(element: Element) -> float:
    if slenderness_x(element) <= buckling_limit(element):
        Fcr = (0.658 ** (element.Fy / euler_buckling_x(element))) * element.Fy
    else:
        Fcr = 0.877 * euler_buckling_x(element)
    return Fcr


def aisc_buckling_y(element: Element) -> float:
    if slenderness_y(element) <= buckling_limit(element):
        Fcr = (0.658 ** (element.Fy / euler_buckling_y(element))) * element.Fy
    else:
        Fcr = 0.877 * euler_buckling_y(element)
    return Fcr


def critical_buckling_stress(element: Element) -> float:
    return min(aisc_buckling_x(element), aisc_buckling_y(element))


def compression_resistent_force(element: Element) -> float:
    "Outputs force un kips."
    phi = 0.90  # compression
    Pu = phi * element.A * critical_buckling_stress(element)
    return Pu


def check_slenderness(element: Element) -> float:
    if check_global_slenderness(element) and check_local_slenderness(element):
        return True

    return False


if __name__ == "__main__":
    pass
