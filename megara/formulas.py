def moment_beam(W: float, L: float):
    """
    Momento por metro lineal en una viga simplemente apoyada:
        - W: Peso distribuido (force/length)
        - L: Largo de la viga"""
    return W * L**2 / 8
