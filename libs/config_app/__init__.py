"""
ConfigApp - Module de gestion de configuration pour applications PySide6.

Ce package fournit un gestionnaire QSettings prêt à l'emploi avec support
du mode développement et détection du mode exécutable (Nuitka).
"""

from .config_app import ConfigApp

__version__ = "1.0.0"
__author__ = "Sébastux"

__all__ = [
    "ConfigApp",
]