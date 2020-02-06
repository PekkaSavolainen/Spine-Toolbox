# -*- coding: utf-8 -*-
######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

# Form implementation generated from reading ui file 'C:\data\GIT\SPINETOOLBOX\bin\..\spinetoolbox\project_items\data_store\ui\data_store_properties.ui',
# licensing of 'C:\data\GIT\SPINETOOLBOX\bin\..\spinetoolbox\project_items\data_store\ui\data_store_properties.ui' applies.
#
# Created: Thu Feb  6 17:07:28 2020
#      by: pyside2-uic  running on PySide2 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(415, 382)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_ds_name = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_ds_name.sizePolicy().hasHeightForWidth())
        self.label_ds_name.setSizePolicy(sizePolicy)
        self.label_ds_name.setMinimumSize(QtCore.QSize(0, 20))
        self.label_ds_name.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(50)
        font.setBold(False)
        self.label_ds_name.setFont(font)
        self.label_ds_name.setStyleSheet("background-color: #ecd8c6;")
        self.label_ds_name.setFrameShape(QtWidgets.QFrame.Box)
        self.label_ds_name.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.label_ds_name.setLineWidth(1)
        self.label_ds_name.setScaledContents(False)
        self.label_ds_name.setAlignment(QtCore.Qt.AlignCenter)
        self.label_ds_name.setWordWrap(True)
        self.label_ds_name.setObjectName("label_ds_name")
        self.verticalLayout.addWidget(self.label_ds_name)
        self.scrollArea_5 = QtWidgets.QScrollArea(Form)
        self.scrollArea_5.setWidgetResizable(True)
        self.scrollArea_5.setObjectName("scrollArea_5")
        self.scrollAreaWidgetContents_7 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_7.setGeometry(QtCore.QRect(0, 0, 413, 360))
        self.scrollAreaWidgetContents_7.setObjectName("scrollAreaWidgetContents_7")
        self.verticalLayout_25 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_7)
        self.verticalLayout_25.setObjectName("verticalLayout_25")
        self.groupBox_3 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_7)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_26 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_26.setSpacing(6)
        self.verticalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_26.setObjectName("verticalLayout_26")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_database = QtWidgets.QLabel(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_database.sizePolicy().hasHeightForWidth())
        self.label_database.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_database.setFont(font)
        self.label_database.setObjectName("label_database")
        self.gridLayout_3.addWidget(self.label_database, 5, 0, 1, 1)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.comboBox_dialect = QtWidgets.QComboBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_dialect.sizePolicy().hasHeightForWidth())
        self.comboBox_dialect.setSizePolicy(sizePolicy)
        self.comboBox_dialect.setMinimumSize(QtCore.QSize(0, 24))
        self.comboBox_dialect.setMaximumSize(QtCore.QSize(16777215, 24))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboBox_dialect.setFont(font)
        self.comboBox_dialect.setObjectName("comboBox_dialect")
        self.horizontalLayout_12.addWidget(self.comboBox_dialect)
        self.gridLayout_3.addLayout(self.horizontalLayout_12, 0, 2, 1, 2)
        self.comboBox_dsn = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_dsn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_dsn.sizePolicy().hasHeightForWidth())
        self.comboBox_dsn.setSizePolicy(sizePolicy)
        self.comboBox_dsn.setMinimumSize(QtCore.QSize(0, 24))
        self.comboBox_dsn.setMaximumSize(QtCore.QSize(16777215, 24))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboBox_dsn.setFont(font)
        self.comboBox_dsn.setObjectName("comboBox_dsn")
        self.gridLayout_3.addWidget(self.comboBox_dsn, 1, 2, 1, 2)
        self.horizontalLayout_24 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_24.setSpacing(0)
        self.horizontalLayout_24.setObjectName("horizontalLayout_24")
        self.lineEdit_database = CustomQLineEdit(self.groupBox_3)
        self.lineEdit_database.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_database.sizePolicy().hasHeightForWidth())
        self.lineEdit_database.setSizePolicy(sizePolicy)
        self.lineEdit_database.setMinimumSize(QtCore.QSize(0, 24))
        self.lineEdit_database.setMaximumSize(QtCore.QSize(16777215, 24))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEdit_database.setFont(font)
        self.lineEdit_database.setCursor(QtCore.Qt.IBeamCursor)
        self.lineEdit_database.setPlaceholderText("")
        self.lineEdit_database.setClearButtonEnabled(True)
        self.lineEdit_database.setObjectName("lineEdit_database")
        self.horizontalLayout_24.addWidget(self.lineEdit_database)
        self.toolButton_open_sqlite_file = QtWidgets.QToolButton(self.groupBox_3)
        self.toolButton_open_sqlite_file.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_open_sqlite_file.sizePolicy().hasHeightForWidth())
        self.toolButton_open_sqlite_file.setSizePolicy(sizePolicy)
        self.toolButton_open_sqlite_file.setMinimumSize(QtCore.QSize(22, 22))
        self.toolButton_open_sqlite_file.setMaximumSize(QtCore.QSize(22, 22))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/menu_icons/folder-open-regular.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_open_sqlite_file.setIcon(icon)
        self.toolButton_open_sqlite_file.setObjectName("toolButton_open_sqlite_file")
        self.horizontalLayout_24.addWidget(self.toolButton_open_sqlite_file)
        self.gridLayout_3.addLayout(self.horizontalLayout_24, 5, 2, 1, 2)
        self.label_dialect = QtWidgets.QLabel(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_dialect.sizePolicy().hasHeightForWidth())
        self.label_dialect.setSizePolicy(sizePolicy)
        self.label_dialect.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_dialect.setFont(font)
        self.label_dialect.setObjectName("label_dialect")
        self.gridLayout_3.addWidget(self.label_dialect, 0, 0, 1, 1)
        self.label_dsn = QtWidgets.QLabel(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_dsn.sizePolicy().hasHeightForWidth())
        self.label_dsn.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_dsn.setFont(font)
        self.label_dsn.setObjectName("label_dsn")
        self.gridLayout_3.addWidget(self.label_dsn, 1, 0, 1, 1)
        self.lineEdit_username = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_username.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_username.sizePolicy().hasHeightForWidth())
        self.lineEdit_username.setSizePolicy(sizePolicy)
        self.lineEdit_username.setMinimumSize(QtCore.QSize(0, 24))
        self.lineEdit_username.setMaximumSize(QtCore.QSize(5000, 24))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEdit_username.setFont(font)
        self.lineEdit_username.setPlaceholderText("")
        self.lineEdit_username.setClearButtonEnabled(True)
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.gridLayout_3.addWidget(self.lineEdit_username, 2, 2, 1, 2)
        self.label_username = QtWidgets.QLabel(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_username.sizePolicy().hasHeightForWidth())
        self.label_username.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_username.setFont(font)
        self.label_username.setObjectName("label_username")
        self.gridLayout_3.addWidget(self.label_username, 2, 0, 1, 1)
        self.lineEdit_password = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_password.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_password.sizePolicy().hasHeightForWidth())
        self.lineEdit_password.setSizePolicy(sizePolicy)
        self.lineEdit_password.setMinimumSize(QtCore.QSize(0, 24))
        self.lineEdit_password.setMaximumSize(QtCore.QSize(5000, 24))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEdit_password.setFont(font)
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_password.setPlaceholderText("")
        self.lineEdit_password.setClearButtonEnabled(True)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.gridLayout_3.addWidget(self.lineEdit_password, 3, 2, 1, 2)
        self.horizontalLayout_23 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_23.setObjectName("horizontalLayout_23")
        self.lineEdit_host = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_host.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_host.sizePolicy().hasHeightForWidth())
        self.lineEdit_host.setSizePolicy(sizePolicy)
        self.lineEdit_host.setMinimumSize(QtCore.QSize(0, 24))
        self.lineEdit_host.setMaximumSize(QtCore.QSize(5000, 24))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEdit_host.setFont(font)
        self.lineEdit_host.setPlaceholderText("")
        self.lineEdit_host.setClearButtonEnabled(True)
        self.lineEdit_host.setObjectName("lineEdit_host")
        self.horizontalLayout_23.addWidget(self.lineEdit_host)
        self.label_port = QtWidgets.QLabel(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_port.sizePolicy().hasHeightForWidth())
        self.label_port.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_port.setFont(font)
        self.label_port.setObjectName("label_port")
        self.horizontalLayout_23.addWidget(self.label_port)
        self.lineEdit_port = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_port.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_port.sizePolicy().hasHeightForWidth())
        self.lineEdit_port.setSizePolicy(sizePolicy)
        self.lineEdit_port.setMinimumSize(QtCore.QSize(0, 24))
        self.lineEdit_port.setMaximumSize(QtCore.QSize(80, 24))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEdit_port.setFont(font)
        self.lineEdit_port.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_port.setPlaceholderText("")
        self.lineEdit_port.setObjectName("lineEdit_port")
        self.horizontalLayout_23.addWidget(self.lineEdit_port)
        self.gridLayout_3.addLayout(self.horizontalLayout_23, 4, 2, 1, 2)
        self.label_password = QtWidgets.QLabel(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_password.sizePolicy().hasHeightForWidth())
        self.label_password.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_password.setFont(font)
        self.label_password.setObjectName("label_password")
        self.gridLayout_3.addWidget(self.label_password, 3, 0, 1, 1)
        self.label_host = QtWidgets.QLabel(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_host.sizePolicy().hasHeightForWidth())
        self.label_host.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_host.setFont(font)
        self.label_host.setObjectName("label_host")
        self.gridLayout_3.addWidget(self.label_host, 4, 0, 1, 1)
        self.verticalLayout_26.addLayout(self.gridLayout_3)
        self.verticalLayout_25.addWidget(self.groupBox_3)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_create_new_spine_db = QtWidgets.QPushButton(self.scrollAreaWidgetContents_7)
        self.pushButton_create_new_spine_db.setMinimumSize(QtCore.QSize(85, 23))
        self.pushButton_create_new_spine_db.setMaximumSize(QtCore.QSize(16777215, 23))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/symbols/Spine_symbol.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_create_new_spine_db.setIcon(icon1)
        self.pushButton_create_new_spine_db.setObjectName("pushButton_create_new_spine_db")
        self.gridLayout.addWidget(self.pushButton_create_new_spine_db, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.checkBox_for_spine_model = QtWidgets.QCheckBox(self.scrollAreaWidgetContents_7)
        self.checkBox_for_spine_model.setObjectName("checkBox_for_spine_model")
        self.gridLayout.addWidget(self.checkBox_for_spine_model, 0, 2, 1, 1)
        self.verticalLayout_25.addLayout(self.gridLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_25.addItem(spacerItem1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.pushButton_ds_view = QtWidgets.QPushButton(self.scrollAreaWidgetContents_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_ds_view.sizePolicy().hasHeightForWidth())
        self.pushButton_ds_view.setSizePolicy(sizePolicy)
        self.pushButton_ds_view.setMinimumSize(QtCore.QSize(75, 23))
        self.pushButton_ds_view.setMaximumSize(QtCore.QSize(16777215, 23))
        self.pushButton_ds_view.setObjectName("pushButton_ds_view")
        self.horizontalLayout.addWidget(self.pushButton_ds_view)
        self.verticalLayout_25.addLayout(self.horizontalLayout)
        self.line_8 = QtWidgets.QFrame(self.scrollAreaWidgetContents_7)
        self.line_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.verticalLayout_25.addWidget(self.line_8)
        self.horizontalLayout_27 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_27.setObjectName("horizontalLayout_27")
        self.toolButton_copy_url = QtWidgets.QToolButton(self.scrollAreaWidgetContents_7)
        self.toolButton_copy_url.setMinimumSize(QtCore.QSize(22, 22))
        self.toolButton_copy_url.setMaximumSize(QtCore.QSize(22, 22))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/menu_icons/copy.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_copy_url.setIcon(icon2)
        self.toolButton_copy_url.setObjectName("toolButton_copy_url")
        self.horizontalLayout_27.addWidget(self.toolButton_copy_url)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_27.addItem(spacerItem3)
        self.toolButton_ds_open_dir = QtWidgets.QToolButton(self.scrollAreaWidgetContents_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_ds_open_dir.sizePolicy().hasHeightForWidth())
        self.toolButton_ds_open_dir.setSizePolicy(sizePolicy)
        self.toolButton_ds_open_dir.setMinimumSize(QtCore.QSize(22, 22))
        self.toolButton_ds_open_dir.setMaximumSize(QtCore.QSize(22, 22))
        self.toolButton_ds_open_dir.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/menu_icons/folder-open-solid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_ds_open_dir.setIcon(icon3)
        self.toolButton_ds_open_dir.setObjectName("toolButton_ds_open_dir")
        self.horizontalLayout_27.addWidget(self.toolButton_ds_open_dir)
        self.verticalLayout_25.addLayout(self.horizontalLayout_27)
        self.scrollArea_5.setWidget(self.scrollAreaWidgetContents_7)
        self.verticalLayout.addWidget(self.scrollArea_5)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.label_ds_name.setText(QtWidgets.QApplication.translate("Form", "Name", None, -1))
        self.groupBox_3.setTitle(QtWidgets.QApplication.translate("Form", "URL", None, -1))
        self.label_database.setText(QtWidgets.QApplication.translate("Form", "Database", None, -1))
        self.toolButton_open_sqlite_file.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Open SQLite file.</p></body></html>", None, -1))
        self.label_dialect.setText(QtWidgets.QApplication.translate("Form", "Dialect", None, -1))
        self.label_dsn.setText(QtWidgets.QApplication.translate("Form", "DSN", None, -1))
        self.label_username.setText(QtWidgets.QApplication.translate("Form", "Username", None, -1))
        self.label_port.setText(QtWidgets.QApplication.translate("Form", "Port", None, -1))
        self.label_password.setText(QtWidgets.QApplication.translate("Form", "Password", None, -1))
        self.label_host.setText(QtWidgets.QApplication.translate("Form", "Host", None, -1))
        self.pushButton_create_new_spine_db.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Create new Spine database at the selected URL, or at a default one if the selected is not valid.</p></body></html>", None, -1))
        self.pushButton_create_new_spine_db.setText(QtWidgets.QApplication.translate("Form", "New Spine db", None, -1))
        self.checkBox_for_spine_model.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Add specific data structure for Spine model to the new Spine database.</p></body></html>", None, -1))
        self.checkBox_for_spine_model.setText(QtWidgets.QApplication.translate("Form", "For Spine model", None, -1))
        self.pushButton_ds_view.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Open Data Store view</p></body></html>", None, -1))
        self.pushButton_ds_view.setText(QtWidgets.QApplication.translate("Form", "Open view", None, -1))
        self.toolButton_copy_url.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Copy current database url to clipboard.</p></body></html>", None, -1))
        self.toolButton_copy_url.setText(QtWidgets.QApplication.translate("Form", "...", None, -1))
        self.toolButton_ds_open_dir.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Open this Data Store\'s project directory in file browser</p></body></html>", None, -1))

from spinetoolbox.widgets.custom_qlineedit import CustomQLineEdit
from spinetoolbox import resources_icons_rc
