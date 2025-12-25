from megara.compresión import ultimate_compression_force
from megara.definiciones import Steel, Element, Section
from megara.combinaciones import CombinacionCarga
from megara.secciones import read_wshmp_section


def ejemplo():
    # cargas
    peso_grating = 50  # kg/m2
    peso_barandas = 15  # kg/m
    peso_luminarias = 30  # kg/m2
    peso_sobrecarga = 1000  # kg/m2

    # geometría del arriostre
    longitud_tributaria = 3 / 2  # m (debería ser 4 m en el ejercicio)
    ancho_tributario = 2.5 + 2.5  # m

    ### cálculo de cargas

    Distribuida_carga_muerta = peso_luminarias + peso_grating
    Distribuida_carga_viva = peso_sobrecarga

    P_dead = (
        ancho_tributario * longitud_tributaria * Distribuida_carga_muerta
        + peso_barandas * ancho_tributario
    )
    P_live = ancho_tributario * longitud_tributaria * Distribuida_carga_viva
    P_servicio = P_dead + P_live

    ### predimensionamiento

    P_predimensionamiento = P_servicio / 1000  # kg a toneladas
    P_predimensionamiento = P_predimensionamiento * 2.20462262185  # ton to kip
    P_predimensionamiento = P_predimensionamiento * 1.1  # rule of thumb

    # Pa = Ag * (22 - 0.10 K*l/r); en sistema inglés -> in², square inches
    #
    # esbeltez_predimensionamiento = 100  # rule of thumb
    #
    # Ag_predimensionamiento = P_predimensionamiento / (
    #     22 - 0.10 * esbeltez_predimensionamiento
    # )
    #
    # Ag = Wt / 3.4 -> Wt_predimensionamiento = Ag_predimensionamiento * 3.4
    #
    # search for W10 profile on database
    #
    # choosing W10x19 -> should be W10x12 as minimum, but good practice (?) says W10x19

    steel36 = Steel(
        E=29_000,  # ksi
        Fy=36,  # ksi
    )

    section_data = read_wshmp_section("W10x19")
    W10x19 = Section(**section_data)  # everything in inches

    Column_C1 = Element(
        section=W10x19, material=steel36, L=320 / 2.54, Kx=1.35, Ky=1.00
    )

    Pu = ultimate_compression_force(Column_C1) * 1000 / 2.20462262185  # kip to kg

    print(f"LRFD ultimate force (Pu): {Pu} kg")  # already in kg

    combinaciones = CombinacionCarga(D=P_dead, L=P_live)

    P = combinaciones.envelope_max[1]  # already in kg

    print(f"LRFD acting force (P) :{P} kg")
    print(f"Ratio Demanda/Capacidad (R = D/C) = {P / Pu}")
