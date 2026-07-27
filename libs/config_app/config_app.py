import string

from PySide6.QtCore import QSettings, QCoreApplication
import os
import sys
import builtins
from pathlib import Path


class ConfigApp:
    """Gestionnaire de configuration et de paramètres pour application PySide6.

    Cette classe permet de lire et sauvegarder des paramètres applicatifs (types natifs
    et état des fenêtres) via `QSettings`. Elle gère automatiquement la différence
    entre un mode développement (fichier `.ini` local) et un mode production
    (conformité XDG sous Linux / Registre sous Windows).

    Attributes:
        dev_mode (bool): Indique si le mode développement est actif.
        entreprise (str): Nom de l'organisation ou de l'entreprise.
        NomApp (str): Nom de l'application.
        file_path (Path): Chemin absolu vers l'exécutable ou le script principal.
        dir_path (Path): Dossier contenant l'exécutable ou le script principal.
        config (QSettings): Instance de l'objet QSettings configurée.

    Example:
        >>> config = ConfigApp(dev_mode=True, entreprise="Sebastux", NomApp="MonOutil")
        >>> config.SauveString("Serveur", "192.168.1.1", "Reseau")
        >>> ip = config.RecupereString("Reseau", "Serveur", valeur_defaut="127.0.0.1")
    """
    def __init__(self, dev_mode: bool = False, entreprise: str = "SebastuxIntl", NomApp: str = "MonAppli"):
        """Initialise le gestionnaire de configuration.

        Args:
            dev_mode (bool, optional): Active le mode développement. Un fichier
                `config_dev.ini` local sera utilisé. Defaults to False.
            entreprise (str, optional): Nom de l'entreprise/organisation. Defaults to "SebastuxIntl".
            NomApp (str, optional): Nom de l'application. Defaults to "MonAppli".
        """
        # Récupération des valeurs passée en paramètres
        self.dev_mode = dev_mode
        self.entreprise = entreprise
        self.NomApp = NomApp

        # Récupération du répertoire d'exécution du programme ppal.
        self.get_app_paths()

        chemin_fic = os.path.join(self.dir_path, "config_dev.ini")

        if self.dev_mode == True:
            self.config = QSettings(chemin_fic, QSettings.IniFormat)
        else:
            self.config = QSettings(self.entreprise, self.NomApp)

    def get_app_paths(self):
        """Détermine les chemins d'accès du script ou du binaire compilé.

        Détecte automatiquement si le code s'exécute en tant que script Python
        ou sous forme d'exécutable binaire (ex: compilé avec Nuitka).
        Met à jour `self.file_path` et `self.dir_path`.
        """
        # Détection propre de Nuitka (compatible mode main et modules importés)
        is_compiled = hasattr(builtins, '__compiled__') or '__compiled__' in globals()

        if is_compiled:
            # En production (Nuitka) : sys.executable est le binaire compilé
            current_path = Path(sys.executable).resolve()
        else:
            # En développement (Script) : sys.argv[0] est le script principal
            current_path = Path(sys.argv[0]).resolve()

        self.file_path = current_path
        self.dir_path = current_path.parent

    def SauvePosition(self, window: QWidget, group_name: str = "groupe_defaut"):
        """Sauvegarde la géométrie et l'état d'une fenêtre Qt.

        Enregistre la taille et la position pour tous les `QWidget`. Si la fenêtre
        est une `QMainWindow`, enregistre également l'état des barres d'outils et des docks.

        Args:
            window (QWidget): L'instance de la fenêtre à sauvegarder.
            group_name (str, optional): Nom du groupe/section dans la configuration.
                Defaults to "groupe_defaut".
        """
        self.config.beginGroup(group_name)

        # Sauvegarde commune à tous les QWidget (taille, position)
        self.config.setValue("geometry", window.saveGeometry())

        # Sauvegarde spécifique aux QMainWindow (toolbars, dock widgets)
        if isinstance(window, QMainWindow):
            self.config.setValue("state", window.saveState())

        self.config.endGroup()

    def RestaurePosition(self, group_name: str, window: QWidget):
        """Restaure la géométrie et l'état d'une fenêtre Qt si les données existent.

        Args:
            window (QWidget): L'instance de la fenêtre à restaurer.
            group_name (str, optional): Nom du groupe/section dans la configuration.
                Defaults to "groupe_defaut".
        """
        self.config.beginGroup(group_name)

        geometry = self.config.value("geometry")
        if geometry:
            window.restoreGeometry(geometry)

        if isinstance(window, QMainWindow):
            state = self.config.value("state")
            if state:
                window.restoreState(state)

        self.config.endGroup()

    def SauveBool(self, cle:str, valeur: bool = False, group_name: str = "groupe_defaut"):
        """Lit une valeur booléenne depuis la configuration.

        Args:
            group_name (str): La section dans laquelle lire.
            cle (str): La clé de configuration.
            valeur_defaut (bool, optional): Valeur retournée si la clé n'existe pas. Defaults to False.

        Returns:
            bool: La valeur lue ou `valeur_defaut`.
        """
        self.config.beginGroup(group_name)
        self.config.setValue(cle, valeur)
        self.config.endGroup()

    def RecupereBool(self, group_name: str, cle:str) -> bool:
        """Lit une valeur booléenne depuis la configuration.

        Args:
            group_name (str): La section dans laquelle lire.
            cle (str): La clé de configuration.
            valeur_defaut (bool, optional): Valeur retournée si la clé n'existe pas. Defaults to False.

        Returns:
            bool: La valeur lue ou `valeur_defaut`.
        """
        self.config.beginGroup(group_name)
        resultat = self.config.value(cle, defaultValue=False, type=bool)
        self.config.endGroup()
        return resultat

    def SauveString(self, cle:str, valeur: str = "", group_name: str = "groupe_defaut"):
        """
        Sauvegarde une chaine de caractéres. Si la valeur n'est pas fournie, la valeur par défaut est une
        chaine vide.
        group_name est le nom de la section dans laquelle sera sauvegardé le couple clé / valeur.
        Sa valeur par défaut est groupe_defaut.
        """
        self.config.beginGroup(group_name)
        self.config.setValue(cle, valeur)
        self.config.endGroup()

    def RecupereString(self, group_name: str, cle:str) -> str:
        """Lit une chaîne de caractères depuis la configuration.

        Args:
            group_name (str): La section dans laquelle lire.
            cle (str): La clé de configuration.
            valeur_defaut (str, optional): Valeur retournée si la clé n'existe pas. Defaults to "".

        Returns:
            str: La chaîne lue ou `valeur_defaut`.
        """
        self.config.beginGroup(group_name)
        resultat = self.config.value(cle, defaultValue="", type=str)
        self.config.endGroup()
        return resultat

    def Sauveint(self, cle:str, valeur: int = 0, group_name: str = "groupe_defaut"):
        """Sauvegarde un nombre entier.

        Args:
            cle (str): La clé de configuration.
            valeur (int, optional): L'entier à enregistrer. Defaults to 0.
            group_name (str, optional): La section cible. Defaults to "groupe_defaut".
        """
        self.config.beginGroup(group_name)
        self.config.setValue(cle, valeur)
        self.config.endGroup()

    def Recupereint(self, group_name: str, cle:str) -> int:
        """Lit un nombre entier depuis la configuration.

        Args:
            group_name (str): La section dans laquelle lire.
            cle (str): La clé de configuration.
            valeur_defaut (int, optional): Valeur retournée si la clé n'existe pas. Defaults to 0.

        Returns:
            int: L'entier lu ou `valeur_defaut`.
        """
        self.config.beginGroup(group_name)
        resultat = self.config.value(cle, defaultValue=0, type=int)
        self.config.endGroup()
        return resultat

    def Sauvefloat(self, cle:str, valeur: float = 0, group_name: str = "groupe_defaut"):
        """Sauvegarde un nombre réel (float).

        Args:
            cle (str): La clé de configuration.
            valeur (float, optional): Le réel à enregistrer. Defaults to 0.0.
            group_name (str, optional): La section cible. Defaults to "groupe_defaut".
        """
        self.config.beginGroup(group_name)
        self.config.setValue(cle, valeur)
        self.config.endGroup()

    def Recuperefloat(self, group_name: str, cle:str) -> float:
        """Lit un nombre réel (float) depuis la configuration.

        Args:
            group_name (str): La section dans laquelle lire.
            cle (str): La clé de configuration.
            valeur_defaut (float, optional): Valeur retournée si la clé n'existe pas. Defaults to 0.0.

        Returns:
            float: Le réel lu ou `valeur_defaut`.
        """
        self.config.beginGroup(group_name)
        resultat = self.config.value(cle, defaultValue=0, type=float)
        self.config.endGroup()
        return resultat