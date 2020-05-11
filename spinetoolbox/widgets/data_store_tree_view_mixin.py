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
Contains the TreeViewMixin class.

:author: M. Marin (KTH)
:date:   26.11.2018
"""
from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import QInputDialog
from .custom_menus import EntityTreeContextMenu
from .data_store_add_items_dialogs import (
    AddObjectClassesDialog,
    AddObjectsDialog,
    AddRelationshipClassesDialog,
    AddRelationshipsDialog,
)
from .data_store_edit_items_dialogs import (
    EditObjectClassesDialog,
    EditObjectsDialog,
    EditRelationshipClassesDialog,
    EditRelationshipsDialog,
    RemoveEntitiesDialog,
)
from ..mvcmodels.entity_tree_models import ObjectTreeModel, RelationshipTreeModel
from ..helpers import busy_effect, get_save_file_name_in_last_dir
from ..spine_db_parcel import SpineDBParcel


class TreeViewMixin:
    """Provides object and relationship trees for the data store form.
    """

    _object_classes_added = Signal()
    _relationship_classes_added = Signal()
    _object_classes_fetched = Signal()
    _relationship_classes_fetched = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Selected ids
        self.object_tree_model = ObjectTreeModel(self, self.db_mngr, *self.db_maps)
        self.relationship_tree_model = RelationshipTreeModel(self, self.db_mngr, *self.db_maps)
        self.ui.treeView_object.setModel(self.object_tree_model)
        self.ui.treeView_relationship.setModel(self.relationship_tree_model)

    def add_menu_actions(self):
        """Adds toggle view actions to View menu."""
        super().add_menu_actions()
        self.ui.menuView.addSeparator()
        self.ui.menuView.addAction(self.ui.dockWidget_relationship_tree.toggleViewAction())

    def connect_signals(self):
        """Connects signals to slots."""
        super().connect_signals()
        self.ui.treeView_object.selectionModel().selectionChanged.connect(self._handle_object_tree_selection_changed)
        self.ui.treeView_relationship.selectionModel().selectionChanged.connect(
            self._handle_relationship_tree_selection_changed
        )
        self.ui.actionAdd_object_classes.triggered.connect(self.show_add_object_classes_form)
        self.ui.actionAdd_objects.triggered.connect(self.show_add_objects_form)
        self.ui.actionAdd_relationship_classes.triggered.connect(self.show_add_relationship_classes_form)
        self.ui.actionAdd_relationships.triggered.connect(self.show_add_relationships_form)
        self.ui.actionEdit_object_classes.triggered.connect(self.show_edit_object_classes_form)
        self.ui.actionEdit_objects.triggered.connect(self.show_edit_objects_form)
        self.ui.actionEdit_relationship_classes.triggered.connect(self.show_edit_relationship_classes_form)
        self.ui.actionEdit_relationships.triggered.connect(self.show_edit_relationships_form)
        self.object_tree_model.remove_selection_requested.connect(self.show_remove_object_tree_items_form)
        self.relationship_tree_model.remove_selection_requested.connect(self.show_remove_relationship_tree_items_form)
        self.ui.treeView_object.edit_key_pressed.connect(self.edit_object_tree_items)
        self.ui.treeView_object.customContextMenuRequested.connect(self.show_object_tree_context_menu)
        self.ui.treeView_object.doubleClicked.connect(self.find_next_relationship)
        self.ui.treeView_relationship.edit_key_pressed.connect(self.edit_relationship_tree_items)
        self.ui.treeView_relationship.customContextMenuRequested.connect(self.show_relationship_tree_context_menu)
        self._object_classes_added.connect(lambda: self.ui.treeView_object.resizeColumnToContents(0))
        self._object_classes_fetched.connect(lambda: self.ui.treeView_object.expand(self.object_tree_model.root_index))
        self._relationship_classes_added.connect(lambda: self.ui.treeView_relationship.resizeColumnToContents(0))
        self._relationship_classes_fetched.connect(
            lambda: self.ui.treeView_relationship.expand(self.relationship_tree_model.root_index)
        )
        self.ui.treeView_object.expanded.connect(self._resize_tree_view_columns)
        self.ui.treeView_object.collapsed.connect(self._resize_tree_view_columns)
        self.ui.treeView_relationship.expanded.connect(self._resize_tree_view_columns)
        self.ui.treeView_relationship.collapsed.connect(self._resize_tree_view_columns)

    @Slot("QModelIndex")
    def _resize_tree_view_columns(self, index):
        view = {
            self.object_tree_model: self.ui.treeView_object,
            self.relationship_tree_model: self.ui.treeView_relationship,
        }.get(index.model())
        if view is not None:
            view.resizeColumnToContents(0)

    def init_models(self):
        """Initializes models."""
        super().init_models()
        self.object_tree_model.build_tree()
        self.relationship_tree_model.build_tree()
        self.ui.actionExport.setEnabled(self.object_tree_model.root_item.has_children())

    @Slot("QItemSelection", "QItemSelection")
    def _handle_object_tree_selection_changed(self, selected, deselected):
        """Updates object filter and sets default rows."""
        indexes = self.ui.treeView_object.selectionModel().selectedIndexes()
        self.object_tree_model.select_indexes(indexes)
        self._clear_tree_selections_silently(self.ui.treeView_relationship)
        self.set_default_parameter_data(self.ui.treeView_object.currentIndex())
        self._update_object_filter()

    @Slot("QItemSelection", "QItemSelection")
    def _handle_relationship_tree_selection_changed(self, selected, deselected):
        """Updates relationship filter and sets default rows."""
        indexes = self.ui.treeView_relationship.selectionModel().selectedIndexes()
        self.relationship_tree_model.select_indexes(indexes)
        self._clear_tree_selections_silently(self.ui.treeView_object)
        self.set_default_parameter_data(self.ui.treeView_relationship.currentIndex())
        self._update_relationship_filter()

    @staticmethod
    def _clear_tree_selections_silently(tree_view):
        """Clears the selections on a given abstract item view without emitting any signals."""
        selection_model = tree_view.selectionModel()
        if selection_model.hasSelection():
            selection_model.blockSignals(True)
            selection_model.clearSelection()
            selection_model.blockSignals(False)

    @staticmethod
    def _db_map_items(indexes):
        """Groups items from given tree indexes by db map.

        Returns:
            dict: lists of dictionary items keyed by DiffDatabaseMapping
        """
        d = dict()
        for index in indexes:
            item = index.model().item_from_index(index)
            for db_map in item.db_maps:
                d.setdefault(db_map, []).append(item.db_map_data(db_map))
        return d

    def _ids_per_db_map(self, indexes):
        return self.db_mngr.ids_per_db_map(self._db_map_items(indexes))

    def _ids_per_db_map_and_class(self, indexes):
        return self.db_mngr.ids_per_db_map_and_class(self._db_map_items(indexes))

    def _update_object_filter(self):
        """Updates object filter according to object tree selection."""
        selected_obj_clss = set(self.object_tree_model.selected_object_class_indexes.keys())
        selected_objs = set(self.object_tree_model.selected_object_indexes.keys())
        selected_rel_clss = set(self.object_tree_model.selected_relationship_class_indexes.keys())
        # Compute active indexes by merging in the parents from lower levels recursively
        active_rels = set(self.object_tree_model.selected_relationship_indexes.keys())
        active_rel_clss = selected_rel_clss | {ind.parent() for ind in active_rels}
        active_objs = selected_objs | {ind.parent() for ind in active_rel_clss}
        active_obj_clss = selected_obj_clss | {ind.parent() for ind in active_objs}
        self.selected_ent_cls_ids["object class"] = self._ids_per_db_map(active_obj_clss)
        self.selected_ent_cls_ids["relationship class"] = self._ids_per_db_map(active_rel_clss)
        self.selected_ent_ids["object"] = self._ids_per_db_map_and_class(active_objs)
        self.selected_ent_ids["relationship"] = self._ids_per_db_map_and_class(active_rels)
        # Cascade (note that we carefuly select where to cascade from, to avoid 'circularity')
        from_obj_clss = selected_obj_clss | {ind.parent() for ind in selected_objs}
        from_objs = selected_objs | {ind.parent() for ind in selected_rel_clss}
        cascading_rel_clss = self.db_mngr.find_cascading_relationship_classes(self._ids_per_db_map(from_obj_clss))
        cascading_rels = self.db_mngr.find_cascading_relationships(self._ids_per_db_map(from_objs))
        for db_map, ids in self.db_mngr.ids_per_db_map(cascading_rel_clss).items():
            self.selected_ent_cls_ids["relationship class"].setdefault(db_map, set()).update(ids)
        for (db_map, class_id), ids in self.db_mngr.ids_per_db_map_and_class(cascading_rels).items():
            self.selected_ent_ids["relationship"].setdefault((db_map, class_id), set()).update(ids)
        self.update_filter()

    def _update_relationship_filter(self):
        """Update relationship filter according to relationship tree selection."""
        selected_rel_clss = set(self.relationship_tree_model.selected_relationship_class_indexes.keys())
        active_rels = set(self.relationship_tree_model.selected_relationship_indexes.keys())
        active_rel_clss = selected_rel_clss | {ind.parent() for ind in active_rels}
        self.selected_ent_cls_ids["relationship class"] = self._ids_per_db_map(active_rel_clss)
        self.selected_ent_ids["relationship"] = self._ids_per_db_map_and_class(active_rels)
        self.update_filter()

    @Slot("QModelIndex")
    def edit_object_tree_items(self, current):
        """Starts editing the given index in the object tree."""
        current = self.ui.treeView_object.currentIndex()
        current_type = self.object_tree_model.item_from_index(current).item_type
        if current_type == 'object class':
            self.show_edit_object_classes_form()
        elif current_type == 'object':
            self.show_edit_objects_form()
        elif current_type == 'relationship class':
            self.show_edit_relationship_classes_form()
        elif current_type == 'relationship':
            self.show_edit_relationships_form()

    @Slot("QModelIndex")
    def edit_relationship_tree_items(self, current):
        """Starts editing the given index in the relationship tree."""
        current = self.ui.treeView_relationship.currentIndex()
        current_type = self.relationship_tree_model.item_from_index(current).item_type
        if current_type == 'relationship class':
            self.show_edit_relationship_classes_form()
        elif current_type == 'relationship':
            self.show_edit_relationships_form()

    @Slot("QPoint")
    def show_object_tree_context_menu(self, pos):
        """Shows the context menu for object tree.

        Args:
            pos (QPoint): Mouse position
        """
        index = self.ui.treeView_object.indexAt(pos)
        if index.column() != 0:
            return
        global_pos = self.ui.treeView_object.viewport().mapToGlobal(pos)
        object_tree_context_menu = EntityTreeContextMenu(self, global_pos, index)
        option = object_tree_context_menu.get_action()
        if option == "Copy text":
            self.ui.treeView_object.copy()
        elif option == "Add object classes":
            self.show_add_object_classes_form()
        elif option == "Add objects":
            self.call_show_add_objects_form(index)
        elif option == "Add relationship classes":
            self.call_show_add_relationship_classes_form(index)
        elif option == "Add relationships":
            self.call_show_add_relationships_form(index)
        elif option == "Edit object classes":
            self.show_edit_object_classes_form()
        elif option == "Edit objects":
            self.show_edit_objects_form()
        elif option == "Edit relationship classes":
            self.show_edit_relationship_classes_form()
        elif option == "Edit relationships":
            self.show_edit_relationships_form()
        elif option == "Find next":
            self.find_next_relationship(index)
        elif option == "Remove selection":
            self.show_remove_object_tree_items_form()
        elif option == "Fully expand":
            self.fully_expand_view(self.ui.treeView_object)
        elif option == "Fully collapse":
            self.fully_collapse_view(self.ui.treeView_object)
        elif option == "Duplicate":
            self.duplicate_object(index)
        elif option == "Export selection":
            self.export_selection(self.object_tree_model)
        else:  # No option selected
            pass
        object_tree_context_menu.deleteLater()

    @Slot("QPoint")
    def show_relationship_tree_context_menu(self, pos):
        """Shows the context for relationship tree.

        Args:
            pos (QPoint): Mouse position
        """
        index = self.ui.treeView_relationship.indexAt(pos)
        if index.column() != 0:
            return
        global_pos = self.ui.treeView_relationship.viewport().mapToGlobal(pos)
        relationship_tree_context_menu = EntityTreeContextMenu(self, global_pos, index)
        option = relationship_tree_context_menu.get_action()
        if option == "Copy text":
            self.ui.treeView_relationship.copy()
        elif option == "Add relationship classes":
            self.show_add_relationship_classes_form()
        elif option == "Add relationships":
            self.call_show_add_relationships_form(index)
        elif option == "Edit relationship classes":
            self.show_edit_relationship_classes_form()
        elif option == "Edit relationships":
            self.show_edit_relationships_form()
        elif option == "Remove selection":
            self.show_remove_relationship_tree_items_form()
        elif option == "Fully expand":
            self.fully_expand_view(self.ui.treeView_relationship)
        elif option == "Fully collapse":
            self.fully_collapse_view(self.ui.treeView_relationship)
        elif option == "Export selection":
            self.export_selection(self.relationship_tree_model)
        else:  # No option selected
            pass
        relationship_tree_context_menu.deleteLater()

    def export_selection(self, model):
        self.qsettings.beginGroup(self.settings_group)
        file_path, selected_filter = get_save_file_name_in_last_dir(
            self.qsettings,
            "exportDBSelection",
            self,
            "Export selection",
            self._get_base_dir(),
            "SQLite (*.sqlite);; JSON file (*.json);; Excel file (*.xlsx)",
        )
        self.qsettings.endGroup()
        if not file_path:  # File selection cancelled
            return
        parcel = self._make_data_parcel_from_selection(model)
        data_for_export = self._make_data_for_export(parcel.data)
        if selected_filter.startswith("JSON"):
            self.export_to_json(file_path, data_for_export)
        elif selected_filter.startswith("SQLite"):
            self.export_to_sqlite(file_path, data_for_export)
        elif selected_filter.startswith("Excel"):
            self.export_to_excel(file_path, data_for_export)
        else:
            raise ValueError()

    def _make_data_parcel_from_selection(self, model):
        """Returns a SpineDBParcel with data from the given model's selection.

        Args:
            model (EntityTreeModel)

        Returns:
            SpineDBParcel
        """
        parcel = SpineDBParcel(self.db_mngr)
        db_map_obj_cls_ids = self._ids_per_db_map(model.selected_object_class_indexes)
        db_map_obj_ids = self._ids_per_db_map(model.selected_object_indexes)
        db_map_rel_cls_ids = self._ids_per_db_map(model.selected_relationship_class_indexes)
        db_map_rel_ids = self._ids_per_db_map(model.selected_relationship_indexes)
        parcel.push_object_class_ids(db_map_obj_cls_ids)
        parcel.push_object_ids(db_map_obj_ids)
        parcel.push_relationship_class_ids(db_map_rel_cls_ids)
        parcel.push_relationship_ids(db_map_rel_ids)
        return parcel

    @busy_effect
    def fully_expand_view(self, view):
        view.expanded.disconnect(self._resize_tree_view_columns)
        model = view.model()
        for index in view.selectionModel().selectedIndexes():
            if index.column() != 0:
                continue
            for item in model.visit_all(index):
                view.expand(model.index_from_item(item))
        view.expanded.connect(self._resize_tree_view_columns)
        view.resizeColumnToContents(0)

    @busy_effect
    def fully_collapse_view(self, view):
        view.collapsed.disconnect(self._resize_tree_view_columns)
        model = view.model()
        for index in view.selectionModel().selectedIndexes():
            if index.column() != 0:
                continue
            for item in model.visit_all(index):
                view.collapse(model.index_from_item(item))
        view.collapsed.connect(self._resize_tree_view_columns)
        view.resizeColumnToContents(0)

    @Slot("QModelIndex")
    def find_next_relationship(self, index):
        """Expands next occurrence of a relationship in object tree."""
        next_index = self.object_tree_model.find_next_relationship_index(index)
        if not next_index:
            return
        self.ui.treeView_object.setCurrentIndex(next_index)
        self.ui.treeView_object.scrollTo(next_index)
        self.ui.treeView_object.expand(next_index)

    def _get_cascading_relationships(self, object_item):
        """
        Returns a dict mapping db maps to a list of cascading relationship for the given object item.

        Args:
            object_item (ObjectItem)

        Returns:
            dict(DiffDatabaseMapping, list)
        """
        return {
            db_map: [
                rel
                for rel in self.db_mngr.get_items(db_map, "relationship")
                if str(object_item.db_map_id(db_map)) in rel["object_id_list"].split(",")
            ]
            for db_map in object_item.db_maps
        }

    @staticmethod
    def _get_duplicate_object_name_list(object_name_list, orig_name, dup_name):
        return tuple(name if name != orig_name else dup_name for name in object_name_list.split(","))

    def duplicate_object(self, index):
        """
        Duplicates the object at the given object tree model index.

        Args:
            index (QModelIndex)
        """
        orig_name = index.data()
        dup_name, ok = QInputDialog.getText(
            self, "Duplicate object", "Enter a name for the duplicate object:", text=orig_name + "_copy"
        )
        if not ok:
            return
        class_name = index.parent().data()
        object_item = index.internalPointer()
        cascading_relationships = self._get_cascading_relationships(object_item)
        data = {"objects": [(class_name, dup_name)]}
        data["relationships"] = [
            (rel["class_name"], self._get_duplicate_object_name_list(rel["object_name_list"], orig_name, dup_name))
            for db_map in object_item.db_maps
            for rel in cascading_relationships[db_map]
        ]
        data["object_parameter_values"] = [
            (class_name, dup_name, val["parameter_name"], val["formatted_value"])
            for db_map in object_item.db_maps
            for val in self.db_mngr.get_items_by_field(
                db_map, "parameter value", "object_id", object_item.db_map_id(db_map)
            )
        ]
        data["relationship_parameter_values"] = [
            (
                val["relationship_class_name"],
                self._get_duplicate_object_name_list(val["object_name_list"], orig_name, dup_name),
                val["parameter_name"],
                val["formatted_value"],
            )
            for db_map in object_item.db_maps
            for rel in cascading_relationships[db_map]
            for val in self.db_mngr.get_items_by_field(db_map, "parameter value", "relationship_id", rel["id"])
        ]
        self.db_mngr.import_data({db_map: data for db_map in object_item.db_maps}, command_text="Duplicate object")

    def call_show_add_objects_form(self, index):
        class_name = index.internalPointer().display_data
        self.show_add_objects_form(class_name=class_name)

    def call_show_add_relationship_classes_form(self, index):
        object_class_one_name = index.internalPointer().display_data
        self.show_add_relationship_classes_form(object_class_one_name=object_class_one_name)

    def call_show_add_relationships_form(self, index):
        item = index.internalPointer()
        relationship_class_key = item.display_id
        try:
            object_name = item.parent_item.display_data
            object_class_name = item.parent_item.parent_item.display_data
        except AttributeError:
            object_name = object_class_name = None
        self.show_add_relationships_form(
            relationship_class_key=relationship_class_key, object_class_name=object_class_name, object_name=object_name
        )

    @Slot(bool)
    def show_add_object_classes_form(self, checked=False):
        """Shows dialog to let user select preferences for new object classes."""
        dialog = AddObjectClassesDialog(self, self.db_mngr, *self.db_maps)
        dialog.show()

    @Slot(bool)
    def show_add_objects_form(self, checked=False, class_name=""):
        """Shows dialog to let user select preferences for new objects."""
        dialog = AddObjectsDialog(self, self.db_mngr, *self.db_maps, class_name=class_name)
        dialog.show()

    @Slot(bool)
    def show_add_relationship_classes_form(self, checked=False, object_class_one_name=None):
        """Shows dialog to let user select preferences for new relationship class."""
        dialog = AddRelationshipClassesDialog(
            self, self.db_mngr, *self.db_maps, object_class_one_name=object_class_one_name
        )
        dialog.show()

    @Slot(bool)
    def show_add_relationships_form(
        self, checked=False, relationship_class_key=(), object_class_name="", object_name=""
    ):
        """Shows dialog to let user select preferences for new relationships."""
        dialog = AddRelationshipsDialog(
            self,
            self.db_mngr,
            *self.db_maps,
            relationship_class_key=relationship_class_key,
            object_class_name=object_class_name,
            object_name=object_name,
        )
        dialog.show()

    @Slot(bool)
    def show_edit_object_classes_form(self, checked=False):
        selected = {ind.internalPointer() for ind in self.object_tree_model.selected_object_class_indexes}
        dialog = EditObjectClassesDialog(self, self.db_mngr, selected)
        dialog.show()

    @Slot(bool)
    def show_edit_objects_form(self, checked=False):
        selected = {ind.internalPointer() for ind in self.object_tree_model.selected_object_indexes}
        dialog = EditObjectsDialog(self, self.db_mngr, selected)
        dialog.show()

    @Slot(bool)
    def show_edit_relationship_classes_form(self, checked=False):
        selected = {
            ind.internalPointer()
            for ind in self.object_tree_model.selected_relationship_class_indexes.keys()
            | self.relationship_tree_model.selected_relationship_class_indexes.keys()
        }
        dialog = EditRelationshipClassesDialog(self, self.db_mngr, selected)
        dialog.show()

    @Slot(bool)
    def show_edit_relationships_form(self, checked=False):
        # NOTE: Only edits relationships that are in the same class
        selected = {
            ind.internalPointer()
            for ind in self.object_tree_model.selected_relationship_indexes.keys()
            | self.relationship_tree_model.selected_relationship_indexes.keys()
        }
        first_item = next(iter(selected))
        relationship_class_key = first_item.parent_item.display_id
        selected = {item for item in selected if item.parent_item.display_id == relationship_class_key}
        dialog = EditRelationshipsDialog(self, self.db_mngr, selected, relationship_class_key)
        dialog.show()

    @Slot()
    def show_remove_object_tree_items_form(self):
        """Shows form to remove items from object treeview."""
        selected = {
            item_type: [ind.model().item_from_index(ind) for ind in indexes]
            for item_type, indexes in self.object_tree_model.selected_indexes.items()
        }
        dialog = RemoveEntitiesDialog(self, self.db_mngr, selected)
        dialog.show()

    @Slot()
    def show_remove_relationship_tree_items_form(self):
        """Shows form to remove items from relationship treeview."""
        selected = {
            item_type: [ind.model().item_from_index(ind) for ind in indexes]
            for item_type, indexes in self.relationship_tree_model.selected_indexes.items()
        }
        dialog = RemoveEntitiesDialog(self, self.db_mngr, selected)
        dialog.show()

    def notify_items_changed(self, action, item_type, db_map_data):
        """Enables or disables actions and informs the user about what just happened."""
        super().notify_items_changed(action, item_type, db_map_data)
        self.ui.actionExport.setEnabled(self.object_tree_model.root_item.has_children())

    def receive_object_classes_fetched(self, db_map_data):
        super().receive_object_classes_fetched(db_map_data)
        self._object_classes_fetched.emit()

    def receive_relationship_classes_fetched(self, db_map_data):
        super().receive_object_classes_fetched(db_map_data)
        self._relationship_classes_fetched.emit()

    def receive_object_classes_added(self, db_map_data):
        super().receive_object_classes_added(db_map_data)
        self.object_tree_model.add_object_classes(db_map_data)
        self._object_classes_added.emit()

    def receive_objects_added(self, db_map_data):
        super().receive_objects_added(db_map_data)
        self.object_tree_model.add_objects(db_map_data)

    def receive_relationship_classes_added(self, db_map_data):
        super().receive_relationship_classes_added(db_map_data)
        self.object_tree_model.add_relationship_classes(db_map_data)
        self.relationship_tree_model.add_relationship_classes(db_map_data)
        self._relationship_classes_added.emit()

    def receive_relationships_added(self, db_map_data):
        super().receive_relationships_added(db_map_data)
        self.object_tree_model.add_relationships(db_map_data)
        self.relationship_tree_model.add_relationships(db_map_data)

    def receive_object_classes_updated(self, db_map_data):
        super().receive_object_classes_updated(db_map_data)
        self.object_tree_model.update_object_classes(db_map_data)

    def receive_objects_updated(self, db_map_data):
        super().receive_objects_updated(db_map_data)
        self.object_tree_model.update_objects(db_map_data)

    def receive_relationship_classes_updated(self, db_map_data):
        super().receive_relationship_classes_updated(db_map_data)
        self.object_tree_model.update_relationship_classes(db_map_data)
        self.relationship_tree_model.update_relationship_classes(db_map_data)

    def receive_relationships_updated(self, db_map_data):
        super().receive_relationships_updated(db_map_data)
        self.object_tree_model.update_relationships(db_map_data)
        self.relationship_tree_model.update_relationships(db_map_data)

    def receive_object_classes_removed(self, db_map_data):
        super().receive_object_classes_removed(db_map_data)
        self.object_tree_model.remove_object_classes(db_map_data)

    def receive_objects_removed(self, db_map_data):
        super().receive_objects_removed(db_map_data)
        self.object_tree_model.remove_objects(db_map_data)

    def receive_relationship_classes_removed(self, db_map_data):
        super().receive_relationship_classes_removed(db_map_data)
        self.object_tree_model.remove_relationship_classes(db_map_data)
        self.relationship_tree_model.remove_relationship_classes(db_map_data)

    def receive_relationships_removed(self, db_map_data):
        super().receive_relationships_removed(db_map_data)
        self.object_tree_model.remove_relationships(db_map_data)
        self.relationship_tree_model.remove_relationships(db_map_data)
