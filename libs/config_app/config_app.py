from PySide6.QtCore import QSettings, QCoreApplication
import os
import sys
from pathlib import Path


class ConfigApp:
    def __init__(self, dev_mode: bool = False, entreprise: str = "SebastuxIntl", NomApp: str = "MonAppli"):
        # Récupération des valeurs passée en paramètres
        self.dev_mode = dev_mode
        self.entreprise = entreprise
        self.NomApp = NomApp

        # récuparation du répertoire d'éxécution du programme ppal.
        self.get_app_paths()

        chemin_fic = os.path.join(self.dir_path, "config_dev.ini")

        if self.dev_mode == True:
            self.config = QSettings(chemin_fic, QSettings.IniFormat)
        else:
            self.config = QSettings(self.entreprise, self.NomApp)


    def get_app_paths():
        """
        Retourne le chemin absolu de l'exécutable/script
        et le dossier qui le contient.
        """
        # Détection si le code tourne sous Nuitka
        is_compiled = '__compiled__' in globals() or '__compiled__' in __builtins__.__dict__

        if is_compiled:
            # En production (Nuitka) : sys.executable est le binaire compilé
            current_path = Path(sys.executable).resolve()
        else:
            # En développement (Script) : sys.argv[0] est le script principal
            current_path = Path(sys.argv[0]).resolve()

        self.file_path = current_path  # /chemin/vers/mon_app ou mon_app.py
        self.dir_path = current_path.parent  # /chemin/vers/ (le dossier contenant)

    def SauvePosition(self, group_name: str, window: QWidget):
        """
        Sauvegarde la géométrie (et l'état si QMainWindow) de n'importe quelle fenêtre.
        group_name: Le nom de la section dans le fichier INI (ex: 'MainWindow', 'SettingsDialog')
        """
        self.config.beginGroup(group_name)

        # Sauvegarde commune à tous les QWidget (taille, position)
        self.config.setValue("geometry", window.saveGeometry())

        # Sauvegarde spécifique aux QMainWindow (toolbars, dock widgets)
        if isinstance(window, QMainWindow):
            self.config.setValue("state", window.saveState())

        self.config.endGroup()

    def RestaurePosition(self, group_name: str, window: QWidget):
        """Restaure la géométrie et l'état d'une fenêtre si les données existent."""
        self.config.beginGroup(group_name)

        geometry = self.config.value("geometry")
        if geometry:
            window.restoreGeometry(geometry)

        if isinstance(window, QMainWindow):
            state = self.config.value("state")
            if state:
                window.restoreState(state)

        self.config.endGroup()

    def SauveBool(self, group_name: str = "groupe_defaut", cle:str, valeur: bool = False):
        """
        Sauvegarde des valeurs booléennes. Si la valeur n'est pas fournie, la valeur par défaut est False.
        group_name est le nom de la section dans laquelle sera sauvegardé le couple clé / valeur
        """
        self.config.beginGroup(group_name)
        self.config.setValue(cle, valeur)
        self.config.endGroup()

    def RecupereBool(self, group_name: str = "groupe_defaut", cle:str) -> bool:
        """
        Lit des valeurs booléennes. Si la valeur est absente ou incorrecte, la valeur par défaut est false.
        group_name est le nom de la section dans laquelle sera lu le couple clé / valeur
        """


