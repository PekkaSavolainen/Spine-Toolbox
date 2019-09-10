######################################################################################################################
# Copyright (C) 2017 - 2019 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Module for view class.

:authors: P. Savolainen (VTT), M. Marin (KHT), J. Olauson (KTH)
:date:   14.07.2018
"""

import logging
import os
from PySide2.QtCore import Qt, Slot, QUrl
from PySide2.QtGui import QStandardItem, QStandardItemModel, QIcon, QPixmap, QDesktopServices
from sqlalchemy.engine.url import URL
from spinedb_api import DiffDatabaseMapping, SpineDBAPIError, SpineDBVersionError
from project_item import ProjectItem
from widgets.graph_view_widget import GraphViewForm
from widgets.tabular_view_widget import TabularViewForm
from widgets.tree_view_widget import TreeViewForm
from graphics_items import ViewIcon
from helpers import create_dir


class View(ProjectItem):
    """
    View class.

    Attributes:
        toolbox (ToolboxUI): QMainWindow instance
        name (str): Object name
        description (str): Object description
        x (int): Initial X coordinate of item icon
        y (int): Initial Y coordinate of item icon
    """

    def __init__(self, toolbox, name, description, x, y):
        super().__init__(toolbox, name, description)
        self._project = self._toolbox.project()
        self.item_type = "View"
        self._graph_views = {}
        self._tabular_views = {}
        self._tree_views = {}
        self._references = list()
        self.reference_model = QStandardItemModel()  # References to databases
        self.spine_ref_icon = QIcon(QPixmap(":/icons/Spine_db_ref_icon.png"))
        # Make project directory for this View
        self.data_dir = os.path.join(self._project.project_dir, self.short_name)
        try:
            create_dir(self.data_dir)
        except OSError:
            self._toolbox.msg_error.emit(
                "[OSError] Creating directory {0} failed." " Check permissions.".format(self.data_dir)
            )
        self._graphics_item = ViewIcon(self._toolbox, x - 35, y - 35, 70, 70, self.name)
        self._sigs = self.make_signal_handler_dict()

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = dict()
        s[self._toolbox.ui.toolButton_view_open_dir.clicked] = self.open_directory
        s[self._toolbox.ui.pushButton_view_open_graph_view.clicked] = self.open_graph_view_btn_clicked
        s[self._toolbox.ui.pushButton_view_open_tabular_view.clicked] = self.open_tabular_view_btn_clicked
        s[self._toolbox.ui.pushButton_view_open_tree_view.clicked] = self.open_tree_view_btn_clicked
        return s

    def activate(self):
        """Restore selections and connect signals."""
        self.restore_selections()
        super().connect_signals()

    def deactivate(self):
        """Save selections and disconnect signals."""
        self.save_selections()
        if not super().disconnect_signals():
            logging.error("Item %s deactivation failed", self.name)
            return False
        return True

    def restore_selections(self):
        """Restore selections into shared widgets when this project item is selected."""
        self._toolbox.ui.label_view_name.setText(self.name)
        self._toolbox.ui.treeView_view.setModel(self.reference_model)

    def save_selections(self):
        """Save selections in shared widgets for this project item into instance variables."""
        self._toolbox.ui.treeView_view.setModel(None)

    def references(self):
        """Returns a list of url strings that are in this item as references."""
        return self._references

    def find_input_items(self):
        """Find input project items (only Data Stores now) that are connected to this View.

        Returns:
            List of Data Store items.
        """
        item_list = list()
        for input_item in self._toolbox.connection_model.input_items(self.name):
            found_index = self._toolbox.project_item_model.find_item(input_item)
            if not found_index:
                self._toolbox.msg_error.emit("Item {0} not found. Something is seriously wrong.".format(input_item))
                continue
            item = self._toolbox.project_item_model.project_item(found_index)
            if item.item_type not in ("Data Store", "Tool"):
                continue
            item_list.append(item)
        return item_list

    @Slot(bool, name="open_graph_view_btn_clicked")
    def open_graph_view_btn_clicked(self, checked=False):
        """Slot for handling the signal emitted by clicking on 'Graph view' button."""
        self._open_view(self._graph_views, supports_multiple_databases=False)

    @Slot(bool, name="open_tabular_view_btn_clicked")
    def open_tabular_view_btn_clicked(self, checked=False):
        """Slot for handling the signal emitted by clicking on 'Tabular view' button."""
        self._open_view(self._tabular_views, supports_multiple_databases=False)

    @Slot(bool, name="open_tree_view_btn_clicked")
    def open_tree_view_btn_clicked(self, checked=False):
        """Slot for handling the signal emitted by clicking on 'Tree view' button."""
        self._open_view(self._tree_views, supports_multiple_databases=True)

    def _open_view(self, view_store, supports_multiple_databases):
        """
        Opens references in a view window.

        Args:
            view_store (dict): a dictionary where to store the view window
            supports_multiple_databases (bool): True if the view supports more than one database
        """
        indexes = self._selected_indexes()
        db_maps, databases = self._database_maps(indexes)
        # Mangle database paths to get a hashable string identifying the view window.
        view_id = ";".join(sorted(databases))
        if not supports_multiple_databases and len(db_maps) > 1:
            # Currently, Graph and Tabular views do not support multiple databases.
            # This if clause can be removed once that support has been implemented.
            self._toolbox.msg_error.emit("Selected view does not support multiple databases.")
            return
        if self._restore_existing_view_window(view_id, view_store):
            return
        view_window = self._make_view_window(view_store, db_maps, databases)
        view_window.show()
        view_window.destroyed.connect(lambda: view_store.pop(view_id))
        view_store[view_id] = view_window

    def close_all_views(self):
        """Closes all view windows."""
        for view in self._graph_views.values():
            view.close()
        for view in self._tabular_views.values():
            view.close()
        for view in self._tree_views.values():
            view.close()

    def populate_reference_list(self, items):
        """Add given list of items to the reference model. If None or
        an empty list given, the model is cleared."""
        self.reference_model.clear()
        self.reference_model.setHorizontalHeaderItem(0, QStandardItem("References"))  # Add header
        if items is not None:
            for item in items:
                qitem = QStandardItem(item.database)
                qitem.setFlags(~Qt.ItemIsEditable)
                qitem.setData(self.spine_ref_icon, Qt.DecorationRole)
                self.reference_model.appendRow(qitem)

    def update_name_label(self):
        """Update View tab name label. Used only when renaming project items."""
        self._toolbox.ui.label_view_name.setText(self.name)

    @Slot(bool, name="open_directory")
    def open_directory(self, checked=False):
        """Open file explorer in View data directory."""
        url = "file:///" + self.data_dir
        # noinspection PyTypeChecker, PyCallByClass, PyArgumentList
        res = QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))
        if not res:
            self._toolbox.msg_error.emit("Failed to open directory: {0}".format(self.data_dir))

    def execute(self):
        """Executes this View."""
        self._toolbox.msg.emit("")
        self._toolbox.msg.emit("Executing View <b>{0}</b>".format(self.name))
        self._toolbox.msg.emit("***")
        inst = self._toolbox.project().execution_instance
        self._references.clear()
        for url in inst.ds_urls_at_sight(self.name):
            drivername = url.drivername.lower()
            if drivername.startswith('sqlite'):
                self._references.append(url)
        for filepath in inst.tool_output_files_at_sight(self.name):
            if filepath.lower().endswith('.sqlite'):
                url = URL("sqlite", database=filepath)
                self._references.append(url)
        self.populate_reference_list(self._references)
        self._toolbox.project().execution_instance.project_item_execution_finished_signal.emit(0)  # 0 success

    def stop_execution(self):
        """Stops executing this View."""
        self._toolbox.msg.emit("Stopping {0}".format(self.name))

    def simulate_execution(self):
        """Update the list of references that this item is viewing."""
        super().simulate_execution()
        inst = self._toolbox.project().execution_instance
        self._references.clear()
        for url in inst.ds_urls_at_sight(self.name):
            drivername = url.drivername.lower()
            if drivername.startswith('sqlite'):
                self._references.append(url)
        self.populate_reference_list(self._references)

    def _selected_indexes(self):
        """Returns selected indexes."""
        selection_model = self._toolbox.ui.treeView_view.selectionModel()
        if not selection_model.hasSelection():
            self._toolbox.ui.treeView_view.selectAll()
        return self._toolbox.ui.treeView_view.selectionModel().selectedRows()

    def _database_maps(self, indexes):
        """Returns database maps and database paths for given indexes."""
        db_maps = dict()
        databases = list()
        for index in indexes:
            url = self._references[index.row()]
            try:
                db_map = DiffDatabaseMapping(url, url.username)
            except (SpineDBAPIError, SpineDBVersionError) as e:
                self._toolbox.msg_error.emit(e.msg)
                return
            database = url.database
            db_maps[database] = db_map
            databases.append(database)
        return db_maps, databases

    @staticmethod
    def _restore_existing_view_window(view_id, view_store):
        """Restores an existing view window and returns True if the operation was successful."""
        if view_id not in view_store:
            return False
        view_window = view_store[view_id]
        if view_window.windowState() & Qt.WindowMinimized:
            view_window.setWindowState(view_window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        view_window.activateWindow()
        return True

    def _make_view_window(self, view_store, db_maps, databases):
        if view_store is self._graph_views:
            return GraphViewForm(self, db_maps, read_only=True)
        if view_store is self._tabular_views:
            return TabularViewForm(self, db_maps[databases[0]], databases[0])
        if view_store is self._tree_views:
            return TreeViewForm(self._project, db_maps)
        raise RuntimeError("view_store must be self._graph_views, self._tabular_views or self._tree_views")
