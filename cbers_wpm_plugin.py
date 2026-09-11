# -*- coding: utf-8 -*-
# Created by Miguel Alexandre da Cunha; Guilherme Gomes Correia
import os

from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar

from .cbers_wpm_dialog import CbersWpmDialog

PLUGIN_DIR = os.path.abspath(os.path.dirname(__file__))

class CbersWpmPlugin:
    """Ponto de entrada do plugin, exigido pelo QGIS (classFactory)."""

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        icon_path = os.path.join(PLUGIN_DIR, "icons", "icon.png")
        self.action = QAction(
            QIcon(icon_path),
            "WPM 1-meter spatial resolution",
            self.iface.mainWindow()
        )
        self.action.setWhatsThis("Gera imagens RGB de alta resolução espacial")
        self.action.setStatusTip("Abrir o WPM 1-meter spatial resolution")
        self.action.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&WPM 1-meter spatial resolution", self.action)

        for toolbar in self.iface.mainWindow().findChildren(QToolBar):
            button = toolbar.widgetForAction(self.action)
            if button is not None:
                button.setIconSize(QSize(40, 40))
                break

    def unload(self):
        self.iface.removePluginMenu(
            "&WPM 1-meter spatial resolution",
            self.action
        )
        self.iface.removeToolBarIcon(self.action)
        self.action = None
        self.dialog = None

    def run(self):
        if self.dialog is None:
            self.dialog = CbersWpmDialog(self.iface, self.iface.mainWindow())
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
