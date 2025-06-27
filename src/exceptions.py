class LivreIndisponibleError(Exception):
    """Levée quand on tente d'emprunter un livre indisponible."""
    def __init__(self, message="Le livre n'est pas disponible."):
        super().__init__(message)

class QuotaEmpruntDepasseError(Exception):
    """Levée quand un membre atteint son quota d'emprunts."""
    def __init__(self, message="Le quota d'emprunts a été dépassé."):
        super().__init__(message)

class MembreInexistantError(Exception):
    """Levée quand on référence un membre qui n'existe pas."""
    def __init__(self, message="Le membre n'existe pas."):
        super().__init__(message)

class LivreInexistantError(Exception):
    """Levée quand on référence un livre qui n'existe pas."""
    def __init__(self, message="Le livre n'existe pas."):
        super().__init__(message)

