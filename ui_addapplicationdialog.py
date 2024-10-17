# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'addapplicationdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_AddApplicationDialog(object):
    def setupUi(self, AddApplicationDialog):
        if not AddApplicationDialog.objectName():
            AddApplicationDialog.setObjectName(u"AddApplicationDialog")
        AddApplicationDialog.resize(400, 300)
        self.verticalLayout = QVBoxLayout(AddApplicationDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(AddApplicationDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabApplications = QWidget()
        self.tabApplications.setObjectName(u"tabApplications")
        self.verticalLayout_2 = QVBoxLayout(self.tabApplications)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listApplications = QListWidget(self.tabApplications)
        self.listApplications.setObjectName(u"listApplications")
        self.listApplications.setSelectionMode(QAbstractItemView.MultiSelection)

        self.verticalLayout_2.addWidget(self.listApplications)

        self.tabWidget.addTab(self.tabApplications, "")
        self.tabSystem = QWidget()
        self.tabSystem.setObjectName(u"tabSystem")
        self.verticalLayout_3 = QVBoxLayout(self.tabSystem)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.listSystem = QListWidget(self.tabSystem)
        self.listSystem.setObjectName(u"listSystem")
        self.listSystem.setSelectionMode(QAbstractItemView.MultiSelection)

        self.verticalLayout_3.addWidget(self.listSystem)

        self.tabWidget.addTab(self.tabSystem, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.okButton = QPushButton(AddApplicationDialog)
        self.okButton.setObjectName(u"okButton")

        self.buttonLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton(AddApplicationDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.buttonLayout.addWidget(self.cancelButton)


        self.verticalLayout.addLayout(self.buttonLayout)


        self.retranslateUi(AddApplicationDialog)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AddApplicationDialog)
    # setupUi

    def retranslateUi(self, AddApplicationDialog):
        AddApplicationDialog.setWindowTitle(QCoreApplication.translate("AddApplicationDialog", u"Add Application", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabApplications), QCoreApplication.translate("AddApplicationDialog", u"Applications", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSystem), QCoreApplication.translate("AddApplicationDialog", u"System", None))
        self.okButton.setText(QCoreApplication.translate("AddApplicationDialog", u"OK", None))
        self.cancelButton.setText(QCoreApplication.translate("AddApplicationDialog", u"Cancel", None))
    # retranslateUi

