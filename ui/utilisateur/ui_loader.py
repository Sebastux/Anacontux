import os
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


class UiWindow:
    """
    Classe utilitaire pour charger un fichier .ui depuis le répertoire du module courant.
    """

    def load_ui(self, filename):
        # Répertoire du module appelant
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # On remonte d’un cran pour atteindre le package de la fenêtre
        # Exemple : libs/about/about.py → libs/about/
        package_dir = os.path.dirname(base_dir)

        ui_path = os.path.join(package_dir, "UI", filename)

        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"UI file not found: {ui_path}")

        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)

        ui = loader.load(ui_file)
        ui_file.close()

        return ui