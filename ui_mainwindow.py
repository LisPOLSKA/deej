# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QHBoxLayout,
    QListWidget, QListWidgetItem, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1100, 573)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_0 = QVBoxLayout()
        self.verticalLayout_0.setObjectName(u"verticalLayout_0")
        self.listSlider0 = QListWidget(self.groupBox)
        self.listSlider0.setObjectName(u"listSlider0")

        self.verticalLayout_0.addWidget(self.listSlider0)

        self.addButton0 = QPushButton(self.groupBox)
        self.addButton0.setObjectName(u"addButton0")

        self.verticalLayout_0.addWidget(self.addButton0)


        self.horizontalLayout.addLayout(self.verticalLayout_0)

        self.verticalLayout_1 = QVBoxLayout()
        self.verticalLayout_1.setObjectName(u"verticalLayout_1")
        self.listSlider1 = QListWidget(self.groupBox)
        self.listSlider1.setObjectName(u"listSlider1")

        self.verticalLayout_1.addWidget(self.listSlider1)

        self.addButton1 = QPushButton(self.groupBox)
        self.addButton1.setObjectName(u"addButton1")

        self.verticalLayout_1.addWidget(self.addButton1)


        self.horizontalLayout.addLayout(self.verticalLayout_1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listSlider2 = QListWidget(self.groupBox)
        self.listSlider2.setObjectName(u"listSlider2")

        self.verticalLayout_2.addWidget(self.listSlider2)

        self.addButton2 = QPushButton(self.groupBox)
        self.addButton2.setObjectName(u"addButton2")

        self.verticalLayout_2.addWidget(self.addButton2)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.listSlider3 = QListWidget(self.groupBox)
        self.listSlider3.setObjectName(u"listSlider3")

        self.verticalLayout_3.addWidget(self.listSlider3)

        self.addButton3 = QPushButton(self.groupBox)
        self.addButton3.setObjectName(u"addButton3")

        self.verticalLayout_3.addWidget(self.addButton3)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.listSlider4 = QListWidget(self.groupBox)
        self.listSlider4.setObjectName(u"listSlider4")

        self.verticalLayout_4.addWidget(self.listSlider4)

        self.addButton4 = QPushButton(self.groupBox)
        self.addButton4.setObjectName(u"addButton4")

        self.verticalLayout_4.addWidget(self.addButton4)


        self.horizontalLayout.addLayout(self.verticalLayout_4)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(21)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(11, 5, 11, 10)
        self.refreshButton = QPushButton(self.centralwidget)
        self.refreshButton.setObjectName(u"refreshButton")

        self.verticalLayout_5.addWidget(self.refreshButton)

        self.invertSliders = QCheckBox(self.centralwidget)
        self.invertSliders.setObjectName(u"invertSliders")

        self.verticalLayout_5.addWidget(self.invertSliders)


        self.verticalLayout.addLayout(self.verticalLayout_5)

        self.horizontalLayout_buttons = QHBoxLayout()
        self.horizontalLayout_buttons.setObjectName(u"horizontalLayout_buttons")
        self.horizontalLayout_buttons.setContentsMargins(11, -1, 11, -1)
        self.loadButton = QPushButton(self.centralwidget)
        self.loadButton.setObjectName(u"loadButton")

        self.horizontalLayout_buttons.addWidget(self.loadButton)

        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setObjectName(u"saveButton")

        self.horizontalLayout_buttons.addWidget(self.saveButton)


        self.verticalLayout.addLayout(self.horizontalLayout_buttons)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1100, 25))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Deej Config Manager", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Slider Mappings", None))
        self.addButton0.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.addButton1.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.addButton2.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.addButton3.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.addButton4.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.refreshButton.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.invertSliders.setText(QCoreApplication.translate("MainWindow", u"Invert Sliders", None))
        self.loadButton.setText(QCoreApplication.translate("MainWindow", u"Load Config", None))
        self.saveButton.setText(QCoreApplication.translate("MainWindow", u"Save Config", None))
    # retranslateUi

