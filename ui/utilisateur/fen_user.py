#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QStyle, QComboBox, QMessageBox

from PySide6.QtGui import QIcon, QPixmap, QTextCursor
from . import rc_icones
from .ui_loader import UiWindow


class FenUser(QMainWindow):
    def __init__(self, config_shared):

        # Appel du constructeur de la classe mère
        super().__init__()

        # Déclaration de divers variables
        valideIcon = QIcon(":/icontux/valide.png")
        cancelIcon = QIcon(":/icontux/multiply.png")
        adddIcon = QIcon(":/icontux/new_file.png")
        suppressIcon = QIcon(":/icontux/supprimer.png")
        emptyIcon = QIcon(":/icontux/balayer.png")
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
        self.ui.btn_supprimer.setIcon(suppressIcon)
        self.ui.btn_ajouter.setIcon(adddIcon)
        self.ui.btn_vider.setIcon(emptyIcon)

        # Création des événements
        self.ui.cbx_desactiveRoot.toggled.connect(self.desactive_root)
        self.ui.btn_annuler.clicked.connect(self.quitter)
        self.ui.cbx_administrateur.toggled.connect(self.ChangeEtat)
        self.ui.btn_ajouter.clicked.connect(self.ajouter_groupe)
        self.ui.btn_supprimer.clicked.connect(self.supprimer_groupe)
        self.ui.btn_vider.clicked.connect(self.vider_liste_groupes)
        self.ui.btn_ok.clicked.connect(self.validation)
        self.ui.edt_identifiant.textChanged.connect(self.repliquer_identifiant)

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

        if nom_groupe in ["wheel", "sudo"]:
            self.ui.cbx_administrateur.setChecked(True)
            self.active_sudo = True  # <--- On mémorise l'état pour le retour du mode root
            self.ui.edt_SaisieGroupe.clear()
            if nom_groupe == "wheel":
                QMessageBox.information(
                    self, "Information",
                    "Pour donner les droits administrateur à l'utilisateur, vous \n"
                    "devez cocher la case administrateur."
                )
            else:
                 QMessageBox.warning(
                self, "Erreur",
                "Le groupe sudo n'existe pas dans la branche Red Hat. Vous devez \n "
                "soit ajouter le groupe wheel soit cocher la case administrateur."
            )

            return

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
        # On récupère le curseur actuel du widget
        cursor = self.ui.tedt_ListeGroupe.textCursor()

        # On vérifie s'il n'y a pas déjà une sélection
        if not cursor.hasSelection():
            # ICI : On utilise la classe QTextCursor pour accéder à la constante
            cursor.select(QTextCursor.LineUnderCursor)

        # On supprime la sélection
        cursor.removeSelectedText()

        # Nettoyage pour éviter les sauts de ligne orphelins
        texte = self.ui.tedt_ListeGroupe.toPlainText()
        nettoye = "\n".join([l for l in texte.splitlines() if l.strip()])
        self.ui.tedt_ListeGroupe.setPlainText(nettoye)

    def vider_liste_groupes(self) -> None:
        if self.ui.tedt_ListeGroupe.toPlainText().strip():
            rep = QMessageBox.question(self, "Confirmer", "Voulez-vous vider toute la liste ?")
            if rep == QMessageBox.Yes:
                self.ui.tedt_ListeGroupe.clear()


    def show_fenuser(self) -> None:
        self.setup_window()
        self.show()

    def setup_window(self) -> None:
        # Ajuste la fenêtre à la taille idéale calculée par les layouts du .ui
        self.adjustSize()

        self.setFixedSize(self.sizeHint())

        # Centrage de la fenêtre
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def repliquer_identifiant(self, texte: str) -> None:
        """Recopie l'identifiant dans l'étiquette (GECOS)."""
        # On met à jour l'étiquette uniquement si elle est vide ou
        # si elle contient déjà une version précédente de l'identifiant.
        self.ui.edt_etiquette.setText(texte)

    def validation(self) -> None:
        # Récupération des valeurs saisie
        root_passwd = self.ui.edt_rootPasswd.strip()
        login = self.ui.edt_identifiant.text().strip().lower()
        etiquette = self.ui.edt_etiquette.text().strip()
        user_password = self.ui.edt_UserPasswd.text().strip()
        nom_groupe = self.ui.edt_SaisieGroupe.text().strip().lower()

        # Export des valeurs dans la dataclass
        self.config.root_pw_crypted = root_passwd
        self.config.user_name = login
        self.config.user_gecos = etiquette
        self.config.user_pw_crypted = user_password
        self.config.user_groups = nom_groupe
        self.close()