######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Unit tests for DB editor's custom ``QTreeView`` classes.

:author: A. Soininen
:date:   17.8.2021
"""
import os.path
from tempfile import TemporaryDirectory
from types import MethodType
import unittest
from unittest import mock
from PySide2.QtCore import Qt, QItemSelectionModel, QEvent
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QApplication

from spinedb_api import (
    DatabaseMapping,
    from_database,
    import_object_classes,
    import_objects,
    import_parameter_value_lists,
    import_relationship_classes,
    import_relationships,
    import_object_parameters,
    import_tools,
    import_features,
    import_tool_features,
    import_tool_feature_methods,
)
from spinetoolbox.spine_db_manager import SpineDBManager
from spinetoolbox.spine_db_editor.widgets.add_items_dialogs import (
    AddObjectClassesDialog,
    AddObjectsDialog,
    AddRelationshipsDialog,
    AddRelationshipClassesDialog,
)
from spinetoolbox.spine_db_editor.widgets.edit_or_remove_items_dialogs import (
    EditObjectClassesDialog,
    EditObjectsDialog,
    RemoveEntitiesDialog,
    EditRelationshipClassesDialog,
    EditRelationshipsDialog,
)
from spinetoolbox.spine_db_editor.widgets.spine_db_editor import SpineDBEditor
from spinetoolbox.helpers import signal_waiter
from spinetoolbox.widgets.custom_editors import SearchBarEditor


class _EditorDelegateMocking:
    def __init__(self):
        self._cell_editor = None

    def write_to_index(self, view, index, value):
        delegate = view.itemDelegate(index)
        if self._cell_editor is None:
            original_create_editor = delegate.createEditor

            def create_and_store_editor(instance, parent, option, target_index):
                self._cell_editor = original_create_editor(parent, option, target_index)
                return self._cell_editor

            delegate.createEditor = MethodType(create_and_store_editor, delegate)
        view.setCurrentIndex(index)
        view.edit(index)
        if self._cell_editor is None:
            # Native editor widget is being used, fall back to setting value directly in model.
            view.model().setData(index, value)
            return
        if isinstance(self._cell_editor, SearchBarEditor):
            key_press_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier, 0, 0, 0)
            i = 0
            while self._cell_editor.data() != value:
                if i == self._cell_editor.model.rowCount():
                    raise RuntimeError("Value not found in editor widget.")
                self._cell_editor.keyPressEvent(key_press_event)
                i += 1
        else:
            self._cell_editor.setText(str(value))
        delegate.commitData.emit(self._cell_editor)
        delegate.closeEditor.emit(self._cell_editor)

    def try_to_edit_index(self, view, index):
        delegate = view.itemDelegate(index)
        if self._cell_editor is None:
            original_create_editor = delegate.createEditor

            def create_and_store_editor(instance, parent, option, target_index):
                self._cell_editor = original_create_editor(parent, option, target_index)
                return self._cell_editor

            delegate.createEditor = MethodType(create_and_store_editor, delegate)
        view.setCurrentIndex(index)
        view.edit(index)


class _ParameterValueListEdits:
    def __init__(self, view):
        self._view = view
        self.view_editor = _EditorDelegateMocking()

    def append_value_list(self, db_mngr, list_name):
        model = self._view.model()
        root_index = model.index(0, 0)
        empty_name_row = model.rowCount(root_index) - 1
        empty_name_index = model.index(empty_name_row, 0, root_index)
        with signal_waiter(db_mngr.parameter_value_lists_added) as waiter:
            self.view_editor.write_to_index(self._view, empty_name_index, list_name)
            waiter.wait()
        new_name_row = model.rowCount(root_index) - 2
        return model.index(new_name_row, 0, root_index)

    def append_value(self, db_mngr, list_name, value):
        model = self._view.model()
        root_index = model.index(0, 0)
        for list_row in range(model.rowCount(root_index)):
            list_index = model.index(list_row, 0, root_index)
            if list_index.data() == list_name:
                last_row = model.rowCount(list_index) - 1
                empty_value_index = model.index(last_row, 0, list_index)
                with signal_waiter(db_mngr.list_values_added) as waiter:
                    self.view_editor.write_to_index(self._view, empty_value_index, value)
                    waiter.wait()
                return model.index(last_row, 0, list_index)
        raise RuntimeError(f"{list_name} not found.")


def _add_entity_tree_item(item_names, view, menu_action_text, dialog_class):
    add_items_action = None
    for action in view._menu.actions():
        if action.text() == menu_action_text:
            add_items_action = action
            break
    if add_items_action is None:
        raise RuntimeError("Menu action not found.")
    patched = "spinetoolbox.spine_db_editor.widgets.tree_view_mixin." + dialog_class.__name__
    with mock.patch(patched) as mock_dialog:
        add_items_action.trigger()
        arguments_list = mock_dialog.call_args_list
    for arguments in arguments_list:
        add_items_dialog = dialog_class(*arguments[0])
        with signal_waiter(add_items_dialog.model.rowsInserted) as waiter:
            QApplication.processEvents()
            waiter.wait()
        for column, name in item_names.items():
            item_name_index = add_items_dialog.model.index(0, column)
            add_items_dialog.set_model_data(item_name_index, name)
        add_items_dialog.accept()


def _add_object_class(view, class_name):
    _add_entity_tree_item({0: class_name}, view, "Add object classes", AddObjectClassesDialog)


def _add_object(view, object_name):
    model = view.model()
    root_index = model.index(0, 0)
    class_index = model.index(0, 0, root_index)
    view._context_item = model.item_from_index(class_index)
    _add_entity_tree_item({1: object_name}, view, "Add objects", AddObjectsDialog)


def _edit_entity_tree_item(new_entries, view, menu_action_text, dialog_class):
    edit_items_action = None
    for action in view._menu.actions():
        if action.text() == menu_action_text:
            edit_items_action = action
            break
    if edit_items_action is None:
        raise RuntimeError("Menu action not found.")
    patched = "spinetoolbox.spine_db_editor.widgets.tree_view_mixin." + dialog_class.__name__
    with mock.patch(patched) as mock_dialog:
        edit_items_action.trigger()
        arguments_list = mock_dialog.call_args_list
    for arguments in arguments_list:
        edit_items_dialog = dialog_class(*arguments[0])
        for column, entry in new_entries.items():
            item_name_index = edit_items_dialog.model.index(0, column)
            edit_items_dialog.set_model_data(item_name_index, entry)
            edit_items_dialog.accept()


def _remove_entity_tree_item(view, menu_action_text, dialog_class):
    remove_items_action = None
    for action in view._menu.actions():
        if action.text() == menu_action_text:
            remove_items_action = action
            break
    patched = "spinetoolbox.spine_db_editor.widgets.tree_view_mixin." + dialog_class.__name__
    if remove_items_action is None:
        raise RuntimeError("Menu action not found.")
    with mock.patch(patched) as mock_dialog:
        remove_items_action.trigger()
        arguments_list = mock_dialog.call_args_list
    for arguments in arguments_list:
        edit_items_dialog = dialog_class(*arguments[0])
        edit_items_dialog.accept()


def _remove_object_class(view):
    _remove_entity_tree_item(view, "Remove...", RemoveEntitiesDialog)


def _remove_object(view):
    _remove_entity_tree_item(view, "Remove...", RemoveEntitiesDialog)


def _append_table_row(view, row):
    model = view.model()
    last_row = model.rowCount() - 1
    for column, value in enumerate(row):
        delegate_mock = _EditorDelegateMocking()
        index = model.index(last_row, column)
        delegate_mock.write_to_index(view, index, value)


class _Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def _common_setup(self, url, create):
        with mock.patch("spinetoolbox.spine_db_editor.widgets.spine_db_editor.SpineDBEditor.restore_ui"), mock.patch(
            "spinetoolbox.spine_db_editor.widgets.spine_db_editor.SpineDBEditor.show"
        ):
            mock_settings = mock.Mock()
            mock_settings.value.side_effect = lambda *args, **kwargs: 0
            self._db_mngr = SpineDBManager(mock_settings, None)
            logger = mock.MagicMock()
            self._db_map = self._db_mngr.get_db_map(url, logger, codename="database", create=create)
            self._db_editor = SpineDBEditor(self._db_mngr, {url: "database"})
        QApplication.processEvents()

    def _common_tear_down(self):
        with mock.patch(
            "spinetoolbox.spine_db_editor.widgets.spine_db_editor.SpineDBEditor.save_window_state"
        ), mock.patch("spinetoolbox.spine_db_manager.QMessageBox"):
            self._db_editor.close()
        self._db_mngr.close_all_sessions()
        while not self._db_map.connection.closed:
            QApplication.processEvents()
        self._db_mngr.clean_up()
        self._db_editor.deleteLater()
        self._db_editor = None

    def _commit_changes_to_database(self, commit_message):
        with mock.patch.object(self._db_editor, "_get_commit_msg") as commit_msg:
            commit_msg.return_value = commit_message
            with signal_waiter(self._db_mngr.session_committed) as waiter:
                self._db_editor.ui.actionCommit.trigger()
                waiter.wait()


class TestObjectTreeViewWithInitiallyEmptyDatabase(_Base):
    def setUp(self):
        self._common_setup("sqlite://", create=True)

    def tearDown(self):
        self._common_tear_down()

    def test_empty_view(self):
        view = self._db_editor.ui.treeView_object
        model = view.model()
        root_index = model.index(0, 0)
        self.assertEqual(model.rowCount(root_index), 0)
        self.assertEqual(model.columnCount(root_index), 2)
        self.assertEqual(root_index.data(), "root")
        self.assertEqual(model.headerData(0, Qt.Horizontal), "name")
        self.assertEqual(model.headerData(1, Qt.Horizontal), "database")

    def test_add_object_class(self):
        view = self._db_editor.ui.treeView_object
        _add_object_class(view, "an_object_class")
        model = view.model()
        root_index = model.index(0, 0)
        self.assertEqual(model.rowCount(root_index), 1)
        class_index = model.index(0, 0, root_index)
        self.assertEqual(model.rowCount(class_index), 0)
        self.assertEqual(class_index.data(), "an_object_class")
        class_database_index = model.index(0, 1, root_index)
        self.assertEqual(class_database_index.data(), "database")
        self._commit_changes_to_database("Add object class.")
        data = self._db_mngr.query(self._db_map, "object_class_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "an_object_class")

    def test_add_object(self):
        view = self._db_editor.ui.treeView_object
        _add_object_class(view, "an_object_class")
        _add_object(view, "an_object")
        model = view.model()
        root_index = model.index(0, 0)
        class_index = model.index(0, 0, root_index)
        self.assertEqual(model.rowCount(class_index), 1)
        self.assertEqual(class_index.data(), "an_object_class")
        object_index = model.index(0, 0, class_index)
        self.assertEqual(model.rowCount(object_index), 0)
        self.assertEqual(object_index.data(), "an_object")
        object_database_index = model.index(0, 1, class_index)
        self.assertEqual(object_database_index.data(), "database")
        self._commit_changes_to_database("Add object.")
        data = self._db_mngr.query(self._db_map, "object_class_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "an_object_class")
        data = self._db_mngr.query(self._db_map, "object_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "an_object")

    def test_add_relationship_class_from_object_tree_view(self):
        object_tree_view = self._db_editor.ui.treeView_object
        _add_object_class(object_tree_view, "an_object_class")
        object_model = object_tree_view.model()
        root_index = object_model.index(0, 0)
        object_class_index = object_model.index(0, 0, root_index)
        object_tree_view._context_item = object_model.item_from_index(object_class_index)
        _add_entity_tree_item(
            {1: "a_relationship_class"}, object_tree_view, "Add relationship classes", AddRelationshipClassesDialog
        )
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        class_index = model.index(0, 0, root_index)
        self.assertEqual(model.rowCount(class_index), 0)
        self.assertEqual(class_index.data(), "a_relationship_class")
        class_database_index = model.index(0, 1, root_index)
        self.assertEqual(class_database_index.data(), "database")
        self._commit_changes_to_database("Add object and relationship classes.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_class_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "a_relationship_class")
        self.assertEqual(data[0].object_class_name_list, "an_object_class")


class TestObjectTreeViewWithExistingData(_Base):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()
        url = "sqlite:///" + os.path.join(self._temp_dir.name, "test_database.sqlite")
        db_map = DatabaseMapping(url, create=True)
        import_object_classes(db_map, ("object_class_1",))
        import_objects(db_map, (("object_class_1", "object_1"), ("object_class_1", "object_2")))
        db_map.commit_session("Add objects.")
        db_map.connection.close()
        self._common_setup(url, create=False)
        model = self._db_editor.ui.treeView_object.model()
        root_index = model.index(0, 0)
        while model.rowCount(root_index) != 1:
            # Wait for fetching to finish.
            QApplication.processEvents()

    def tearDown(self):
        self._common_tear_down()
        self._temp_dir.cleanup()

    def test_database_contents_shown_correctly(self):
        view = self._db_editor.ui.treeView_object
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        self.assertEqual(model.columnCount(root_index), 2)
        self.assertEqual(root_index.data(), "root")
        self.assertEqual(model.headerData(0, Qt.Horizontal), "name")
        self.assertEqual(model.headerData(1, Qt.Horizontal), "database")
        class_index = model.index(0, 0, root_index)
        model.fetchMore(class_index)
        while model.rowCount(class_index) != 2:
            QApplication.processEvents()
        self.assertEqual(model.columnCount(class_index), 2)
        self.assertEqual(class_index.data(), "object_class_1")
        database_index = model.index(0, 1, root_index)
        self.assertEqual(database_index.data(), "database")
        object_index = model.index(0, 0, class_index)
        self.assertEqual(model.rowCount(object_index), 0)
        self.assertEqual(model.columnCount(object_index), 2)
        self.assertEqual(object_index.data(), "object_1")
        database_index = model.index(0, 1, class_index)
        self.assertEqual(database_index.data(), "database")
        object_index = model.index(1, 0, class_index)
        self.assertEqual(model.rowCount(object_index), 0)
        self.assertEqual(model.columnCount(object_index), 2)
        self.assertEqual(object_index.data(), "object_2")
        database_index = model.index(1, 1, class_index)
        self.assertEqual(database_index.data(), "database")

    def test_rename_object_class(self):
        view = self._db_editor.ui.treeView_object
        model = view.model()
        root_index = model.index(0, 0)
        class_index = model.index(0, 0, root_index)
        view.setCurrentIndex(class_index)
        with signal_waiter(self._db_mngr.object_classes_updated) as waiter:
            self._rename_object_class("renamed_class")
            waiter.wait()
        class_index = model.index(0, 0, root_index)
        self.assertEqual(class_index.data(), "renamed_class")
        self._commit_changes_to_database("Rename object class.")
        data = self._db_mngr.query(self._db_map, "object_class_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "renamed_class")

    def test_rename_object(self):
        view = self._db_editor.ui.treeView_object
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        class_index = model.index(0, 0, root_index)
        model.fetchMore(class_index)
        while model.rowCount(class_index) != 2:
            QApplication.processEvents()
        object_index = model.index(0, 0, class_index)
        view.setCurrentIndex(object_index)
        with signal_waiter(self._db_mngr.objects_updated) as waiter:
            self._rename_object("renamed_object")
            waiter.wait()
        object_index = model.index(0, 0, class_index)
        self.assertEqual(object_index.data(), "renamed_object")
        self._commit_changes_to_database("Rename object.")
        data = self._db_mngr.query(self._db_map, "object_sq")
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0].name, "renamed_object")

    def test_remove_object_class(self):
        view = self._db_editor.ui.treeView_object
        model = view.model()
        root_index = model.index(0, 0)
        class_index = model.index(0, 0, root_index)
        view.selectionModel().setCurrentIndex(class_index, QItemSelectionModel.ClearAndSelect)
        with signal_waiter(self._db_mngr.object_classes_removed) as waiter:
            _remove_object_class(view)
            waiter.wait()
        self.assertEqual(model.rowCount(root_index), 0)
        self._commit_changes_to_database("Remove object class.")
        data = self._db_mngr.query(self._db_map, "object_class_sq")
        self.assertEqual(len(data), 0)

    def test_remove_object(self):
        view = self._db_editor.ui.treeView_object
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        class_index = model.index(0, 0, root_index)
        model.fetchMore(class_index)
        while model.rowCount(class_index) != 2:
            QApplication.processEvents()
        object_index = model.index(0, 0, class_index)
        view.selectionModel().setCurrentIndex(object_index, QItemSelectionModel.ClearAndSelect)
        with signal_waiter(self._db_mngr.objects_removed) as waiter:
            _remove_object(view)
            waiter.wait()
        self.assertEqual(model.rowCount(class_index), 1)
        object_index = model.index(0, 0, class_index)
        self.assertEqual(object_index.data(), "object_2")
        self._commit_changes_to_database("Remove object.")
        data = self._db_mngr.query(self._db_map, "object_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "object_2")

    def _rename_object_class(self, class_name):
        view = self._db_editor.ui.treeView_object
        _edit_entity_tree_item({0: class_name}, view, "Edit...", EditObjectClassesDialog)

    def _rename_object(self, object_name):
        view = self._db_editor.ui.treeView_object
        _edit_entity_tree_item({0: object_name}, view, "Edit...", EditObjectsDialog)


class TestRelationshipTreeViewWithInitiallyEmptyDatabase(_Base):
    def setUp(self):
        self._common_setup("sqlite://", create=True)

    def tearDown(self):
        self._common_tear_down()

    def test_empty_view(self):
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        self.assertEqual(model.rowCount(root_index), 0)
        self.assertEqual(model.columnCount(root_index), 2)
        self.assertEqual(root_index.data(), "root")
        self.assertEqual(model.headerData(0, Qt.Horizontal), "name")
        self.assertEqual(model.headerData(1, Qt.Horizontal), "database")

    def test_add_relationship_class(self):
        _add_object_class(self._db_editor.ui.treeView_object, "an_object_class")
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        view._context_item = model.item_from_index(root_index)
        self._add_relationship_class("a_relationship_class", ["an_object_class"])
        class_index = model.index(0, 0, root_index)
        self.assertEqual(model.rowCount(class_index), 0)
        self.assertEqual(class_index.data(), "a_relationship_class")
        class_database_index = model.index(0, 1, root_index)
        self.assertEqual(class_database_index.data(), "database")
        self._commit_changes_to_database("Add object and relationship classes.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_class_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "a_relationship_class")
        self.assertEqual(data[0].object_class_name_list, "an_object_class")

    def test_add_relationship(self):
        object_tree_view = self._db_editor.ui.treeView_object
        _add_object_class(object_tree_view, "an_object_class")
        _add_object(object_tree_view, "an_object")
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        view._context_item = model.item_from_index(root_index)
        self._add_relationship_class("a_relationship_class", ["an_object_class"])
        class_index = model.index(0, 0, root_index)
        view._context_item = model.item_from_index(class_index)
        self._add_relationship("a_relationship", ["an_object"])
        class_index = model.index(0, 0, root_index)
        self.assertEqual(model.rowCount(class_index), 1)
        relationship_index = model.index(0, 0, class_index)
        self.assertEqual(model.rowCount(relationship_index), 0)
        self.assertEqual(relationship_index.data(), "an_object")
        relationship_database_index = model.index(0, 1, class_index)
        self.assertEqual(relationship_database_index.data(), "database")
        self._commit_changes_to_database("Add an object and a relationship.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "a_relationship")
        self.assertEqual(data[0].object_name_list, "an_object")

    def _add_relationship_class(self, class_name, object_class_names):
        item_names = {i: name for i, name in enumerate(object_class_names)}
        item_names[len(object_class_names)] = class_name
        _add_entity_tree_item(
            item_names,
            self._db_editor.ui.treeView_relationship,
            "Add relationship classes",
            AddRelationshipClassesDialog,
        )

    def _add_relationship(self, relationship_name, object_names):
        item_names = {i: name for i, name in enumerate(object_names)}
        item_names[len(object_names)] = relationship_name
        _add_entity_tree_item(
            item_names, self._db_editor.ui.treeView_relationship, "Add relationships", AddRelationshipsDialog
        )


class TestRelationshipTreeViewWithExistingData(_Base):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()
        url = "sqlite:///" + os.path.join(self._temp_dir.name, "test_database.sqlite")
        db_map = DatabaseMapping(url, create=True)
        import_object_classes(db_map, ("object_class_1", "object_class_2"))
        import_objects(
            db_map,
            (
                ("object_class_1", "object_11"),
                ("object_class_1", "object_12"),
                ("object_class_2", "object_21"),
                ("object_class_2", "object_22"),
            ),
        )
        import_relationship_classes(db_map, (("relationship_class", ("object_class_1", "object_class_2")),))
        import_relationships(
            db_map,
            (("relationship_class", ("object_11", "object_21")), ("relationship_class", ("object_11", "object_22"))),
        )
        db_map.commit_session("Add relationships.")
        db_map.connection.close()
        self._common_setup(url, create=False)
        model = self._db_editor.ui.treeView_relationship.model()
        root_index = model.index(0, 0)
        while model.rowCount(root_index) != 1:
            # Wait for fetching to finish.
            QApplication.processEvents()

    def tearDown(self):
        self._common_tear_down()
        self._temp_dir.cleanup()

    def test_database_contents_shown_correctly(self):
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        self.assertEqual(model.columnCount(root_index), 2)
        self.assertEqual(root_index.data(), "root")
        self.assertEqual(model.headerData(0, Qt.Horizontal), "name")
        self.assertEqual(model.headerData(1, Qt.Horizontal), "database")
        class_index = model.index(0, 0, root_index)
        model.fetchMore(class_index)
        while model.rowCount(class_index) != 2:
            QApplication.processEvents()
        self.assertEqual(model.columnCount(class_index), 2)
        self.assertEqual(class_index.data(), "relationship_class")
        database_index = model.index(0, 1, root_index)
        self.assertEqual(database_index.data(), "database")
        relationship_index = model.index(0, 0, class_index)
        self.assertEqual(model.rowCount(relationship_index), 0)
        self.assertEqual(model.columnCount(relationship_index), 2)
        self.assertEqual(relationship_index.data(), "object_11 ǀ object_21")
        database_index = model.index(0, 1, class_index)
        self.assertEqual(database_index.data(), "database")
        relationship_index = model.index(1, 0, class_index)
        self.assertEqual(model.rowCount(relationship_index), 0)
        self.assertEqual(model.columnCount(relationship_index), 2)
        self.assertEqual(relationship_index.data(), "object_11 ǀ object_22")
        database_index = model.index(1, 1, class_index)
        self.assertEqual(database_index.data(), "database")

    def test_rename_relationship_class(self):
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        class_index = model.index(0, 0, root_index)
        view.setCurrentIndex(class_index)
        with signal_waiter(self._db_mngr.relationship_classes_updated) as waiter:
            self._rename_relationship_class("renamed_class")
            waiter.wait()
        class_index = model.index(0, 0, root_index)
        self.assertEqual(class_index.data(), "renamed_class")
        self._commit_changes_to_database("Rename relationship class.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_class_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "renamed_class")

    def test_rename_relationship(self):
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        class_index = model.index(0, 0, root_index)
        model.fetchMore(class_index)
        while model.rowCount(class_index) != 2:
            QApplication.processEvents()
        relationship_index = model.index(0, 0, class_index)
        view.setCurrentIndex(relationship_index)
        with signal_waiter(self._db_mngr.relationships_updated) as waiter:
            self._rename_relationship("renamed_relationship")
            waiter.wait()
        self._commit_changes_to_database("Rename relationship.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_sq")
        self.assertEqual(len(data), 2)
        names = {i.name for i in data}
        self.assertEqual(names, {"renamed_relationship", "relationship_class_object_11__object_22"})

    def test_modify_relationships_objects(self):
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        class_index = model.index(0, 0, root_index)
        model.fetchMore(class_index)
        while model.rowCount(class_index) != 2:
            QApplication.processEvents()
        relationship_index = model.index(0, 0, class_index)
        view.setCurrentIndex(relationship_index)
        with signal_waiter(self._db_mngr.relationships_updated) as waiter:
            _edit_entity_tree_item({0: "object_12"}, view, "Edit...", EditRelationshipsDialog)
            waiter.wait()
        self.assertEqual(relationship_index.data(), "object_12 ǀ object_21")
        self._commit_changes_to_database("Change relationship's objects.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_sq")
        self.assertEqual(len(data), 2)
        objects = {i.object_name_list for i in data}
        self.assertEqual(objects, {"object_12,object_21", "object_11,object_22"})

    def test_remove_relationship_class(self):
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        class_index = model.index(0, 0, root_index)
        view.selectionModel().setCurrentIndex(class_index, QItemSelectionModel.ClearAndSelect)
        with signal_waiter(self._db_mngr.relationship_classes_removed) as waiter:
            self._remove_relationship_class()
            waiter.wait()
        self.assertEqual(model.rowCount(root_index), 0)
        self._commit_changes_to_database("Remove relationship class.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_class_sq")
        self.assertEqual(len(data), 0)

    def test_remove_relationship(self):
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        class_index = model.index(0, 0, root_index)
        model.fetchMore(class_index)
        while model.rowCount(class_index) != 2:
            QApplication.processEvents()
        relationship_index = model.index(0, 0, class_index)
        view.selectionModel().setCurrentIndex(relationship_index, QItemSelectionModel.ClearAndSelect)
        with signal_waiter(self._db_mngr.relationships_removed) as waiter:
            self._remove_relationship()
            waiter.wait()
        self.assertEqual(model.rowCount(class_index), 1)
        self._commit_changes_to_database("Remove relationship.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "relationship_class_object_11__object_22")

    def test_removing_object_class_removes_corresponding_relationship_class(self):
        object_tree_view = self._db_editor.ui.treeView_object
        object_model = object_tree_view.model()
        root_index = object_model.index(0, 0)
        object_model.fetchMore(root_index)
        while object_model.rowCount(root_index) != 2:
            QApplication.processEvents()
        class_index = object_model.index(0, 0, root_index)
        object_tree_view.selectionModel().setCurrentIndex(class_index, QItemSelectionModel.ClearAndSelect)
        _remove_object_class(object_tree_view)
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        QApplication.processEvents()
        self.assertEqual(model.rowCount(root_index), 0)
        self._commit_changes_to_database("Remove object class.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_class_sq")
        self.assertEqual(len(data), 0)

    def test_removing_object_removes_corresponding_relationship(self):
        object_tree_view = self._db_editor.ui.treeView_object
        object_model = object_tree_view.model()
        root_index = object_model.index(0, 0)
        object_model.fetchMore(root_index)
        while object_model.rowCount(root_index) != 2:
            QApplication.processEvents()
        class_index = object_model.index(1, 0, root_index)
        self.assertEqual(class_index.data(), "object_class_2")
        object_model.fetchMore(class_index)
        while object_model.rowCount(class_index) != 2:
            QApplication.processEvents()
        object_index = object_model.index(0, 0, class_index)
        self.assertEqual(object_index.data(), "object_21")
        object_tree_view.selectionModel().setCurrentIndex(object_index, QItemSelectionModel.ClearAndSelect)
        _remove_object(object_tree_view)
        view = self._db_editor.ui.treeView_relationship
        model = view.model()
        root_index = model.index(0, 0)
        model.fetchMore(root_index)
        while model.rowCount(root_index) != 1:
            QApplication.processEvents()
        class_index = model.index(0, 0, root_index)
        model.fetchMore(class_index)
        while model.rowCount(class_index) != 1:
            QApplication.processEvents()
        relationship_index = model.index(0, 0, class_index)
        self.assertEqual(relationship_index.data(), "object_11 ǀ object_22")
        self._commit_changes_to_database("Remove object.")
        data = self._db_mngr.query(self._db_map, "wide_relationship_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "relationship_class_object_11__object_22")

    def _rename_relationship_class(self, class_name):
        view = self._db_editor.ui.treeView_relationship
        _edit_entity_tree_item({0: class_name}, view, "Edit...", EditRelationshipClassesDialog)

    def _rename_relationship(self, name):
        view = self._db_editor.ui.treeView_relationship
        _edit_entity_tree_item({2: name}, view, "Edit...", EditRelationshipsDialog)

    def _remove_relationship_class(self):
        view = self._db_editor.ui.treeView_relationship
        _remove_entity_tree_item(view, "Remove...", RemoveEntitiesDialog)

    def _remove_relationship(self):
        view = self._db_editor.ui.treeView_relationship
        _remove_entity_tree_item(view, "Remove...", RemoveEntitiesDialog)


class TestParameterValueListTreeViewWithInitiallyEmptyDatabase(_Base):
    def setUp(self):
        self._common_setup("sqlite://", create=True)
        self._edits = _ParameterValueListEdits(self._db_editor.ui.treeView_parameter_value_list)

    def tearDown(self):
        self._common_tear_down()

    def test_empty_tree_has_correct_contents(self):
        model = self._db_editor.ui.treeView_parameter_value_list.model()
        root_index = model.index(0, 0)
        self.assertTrue(root_index.isValid())
        self.assertEqual(model.rowCount(root_index), 1)
        list_name_index = model.index(0, 0, root_index)
        self.assertEqual(list_name_index.data(), "Type new list name here...")
        self.assertEqual(model.rowCount(list_name_index), 0)

    def test_add_parameter_value_list(self):
        list_name_index = self._edits.append_value_list(self._db_mngr, "a_value_list")
        self.assertEqual(list_name_index.data(), "a_value_list")
        view = self._db_editor.ui.treeView_parameter_value_list
        model = view.model()
        self.assertEqual(model.rowCount(list_name_index), 1)
        new_value_index = model.index(0, 0, list_name_index)
        self.assertEqual(new_value_index.data(), "Enter new list value here...")
        root_index = model.index(0, 0)
        self.assertEqual(model.rowCount(root_index), 2)
        new_name_index = model.index(1, 0, root_index)
        self.assertEqual(new_name_index.data(), "Type new list name here...")
        self.assertEqual(model.rowCount(new_name_index), 0)

    def test_add_list_then_remove_it(self):
        list_name_index = self._edits.append_value_list(self._db_mngr, "a_value_list")
        self.assertEqual(list_name_index.data(), "a_value_list")
        view = self._db_editor.ui.treeView_parameter_value_list
        view.selectionModel().select(list_name_index, QItemSelectionModel.ClearAndSelect)
        view.remove_selected()
        model = view.model()
        root_index = model.index(0, 0)
        self.assertEqual(model.rowCount(root_index), 1)
        list_name_index = model.index(0, 0, root_index)
        self.assertEqual(list_name_index.data(), "Type new list name here...")

    def test_add_two_parameter_value_list_values(self):
        list_name_index = self._edits.append_value_list(self._db_mngr, "a_value_list")
        view = self._db_editor.ui.treeView_parameter_value_list
        model = view.model()
        value_index1 = model.index(0, 0, list_name_index)
        with signal_waiter(self._db_mngr.list_values_added) as waiter:
            self._edits.view_editor.write_to_index(view, value_index1, "value_1")
            waiter.wait()
        self.assertEqual(model.index(0, 0, list_name_index).data(), "value_1")
        self.assertEqual(model.rowCount(list_name_index), 2)
        value_index2 = model.index(1, 0, list_name_index)
        with signal_waiter(self._db_mngr.list_values_added) as waiter:
            self._edits.view_editor.write_to_index(view, value_index2, "value_2")
            waiter.wait()
        while model.rowCount(list_name_index) != 3:
            QApplication.processEvents()
        self.assertEqual(model.index(1, 0, list_name_index).data(), "value_2")
        self._commit_changes_to_database("Add parameter value list.")
        data = self._db_mngr.query(self._db_map, "parameter_value_list_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "a_value_list")
        data = self._db_mngr.query(self._db_map, "list_value_sq")
        self.assertEqual(len(data), 2)
        for i, expected_value in enumerate(("value_1", "value_2")):
            self.assertEqual(from_database(data[i].value), expected_value)


class TestParameterValueListTreeViewWithExistingData(_Base):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()
        url = "sqlite:///" + os.path.join(self._temp_dir.name, "test_database.sqlite")
        db_map = DatabaseMapping(url, create=True)
        import_parameter_value_lists(db_map, (("value_list_1", "value_1"), ("value_list_1", "value_2")))
        db_map.commit_session("Add parameter value list.")
        db_map.connection.close()
        self._common_setup(url, create=False)

        view = self._db_editor.ui.treeView_parameter_value_list
        self._edits = _ParameterValueListEdits(view)
        model = view.model()
        root_index = model.index(0, 0)
        while model.rowCount(root_index) != 2:
            # Wait for fetching to finish.
            QApplication.processEvents()
        list_name_index = model.index(0, 0, root_index)
        model.fetchMore(list_name_index)
        while model.rowCount(list_name_index) != 3:
            QApplication.processEvents()

    def tearDown(self):
        self._common_tear_down()
        self._temp_dir.cleanup()

    def test_tree_has_correct_initial_contents(self):
        model = self._db_editor.ui.treeView_parameter_value_list.model()
        root_index = model.index(0, 0)
        self.assertEqual(model.rowCount(root_index), 2)
        list_name_index = model.index(0, 0, root_index)
        self.assertEqual(list_name_index.data(), "value_list_1")
        self.assertEqual(model.rowCount(list_name_index), 3)
        self.assertEqual(model.index(0, 0, list_name_index).data(), "value_1")
        self.assertEqual(model.index(1, 0, list_name_index).data(), "value_2")
        self.assertEqual(model.index(2, 0, list_name_index).data(), "Enter new list value here...")
        list_name_index = model.index(1, 0, root_index)
        self.assertEqual(list_name_index.data(), "Type new list name here...")

    def test_remove_value(self):
        view = self._db_editor.ui.treeView_parameter_value_list
        model = view.model()
        root_index = model.index(0, 0)
        list_name_index = model.index(0, 0, root_index)
        value_index = model.index(0, 0, list_name_index)
        view.selectionModel().setCurrentIndex(value_index, QItemSelectionModel.ClearAndSelect)
        with signal_waiter(self._db_mngr.list_values_removed) as waiter:
            view.remove_selected()
            waiter.wait()
        root_index = model.index(0, 0)
        self.assertEqual(model.rowCount(root_index), 2)
        list_name_index = model.index(0, 0, root_index)
        self.assertEqual(list_name_index.data(), "value_list_1")
        self.assertEqual(model.rowCount(list_name_index), 2)
        self.assertEqual(model.index(0, 0, list_name_index).data(), "value_2")
        self.assertEqual(model.index(1, 0, list_name_index).data(), "Enter new list value here...")
        list_name_index = model.index(1, 0, root_index)
        self.assertEqual(list_name_index.data(), "Type new list name here...")
        self._commit_changes_to_database("Remove parameter value list value.")
        data = self._db_mngr.query(self._db_map, "parameter_value_list_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "value_list_1")
        data = self._db_mngr.query(self._db_map, "list_value_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(from_database(data[0].value, data[0].type), "value_2")

    def test_remove_list(self):
        view = self._db_editor.ui.treeView_parameter_value_list
        model = view.model()
        root_index = model.index(0, 0)
        list_name_index = model.index(0, 0, root_index)
        view.selectionModel().setCurrentIndex(list_name_index, QItemSelectionModel.ClearAndSelect)
        with signal_waiter(self._db_mngr.parameter_value_lists_removed) as waiter:
            view.remove_selected()
            waiter.wait()
        root_index = model.index(0, 0)
        self.assertEqual(model.rowCount(root_index), 1)
        list_name_index = model.index(0, 0, root_index)
        self.assertEqual(model.rowCount(list_name_index), 0)
        self.assertEqual(list_name_index.data(), "Type new list name here...")
        self._commit_changes_to_database("Remove parameter value list.")
        data = self._db_mngr.query(self._db_map, "parameter_value_list_sq")
        self.assertEqual(len(data), 0)

    def test_change_value(self):
        view = self._db_editor.ui.treeView_parameter_value_list
        model = view.model()
        root_index = model.index(0, 0)
        list_name_index = model.index(0, 0, root_index)
        value_index1 = model.index(0, 0, list_name_index)
        with signal_waiter(self._db_mngr.list_values_updated) as waiter:
            self._edits.view_editor.write_to_index(view, value_index1, "new_value")
            waiter.wait()
        self.assertEqual(model.index(0, 0, list_name_index).data(), "new_value")
        self.assertEqual(model.index(1, 0, list_name_index).data(), "value_2")
        self._commit_changes_to_database("Update parameter value list value.")
        data = self._db_mngr.query(self._db_map, "parameter_value_list_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "value_list_1")
        data = self._db_mngr.query(self._db_map, "list_value_sq")
        self.assertEqual(len(data), 2)
        for i, expected_value in enumerate(("new_value", "value_2")):
            self.assertEqual(from_database(data[i].value, data[i].type), expected_value)

    def test_rename_list(self):
        view = self._db_editor.ui.treeView_parameter_value_list
        model = view.model()
        root_index = model.index(0, 0)
        list_name_index = model.index(0, 0, root_index)
        with signal_waiter(self._db_mngr.parameter_value_lists_updated) as waiter:
            self._edits.view_editor.write_to_index(view, list_name_index, "new_list_name")
            waiter.wait()
        self.assertEqual(model.rowCount(root_index), 2)
        list_name_index = model.index(0, 0, root_index)
        self.assertEqual(list_name_index.data(), "new_list_name")
        self.assertEqual(model.rowCount(list_name_index), 3)
        self.assertEqual(model.index(0, 0, list_name_index).data(), "value_1")
        self.assertEqual(model.index(1, 0, list_name_index).data(), "value_2")
        self.assertEqual(model.index(2, 0, list_name_index).data(), "Enter new list value here...")
        list_name_index = model.index(1, 0, root_index)
        self.assertEqual(list_name_index.data(), "Type new list name here...")
        self._commit_changes_to_database("Rename parameter value list.")
        data = self._db_mngr.query(self._db_map, "parameter_value_list_sq")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "new_list_name")
        data = self._db_mngr.query(self._db_map, "list_value_sq")
        self.assertEqual(len(data), 2)
        for i, expected_value in enumerate(("value_1", "value_2")):
            self.assertEqual(from_database(data[i].value), expected_value)


class TestToolFeatureTreeViewWithInitiallyEmptyDatabase(_Base):
    def setUp(self):
        self._common_setup("sqlite://", create=True)
        self._value_list_edits = _ParameterValueListEdits(self._db_editor.ui.treeView_parameter_value_list)

    def tearDown(self):
        self._common_tear_down()

    def test_empty_tree_has_correct_contents(self):
        model = self._db_editor.ui.treeView_tool_feature.model()
        db_index = model.index(0, 0)
        self.assertTrue(db_index.isValid())
        self.assertEqual(model.rowCount(db_index), 2)
        feature_root_index = model.index(0, 0, db_index)
        self.assertEqual(feature_root_index.data(), "feature")
        self.assertEqual(model.rowCount(feature_root_index), 1)
        feature_index = model.index(0, 0, feature_root_index)
        self.assertEqual(feature_index.data(), "Enter new feature here...")
        self.assertEqual(model.rowCount(feature_index), 0)
        tool_root_index = model.index(1, 0, db_index)
        self.assertEqual(tool_root_index.data(), "tool")
        self.assertEqual(model.rowCount(tool_root_index), 1)
        tool_index = model.index(0, 0, tool_root_index)
        self.assertEqual(tool_index.data(), "Type new tool name here...")
        self.assertEqual(model.rowCount(tool_index), 0)

    def test_add_feature_without_parameter_definitions_opens_error_box(self):
        tree_view = self._db_editor.ui.treeView_tool_feature
        model = tree_view.model()
        db_index = model.index(0, 0)
        feature_root_index = model.index(0, 0, db_index)
        feature_index = model.index(0, 0, feature_root_index)
        view_edit = _EditorDelegateMocking()
        with mock.patch.object(self._db_editor, "msg_error") as mock_error:
            view_edit.try_to_edit_index(tree_view, feature_index)
            mock_error.emit.assert_called_once_with(
                "There aren't any listed parameter definitions to create features from."
            )

    def test_add_feature(self):
        self._add_parameter_with_value_list()
        self._add_feature()
        model = self._db_editor.ui.treeView_tool_feature.model()
        db_index = model.index(0, 0)
        feature_root_index = model.index(0, 0, db_index)
        self.assertEqual(model.rowCount(feature_root_index), 2)
        self.assertEqual(model.index(0, 0, feature_root_index).data(), "my_object_class/my_parameter")
        self.assertEqual(model.index(1, 0, feature_root_index).data(), "Enter new feature here...")

    def test_add_tool(self):
        self._add_tool()
        view = self._db_editor.ui.treeView_tool_feature
        model = view.model()
        db_index = model.index(0, 0)
        tool_root_index = model.index(1, 0, db_index)
        self.assertEqual(model.rowCount(tool_root_index), 2)
        tool_index = model.index(0, 0, tool_root_index)
        self.assertEqual(tool_index.data(), "my_tool")
        self.assertEqual(model.index(1, 0, tool_root_index).data(), "Type new tool name here...")
        self.assertEqual(model.rowCount(tool_index), 1)
        tool_feature_root_index = model.index(0, 0, tool_index)
        self.assertEqual(tool_feature_root_index.data(), "tool_feature")
        self.assertEqual(model.rowCount(tool_feature_root_index), 1)
        tool_feature_index = model.index(0, 0, tool_feature_root_index)
        self.assertEqual(tool_feature_index.data(), "Type tool feature name here...")
        self.assertEqual(model.rowCount(tool_feature_index), 0)

    def test_add_tool_feature(self):
        self._add_parameter_with_value_list()
        self._add_feature()
        self._add_tool()
        self._add_tool_feature()
        view = self._db_editor.ui.treeView_tool_feature
        model = view.model()
        db_index = model.index(0, 0)
        tool_root_index = model.index(1, 0, db_index)
        tool_index = model.index(0, 0, tool_root_index)
        tool_feature_root_index = model.index(0, 0, tool_index)
        self.assertEqual(model.rowCount(tool_feature_root_index), 2)
        tool_feature_index = model.index(0, 0, tool_feature_root_index)
        self.assertEqual(tool_feature_index.data(), "my_object_class/my_parameter")
        self.assertEqual(model.rowCount(tool_feature_index), 2)
        self.assertEqual(model.index(1, 0, tool_feature_root_index).data(), "Type tool feature name here...")
        self.assertEqual(model.index(0, 0, tool_feature_index).data(), "required: no")
        method_root_index = model.index(1, 0, tool_feature_index)
        self.assertEqual(method_root_index.data(), "tool_feature_method")
        self.assertEqual(model.rowCount(method_root_index), 1)
        method_index = model.index(0, 0, method_root_index)
        self.assertEqual(method_index.data(), "Enter new method here...")
        self.assertEqual(model.rowCount(method_index), 0)

    def test_add_tool_feature_method(self):
        self._add_parameter_with_value_list()
        self._add_feature()
        self._add_tool()
        self._add_tool_feature()
        view = self._db_editor.ui.treeView_tool_feature
        model = view.model()
        db_index = model.index(0, 0)
        tool_root_index = model.index(1, 0, db_index)
        tool_index = model.index(0, 0, tool_root_index)
        tool_feature_root_index = model.index(0, 0, tool_index)
        tool_feature_index = model.index(0, 0, tool_feature_root_index)
        method_root_index = model.index(1, 0, tool_feature_index)
        method_index = model.index(0, 0, method_root_index)
        view_edit = _EditorDelegateMocking()
        with signal_waiter(self._db_mngr.tool_feature_methods_added) as waiter:
            view_edit.write_to_index(view, method_index, "2.3")
            waiter.wait()
        method_root_index = model.index(1, 0, tool_feature_index)
        self.assertEqual(model.rowCount(method_root_index), 2)
        method_index = model.index(0, 0, method_root_index)
        self.assertEqual(method_index.data(), "2.3")
        self.assertEqual(model.rowCount(method_index), 0)
        self.assertEqual(model.index(1, 0, method_root_index).data(), "Enter new method here...")

    def _add_parameter_with_value_list(self):
        self._value_list_edits.append_value_list(self._db_mngr, "my_value_list")
        self._value_list_edits.append_value(self._db_mngr, "my_value_list", 2.3)
        object_tree_view = self._db_editor.ui.treeView_object
        _add_object_class(object_tree_view, "my_object_class")
        object_parameter_definition_view = self._db_editor.ui.tableView_object_parameter_definition
        with signal_waiter(self._db_mngr.parameter_definitions_added) as waiter:
            _append_table_row(object_parameter_definition_view, ["my_object_class", "my_parameter", "my_value_list"])
            waiter.wait()

    def _add_feature(self):
        view = self._db_editor.ui.treeView_tool_feature
        model = view.model()
        db_index = model.index(0, 0)
        feature_root_index = model.index(0, 0, db_index)
        feature_index = model.index(0, 0, feature_root_index)
        view_edit = _EditorDelegateMocking()
        with signal_waiter(self._db_mngr.features_added) as waiter:
            view_edit.write_to_index(view, feature_index, "my_object_class/my_parameter")
            waiter.wait()

    def _add_tool(self):
        view = self._db_editor.ui.treeView_tool_feature
        model = view.model()
        db_index = model.index(0, 0)
        tool_root_index = model.index(1, 0, db_index)
        tool_index = model.index(0, 0, tool_root_index)
        view_edit = _EditorDelegateMocking()
        with signal_waiter(self._db_mngr.tools_added) as waiter:
            view_edit.write_to_index(view, tool_index, "my_tool")
            waiter.wait()

    def _add_tool_feature(self):
        view = self._db_editor.ui.treeView_tool_feature
        model = view.model()
        db_index = model.index(0, 0)
        tool_root_index = model.index(1, 0, db_index)
        tool_index = model.index(0, 0, tool_root_index)
        tool_feature_root_index = model.index(0, 0, tool_index)
        tool_feature_index = model.index(0, 0, tool_feature_root_index)
        view_edit = _EditorDelegateMocking()
        with signal_waiter(self._db_mngr.tool_features_added) as waiter:
            view_edit.write_to_index(view, tool_feature_index, "my_object_class/my_parameter")
            waiter.wait()


class TestToolFeatureTreeViewWithExistingData(_Base):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()
        url = "sqlite:///" + os.path.join(self._temp_dir.name, "test_database.sqlite")
        db_map = DatabaseMapping(url, create=True)
        import_parameter_value_lists(
            db_map, (("value_list_1", 5.0), ("value_list_1", 2.3), ("value_list_2", "law_of_fives"))
        )
        import_object_classes(db_map, ("my_object_class",))
        import_object_parameters(
            db_map,
            (
                ("my_object_class", "parameter_1", None, "value_list_1"),
                ("my_object_class", "parameter_2", None, "value_list_2"),
            ),
        )
        import_features(db_map, (("my_object_class", "parameter_1"), ("my_object_class", "parameter_2")))
        import_tools(db_map, ("tool_1", "tool_2"))
        import_tool_features(
            db_map,
            (
                ("tool_1", "my_object_class", "parameter_1"),
                ("tool_1", "my_object_class", "parameter_2"),
                ("tool_2", "my_object_class", "parameter_1"),
                ("tool_2", "my_object_class", "parameter_2"),
            ),
        )
        import_tool_feature_methods(
            db_map,
            (
                ("tool_1", "my_object_class", "parameter_1", 5.0),
                ("tool_1", "my_object_class", "parameter_1", 2.3),
                ("tool_1", "my_object_class", "parameter_2", "law_of_fives"),
                ("tool_2", "my_object_class", "parameter_1", 5.0),
                ("tool_2", "my_object_class", "parameter_1", 2.3),
                ("tool_2", "my_object_class", "parameter_2", "law_of_fives"),
            ),
        )
        db_map.commit_session("Add tool feature methods.")
        db_map.connection.close()
        self._common_setup(url, create=False)
        view = self._db_editor.ui.treeView_tool_feature
        model = view.model()
        db_index = model.index(0, 0)
        tool_root_index = model.index(1, 0, db_index)
        while model.rowCount(tool_root_index) != 3:
            # Wait for fetching to finish.
            QApplication.processEvents()
        tool_index = model.index(1, 0, tool_root_index)
        tool_feature_root_index = model.index(0, 0, tool_index)
        while model.rowCount(tool_feature_root_index) != 3:
            model.fetchMore(tool_feature_root_index)
            QApplication.processEvents()
        tool_feature_index = model.index(1, 0, tool_feature_root_index)
        method_root_index = model.index(1, 0, tool_feature_index)
        while model.rowCount(method_root_index) != 2:
            model.fetchMore(method_root_index)
            QApplication.processEvents()
        # Also fetch parameter value lists
        view = self._db_editor.ui.treeView_parameter_value_list
        model = view.model()
        root_index = model.index(0, 0)
        while model.rowCount(root_index) != 3:
            # Wait for fetching to finish.
            QApplication.processEvents()
        list_name_index1 = model.index(0, 0, root_index)
        list_name_index2 = model.index(1, 0, root_index)
        model.fetchMore(list_name_index1)
        while model.rowCount(list_name_index1) != 3:
            # Wait for fetching to finish.
            QApplication.processEvents()
        model.fetchMore(list_name_index2)
        while model.rowCount(list_name_index2) != 2:
            QApplication.processEvents()
        with signal_waiter(self._db_mngr.parameter_value_lists_updated) as waiter:
            waiter.wait()

    def tearDown(self):
        self._common_tear_down()
        self._temp_dir.cleanup()

    def test_tree_has_correct_initial_contents(self):
        view = self._db_editor.ui.treeView_tool_feature
        model = view.model()
        db_index = model.index(0, 0)
        feature_root_index = model.index(0, 0, db_index)
        self.assertEqual(model.rowCount(feature_root_index), 3)
        self.assertEqual(model.index(0, 0, feature_root_index).data(), "my_object_class/parameter_1")
        self.assertEqual(model.index(1, 0, feature_root_index).data(), "my_object_class/parameter_2")
        self.assertEqual(model.index(2, 0, feature_root_index).data(), "Enter new feature here...")
        tool_root_index = model.index(1, 0, db_index)
        self.assertEqual(model.rowCount(tool_root_index), 3)
        self.assertEqual(model.index(0, 0, tool_root_index).data(), "tool_1")
        self.assertEqual(model.index(1, 0, tool_root_index).data(), "tool_2")
        self.assertEqual(model.index(2, 0, tool_root_index).data(), "Type new tool name here...")
        tool_index = model.index(0, 0, tool_root_index)
        self.assertEqual(model.rowCount(tool_index), 1)
        tool_feature_root_index = model.index(0, 0, tool_index)
        self.assertEqual(model.rowCount(tool_feature_root_index), 3)
        self.assertEqual(model.index(0, 0, tool_feature_root_index).data(), "my_object_class/parameter_1")
        self.assertEqual(model.index(1, 0, tool_feature_root_index).data(), "my_object_class/parameter_2")
        self.assertEqual(model.index(2, 0, tool_feature_root_index).data(), "Type tool feature name here...")
        tool_feature_index = model.index(0, 0, tool_feature_root_index)
        self.assertEqual(model.rowCount(tool_feature_index), 2)
        self.assertEqual(model.index(0, 0, tool_feature_index).data(), "required: no")
        self.assertEqual(model.index(1, 0, tool_feature_index).data(), "tool_feature_method")
        method_root_index = model.index(1, 0, tool_feature_index)
        self.assertEqual(model.rowCount(method_root_index), 3)
        self.assertEqual(model.index(0, 0, method_root_index).data(), "5.0")
        self.assertEqual(model.index(1, 0, method_root_index).data(), "2.3")
        self.assertEqual(model.index(2, 0, method_root_index).data(), "Enter new method here...")
        tool_feature_index = model.index(1, 0, tool_feature_root_index)
        self.assertEqual(model.rowCount(tool_feature_index), 2)
        self.assertEqual(model.index(0, 0, tool_feature_index).data(), "required: no")
        self.assertEqual(model.index(1, 0, tool_feature_index).data(), "tool_feature_method")
        method_root_index = model.index(1, 0, tool_feature_index)
        self.assertEqual(model.rowCount(method_root_index), 2)
        self.assertEqual(model.index(0, 0, method_root_index).data(), "law_of_fives")
        self.assertEqual(model.index(1, 0, method_root_index).data(), "Enter new method here...")
        tool_index = model.index(1, 0, tool_root_index)
        self.assertEqual(model.rowCount(tool_index), 1)
        tool_feature_root_index = model.index(0, 0, tool_index)
        self.assertEqual(model.rowCount(tool_feature_root_index), 3)
        self.assertEqual(model.index(0, 0, tool_feature_root_index).data(), "my_object_class/parameter_1")
        self.assertEqual(model.index(1, 0, tool_feature_root_index).data(), "my_object_class/parameter_2")
        self.assertEqual(model.index(2, 0, tool_feature_root_index).data(), "Type tool feature name here...")
        tool_feature_index = model.index(0, 0, tool_feature_root_index)
        self.assertEqual(model.rowCount(tool_feature_index), 2)
        self.assertEqual(model.index(0, 0, tool_feature_index).data(), "required: no")
        self.assertEqual(model.index(1, 0, tool_feature_index).data(), "tool_feature_method")
        method_root_index = model.index(1, 0, tool_feature_index)
        self.assertEqual(model.rowCount(method_root_index), 3)
        self.assertEqual(model.index(0, 0, method_root_index).data(), "5.0")
        self.assertEqual(model.index(1, 0, method_root_index).data(), "2.3")
        self.assertEqual(model.index(2, 0, method_root_index).data(), "Enter new method here...")
        tool_feature_index = model.index(1, 0, tool_feature_root_index)
        self.assertEqual(model.rowCount(tool_feature_index), 2)
        self.assertEqual(model.index(0, 0, tool_feature_index).data(), "required: no")
        self.assertEqual(model.index(1, 0, tool_feature_index).data(), "tool_feature_method")
        method_root_index = model.index(1, 0, tool_feature_index)
        self.assertEqual(model.rowCount(method_root_index), 2)
        self.assertEqual(model.index(0, 0, method_root_index).data(), "law_of_fives")
        self.assertEqual(model.index(1, 0, method_root_index).data(), "Enter new method here...")


if __name__ == '__main__':
    unittest.main()
