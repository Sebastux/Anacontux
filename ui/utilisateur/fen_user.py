#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QStyle, QComboBox, QMessageBox

from PySide6.QtGui import QIcon, QPixmap
from . import rc_icones
from .ui_loader import UiWindow


class FenUser(QMainWindow):
    def __init__(self, config_shared):

        # Appel du constructeur de la classe mère
        super().__init__()

        # Déclaration de divers variables
        valideIcon = QIcon(":/icontux/valide.png")
        cancelIcon = QIcon(":/icontux/multiply.png")
        self.active_sudo = False

        self.config = config_shared

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
        self.ui.btn_annuler.clicked.connect(self.quitter)
        self.ui.cbx_administrateur.toggled.connect(self.ChangeEtat)
        self.ui.btn_ajouter.clicked.connect(self.ajouter_groupe)
        self.ui.btn_supprimer.clicked.connect(self.supprimer_groupe)
        self.ui.btn_vider.clicked.connect(self.vider_liste_groupes)

    def desactive_root(self, is_checked) -> None:
        if is_checked:
            self.ui.edt_rootPasswd.setText("!")
            self.ui.edt_rootPasswd.setEnabled(False)
            self.ui.cbx_administrateur.setChecked(True)
            self.ui.cbx_administrateur.setEnabled(False)
        else:
            self.ui.edt_rootPasswd.clear()
            self.ui.edt_rootPasswd.setEnabled(True)
            self.ui.cbx_administrateur.setChecked(self.active_sudo)
            self.ui.cbx_administrateur.setEnabled(True)


    def quitter(self) -> None:
        self.close()

    def ChangeEtat(self, is_checked) -> None:
        if self.ui.cbx_administrateur.isEnabled():
            self.active_sudo = is_checked

    def ajouter_groupe(self) -> None:

        # Déclarations de variables internes.
        nom_groupe = self.ui.edt_SaisieGroupe.text().strip().lower()
        login = self.ui.edt_identifiant.text().strip().lower()
        liste_groupe = self.ui.tedt_ListeGroupe.toPlainText()

        # Tests
        if len(nom_groupe) == 0:
            QMessageBox.warning(
                self,
                "Groupe secondaire vide",
                "Vous devez ajouter un groupe secondaire. "
            )
            return

        if nom_groupe == "wheel":
            self.ui.cbx_administrateur.setChecked(True)
            self.ui.edt_SaisieGroupe.clear()
            QMessageBox.information(
                self,
                "Droits d'aministrateur",
                "Pour donner les droits d'administrateur au compte utilisateur, vous devez cocher la case Administrateur."
            )

        if nom_groupe == "sudo":
            self.ui.cbx_administrateur.setChecked(True)
            self.ui.edt_SaisieGroupe.clear()
            QMessageBox.information(
                self,
                "Droits d'aministrateur",
                "Le grouppe sudo n'existe pas dans la branche Red Hat. Veuillez cocher la case administraeur pour ajouter le compte au groupe wheel."
            )

        if nom_groupe == "root":
            self.ui.edt_SaisieGroupe.clear()
            QMessageBox.warning(
                self, "Sécurité",
                "L'ajout au groupe 'root' est bloqué pour respecter les principes de durcissement. "
                "Utilisez la case administrateur à la place."
            )
            return

        if nom_groupe == login:
            self.ui.edt_SaisieGroupe.clear()
            QMessageBox.information(
                self, "Information",
                f"L'utilisateur appartient déjà par défaut à son groupe primaire '{nom_groupe}'.\n"
                "Il est inutile de l'ajouter aux groupes secondaires."
            )
            return

        # Vérification : Caractères autorisés (Regex Linux standard)
        # Autorise : a-z, 0-9, tiret et underscore. Doit commencer par a-z ou _
        if not re.match(r'^[a-z_][a-z0-9_-]*$', nom_groupe):
            QMessageBox.critical(
                self, "Format invalide",
                "Le nom du groupe contient des caractères interdits.\n\n"
                "Utilisez uniquement des minuscules, chiffres, '-' ou '_'. "
                "Il doit commencer par une lettre ou un underscore."
            )
            return

        if nom_groupe in liste_groupe:
            QMessageBox.information(
                self,
                "Doublon dans la liste",
                f" Le groupe {nom_groupe} est déjà présent dans la liste."
            )
            self.ui.edt_SaisieGroupe.clear()
            return

        self.ui.tedt_ListeGroupe.append(nom_groupe)
        self.ui.edt_SaisieGroupe.clear()

    def supprimer_groupe(self) -> None:
        """Supprime la ligne où se trouve le curseur dans le QTextEdit."""
        cursor = self.ui.tedt_ListeGroupe.textCursor()
        if not cursor.hasSelection():
            cursor.select(cursor.LineUnderCursor)

        cursor.removeSelectedText()
        # Nettoyage des lignes vides potentielles après suppression
        texte = self.ui.tedt_ListeGroupe.toPlainText()
        nettoye = "\n".join([l for l in texte.splitlines() if l.strip()])
        self.ui.tedt_ListeGroupe.setPlainText(nettoye)

    def vider_liste_groupes(self) -> None:
        if self.ui.tedt_ListeGroupe.toPlainText().strip():
            rep = QMessageBox.question(self, "Confirmer", "Voulez-vous vider toute la liste ?")
            if rep == QMessageBox.Yes:
                self.ui.tedt_ListeGroupe.clear()