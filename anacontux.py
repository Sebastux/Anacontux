#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Instructions de compilations pour Nuitka
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

import sys
import logging
import os
from PySide6.QtWidgets import QApplication
from datetime import datetime

from ui import utilisateur
# Import des module perso
from ui.kick_config.kick_config import KickstartConfig

# Import de la Fenêtre Principale
from ui.ppale.fen_ppale import FenPpale

# Import de la fenetre utillisateur.
from ui.utilisateur.fen_user import FenUser


def main():
# Création d'objets
    fic_log = logging.getLogger(__name__)
    now_str = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")


# Configuration du fichier de log
    nom_fichier = f"logtux_{now_str}.log"
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    chemin = os.path.join(log_dir, nom_fichier)

# Configuration du fichier de log
    logging.basicConfig(
        filename=chemin,
        encoding='utf-8',
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%d-%m-%Y %H:%M"
    )


    fic_log = logging.getLogger(__name__)

# Initialisation de la data class
    kick_fic = KickstartConfig()

    fic_log.info("Démarrage de l'application.")
    fic_log.debug("Création de l'application.")
    app = QApplication(sys.argv)

    fic_log.debug("Création de la fenêtre principale.")
    # principale = FenPpale(kick_fic)

    fic_log.debug("Affichage de la fenêtre principale.")
    # principale.show()

    fic_log.debug("Création de la fenêtre utilisateur.")
    utilisateur = FenUser(kick_fic)

    fic_log.debug("Affichage de la fenêtre utilisateur.")
    utilisateur.show()

    # On lance la boucle d'événements et on stocke le code de retour
    exit_code = app.exec()

    # Maintenant que la fenêtre est fermée, le print fonctionnera !
    fic_log.debug(f"Configuration Distribution : {kick_fic.distribution}")
    fic_log.debug(f"Configuration Langue : {kick_fic.langue}")
    fic_log.debug(f"Configuration Clavier : {kick_fic.clavier}")
    fic_log.debug(f"Configuration Fuseau horaire : {kick_fic.timezone}")

    # On quitte proprement avec le code de retour
    fic_log.debug("Fermeture de l'application.")
    fic_log.info("Fermeture de l'application.")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
