#############################################################################
# Copyright (C) 2017 - 2018 VTT Technical Research Centre of Finland
#
# This file is part of Spine Toolbox.
#
# Spine Toolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../spinetoolbox/ui/data_store_form.ui',
# licensing of '../spinetoolbox/ui/data_store_form.ui' applies.
#
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(789, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.splitter_tree_parameter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_tree_parameter.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.splitter_tree_parameter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_tree_parameter.setHandleWidth(6)
        self.splitter_tree_parameter.setObjectName("splitter_tree_parameter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter_tree_parameter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_object_tree = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_object_tree.setFont(font)
        self.label_object_tree.setObjectName("label_object_tree")
        self.verticalLayout_3.addWidget(self.label_object_tree)
        self.treeView_object = ObjectTreeView(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView_object.sizePolicy().hasHeightForWidth())
        self.treeView_object.setSizePolicy(sizePolicy)
        self.treeView_object.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView_object.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self.treeView_object.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.treeView_object.setObjectName("treeView_object")
        self.verticalLayout_3.addWidget(self.treeView_object)
        self.layoutWidget_2 = QtWidgets.QWidget(self.splitter_tree_parameter)
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.splitter = QtWidgets.QSplitter(self.layoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.splitter.setObjectName("splitter")
        self.tabWidget_object = QtWidgets.QTabWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget_object.sizePolicy().hasHeightForWidth())
        self.tabWidget_object.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.tabWidget_object.setFont(font)
        self.tabWidget_object.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tabWidget_object.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget_object.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget_object.setTabBarAutoHide(False)
        self.tabWidget_object.setObjectName("tabWidget_object")
        self.tab_object_parameter_value = QtWidgets.QWidget()
        self.tab_object_parameter_value.setObjectName("tab_object_parameter_value")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_object_parameter_value)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.toolButton_add_object_parameter_values = QtWidgets.QToolButton(self.tab_object_parameter_value)
        self.toolButton_add_object_parameter_values.setIconSize(QtCore.QSize(16, 16))
        self.toolButton_add_object_parameter_values.setObjectName("toolButton_add_object_parameter_values")
        self.verticalLayout_2.addWidget(self.toolButton_add_object_parameter_values)
        self.toolButton_remove_object_parameter_values = QtWidgets.QToolButton(self.tab_object_parameter_value)
        self.toolButton_remove_object_parameter_values.setIconSize(QtCore.QSize(16, 16))
        self.toolButton_remove_object_parameter_values.setObjectName("toolButton_remove_object_parameter_values")
        self.verticalLayout_2.addWidget(self.toolButton_remove_object_parameter_values)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.tableView_object_parameter_value = AutoFilterCopyPasteTableView(self.tab_object_parameter_value)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_object_parameter_value.sizePolicy().hasHeightForWidth())
        self.tableView_object_parameter_value.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.tableView_object_parameter_value.setFont(font)
        self.tableView_object_parameter_value.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_object_parameter_value.setTabKeyNavigation(False)
        self.tableView_object_parameter_value.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableView_object_parameter_value.setSortingEnabled(False)
        self.tableView_object_parameter_value.setWordWrap(False)
        self.tableView_object_parameter_value.setObjectName("tableView_object_parameter_value")
        self.tableView_object_parameter_value.horizontalHeader().setHighlightSections(False)
        self.tableView_object_parameter_value.verticalHeader().setVisible(False)
        self.tableView_object_parameter_value.verticalHeader().setHighlightSections(False)
        self.tableView_object_parameter_value.verticalHeader().setMinimumSectionSize(20)
        self.horizontalLayout.addWidget(self.tableView_object_parameter_value)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/object_parameter_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget_object.addTab(self.tab_object_parameter_value, icon, "")
        self.tab_object_parameter = QtWidgets.QWidget()
        self.tab_object_parameter.setObjectName("tab_object_parameter")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab_object_parameter)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.toolButton_add_object_parameters = QtWidgets.QToolButton(self.tab_object_parameter)
        self.toolButton_add_object_parameters.setObjectName("toolButton_add_object_parameters")
        self.verticalLayout_5.addWidget(self.toolButton_add_object_parameters)
        self.toolButton_remove_object_parameters = QtWidgets.QToolButton(self.tab_object_parameter)
        self.toolButton_remove_object_parameters.setObjectName("toolButton_remove_object_parameters")
        self.verticalLayout_5.addWidget(self.toolButton_remove_object_parameters)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.horizontalLayout_5.addLayout(self.verticalLayout_5)
        self.tableView_object_parameter = AutoFilterCopyPasteTableView(self.tab_object_parameter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_object_parameter.sizePolicy().hasHeightForWidth())
        self.tableView_object_parameter.setSizePolicy(sizePolicy)
        self.tableView_object_parameter.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_object_parameter.setTabKeyNavigation(False)
        self.tableView_object_parameter.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableView_object_parameter.setSortingEnabled(False)
        self.tableView_object_parameter.setWordWrap(False)
        self.tableView_object_parameter.setObjectName("tableView_object_parameter")
        self.tableView_object_parameter.horizontalHeader().setHighlightSections(False)
        self.tableView_object_parameter.horizontalHeader().setSortIndicatorShown(False)
        self.tableView_object_parameter.verticalHeader().setVisible(False)
        self.tableView_object_parameter.verticalHeader().setHighlightSections(False)
        self.horizontalLayout_5.addWidget(self.tableView_object_parameter)
        self.verticalLayout_6.addLayout(self.horizontalLayout_5)
        self.tabWidget_object.addTab(self.tab_object_parameter, "")
        self.tabWidget_relationship = QtWidgets.QTabWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget_relationship.sizePolicy().hasHeightForWidth())
        self.tabWidget_relationship.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.tabWidget_relationship.setFont(font)
        self.tabWidget_relationship.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tabWidget_relationship.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget_relationship.setObjectName("tabWidget_relationship")
        self.tab_relationship_parameter_value = QtWidgets.QWidget()
        self.tab_relationship_parameter_value.setObjectName("tab_relationship_parameter_value")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.tab_relationship_parameter_value)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.toolButton_add_relationship_parameter_values = QtWidgets.QToolButton(self.tab_relationship_parameter_value)
        self.toolButton_add_relationship_parameter_values.setObjectName("toolButton_add_relationship_parameter_values")
        self.verticalLayout.addWidget(self.toolButton_add_relationship_parameter_values)
        self.toolButton_remove_relationship_parameter_values = QtWidgets.QToolButton(self.tab_relationship_parameter_value)
        self.toolButton_remove_relationship_parameter_values.setObjectName("toolButton_remove_relationship_parameter_values")
        self.verticalLayout.addWidget(self.toolButton_remove_relationship_parameter_values)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.tableView_relationship_parameter_value = AutoFilterCopyPasteTableView(self.tab_relationship_parameter_value)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_relationship_parameter_value.sizePolicy().hasHeightForWidth())
        self.tableView_relationship_parameter_value.setSizePolicy(sizePolicy)
        self.tableView_relationship_parameter_value.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_relationship_parameter_value.setTabKeyNavigation(False)
        self.tableView_relationship_parameter_value.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableView_relationship_parameter_value.setSortingEnabled(False)
        self.tableView_relationship_parameter_value.setWordWrap(False)
        self.tableView_relationship_parameter_value.setObjectName("tableView_relationship_parameter_value")
        self.tableView_relationship_parameter_value.horizontalHeader().setHighlightSections(False)
        self.tableView_relationship_parameter_value.verticalHeader().setVisible(False)
        self.tableView_relationship_parameter_value.verticalHeader().setHighlightSections(False)
        self.horizontalLayout_2.addWidget(self.tableView_relationship_parameter_value)
        self.verticalLayout_8.addLayout(self.horizontalLayout_2)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/relationship_parameter_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget_relationship.addTab(self.tab_relationship_parameter_value, icon1, "")
        self.tab_relationship_parameter = QtWidgets.QWidget()
        self.tab_relationship_parameter.setObjectName("tab_relationship_parameter")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.tab_relationship_parameter)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.toolButton_add_relationship_parameters = QtWidgets.QToolButton(self.tab_relationship_parameter)
        self.toolButton_add_relationship_parameters.setObjectName("toolButton_add_relationship_parameters")
        self.verticalLayout_7.addWidget(self.toolButton_add_relationship_parameters)
        self.toolButton_remove_relationship_parameters = QtWidgets.QToolButton(self.tab_relationship_parameter)
        self.toolButton_remove_relationship_parameters.setObjectName("toolButton_remove_relationship_parameters")
        self.verticalLayout_7.addWidget(self.toolButton_remove_relationship_parameters)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem3)
        self.horizontalLayout_3.addLayout(self.verticalLayout_7)
        self.tableView_relationship_parameter = AutoFilterCopyPasteTableView(self.tab_relationship_parameter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_relationship_parameter.sizePolicy().hasHeightForWidth())
        self.tableView_relationship_parameter.setSizePolicy(sizePolicy)
        self.tableView_relationship_parameter.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_relationship_parameter.setTabKeyNavigation(False)
        self.tableView_relationship_parameter.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableView_relationship_parameter.setSortingEnabled(False)
        self.tableView_relationship_parameter.setWordWrap(False)
        self.tableView_relationship_parameter.setObjectName("tableView_relationship_parameter")
        self.tableView_relationship_parameter.horizontalHeader().setHighlightSections(False)
        self.tableView_relationship_parameter.verticalHeader().setVisible(False)
        self.tableView_relationship_parameter.verticalHeader().setHighlightSections(False)
        self.horizontalLayout_3.addWidget(self.tableView_relationship_parameter)
        self.verticalLayout_9.addLayout(self.horizontalLayout_3)
        self.tabWidget_relationship.addTab(self.tab_relationship_parameter, "")
        self.horizontalLayout_6.addWidget(self.splitter)
        self.verticalLayout_10.addWidget(self.splitter_tree_parameter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 789, 27))
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")
        self.menuSession = QtWidgets.QMenu(self.menubar)
        self.menuSession.setObjectName("menuSession")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionCommit = QtWidgets.QAction(MainWindow)
        self.actionCommit.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCommit.setIcon(icon2)
        self.actionCommit.setObjectName("actionCommit")
        self.actionRollback = QtWidgets.QAction(MainWindow)
        self.actionRollback.setEnabled(False)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/nok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRollback.setIcon(icon3)
        self.actionRollback.setObjectName("actionRollback")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionQuit.setIcon(icon4)
        self.actionQuit.setObjectName("actionQuit")
        self.actionAdd_object_classes = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/plus_object_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_object_classes.setIcon(icon5)
        self.actionAdd_object_classes.setObjectName("actionAdd_object_classes")
        self.actionAdd_objects = QtWidgets.QAction(MainWindow)
        self.actionAdd_objects.setIcon(icon5)
        self.actionAdd_objects.setObjectName("actionAdd_objects")
        self.actionAdd_relationship_classes = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/plus_relationship_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_relationship_classes.setIcon(icon6)
        self.actionAdd_relationship_classes.setObjectName("actionAdd_relationship_classes")
        self.actionAdd_relationships = QtWidgets.QAction(MainWindow)
        self.actionAdd_relationships.setIcon(icon6)
        self.actionAdd_relationships.setObjectName("actionAdd_relationships")
        self.actionAdd_parameters = QtWidgets.QAction(MainWindow)
        self.actionAdd_parameters.setObjectName("actionAdd_parameters")
        self.actionAdd_parameter_values = QtWidgets.QAction(MainWindow)
        self.actionAdd_parameter_values.setObjectName("actionAdd_parameter_values")
        self.actionImport = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/import_ds.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionImport.setIcon(icon7)
        self.actionImport.setObjectName("actionImport")
        self.actionExport = QtWidgets.QAction(MainWindow)
        self.actionExport.setEnabled(False)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/export_ds.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExport.setIcon(icon8)
        self.actionExport.setObjectName("actionExport")
        self.actionConnect = QtWidgets.QAction(MainWindow)
        self.actionConnect.setObjectName("actionConnect")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setEnabled(True)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icons/copy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCopy.setIcon(icon9)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setEnabled(True)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/icons/paste.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPaste.setIcon(icon10)
        self.actionPaste.setObjectName("actionPaste")
        self.actionAdd_object_parameters = QtWidgets.QAction(MainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/icons/plus_object_parameter_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_object_parameters.setIcon(icon11)
        self.actionAdd_object_parameters.setObjectName("actionAdd_object_parameters")
        self.actionAdd_object_parameter_values = QtWidgets.QAction(MainWindow)
        self.actionAdd_object_parameter_values.setIcon(icon11)
        self.actionAdd_object_parameter_values.setObjectName("actionAdd_object_parameter_values")
        self.actionRemove_object_parameter_values = QtWidgets.QAction(MainWindow)
        self.actionRemove_object_parameter_values.setEnabled(False)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/icons/minus_object_parameter_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRemove_object_parameter_values.setIcon(icon12)
        self.actionRemove_object_parameter_values.setObjectName("actionRemove_object_parameter_values")
        self.actionAdd_relationship_parameters = QtWidgets.QAction(MainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/icons/plus_relationship_parameter_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_relationship_parameters.setIcon(icon13)
        self.actionAdd_relationship_parameters.setObjectName("actionAdd_relationship_parameters")
        self.actionAdd_relationship_parameter_values = QtWidgets.QAction(MainWindow)
        self.actionAdd_relationship_parameter_values.setIcon(icon13)
        self.actionAdd_relationship_parameter_values.setObjectName("actionAdd_relationship_parameter_values")
        self.actionRemove_relationship_parameter_values = QtWidgets.QAction(MainWindow)
        self.actionRemove_relationship_parameter_values.setEnabled(False)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(":/icons/minus_relationship_parameter_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRemove_relationship_parameter_values.setIcon(icon14)
        self.actionRemove_relationship_parameter_values.setObjectName("actionRemove_relationship_parameter_values")
        self.actionRemove_object_parameters = QtWidgets.QAction(MainWindow)
        self.actionRemove_object_parameters.setEnabled(False)
        self.actionRemove_object_parameters.setIcon(icon12)
        self.actionRemove_object_parameters.setObjectName("actionRemove_object_parameters")
        self.actionRemove_relationship_parameters = QtWidgets.QAction(MainWindow)
        self.actionRemove_relationship_parameters.setEnabled(False)
        self.actionRemove_relationship_parameters.setIcon(icon14)
        self.actionRemove_relationship_parameters.setObjectName("actionRemove_relationship_parameters")
        self.actionRefresh = QtWidgets.QAction(MainWindow)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(":/icons/refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRefresh.setIcon(icon15)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionEdit_object_classes = QtWidgets.QAction(MainWindow)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(":/icons/edit_object_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEdit_object_classes.setIcon(icon16)
        self.actionEdit_object_classes.setObjectName("actionEdit_object_classes")
        self.actionEdit_relationship_classes = QtWidgets.QAction(MainWindow)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(":/icons/edit_relationship_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEdit_relationship_classes.setIcon(icon17)
        self.actionEdit_relationship_classes.setObjectName("actionEdit_relationship_classes")
        self.actionEdit_objects = QtWidgets.QAction(MainWindow)
        self.actionEdit_objects.setIcon(icon16)
        self.actionEdit_objects.setObjectName("actionEdit_objects")
        self.actionEdit_relationships = QtWidgets.QAction(MainWindow)
        self.actionEdit_relationships.setIcon(icon17)
        self.actionEdit_relationships.setObjectName("actionEdit_relationships")
        self.actionRemove_object_tree_items = QtWidgets.QAction(MainWindow)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap(":/icons/minus_object_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRemove_object_tree_items.setIcon(icon18)
        self.actionRemove_object_tree_items.setObjectName("actionRemove_object_tree_items")
        self.menuSession.addAction(self.actionRefresh)
        self.menuSession.addAction(self.actionCommit)
        self.menuSession.addAction(self.actionRollback)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionAdd_object_classes)
        self.menuEdit.addAction(self.actionAdd_objects)
        self.menuEdit.addAction(self.actionAdd_relationship_classes)
        self.menuEdit.addAction(self.actionAdd_relationships)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionAdd_object_parameters)
        self.menuEdit.addAction(self.actionAdd_object_parameter_values)
        self.menuEdit.addAction(self.actionAdd_relationship_parameters)
        self.menuEdit.addAction(self.actionAdd_relationship_parameter_values)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionEdit_object_classes)
        self.menuEdit.addAction(self.actionEdit_objects)
        self.menuEdit.addAction(self.actionEdit_relationship_classes)
        self.menuEdit.addAction(self.actionEdit_relationships)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionRemove_object_tree_items)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionRemove_object_parameters)
        self.menuEdit.addAction(self.actionRemove_object_parameter_values)
        self.menuEdit.addAction(self.actionRemove_relationship_parameters)
        self.menuEdit.addAction(self.actionRemove_relationship_parameter_values)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuSession.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget_object.setCurrentIndex(0)
        self.tabWidget_relationship.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.label_object_tree.setText(QtWidgets.QApplication.translate("MainWindow", "<html><head/><body><p>Object tree</p></body></html>", None, -1))
        self.toolButton_add_object_parameter_values.setText(QtWidgets.QApplication.translate("MainWindow", "...", None, -1))
        self.toolButton_remove_object_parameter_values.setText(QtWidgets.QApplication.translate("MainWindow", "...", None, -1))
        self.toolButton_remove_object_parameter_values.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+S", None, -1))
        self.tabWidget_object.setTabText(self.tabWidget_object.indexOf(self.tab_object_parameter_value), QtWidgets.QApplication.translate("MainWindow", "Object parameter value", None, -1))
        self.toolButton_add_object_parameters.setText(QtWidgets.QApplication.translate("MainWindow", "...", None, -1))
        self.toolButton_remove_object_parameters.setText(QtWidgets.QApplication.translate("MainWindow", "...", None, -1))
        self.tabWidget_object.setTabText(self.tabWidget_object.indexOf(self.tab_object_parameter), QtWidgets.QApplication.translate("MainWindow", "Definition", None, -1))
        self.toolButton_add_relationship_parameter_values.setText(QtWidgets.QApplication.translate("MainWindow", "...", None, -1))
        self.toolButton_remove_relationship_parameter_values.setText(QtWidgets.QApplication.translate("MainWindow", "...", None, -1))
        self.tabWidget_relationship.setTabText(self.tabWidget_relationship.indexOf(self.tab_relationship_parameter_value), QtWidgets.QApplication.translate("MainWindow", "Relationship parameter value", None, -1))
        self.toolButton_add_relationship_parameters.setText(QtWidgets.QApplication.translate("MainWindow", "...", None, -1))
        self.toolButton_remove_relationship_parameters.setText(QtWidgets.QApplication.translate("MainWindow", "...", None, -1))
        self.tabWidget_relationship.setTabText(self.tabWidget_relationship.indexOf(self.tab_relationship_parameter), QtWidgets.QApplication.translate("MainWindow", "Definition", None, -1))
        self.menuSession.setTitle(QtWidgets.QApplication.translate("MainWindow", "Session", None, -1))
        self.menuEdit.setTitle(QtWidgets.QApplication.translate("MainWindow", "Edit", None, -1))
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "File", None, -1))
        self.actionCommit.setText(QtWidgets.QApplication.translate("MainWindow", "Commit", None, -1))
        self.actionCommit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Return", None, -1))
        self.actionRollback.setText(QtWidgets.QApplication.translate("MainWindow", "Rollback", None, -1))
        self.actionRollback.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Backspace", None, -1))
        self.actionQuit.setText(QtWidgets.QApplication.translate("MainWindow", "Close", None, -1))
        self.actionQuit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Esc", None, -1))
        self.actionAdd_object_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Add object classes", None, -1))
        self.actionAdd_object_classes.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add object classes", None, -1))
        self.actionAdd_object_classes.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Shift+O", None, -1))
        self.actionAdd_objects.setText(QtWidgets.QApplication.translate("MainWindow", "Add objects", None, -1))
        self.actionAdd_objects.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add objects", None, -1))
        self.actionAdd_objects.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+O", None, -1))
        self.actionAdd_relationship_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Add relationship classes", None, -1))
        self.actionAdd_relationship_classes.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add relationship classes", None, -1))
        self.actionAdd_relationship_classes.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Shift+R", None, -1))
        self.actionAdd_relationships.setText(QtWidgets.QApplication.translate("MainWindow", "Add relationships", None, -1))
        self.actionAdd_relationships.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add relationships", None, -1))
        self.actionAdd_relationships.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+R", None, -1))
        self.actionAdd_parameters.setText(QtWidgets.QApplication.translate("MainWindow", "Add parameters", None, -1))
        self.actionAdd_parameters.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add parameters", None, -1))
        self.actionAdd_parameters.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Shift+P", None, -1))
        self.actionAdd_parameter_values.setText(QtWidgets.QApplication.translate("MainWindow", "Add parameter values", None, -1))
        self.actionAdd_parameter_values.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add parameter values", None, -1))
        self.actionAdd_parameter_values.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+P", None, -1))
        self.actionImport.setText(QtWidgets.QApplication.translate("MainWindow", "Import", None, -1))
        self.actionImport.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+I", None, -1))
        self.actionExport.setText(QtWidgets.QApplication.translate("MainWindow", "Export", None, -1))
        self.actionExport.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+E", None, -1))
        self.actionConnect.setText(QtWidgets.QApplication.translate("MainWindow", "Connect", None, -1))
        self.actionCopy.setText(QtWidgets.QApplication.translate("MainWindow", "Copy", None, -1))
        self.actionCopy.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+C", None, -1))
        self.actionPaste.setText(QtWidgets.QApplication.translate("MainWindow", "Paste", None, -1))
        self.actionPaste.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+V", None, -1))
        self.actionAdd_object_parameters.setText(QtWidgets.QApplication.translate("MainWindow", "Add object parameter definitions", None, -1))
        self.actionAdd_object_parameter_values.setText(QtWidgets.QApplication.translate("MainWindow", "Add object parameter values", None, -1))
        self.actionRemove_object_parameter_values.setText(QtWidgets.QApplication.translate("MainWindow", "Remove object parameter values", None, -1))
        self.actionAdd_relationship_parameters.setText(QtWidgets.QApplication.translate("MainWindow", "Add relationship parameter definitions", None, -1))
        self.actionAdd_relationship_parameter_values.setText(QtWidgets.QApplication.translate("MainWindow", "Add relationship parameter values", None, -1))
        self.actionRemove_relationship_parameter_values.setText(QtWidgets.QApplication.translate("MainWindow", "Remove relationship parameter values", None, -1))
        self.actionRemove_object_parameters.setText(QtWidgets.QApplication.translate("MainWindow", "Remove object parameter definitions", None, -1))
        self.actionRemove_relationship_parameters.setText(QtWidgets.QApplication.translate("MainWindow", "Remove relationship parameter definitions", None, -1))
        self.actionRefresh.setText(QtWidgets.QApplication.translate("MainWindow", "Refresh", None, -1))
        self.actionRefresh.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Shift+Return", None, -1))
        self.actionEdit_object_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Edit object classes", None, -1))
        self.actionEdit_relationship_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Edit relationship classes", None, -1))
        self.actionEdit_objects.setText(QtWidgets.QApplication.translate("MainWindow", "Edit objects", None, -1))
        self.actionEdit_relationships.setText(QtWidgets.QApplication.translate("MainWindow", "Edit relationships", None, -1))
        self.actionRemove_object_tree_items.setText(QtWidgets.QApplication.translate("MainWindow", "Remove object tree items", None, -1))

from widgets.custom_qtreeview import ObjectTreeView
from widgets.custom_qtableview import AutoFilterCopyPasteTableView
import resources_icons_rc
