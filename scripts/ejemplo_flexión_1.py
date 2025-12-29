from megara.flexión import FlexedElement
from megara.definiciones import Steel, Element, Section
from megara.secciones import read_wshmp_section


def ejemplo():
    peso_ventiladores = 285  # kg/m²
    peso_grating = 45  # kg/m²
    sobrecarga_plataforma = 500  # kg/m²

    largo_viga = 5  # metros

    ancho_tributario = 1.2  # metros

    dead_distribuida = (peso_ventiladores + peso_grating) * ancho_tributario
    live_distribuida = sobrecarga_plataforma * ancho_tributario

    carga_servicio_distribuida = dead_distribuida + live_distribuida

    momento_servicio = (
        carga_servicio_distribuida * largo_viga**2 / 8
    )  # simplemente apoyada

    momento_servicio = momento_servicio * 7.20 / 1000  # ton-m -> kip-ft

    ### predimensionamiento

    peralte_predimensionado = largo_viga / 25  # rule of thumb

    # resulta 20 cm -> W8, pero se toma W10
    # para evitar la falla por deflexión posteriormente
    # (dato por experiencia del docente)

    peralte_predimensionado = 10  # pulgadas -> W10

    Wt_predimensionado = (
        5 * momento_servicio / peralte_predimensionado
    )  # rule of thumb for Fy = 36 ksi -> Beam Wt = 5 * M / d in lb/ft

    Ag_predimensionada = Wt_predimensionado / 3.4  # rule of thumb, should be 3.52 aprox

    # we be choosing 22 just bc (i would have chosen 19, just sayin)

    section_data = read_wshmp_section("W10x22")

    steel36 = Steel(E=29_000, Fy=36)

    W10x22 = Section(**section_data)

    Beam_V1 = Element(
        name="V1", section=W10x22, material=steel36, L=largo_viga * 100 / 2.54
    )

    Lb = largo_viga * 100 / 2.54 / 3  # 3 espacios entre arriostres  -> x---x---x---x

    cb = 1.01

    flexedBeamV1 = FlexedElement(element=Beam_V1, Lb=Lb, cb=cb)

    flexedBeamV1.show_Mn_curve()
    flexedBeamV1.save_Mn_curve()
