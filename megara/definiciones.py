import logging
from dataclasses import dataclass
from typing import Optional


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
    # ----------------
    # Required (all)
    # ----------------
    shape: str
    a: float
    j: float

    # ----------------
    # Common (optional)
    # ----------------
    d: Optional[float] = None
    k: Optional[float] = None

    ix: Optional[float] = None
    sx: Optional[float] = None
    rx: Optional[float] = None

    iy: Optional[float] = None
    sy: Optional[float] = None
    ry: Optional[float] = None

    cw: Optional[float] = None

    tw: Optional[float] = None
    bf: Optional[float] = None
    tf: Optional[float] = None
    t: Optional[float] = None

    d_af: Optional[float] = None
    gage: Optional[float] = None

    ro_bar: Optional[float] = None
    h: Optional[float] = None

    b: Optional[float] = None
    wt_ft: Optional[float] = None

    zx: Optional[float] = None
    zy: Optional[float] = None

    # ----------------
    # WSMHP only
    # ----------------
    k1: Optional[float] = None
    bf_2tf: Optional[float] = None
    fy: Optional[float] = None
    d_tw: Optional[float] = None
    rt: Optional[float] = None
    wno: Optional[float] = None
    sw: Optional[float] = None
    qf: Optional[float] = None
    qw: Optional[float] = None

    # ----------------
    # CMC only
    # ----------------
    x_bar: Optional[float] = None
    eo: Optional[float] = None

    # ----------------
    # Angles only
    # ----------------
    x: Optional[float] = None
    rz: Optional[float] = None
    tan_a: Optional[float] = None

    # ----------------
    # Two angles only
    # ----------------
    y: Optional[float] = None
    ry_0: Optional[float] = None
    ry_3_8: Optional[float] = None
    ry_3_4: Optional[float] = None
    qs: Optional[float] = None

    # ----------------
    # Pipes only
    # ----------------
    o_d: Optional[float] = None
    i_d: Optional[float] = None
    o_d_t: Optional[float] = None
    i: Optional[float] = None
    s: Optional[float] = None
    r: Optional[float] = None
    z: Optional[float] = None
    c: Optional[float] = None


@dataclass
class Element:
    name: str
    material: Steel
    section: Section
    L: float
    Kx: Optional[float] = None
    Ky: Optional[float] = None
