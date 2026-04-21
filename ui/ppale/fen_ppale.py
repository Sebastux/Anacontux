#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QStyle, QComboBox
from .ui_loader import UiWindow

from PySide6.QtGui import QIcon, QPixmap
from . import rc_icones

# Instructions de compilations pour Nuitka
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

class FenPpale(QMainWindow):
    def __init__(self, config_shared):

        # Déclaration de divers variables
        valideIcon = QIcon(":/icontux/valide.png")
        cancelIcon = QIcon(":/icontux/multiply.png")

        self.config = config_shared

        # Appel du constructeur de la classe mère
        super().__init__()

        # Chargement dynamique de la fenêtre
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'ppale.ui')

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
        self.ui.btn_ok.clicked.connect(self.valider_et_continuer)
        self.ui.btn_annuler.clicked.connect(self.quitter)
        self.ui.cbx_langue.currentIndexChanged.connect(self.verifier_formulaire)
        self.ui.cbx_fuseau.currentIndexChanged.connect(self.verifier_formulaire)
        self.ui.cbx_distribution.currentIndexChanged.connect(self.verifier_formulaire)
        self.ui.cbx_clavier.currentIndexChanged.connect(self.verifier_formulaire)


        # On désactive le bouton au départ
        self.ui.btn_ok.setEnabled(False)

        # Chargement des fichiers de configuration pour les ComboBox
        self.charger_donnees_dans_cbx("OsLangue.txt",self.ui.cbx_langue)
        self.charger_donnees_dans_cbx("Timezones.txt", self.ui.cbx_fuseau)
        self.charger_donnees_dans_cbx("Distributions.txt", self.ui.cbx_distribution)
        self.charger_donnees_dans_cbx("Claviers.txt", self.ui.cbx_clavier)

    def show_ppale(self) -> None:
        self.setup_window()
        self.show()

    def setup_window(self) -> None:
        # Ajuste la fenêtre à la taille idéale calculée par les layouts du .ui
        self.adjustSize()

        # self.setFixedSize(self.sizeHint())

        # Centrage de la fenêtre
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def quitter(self) -> None:
        self.close()


    def charger_donnees_dans_cbx(self, nom_fichier: str, combo_widget: QComboBox) -> bool:
        combo_widget.clear()
        # On ajoute la valeur par défaut "bloquante"
        combo_widget.addItem("--- Inconnu ---")

        try:
            chemin = os.path.join(os.path.dirname(__file__), "datas", nom_fichier)
            with open(chemin, "r", encoding="utf-8") as f:
                for ligne in f:
                    item = ligne.strip()
                    if item:
                        combo_widget.addItem(item)
            return True
        except Exception:
            # En cas d'erreur, on remplace "Inconnu" par un message d'erreur
            combo_widget.clear()
            combo_widget.addItem(f"ERREUR : {nom_fichier}")
            return False

    def verifier_formulaire(self):
        # L'index 0 correspond à "--- Inconnu ---"
        langue_ok = self.ui.cbx_langue.currentIndex() > 0
        timezone_ok = self.ui.cbx_fuseau.currentIndex() > 0
        distrib_ok = self.ui.cbx_distribution.currentIndex() > 0
        clavier_ok = self.ui.cbx_clavier.currentIndex() > 0

        # Le bouton OK n'est cliquable que si les 4 conditions sont vraies
        self.ui.btn_ok.setEnabled(langue_ok and timezone_ok and distrib_ok and clavier_ok)

    def valider_et_continuer(self):
        # On remplit la dataclass avec les textes sélectionnés
        self.config.langue = self.ui.cbx_langue.currentText()
        self.config.timezone = self.ui.cbx_fuseau.currentText()
        self.config.distribution = self.ui.cbx_distribution.currentText()
        self.config.clavier = self.ui.cbx_clavier.currentText()

        self.close()
