"""Jerarquía de excepciones del juego."""

from __future__ import annotations


class WizardsCastleError(Exception):
    """Raíz de la jerarquía."""


class DomainError(WizardsCastleError):
    """Violación de regla del dominio."""


class InvalidMoveError(DomainError):
    """Movimiento ilegal o sin sentido."""


class NoStairsError(DomainError):
    """No hay escaleras donde se intenta subir/bajar."""


class BlindError(DomainError):
    """Acción visual intentada por un personaje cegado."""


class InvalidCommandError(DomainError):
    """El comando dado no es uno de los reconocidos."""


class ApplicationError(WizardsCastleError):
    """Error en la capa de aplicación."""


class SaveCorruptedError(ApplicationError):
    """El fichero de save está corrupto o tiene versión incompatible."""


class PresentationError(WizardsCastleError):
    """Error en la capa de presentación."""
