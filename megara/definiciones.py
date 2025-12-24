import logging
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


@dataclass
class Steel:
    E: float
    Fy: float


@dataclass
class Section:
    name: str
    A: float  # cm²
    tw: float  # mm
    bf: float  # mm
    tf: float  # mm
    h: float  # mm  (clear web height)
    rx: float  # cm
    ry: float  # cm


_section = TypeVar("_section", bound=Section)


@dataclass
class WSection(Section):
    # ---------
    # Geometry
    # ---------

    d: float  # mm
    wt: float  # kg/m


@dataclass
class Element(Generic[_section]):
    material: Steel
    section: _section
    L: float
    Kx: Optional[float] = None
    Ky: Optional[float] = None

    @property
    def A(self):
        return self.section.A

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
    def Fy(self):
        return self.material.Fy

    @property
    def E(self):
        return self.material.E


@dataclass
class WElement(Element):
    section: WSection

    @property
    def d(self):
        return self.section.d

    @property
    def wt(self):
        return self.section.wt
