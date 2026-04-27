#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QStyle, QComboBox

from PySide6.QtGui import QIcon, QPixmap
from . import rc_icones
from .ui_loader import UiWindow


class FenUser(QMainWindow):
    def __init__(self, config_shared):

        # Déclaration de divers variables
        valideIcon = QIcon(":/icontux/valide.png")
        cancelIcon = QIcon(":/icontux/multiply.png")

        self.config = config_shared

        # Appel du constructeur de la classe mère
        super().__init__()

        # Chargement dynamique de la fenêtre
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'fen_user.ui')

        loader = UiWindow()
        # self.ui devient l'instance de QMainWindow définie dans le XML
        self.ui = loader.load_ui(ui_path)

        # CRUCIAL : On récupère le widget central du fichier .ui
        # pour l'installer dans cette instance de QMainWindow
        self.setCentralWidget(self.ui.centralwidget)

        # On récupère aussi le titre de la fenêtre
        self.setWindowTitle(self.ui.windowTitle())

        # Affectation d'icones
        self.ui.btn_ok.setIcon(valideIcon)
        self.ui.btn_annuler.setIcon(cancelIcon)

        # Création des événements
        self.ui.cbx_desactiveRoot.toggled.connect(self.desactive_root)

    def desactive_root(self, is_checked):
        if is_checked:
            self.ui.edt_rootPasswd = "!"
            self.ui.edt_rootPasswd.setEnabled(False)
            self.ui.cbx_administrateur.setChecked(True)
            self.ui.cbx_administrateur.setEnabled(False)
        else:
            self.ui.edt_rootPasswd = ""
            self.ui.edt_rootPasswd.setEnabled(True)
            self.ui.cbx_administrateur.setChecked(False)
            self.ui.cbx_administrateur.setEnabled(True)




