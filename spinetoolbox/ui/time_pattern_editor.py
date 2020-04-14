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

# Form implementation generated from reading ui file 'C:\data\src\toolbox\bin\..\spinetoolbox\ui\time_pattern_editor.ui',
# licensing of 'C:\data\src\toolbox\bin\..\spinetoolbox\ui\time_pattern_editor.ui' applies.
#
# Created: Tue Apr 14 12:29:47 2020
#      by: pyside2-uic  running on PySide2 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_TimePatternEditor(object):
    def setupUi(self, TimePatternEditor):
        TimePatternEditor.setObjectName("TimePatternEditor")
        TimePatternEditor.resize(586, 443)
        self.verticalLayout = QtWidgets.QVBoxLayout(TimePatternEditor)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pattern_edit_table = IndexedValueTableView(TimePatternEditor)
        self.pattern_edit_table.setObjectName("pattern_edit_table")
        self.verticalLayout.addWidget(self.pattern_edit_table)

        self.retranslateUi(TimePatternEditor)
        QtCore.QMetaObject.connectSlotsByName(TimePatternEditor)

    def retranslateUi(self, TimePatternEditor):
        TimePatternEditor.setWindowTitle(QtWidgets.QApplication.translate("TimePatternEditor", "Form", None, -1))

from spinetoolbox.widgets.custom_qtableview import IndexedValueTableView
