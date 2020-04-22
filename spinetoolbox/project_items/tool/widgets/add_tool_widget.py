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

"""
Widget shown to user when a new Tool is created.

:author: P. Savolainen (VTT)
:date:   19.1.2017
"""

from PySide2.QtWidgets import QWidget, QStatusBar
from PySide2.QtCore import Slot, Qt
from spinetoolbox.config import STATUSBAR_SS, INVALID_CHARS
from ..tool import Tool


class AddToolWidget(QWidget):
    """A widget that queries user's preferences for a new item.

    Attributes:
        toolbox (ToolboxUI): Parent widget
        x (int): X coordinate of new item
        y (int): Y coordinate of new item
    """

    def __init__(self, toolbox, x, y):
        """Initialize class."""
        from ..ui.add_tool import Ui_Form

        super().__init__(parent=toolbox, f=Qt.Window)  # Setting parent inherits stylesheet
        self._toolbox = toolbox
        self._x = x
        self._y = y
        self._project = self._toolbox.project()
        #  Set up the user interface from Designer.
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # Add status bar to form
        self.statusbar = QStatusBar(self)
        self.statusbar.setFixedHeight(20)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setStyleSheet(STATUSBAR_SS)
        self.ui.horizontalLayout_statusbar_placeholder.addWidget(self.statusbar)
        # Class attributes
        self.name = toolbox.propose_item_name(Tool.default_name_prefix())
        self.ui.lineEdit_name.setText(self.name)
        self.ui.lineEdit_name.selectAll()
        self.description = ''
        # Init
        self.ui.comboBox_specification.setModel(self._toolbox.tool_specification_model)
        self.ui.lineEdit_name.setFocus()
        self.connect_signals()
        # Ensure this window gets garbage-collected when closed
        self.setAttribute(Qt.WA_DeleteOnClose)

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.lineEdit_name.textChanged.connect(self.name_changed)  # Name -> folder name connection
        self.ui.pushButton_ok.clicked.connect(self.ok_clicked)
        self.ui.pushButton_cancel.clicked.connect(self.close)
        self.ui.comboBox_specification.currentIndexChanged.connect(self.update_args)

    @Slot(int, name='update_args')
    def update_args(self, row):
        """Show Tool specification command line arguments in text input.

        Args:
            row (int): Selected row number
        """
        if row == 0:
            # No Tool selected
            self.ui.lineEdit_tool_specification_args.setText("")
            return
        selected_tool = self._toolbox.tool_specification_model.tool_specification(row)
        args = selected_tool.cmdline_args
        if not args:
            # Tool cmdline_args is None if the line does not exist in Tool definition file
            args = ''
        self.ui.lineEdit_tool_specification_args.setText("{0}".format(args))
        return

    @Slot(name='name_changed')
    def name_changed(self):
        """Update label to show upcoming folder name."""
        name = self.ui.lineEdit_name.text()
        default = "Folder:"
        if name == '':
            self.ui.label_folder.setText(default)
        else:
            folder_name = name.lower().replace(' ', '_')
            msg = default + " " + folder_name
            self.ui.label_folder.setText(msg)

    @Slot(name='ok_clicked')
    def ok_clicked(self):
        """Check that given item name is valid and add it to project."""
        self.name = self.ui.lineEdit_name.text()
        self.description = self.ui.lineEdit_description.text()
        if not self.name:  # No name given
            self.statusbar.showMessage("Name missing", 3000)
            return
        # Check for invalid characters for a folder name
        if any((True for x in self.name if x in INVALID_CHARS)):
            self.statusbar.showMessage("Name not valid for a folder name", 3000)
            return
        # Check that name is not reserved
        if self._toolbox.project_item_model.find_item(self.name):
            msg = "Item '{0}' already exists".format(self.name)
            self.statusbar.showMessage(msg, 3000)
            return
        # Check that short name (folder) is not reserved
        short_name = self.name.lower().replace(' ', '_')
        if self._toolbox.project_item_model.short_name_reserved(short_name):
            msg = "Item using folder '{0}' already exists".format(short_name)
            self.statusbar.showMessage(msg, 3000)
            return
        # Create new Item
        self.call_add_item()
        self.close()

    def call_add_item(self):
        """Creates new Item according to user's selections."""
        tool = self.ui.comboBox_specification.currentText()
        item = dict(name=self.name, description=self.description, x=self._x, y=self._y, tool=tool, execute_in_work=True)
        self._project.add_project_items("Tools", item, set_selected=True)

    def keyPressEvent(self, e):
        """Close Setup form when escape key is pressed.

        Args:
            e (QKeyEvent): Received key press event.
        """
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            self.ok_clicked()

    def closeEvent(self, event=None):
        """Handle close window.

        Args:
            event (QEvent): Closing event if 'X' is clicked.
        """
        if event:
            event.accept()
            scene = self._toolbox.ui.graphicsView.scene()
            item_shadow = scene.item_shadow
            if item_shadow:
                scene.removeItem(item_shadow)
                scene.item_shadow = None
