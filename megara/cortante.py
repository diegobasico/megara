import logging
from enum import Enum
from dataclasses import dataclass
from functools import cached_property

import numpy as np
import matplotlib.pyplot as plt

from .definiciones import Element
from etc.paths import local_paths


logger = logging.getLogger(__name__)


class ShearValueNeeded(ValueError):
    pass


class Slenderness(Enum):
    slender = "slender"
    compact = "compact"
    noncompact = "noncompact"


@dataclass(frozen=True)
class ShearedElement:
    element: Element
    Lb: float
    cb: float

    # ----------------
    # Section geometry
    # ----------------

    def __post_init__(self):
        logger.info(
            f"\n\n:: Applying shear to element {self.element.name}...\n"
            + "-" * 45
            + "\n"
        )

    @cached_property
    def shape(self) -> str:
        if not self.element.section.shape:
            logger.error("Missing shape")
            raise ShearValueNeeded(
                f'Missing parameter "shape" for element {self.element.section.shape}.'
            )
        logger.info(f"shape : {self.element.section.shape}")
        return self.element.section.shape
