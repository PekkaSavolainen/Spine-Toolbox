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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

"""
QWidget that is used to create or edit Tool Templates.
In the former case it is presented empty, but in the latter it
is filled with all the information from the Templated being edited

:author: Manuel Marin <manuelma@kth.se>
:date:   12.4.2018
"""

import os
import json
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import QWidget, QStatusBar, QInputDialog, QMessageBox
from PySide2.QtCore import Slot, Qt, QUrl
from PySide2.QtGui import QDesktopServices
from ui.tool_template_form import Ui_Form
from config import STATUSBAR_SS, INVALID_CHARS, TT_TREEVIEW_HEADER_SS,\
    APPLICATION_PATH, TOOL_TYPES, REQUIRED_KEYS
from helpers import custom_getopenfilenames, custom_getsavefilename
import logging
import inspect


class ToolTemplateWidget(QWidget):
    """A widget to query user's preferences for a new tool template"""

    def __init__(self, parent, project, tool_template=None):
        """ Initialize class.

        Args:
            parent (ToolBoxUI): QMainWindow instance
            project (SpineToolboxProject): A project instance
            tool_template (ToolTemplate): If given, the form is pre-filled with data
                from this template
        """
        super().__init__()
        # Setup UI from Qt Designer file
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # Class attributes
        self._parent = parent
        self._project = project
        # init models
        self.includes_model = QStandardItemModel()  # Source files
        self.inputfiles_model = QStandardItemModel()  # Input files
        self.inputfiles_opt_model = QStandardItemModel()  # Input files
        self.outputfiles_model = QStandardItemModel()  # Input files
        # Add status bar to form
        self.statusbar = QStatusBar(self)
        self.statusbar.setFixedHeight(20)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setStyleSheet(STATUSBAR_SS)
        # init ui
        self.ui.horizontalLayout_statusbar_placeholder.addWidget(self.statusbar)
        self.ui.treeView_includes.setModel(self.includes_model)
        self.ui.treeView_inputfiles.setModel(self.inputfiles_model)
        self.ui.treeView_inputfiles_opt.setModel(self.inputfiles_opt_model)
        self.ui.treeView_outputfiles.setModel(self.outputfiles_model)
        self.ui.treeView_includes.setStyleSheet(TT_TREEVIEW_HEADER_SS)
        self.ui.treeView_inputfiles.setStyleSheet(TT_TREEVIEW_HEADER_SS)
        self.ui.treeView_inputfiles_opt.setStyleSheet(TT_TREEVIEW_HEADER_SS)
        self.ui.treeView_outputfiles.setStyleSheet(TT_TREEVIEW_HEADER_SS)
        self.ui.comboBox_tooltype.addItem("Select tool type...")
        self.ui.comboBox_tooltype.addItems(TOOL_TYPES)
        # if a template is given, fill the form with data from it
        if tool_template:
            self.ui.lineEdit_name.setText(tool_template.name)
            self.ui.textEdit_description.setPlainText(tool_template.description)
            self.ui.lineEdit_args.setText(tool_template.cmdline_args)
            tool_types = [x.lower() for x in TOOL_TYPES]
            index = tool_types.index(tool_template.tooltype) + 1
            self.ui.comboBox_tooltype.setCurrentIndex(index)
        self.includes = list(tool_template.includes) if tool_template else list()
        self.inputfiles = list(tool_template.inputfiles) if tool_template else list()
        self.inputfiles_opt = list(tool_template.inputfiles_opt) if tool_template else list()
        self.outputfiles = list(tool_template.outputfiles) if tool_template else list()
        self.def_file_path = tool_template.def_file_path if tool_template else None
        self.includes_main_path = tool_template.path if tool_template else None
        self.definition = dict()
        # Populate lists (this will also create headers)
        self.populate_includes_list(self.includes)
        self.populate_inputfiles_list(self.inputfiles)
        self.populate_inputfiles_opt_list(self.inputfiles_opt)
        self.populate_outputfiles_list(self.outputfiles)
        self.ui.lineEdit_name.setFocus()
        self.ui.label_mainpath.setText(self.includes_main_path)
        self.connect_signals()

    def connect_signals(self):
        """Connect signals to slots."""
        #self.ui.lineEdit_name.textChanged.connect(self.name_changed)  # Name -> folder name connection
        self.ui.toolButton_plus_includes.clicked.connect(self.add_includes)
        self.ui.treeView_includes.doubleClicked.connect(self.open_includes_file)
        self.ui.toolButton_minus_includes.clicked.connect(self.remove_includes)
        self.ui.toolButton_plus_inputfiles.clicked.connect(self.add_inputfiles)
        self.ui.toolButton_minus_inputfiles.clicked.connect(self.remove_inputfiles)
        self.ui.pushButton_ok.clicked.connect(self.ok_clicked)
        self.ui.pushButton_cancel.clicked.connect(self.close)

    def make_header_for_includes(self):
        """Add header to includes model. I.e. tool source files and necessary folders."""
        h = QStandardItem("Includes")
        self.includes_model.setHorizontalHeaderItem(0, h)

    def make_header_for_inputfiles(self):
        """Add header to inputfiles model. I.e. tool input files."""
        h = QStandardItem("Input files")
        self.inputfiles_model.setHorizontalHeaderItem(0, h)

    def make_header_for_inputfiles_opt(self):
        """Add header to inputfiles model. I.e. tool optional input files."""
        h = QStandardItem("Optional input files")
        self.inputfiles_opt_model.setHorizontalHeaderItem(0, h)

    def make_header_for_outputfiles(self):
        """Add header to outputfiles model. I.e. tool output files."""
        h = QStandardItem("Output files")
        self.outputfiles_model.setHorizontalHeaderItem(0, h)

    def populate_includes_list(self, items):
        """List source files in QTreeView.
        If items is None or empty list, model is cleared.
        """
        self.includes_model.clear()
        self.make_header_for_includes()
        if items is not None:
            for item in items:
                qitem = QStandardItem(item)
                qitem.setFlags(~Qt.ItemIsEditable)
                self.includes_model.appendRow(qitem)

    def populate_inputfiles_list(self, items):
        """List input files in QTreeView.
        If items is None or empty list, model is cleared.
        """
        self.inputfiles_model.clear()
        self.make_header_for_inputfiles()
        if items is not None:
            for item in items:
                qitem = QStandardItem(item)
                qitem.setFlags(~Qt.ItemIsEditable)
                self.inputfiles_model.appendRow(qitem)

    def populate_inputfiles_opt_list(self, items):
        """List optional input files in QTreeView.
        If items is None or empty list, model is cleared.
        """
        self.inputfiles_opt_model.clear()
        self.make_header_for_inputfiles_opt()
        if items is not None:
            for item in items:
                qitem = QStandardItem(item)
                qitem.setFlags(~Qt.ItemIsEditable)
                self.inputfiles_opt_model.appendRow(qitem)

    def populate_outputfiles_list(self, items):
        """List output files in QTreeView.
        If items is None or empty list, model is cleared.
        """
        self.outputfiles_model.clear()
        self.make_header_for_outputfiles()
        if items is not None:
            for item in items:
                qitem = QStandardItem(item)
                qitem.setFlags(~Qt.ItemIsEditable)
                self.outputfiles_model.appendRow(qitem)

    @Slot(name="add_includes")
    def add_includes(self):
        """Let user select source files for this tool template."""
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        path = self.includes_main_path if self.includes_main_path else APPLICATION_PATH
        answer = custom_getopenfilenames(self._parent.ui.graphicsView, self, "Add source file", path, "*.*")
        file_paths = answer[0]
        if not file_paths:  # Cancel button clicked
            return
        for path in file_paths:
            logging.debug(path)
            dirname, file_pattern = os.path.split(path)
            if not self.includes_main_path:
                self.includes_main_path = dirname
                self.ui.label_mainpath.setText(self.includes_main_path)
                path_to_add = file_pattern
            else:
                # check if path is a descendant of main dir
                common_prefix = os.path.commonprefix([self.includes_main_path, path])
                if common_prefix != self.includes_main_path:
                    self.statusbar.showMessage("Source file {0}'s location is invalid"\
                                                " (should be in main directory)"\
                                                .format(file_pattern), 3000)
                    continue
                path_to_add = os.path.relpath(path, self.includes_main_path)
            if path_to_add in self.includes:
                self.statusbar.showMessage("Source file {0} already included".format(path_to_add), 3000)
                continue
            self.includes.append(path_to_add)
        self.populate_includes_list(self.includes)


    @Slot("QModelIndex", name="open_includes_file")
    def open_includes_file(self, index):
        """Open source file in default program."""
        if not index:
            return
        if not index.isValid():
            logging.error("Index not valid")
            return
        else:
            includes_file = self.includes[index.row()]
            url = "file:///" + os.path.join(self.includes_main_path, includes_file)
            # noinspection PyTypeChecker, PyCallByClass, PyArgumentList
            res = QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))
            if not res:
                self._parent.msg_error.emit("Failed to open file: <b>{0}</b>".format(includes_file))

    @Slot(name="add_inputfiles")
    def add_inputfiles(self):
        """Let user select input files for this tool template."""
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QInputDialog.getText(self, "Add input file", "Input file name (eg data.csv):")
        file_name = answer[0]
        if not file_name:  # Cancel button clicked
            return
        self.inputfiles.append(file_name)
        self.populate_inputfiles_list(self.inputfiles)

    @Slot(name="remove_includes")
    def remove_includes(self):
        """Remove selected source files from include list.
        Removes all files if nothing is selected.
        """
        indexes = self.ui.treeView_includes.selectedIndexes()
        if not indexes:  # Nothing selected
            self.includes.clear()
            self.includes_main_path = None
            self.ui.label_mainpath.clear()
            self.statusbar.showMessage("All includes removed", 3000)
        else:
            rows = [ind.row() for ind in indexes]
            rows.sort(reverse=True)
            for row in rows:
                self.includes.pop(row)
            if not self.includes:
                self.includes_main_path = None
                self.ui.label_mainpath.clear()
            elif 0 in rows: # main program was removed
            # new main is the first one still in the list
            # TODO: isn't it better to pick the new main as the one with the smallest path?
                dirname = os.path.dirname(self.includes[0])
                new_main_path = os.path.join(self.includes_main_path, dirname)
                old_main_path = self.includes_main_path
                old_includes_abspath = [os.path.join(old_main_path, path) for path in self.includes]
                self.includes = [os.path.relpath(path, new_main_path)\
                                    for path in old_includes_abspath\
                                    if os.path.commonprefix([new_main_path, path]) == new_main_path]
                self.includes_main_path = new_main_path
                self.ui.label_mainpath.setText(self.includes_main_path)
            self.statusbar.showMessage("Selected (and invalid) includes removed", 3000)
        self.populate_includes_list(self.includes)

    @Slot(name="remove_inputfiles")
    def remove_inputfiles(self):
        """Remove selected source files from include list.
        Removes all files if nothing is selected.
        """
        indexes = self.ui.treeView_inputfiles.selectedIndexes()
        if not indexes:  # Nothing selected
            self.inputfiles.clear()
            self.statusbar.showMessage("All input files removed", 3000)
        else:
            rows = [ind.row() for ind in indexes]
            rows.sort(reverse=True)
            for row in rows:
                self.inputfiles.pop(row)
            self.statusbar.showMessage("Selected input files removed", 3000)
        self.populate_inputfiles_list(self.inputfiles)

    @Slot(name='ok_clicked')
    def ok_clicked(self):
        """Check that everything is valid, create definition dictionary and add template to project."""
        # Check that tooltype is selected
        if self.ui.comboBox_tooltype.currentIndex() == 0:
            self.statusbar.showMessage("Tool type not selected", 3000)
            return
        self.definition['name'] = self.ui.lineEdit_name.text()
        self.definition['description'] = self.ui.textEdit_description.toPlainText()
        self.definition['tooltype'] = self.ui.comboBox_tooltype.currentText().lower()
        self.definition['includes'] = self.includes
        self.definition['inputfiles'] = self.inputfiles
        self.definition['inputfiles_opt'] = self.inputfiles_opt
        self.definition['outputfiles'] = self.outputfiles
        self.definition['cmdline_args'] = self.ui.lineEdit_args.text()
        #logging.debug(self.definition)
        for k in REQUIRED_KEYS:
            if not self.definition[k]:
                self.statusbar.showMessage("{} missing".format(k.capitalize()), 3000)
                return
        # Create new Template
        short_name = self.definition['name'].lower().replace(' ', '_')
        self.def_file_path = os.path.join(self.includes_main_path, short_name + ".json")
        if self.call_add_tool_template():
            self.close()

    def call_add_tool_template(self):
        """Create or update Tool Template according to user's selections.
        If the name is the same as an existing tool template, it is updated and
        auto-saved to the definition file. (The user is editting an existing
        tool template)
        If the name is not in the tool template model, create a new one and
        offer to save the definition file. (The user is creating a new template
        from scratch or spawning from an existing one)
        """
        # Load tool template
        path = self.includes_main_path
        tool = self._project.load_tool_template_from_dict(self.definition, path)
        if not tool:
            self.statusbar.showMessage("Adding Tool template failed", 3000)
            return False
        # Check if a tool template with this name already exists
        row = self._parent.tool_template_model.tool_template_row(tool.name)
        if row >= 0: #Note: Row 0 at this moment has 'No tool'
            old_tool = self._parent.tool_template_model.tool_template(row)
            def_file = old_tool.get_def_path()
            tool.set_def_path(def_file)
            if tool.__dict__ == old_tool.__dict__:  # Nothing changed. We're done here.
                return True
            logging.debug("Updating definition for tool template '{}'".format(tool.name))
            self._parent.update_tool_template(row, tool)
        else:
            answer = custom_getsavefilename(self._parent.ui.graphicsView, self, 'Save tool template file', \
                                            self.def_file_path, 'JSON (*.json)')
            if answer[0] == '':  # Cancel button clicked
                return False
            def_file = os.path.abspath(answer[0]) # TODO: maybe check that extension is .json?
            tool.set_def_path(def_file)
            self._parent.add_tool_template(tool)
        # Save path of main program file relative to definition file in case they difer
        def_path = os.path.dirname(def_file)
        if def_path != self.includes_main_path:
            self.definition['includes_main_path'] = os.path.relpath(self.includes_main_path, def_path)
        # Save file descriptor
        with open(def_file, 'w') as fp:
            try:
                json.dump(self.definition, fp, indent=4)
            except ValueError:
                self.statusbar.showMessage("Error saving file", 3000)
                logging.exception("Saving JSON file failed.")
                return False
        logging.debug("Tool template added or updated.")
        return True

    def keyPressEvent(self, e):
        """Close Setup form when escape key is pressed.

        Args:
            e (QKeyEvent): Received key press event.
        """
        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event=None):
        """Handle close window.

        Args:
            event (QEvent): Closing event if 'X' is clicked.
        """
        if event:
            event.accept()
