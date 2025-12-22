import logging
from dataclasses import dataclass

import numpy as np

from megara.combinaciones import CombinacionCarga

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


@dataclass
class Steel:
    E: float
    Fy: float


@dataclass
class WSection:
    name: str

    # ---------
    # Geometry
    # ---------

    A: float  # cm²
    d: float  # mm
    tw: float  # mm
    bf: float  # mm
    tf: float  # mm
    h: float  # mm  (clear web height)
    rx: float  # cm
    ry: float  # cm
    wt: float  # kg/m


@dataclass
class WElement:
    material: Steel
    section: WSection
    L: float
    Kx: float
    Ky: float

    # ----------------
    # Geometry proxies
    # ----------------
    @property
    def A(self):
        return self.section.A

    @property
    def d(self):
        return self.section.d

    @property
    def tw(self):
        return self.section.tw

    @property
    def bf(self):
        return self.section.bf

    @property
    def tf(self):
        return self.section.tf

    @property
    def h(self):
        return self.section.h

    @property
    def rx(self):
        return self.section.rx

    @property
    def ry(self):
        return self.section.ry

    @property
    def wt(self):
        return self.section.wt

    # ----------------
    # Material proxies
    # ----------------
    @property
    def Fy(self):
        return self.material.Fy

    @property
    def E(self):
        return self.material.E

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

        if lambda_flange < lambda_r_flange or lambda_web < lambda_r_web:
            logging.info("El elemento no es esbelto localmente ✅.")
            return False
        else:
            logging.error("El elemento es esbelto localmente ⛔.")
            return True

    def check_global_slenderness(self) -> bool:
        slenderness_x = self.Kx * self.L / self.rx
        slenderness_y = self.Ky * self.L / self.ry

        if slenderness_x < 200 or slenderness_y < 200:
            logging.info("El elemento no es esbelto globalmente ✅.")
            return False
        else:
            logging.error("El elemento es esbelto globalmente ⛔.")
            return True

    # ----------------
    # Buckling
    # ----------------

    @property
    def buckling_limit(self) -> float:
        value = 4.71 * np.sqrt(self.E / self.Fy)
        return value

    @property
    def slenderness_x(self):
        value = self.Kx * self.L / self.rx
        return value

    @property
    def slenderness_y(self):
        value = self.Ky * self.L / self.ry
        return value

    @property
    def euler_buckling_x(self) -> float:
        value = np.pi**2 * self.E / self.slenderness_x**2
        return value

    @property
    def euler_buckling_y(self) -> float:
        value = np.pi**2 * self.E / self.slenderness_y**2
        return value

    @property
    def aisc_buckling_x(self) -> float:
        if self.slenderness_x <= self.buckling_limit:
            Fcr = (0.658 ** (self.Fy / self.euler_buckling_x)) * self.Fy
        else:
            Fcr = 0.877 * self.euler_buckling_x
        return Fcr

    @property
    def aisc_buckling_y(self) -> float:
        if self.slenderness_y <= self.buckling_limit:
            Fcr = (0.658 ** (self.Fy / self.euler_buckling_y)) * self.Fy
        else:
            Fcr = 0.877 * self.euler_buckling_y
        return Fcr

    @property
    def critical_buckling_stress(self) -> float:
        return min(self.aisc_buckling_x, self.aisc_buckling_y)

    @property
    def LRFD_resistent_force(self) -> float:
        phi = 0.90  # compression
        Pu = phi * self.A * self.critical_buckling_stress
        return Pu


if __name__ == "__main__":
    # cargas
    peso_grating = 50  # kg/m2
    peso_barandas = 15  # kg/m
    peso_luminarias = 30  # kg/m2
    peso_sobrecarga = 1000  # kg/m2

    # geometría del arriostre
    longitud_tributaria = 3 / 2  # m (debería ser 4 m en el ejercicio)
    ancho_tributario = 2.5 + 2.5  # m
    longitud_elemento = 3.20  # m
    K_x = 1.35  # pórticos a momento
    K_y = 1.00  # sistema arriostrado

    ### cálculo de cargas

    Distribuida_carga_muerta = peso_luminarias + peso_grating
    Distribuida_carga_viva = peso_sobrecarga

    P_dead = (
        ancho_tributario * longitud_tributaria * Distribuida_carga_muerta
        + peso_barandas * ancho_tributario
    )
    P_live = ancho_tributario * longitud_tributaria * Distribuida_carga_viva
    P_servicio = P_dead + P_live

    combinaciones = CombinacionCarga(D=P_dead, L=P_live)

    ### predimensionamiento

    P_predimensionamiento = P_servicio / 1000  # kg a toneladas
    P_predimensionamiento = P_predimensionamiento * 2.2046226218  # ton to kip
    P_predimensionamiento = P_predimensionamiento * 1.1  # rule of thumb

    # Pa = Ag * (22 - 0.10 K*l/r); en sistema inglés -> in², square inches
    esbeltez_predimensionamiento = 100  # rule of thumb
    Ag_predimensionamiento = P_predimensionamiento / (22 - 0.10 * 100)

    # Ag = Wt / 3.4
    Wt_predimensionamiento = Ag_predimensionamiento * 3.4

    # search for W10 profile on database
    perfil_predimensionamiento = (
        "W10x19"  # should be W10x12 as minimum, but good practice (?) says W10x19
    )
    steel36 = Steel(
        E=29_000,  # ksi
        Fy=36,  # ksi
    )

    W10x19 = WSection(
        name="W10x19",
        A=36.258,  # in²
        d=259.08,
        tw=6.35,
        bf=102.108,
        tf=10.033,
        h=(8 + 3 / 8) * 25.4,  # in → mm
        rx=10.516,
        ry=2.220,
        wt=28.463,
    )

    Column_C1 = WElement(section=W10x19, material=steel36, L=320, Kx=1.35, Ky=1.00)

    Column_C1.check_global_slenderness()
    Column_C1.check_local_slenderness()

    critical_buckling_stress = (
        Column_C1.critical_buckling_stress * 70
    )  # 70 kg/cm² = 1 ksi // ksi -> kg/cm²
    print(f"Critical Buckling stress: {critical_buckling_stress} kg/cm²")

    LRFD_resistent_force = (
        Column_C1.LRFD_resistent_force * 70 / 1000
    )  # 70 kg/cm² = 1 ksi // ksi -> kg/cm²
    print(f"LRFD Ultimate Force (ɸPn): {LRFD_resistent_force}")
    print(f"LRFD Acting Force (Pu) :{combinaciones.envelope_max[1] / 1000}")
    print(
        f"Ratio Demanda/Capacidad (R = D/C) = {combinaciones.envelope_max[1] / (LRFD_resistent_force * 1000)}"
    )
