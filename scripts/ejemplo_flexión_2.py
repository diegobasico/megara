from megara.definiciones import Steel, Element, Section
from megara.secciones import read_wshmp_section

from megara.formulas import moment_beam
from megara.predimensionamiento import peralte_viga, wt_viga

from megara.flexión import FlexedElement
from megara.cortante import ShearedElement
from megara.combinaciones import CombinacionCarga


def ejemplo():
    peso_grating = 45  # kg/m²
    peso_instalaciones = 25
    peso_sobrecarga = 500

    ancho_tributario = 1.20

    largo_viga = 6

    w_dead = peso_grating + peso_instalaciones
    w_live = peso_sobrecarga

    w_dead = w_dead * ancho_tributario
    w_live = w_live * ancho_tributario

    w_servicio = w_dead + w_live

    m_servicio = moment_beam(w_servicio, largo_viga)

    m_servicio = m_servicio / 1000 * 7.233014  # ton-m to kip-ft

    print(m_servicio)

    d_predimensionamiento = peralte_viga(largo_viga / 0.0254)
    print(d_predimensionamiento)

    wt_predimensionamiento = wt_viga(m_servicio, d_predimensionamiento)

    print(wt_predimensionamiento)  # choosing W10x22 just bc (web thickness > 1/4 in)

    material = Steel(29000, 36)
    section = read_wshmp_section("W10x22")
    section = Section(**section)
    element = Element("B-1", material, section, largo_viga * 100 / 2.54)
    Lb = 200 / 2.54 / 12  # 3 arriostres, en inches
    flexed_element = FlexedElement(element, Lb, 1)  # debería ser cb = 1.01 :shrug:
    flexed_element.save_Mn_curve()

    phi_Mn = flexed_element.phi_Mn / 12  # kip-ft

    dead = peso_grating + peso_instalaciones
    live = peso_sobrecarga

    combinacion = CombinacionCarga(D=dead, L=live)
    envolvente = combinacion.envelope_max[1]

    W_u = envolvente * ancho_tributario
    M_u = moment_beam(W_u, largo_viga) / 1000  # ton-m
    M_u = M_u * 7.233014  # ton-m to kip-ft

    R = M_u / phi_Mn

    print(
        f"ɸMn = {phi_Mn}\n",
        f"Mu  = {M_u}\n",
        f"R   = {R}",
    )

    flexed_element.deflection_test(
        dead * ancho_tributario / 1000 * 2.2046226218 / 100 * 2.54,  # kg/m to kip/in
        live * ancho_tributario / 1000 * 2.2046226218 / 100 * 2.54,  # kg/m to kip/in
    )

    sheared_beam = ShearedElement(element=element)

    sheared_beam.show_Vn_curve()
