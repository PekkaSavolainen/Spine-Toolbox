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
Classes for handling models in tree and graph views.

:authors: M. Marin (KTH)
:date:   28.6.2019
"""

import os
import json
from PySide2.QtCore import Qt, Slot, QModelIndex, QSortFilterProxyModel, QAbstractItemModel
from PySide2.QtGui import QStandardItem, QStandardItemModel, QBrush, QFont, QIcon, QGuiApplication
from helpers import busy_effect, format_string_list, strip_json_data
from spinedb_api import SpineDBAPIError
from models import MinimalTableModel, EmptyRowModel, HybridTableModel


class ObjectClassListModel(QStandardItemModel):
    """A class to list object classes in the GraphViewForm."""

    # TODO: go from db_map to db_maps

    def __init__(self, graph_view_form):
        """Initialize class"""
        super().__init__(graph_view_form)
        self._graph_view_form = graph_view_form
        self.db_map = graph_view_form.db_map
        self.add_more_index = None

    def populate_list(self):
        """Populate model."""
        self.clear()
        object_class_list = [x for x in self.db_map.object_class_list()]
        for object_class in object_class_list:
            object_class_item = QStandardItem(object_class.name)
            data = {"type": "object_class"}
            data.update(object_class._asdict())
            object_class_item.setData(data, Qt.UserRole + 1)
            object_class_item.setData(object_class.name, Qt.ToolTipRole)
            self.appendRow(object_class_item)
        add_more_item = QStandardItem()
        add_more_item.setData("Add more...", Qt.DisplayRole)
        self.appendRow(add_more_item)
        self.add_more_index = self.indexFromItem(add_more_item)

    def add_object_class(self, object_class):
        """Add object class item to model."""
        object_class_item = QStandardItem(object_class.name)
        data = {"type": "object_class", **object_class._asdict()}
        object_class_item.setData(data, Qt.UserRole + 1)
        object_class_item.setData(object_class.name, Qt.ToolTipRole)
        for i in range(self.rowCount()):
            visited_index = self.index(i, 0)
            visited_display_order = visited_index.data(Qt.UserRole + 1)['display_order']
            if visited_display_order >= object_class.display_order:
                self.insertRow(i, object_class_item)
                return
        self.insertRow(self.rowCount() - 1, object_class_item)

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index."""
        if role == Qt.DecorationRole and index.data(Qt.UserRole + 1):
            return self._graph_view_form.icon_mngr.object_icon(index.data(Qt.UserRole + 1)["name"])
        return super().data(index, role)


class RelationshipClassListModel(QStandardItemModel):
    """A class to list relationship classes in the GraphViewForm."""

    # TODO: go from db_map to db_maps

    def __init__(self, graph_view_form):
        """Initialize class"""
        super().__init__(graph_view_form)
        self._graph_view_form = graph_view_form
        self.db_map = graph_view_form.db_map
        self.add_more_index = None

    def populate_list(self):
        """Populate model."""
        self.clear()
        relationship_class_list = [x for x in self.db_map.wide_relationship_class_list()]
        for relationship_class in relationship_class_list:
            relationship_class_item = QStandardItem(relationship_class.name)
            data = {"type": "relationship_class"}
            data.update(relationship_class._asdict())
            relationship_class_item.setData(data, Qt.UserRole + 1)
            relationship_class_item.setData(relationship_class.name, Qt.ToolTipRole)
            self.appendRow(relationship_class_item)
        add_more_item = QStandardItem()
        add_more_item.setData("Add more...", Qt.DisplayRole)
        self.appendRow(add_more_item)
        self.add_more_index = self.indexFromItem(add_more_item)

    def add_relationship_class(self, relationship_class):
        """Add relationship class."""
        relationship_class_item = QStandardItem(relationship_class.name)
        data = {"type": "relationship_class", **relationship_class._asdict()}
        relationship_class_item.setData(data, Qt.UserRole + 1)
        relationship_class_item.setData(relationship_class.name, Qt.ToolTipRole)
        self.insertRow(self.rowCount() - 1, relationship_class_item)

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index."""
        if role == Qt.DecorationRole and index.data(Qt.UserRole + 1):
            return self._graph_view_form.icon_mngr.relationship_icon(
                index.data(Qt.UserRole + 1)["object_class_name_list"]
            )
        return super().data(index, role)


class ObjectTreeModel(QStandardItemModel):
    """A class to display Spine data structure in a treeview
    with object classes at the outer level.
    """

    def __init__(self, parent, flat=False):
        """Initialize class"""
        super().__init__(parent)
        self._parent = parent
        self.db_maps = parent.db_maps
        self.bold_font = QFont()
        self.bold_font.setBold(True)
        self.flat = flat
        self._fetched = {}
        self.root_item = None

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index."""
        if index.column() != 0:
            return super().data(index, role)
        if role == Qt.ForegroundRole:
            item_type = index.data(Qt.UserRole)
            if item_type.endswith('class') and not self.hasChildren(index):
                return QBrush(Qt.gray)
        elif role == Qt.DecorationRole:
            item_type = index.data(Qt.UserRole)
            if item_type == 'root':
                return QIcon(":/symbols/Spine_symbol.png")
            if item_type == 'object_class':
                return self._parent.icon_mngr.object_icon(index.data(Qt.DisplayRole))
            if item_type == 'object':
                return self._parent.icon_mngr.object_icon(index.parent().data(Qt.DisplayRole))
            if item_type == 'relationship_class':
                return self._parent.icon_mngr.relationship_icon(index.data(Qt.ToolTipRole))
            if item_type == 'relationship':
                return self._parent.icon_mngr.relationship_icon(index.parent().data(Qt.ToolTipRole))
        return super().data(index, role)

    def backward_sweep(self, index, call=None):
        """Sweep the tree from the given index towards the root, and apply `call` on each."""
        current = index
        while True:
            if call:
                call(current)
            # Try and visit parent
            next_ = current.parent()
            if not next_.isValid():
                break
            current = next_
            continue

    def forward_sweep(self, index, call=None):
        """Sweep the tree from the given index towards the leaves, and apply `call` on each."""
        if call:
            call(index)
        if not self.hasChildren(index):
            return
        current = index
        back_to_parent = False  # True if moving back to the parent index
        while True:
            if call:
                call(current)
            if not back_to_parent:
                # Try and visit first child
                next_ = self.index(0, 0, current)
                if next_.isValid():
                    back_to_parent = False
                    current = next_
                    continue
            # Try and visit next sibling
            next_ = current.sibling(current.row() + 1, 0)
            if next_.isValid():
                back_to_parent = False
                current = next_
                continue
            # Go back to parent
            next_ = self.parent(current)
            if next_ != index:
                back_to_parent = True
                current = next_
                continue
            break

    def hasChildren(self, parent):
        """Return True if not fetched, so the user can try and expand it."""
        if not parent.isValid():
            return super().hasChildren(parent)
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return super().hasChildren(parent)
        if parent_type == 'relationship':
            return False
        if self.flat and parent_type in ('object', 'relationship_class'):
            return False
        fetched = self._fetched[parent_type]
        if parent in fetched:
            return super().hasChildren(parent)
        return True

    def canFetchMore(self, parent):
        """Return True if not fetched."""
        if not parent.isValid():
            return True
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return True
        fetched = self._fetched[parent_type]
        return parent not in fetched

    @busy_effect
    def fetchMore(self, parent):
        """Build the deeper levels of the tree"""
        if not parent.isValid():
            return False
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return False
        parent_type = parent.data(Qt.UserRole)
        fetched = self._fetched[parent_type]
        if parent_type == 'object_class':
            parent_db_map_dict = parent.data(Qt.UserRole + 1)
            object_class_item = self.itemFromIndex(parent)
            for db_map, object_class in parent_db_map_dict.items():
                self.add_objects_to_class(db_map, db_map.object_list(class_id=object_class['id']), object_class_item)
            fetched.add(parent)
        elif parent_type == 'object':
            parent_db_map_dict = parent.data(Qt.UserRole + 1)
            object_item = self.itemFromIndex(parent)
            for db_map, object_ in parent_db_map_dict.items():
                relationship_classes = db_map.wide_relationship_class_list(object_class_id=object_['class_id'])
                self.add_relationships_classes_to_object(db_map, relationship_classes, object_item)
            fetched.add(parent)
        elif parent_type == 'relationship_class':
            grand_parent_db_map_dict = parent.parent().data(Qt.UserRole + 1)
            parent_db_map_dict = parent.data(Qt.UserRole + 1)
            rel_cls_item = self.itemFromIndex(parent)
            for db_map, relationship_class in parent_db_map_dict.items():
                object_ = grand_parent_db_map_dict[db_map]  # TODO: is KeyError possible here?
                relationships = db_map.wide_relationship_list(
                    class_id=relationship_class['id'], object_id=object_['id']
                )
                self.add_relationships_to_class(db_map, relationships, rel_cls_item)
            fetched.add(parent)
        self.dataChanged.emit(parent, parent)

    def build_tree(self, flat=False):
        """Build the first level of the tree"""
        self.clear()
        self.setHorizontalHeaderLabels(["item", "databases"])
        self._fetched = {"object_class": set(), "object": set(), "relationship_class": set(), "relationship": set()}
        self.root_item = QStandardItem('root')
        self.root_item.setData('root', Qt.UserRole)
        db_item = QStandardItem(", ".join([self._parent.db_map_to_name[x] for x in self.db_maps]))
        for db_map in self.db_maps:
            self.add_object_classes(db_map, db_map.object_class_list())
        self.appendRow([self.root_item, db_item])

    def new_object_class_row(self, db_map, object_class):
        """Returns new object class item."""
        object_class_item = QStandardItem(object_class.name)
        object_class_item.setData('object_class', Qt.UserRole)
        object_class_item.setData({db_map: object_class._asdict()}, Qt.UserRole + 1)
        object_class_item.setData(object_class.description, Qt.ToolTipRole)
        object_class_item.setData(self.bold_font, Qt.FontRole)
        db_item = QStandardItem(self._parent.db_map_to_name[db_map])
        return [object_class_item, db_item]

    def new_object_row(self, db_map, object_):
        """Returns new object item."""
        object_item = QStandardItem(object_.name)
        object_item.setData('object', Qt.UserRole)
        object_item.setData({db_map: object_._asdict()}, Qt.UserRole + 1)
        object_item.setData(object_.description, Qt.ToolTipRole)
        db_item = QStandardItem(self._parent.db_map_to_name[db_map])
        return [object_item, db_item]

    def new_relationship_class_row(self, db_map, relationship_class):
        """Returns new relationship class item."""
        relationship_class_item = QStandardItem(relationship_class.name)
        relationship_class_item.setData('relationship_class', Qt.UserRole)
        relationship_class_item.setData({db_map: relationship_class._asdict()}, Qt.UserRole + 1)
        relationship_class_item.setData(relationship_class.object_class_name_list, Qt.ToolTipRole)
        relationship_class_item.setData(self.bold_font, Qt.FontRole)
        db_item = QStandardItem(self._parent.db_map_to_name[db_map])
        return [relationship_class_item, db_item]

    def new_relationship_row(self, db_map, relationship):
        """Returns new relationship item."""
        relationship_item = QStandardItem(relationship.object_name_list)
        relationship_item.setData('relationship', Qt.UserRole)
        relationship_item.setData({db_map: relationship._asdict()}, Qt.UserRole + 1)
        db_item = QStandardItem(self._parent.db_map_to_name[db_map])
        return [relationship_item, db_item]

    def add_object_classes(self, db_map, object_classes):
        """Add object class items to given db.
        """
        existing_rows = [
            [self.root_item.child(i, 0), self.root_item.child(i, 1)] for i in range(self.root_item.rowCount())
        ]
        existing_row_d = {row[0].text(): row for row in existing_rows}
        new_rows = []
        for object_class in object_classes:
            if object_class.name in existing_row_d:
                # Already in model, append db_map information
                object_class_item, db_item = existing_row_d[object_class.name]
                db_map_dict = object_class_item.data(Qt.UserRole + 1)
                db_map_dict[db_map] = object_class._asdict()
                databases = db_item.data(Qt.DisplayRole)
                databases += "," + self._parent.db_map_to_name[db_map]
                db_item.setData(databases, Qt.DisplayRole)
                # Add objects from this db if fetched
                object_class_index = self.indexFromItem(object_class_item)
                if not self.canFetchMore(object_class_index):
                    self.add_objects_to_class(db_map, db_map.object_list(class_id=object_class.id), object_class_item)
            else:
                new_rows.append(self.new_object_class_row(db_map, object_class))
        # Insert rows at right position given display_order
        for row in new_rows:
            object_class_item = row[0]
            db_map_dict = object_class_item.data(Qt.UserRole + 1)
            object_class = db_map_dict[db_map]
            for i in range(self.root_item.rowCount()):
                visited_object_class_item = self.root_item.child(i)
                visited_db_map_dict = visited_object_class_item.data(Qt.UserRole + 1)
                if db_map not in visited_db_map_dict:
                    continue
                visited_object_class = visited_db_map_dict[db_map]
                if visited_object_class['display_order'] > object_class['display_order']:
                    self.root_item.insertRow(i, row)
                    break
            else:
                self.root_item.appendRow(row)

    def add_objects(self, db_map, objects):
        """Add object items to the given db."""
        object_dict = {}
        for object_ in objects:
            object_dict.setdefault(object_.class_id, list()).append(object_)
        for i in range(self.root_item.rowCount()):
            object_class_item = self.root_item.child(i, 0)
            object_class_index = self.indexFromItem(object_class_item)
            if self.canFetchMore(object_class_index):
                continue
            db_map_dict = object_class_item.data(Qt.UserRole + 1)
            if db_map not in db_map_dict:
                # Can someone be adding objects to a class that doesn't exist in the same db?
                continue
            object_class = db_map_dict[db_map]
            object_class_id = object_class['id']
            if object_class_id not in object_dict:
                continue
            objects = object_dict[object_class_id]
            self.add_objects_to_class(db_map, objects, object_class_item)

    def add_relationship_classes(self, db_map, relationship_classes):
        """Add relationship class items to model."""
        relationship_class_dict = {}
        for relationship_class in relationship_classes:
            for object_class_id in relationship_class.object_class_id_list.split(","):
                relationship_class_dict.setdefault(int(object_class_id), list()).append(relationship_class)
        for i in range(self.root_item.rowCount()):
            object_class_item = self.root_item.child(i, 0)
            db_map_dict = object_class_item.data(Qt.UserRole + 1)
            if db_map not in db_map_dict:
                # Can someone be adding relationship classes where one of the classes doesn't exist in the same db?
                continue
            object_class = db_map_dict[db_map]
            object_class_id = object_class['id']
            if object_class_id not in relationship_class_dict:
                continue
            relationship_classes = relationship_class_dict[object_class_id]
            for j in range(object_class_item.rowCount()):
                object_item = object_class_item.child(j, 0)
                object_index = self.indexFromItem(object_item)
                if self.canFetchMore(object_index):
                    continue
                self.add_relationships_classes_to_object(db_map, relationship_classes, object_item)

    def add_relationships(self, db_map, relationships):
        """Add relationship items to model."""
        relationship_dict = {}
        for relationship in relationships:
            class_id = relationship.class_id
            for object_id in relationship.object_id_list.split(","):
                d = relationship_dict.setdefault(int(object_id), {})
                d.setdefault(class_id, []).append(relationship)
        for i in range(self.root_item.rowCount()):
            object_class_item = self.root_item.child(i, 0)
            for j in range(object_class_item.rowCount()):
                object_item = object_class_item.child(j, 0)
                db_map_dict = object_item.data(Qt.UserRole + 1)
                if db_map not in db_map_dict:
                    # Can someone be adding relationships where one of the objects doesn't exist in the same db?
                    continue
                object_ = db_map_dict[db_map]
                object_id = object_['id']
                if object_id not in relationship_dict:
                    continue
                class_relationship_dict = relationship_dict[object_id]
                for k in range(object_item.rowCount()):
                    rel_cls_item = object_item.child(k, 0)
                    rel_cls_index = self.indexFromItem(rel_cls_item)
                    if self.canFetchMore(rel_cls_index):
                        continue
                    db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
                    if db_map not in db_map_dict:
                        # Can someone be adding relationships to a class that doesn't exist in the same db?
                        continue
                    rel_cls = db_map_dict[db_map]
                    rel_cls_id = rel_cls['id']
                    if rel_cls_id not in class_relationship_dict:
                        continue
                    relationships = class_relationship_dict[rel_cls_id]
                    self.add_relationships_to_class(db_map, relationships, rel_cls_item)

    def add_objects_to_class(self, db_map, objects, object_class_item):
        existing_rows = [
            [object_class_item.child(j, 0), object_class_item.child(j, 1)] for j in range(object_class_item.rowCount())
        ]
        existing_row_d = {row[0].text(): row for row in existing_rows}
        new_rows = []
        for object_ in objects:
            if object_.name in existing_row_d:
                # Already in model, append db_map information
                object_item, db_item = existing_row_d[object_.name]
                db_map_dict = object_item.data(Qt.UserRole + 1)
                db_map_dict[db_map] = object_._asdict()
                databases = db_item.data(Qt.DisplayRole)
                databases += "," + self._parent.db_map_to_name[db_map]
                db_item.setData(databases, Qt.DisplayRole)
                # Add relationship classes from this db if fetched
                object_index = self.indexFromItem(object_item)
                if not self.canFetchMore(object_index):
                    relationship_classes = db_map.wide_relationship_class_list(object_class_id=object_.class_id)
                    self.add_relationships_classes_to_object(db_map, relationship_classes, object_item)
            else:
                new_rows.append(self.new_object_row(db_map, object_))
        for row in new_rows:
            object_class_item.appendRow(row)

    def add_relationships_classes_to_object(self, db_map, relationship_classes, object_item):
        existing_rows = [[object_item.child(j, 0), object_item.child(j, 1)] for j in range(object_item.rowCount())]
        existing_row_d = {(row[0].text(), row[0].data(Qt.ToolTipRole)): row for row in existing_rows}
        new_rows = []
        for rel_cls in relationship_classes:
            if (rel_cls.name, rel_cls.object_class_name_list) in existing_row_d:
                # Already in model, append db_map information
                rel_cls_item, db_item = existing_row_d[rel_cls.name, rel_cls.object_class_name_list]
                db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
                db_map_dict[db_map] = rel_cls._asdict()
                databases = db_item.data(Qt.DisplayRole)
                databases += "," + self._parent.db_map_to_name[db_map]
                db_item.setData(databases, Qt.DisplayRole)
                # Add relationships from this db if fetched
                rel_cls_index = self.indexFromItem(rel_cls_item)
                if not self.canFetchMore(rel_cls_index):
                    object_id = object_item.data(Qt.UserRole + 1)[db_map]['id']
                    relationships = db_map.wide_relationship_list(class_id=rel_cls.id, object_id=object_id)
                    self.add_relationships_to_class(db_map, relationships, rel_cls_item)
            else:
                new_rows.append(self.new_relationship_class_row(db_map, rel_cls))
        for row in new_rows:
            object_item.appendRow(row)

    def add_relationships_to_class(self, db_map, relationships, rel_cls_item):
        existing_rows = [[rel_cls_item.child(j, 0), rel_cls_item.child(j, 1)] for j in range(rel_cls_item.rowCount())]
        existing_row_d = {row[0].text(): row for row in existing_rows}
        new_rows = []
        for relationship in relationships:
            if relationship.object_name_list in existing_row_d:
                # Already in model, append db_map information
                relationship_item, db_item = existing_row_d[relationship.object_name_list]
                db_map_dict = relationship_item.data(Qt.UserRole + 1)
                db_map_dict[db_map] = relationship._asdict()
                databases = db_item.data(Qt.DisplayRole)
                databases += "," + self._parent.db_map_to_name[db_map]
                db_item.setData(databases, Qt.DisplayRole)
            else:
                new_rows.append(self.new_relationship_row(db_map, relationship))
        for row in new_rows:
            rel_cls_item.appendRow(row)

    def update_object_classes(self, db_map, object_classes):
        """Update object classes in the model.
        This of course means updating the object class name in relationship class items.
        """
        object_class_d = {x.id: x for x in object_classes}
        existing_rows = [
            [self.root_item.child(i, 0), self.root_item.child(i, 1)] for i in range(self.root_item.rowCount())
        ]
        existing_row_d = {row[0].text(): row for row in existing_rows}
        removed_rows = []
        for i in range(self.root_item.rowCount()):
            object_class_item = self.root_item.child(i)
            db_map_dict = object_class_item.data(Qt.UserRole + 1)
            if db_map not in db_map_dict:
                continue
            object_class = db_map_dict[db_map]
            object_class_id = object_class['id']
            upd_object_class = object_class_d.pop(object_class_id, None)
            if not upd_object_class:
                continue
            if upd_object_class.name in existing_row_d:
                # Already in model
                removed_rows.append(i)
                object_class_item, db_item = existing_row_d[upd_object_class.name]
                db_map_dict = object_class_item.data(Qt.UserRole + 1)
                db_map_dict[db_map] = upd_object_class._asdict()
                databases = db_item.data(Qt.DisplayRole)
                databases += "," + self._parent.db_map_to_name[db_map]
                db_item.setData(databases, Qt.DisplayRole)
                # Add objects from this db if fetched
                object_class_index = self.indexFromItem(object_class_item)
                if not self.canFetchMore(object_class_index):
                    self.add_objects_to_class(db_map, db_map.object_list(class_id=object_class_id), object_class_item)
            else:
                db_map_dict[db_map] = upd_object_class._asdict()
                object_class_item.setData(upd_object_class.name, Qt.DisplayRole)
                object_class_item.setData(upd_object_class.description, Qt.ToolTipRole)
            # Update child relationship class items
            for j in range(object_class_item.rowCount()):
                object_item = object_class_item.child(j, 0)
                for k in range(object_item.rowCount()):
                    rel_cls_item = object_item.child(k, 0)
                    db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
                    if db_map not in db_map_dict:
                        continue
                    rel_cls = db_map_dict[db_map]
                    obj_cls_name_list = rel_cls['object_class_name_list'].split(',')
                    obj_cls_id_list = [int(x) for x in rel_cls['object_class_id_list'].split(',')]
                    for k, id_ in enumerate(obj_cls_id_list):
                        if id_ == object_class_id:
                            obj_cls_name_list[k] = upd_object_class.name
                    rel_cls['object_class_name_list'] = ",".join(obj_cls_name_list)
                    rel_cls_item.setData(",".join(obj_cls_name_list), Qt.ToolTipRole)
        self.remove_object_class_rows(db_map, removed_rows)

    def update_objects(self, db_map, objects):
        """Update object in the model.
        This of course means updating the object name in relationship items.
        """
        object_d = {}
        for object_ in objects:
            object_d.setdefault(object_.class_id, {}).update({object_.id: object_})
        for i in range(self.root_item.rowCount()):
            object_class_item = self.root_item.child(i, 0)
            db_map_dict = object_class_item.data(Qt.UserRole + 1)
            if db_map not in db_map_dict:
                continue
            object_class = db_map_dict[db_map]
            object_class_id = object_class['id']
            class_object_dict = object_d.pop(object_class_id, None)
            if not class_object_dict:
                continue
            existing_rows = [
                [object_class_item.child(j, 0), object_class_item.child(j, 1)]
                for j in range(object_class_item.rowCount())
            ]
            existing_row_d = {row[0].text(): row for row in existing_rows}
            removed_rows = []
            for j in range(object_class_item.rowCount()):
                object_item = object_class_item.child(j, 0)
                db_map_dict = object_item.data(Qt.UserRole + 1)
                if db_map not in db_map_dict:
                    continue
                object_ = db_map_dict[db_map]
                object_id = object_['id']
                upd_object = class_object_dict.pop(object_id, None)
                if not upd_object:
                    continue
                if upd_object.name in existing_row_d:
                    # Already in model
                    removed_rows.append(j)
                    object_item, db_item = existing_row_d[upd_object.name]
                    db_map_dict = object_item.data(Qt.UserRole + 1)
                    db_map_dict[db_map] = upd_object._asdict()
                    databases = db_item.data(Qt.DisplayRole)
                    databases += "," + self._parent.db_map_to_name[db_map]
                    db_item.setData(databases, Qt.DisplayRole)
                    # Add relationship classes from this db if fetched
                    object_index = self.indexFromItem(object_item)
                    if not self.canFetchMore(object_index):
                        relationship_classes = db_map.wide_relationship_class_list(object_class_id=object_class_id)
                        self.add_relationships_classes_to_object(db_map, relationship_classes, object_item)
                else:
                    db_map_dict[db_map] = upd_object._asdict()
                    object_item.setData(upd_object.name, Qt.DisplayRole)
                    object_item.setData(upd_object.description, Qt.ToolTipRole)
                # Update child relationship items
                for k in range(object_item.rowCount()):
                    rel_cls_item = object_item.child(k, 0)
                    for l in range(rel_cls_item.rowCount()):
                        relationship_item = rel_cls_item.child(l, 0)
                        db_map_dict = relationship_item.data(Qt.UserRole + 1)
                        if db_map not in db_map_dict:
                            continue
                        relationship = db_map_dict[db_map]
                        object_name_list = relationship['object_name_list'].split(',')
                        object_id_list = [int(x) for x in relationship['object_id_list'].split(',')]
                        for k, id_ in enumerate(object_id_list):
                            if id_ == object_id:
                                object_name_list[k] = upd_object.name
                        relationship['object_name_list'] = ",".join(object_name_list)
                        relationship_item.setData(",".join(object_name_list), Qt.DisplayRole)
            self.remove_object_rows(db_map, removed_rows, object_class_item)

    def update_relationship_classes(self, db_map, relationship_classes):
        """Update relationship classes in the model."""
        relationship_class_dict = {}
        for rel_cls in relationship_classes:
            for object_class_id in rel_cls.object_class_id_list.split(","):
                relationship_class_dict.setdefault(int(object_class_id), {}).update({rel_cls.id: rel_cls})
        for i in range(self.root_item.rowCount()):
            object_class_item = self.root_item.child(i, 0)
            db_map_dict = object_class_item.data(Qt.UserRole + 1)
            if db_map not in db_map_dict:
                continue
            object_class = db_map_dict[db_map]
            object_class_id = object_class['id']
            class_rel_cls_dict = relationship_class_dict.pop(object_class_id, None)
            if not class_rel_cls_dict:
                continue
            for j in range(object_class_item.rowCount()):
                object_item = object_class_item.child(j, 0)
                existing_rows = [
                    [object_item.child(k, 0), object_item.child(k, 1)] for k in range(object_item.rowCount())
                ]
                existing_row_d = {(row[0].text(), row[0].data(Qt.ToolTipRole)): row for row in existing_rows}
                removed_rows = []
                for k in range(object_item.rowCount()):
                    rel_cls_item = object_item.child(k, 0)
                    db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
                    if db_map not in db_map_dict:
                        continue
                    rel_cls = db_map_dict[db_map]
                    rel_cls_id = rel_cls['id']
                    if rel_cls_id not in class_rel_cls_dict:
                        continue
                    upd_rel_cls = class_rel_cls_dict[rel_cls_id]
                    upd_rel_cls_key = (upd_rel_cls.name, upd_rel_cls.object_class_name_list)
                    if upd_rel_cls_key in existing_row_d:
                        # Already in model
                        removed_rows.append(k)
                        rel_cls_item, db_item = existing_row_d[upd_rel_cls_key]
                        db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
                        db_map_dict[db_map] = upd_rel_cls._asdict()
                        databases = db_item.data(Qt.DisplayRole)
                        databases += "," + self._parent.db_map_to_name[db_map]
                        db_item.setData(databases, Qt.DisplayRole)
                        # Add relationships from this db if fetched
                        rel_cls_index = self.indexFromItem(rel_cls_item)
                        if not self.canFetchMore(rel_cls_index):
                            object_id = object_item.data(Qt.UserRole + 1)[db_map]['id']
                            relationships = db_map.wide_relationship_list(class_id=rel_cls_id, object_id=object_id)
                            self.add_relationships_to_class(db_map, relationships, rel_cls_item)
                    else:
                        db_map_dict[db_map] = upd_rel_cls._asdict()
                        rel_cls_item.setData(upd_rel_cls.name, Qt.DisplayRole)
                self.remove_relationship_class_rows(db_map, removed_rows, object_item)

    def update_relationships(self, db_map, relationships):
        """Update relationships in the model.
        Move rows if the objects in the relationship change."""
        relationship_dict = {}
        for relationship in relationships:
            relationship_dict.setdefault(relationship.class_id, {}).update({relationship.id: relationship})
        relationships_to_add = set()
        for i in range(self.root_item.rowCount()):
            object_class_item = self.root_item.child(i, 0)
            for j in range(object_class_item.rowCount()):
                object_item = object_class_item.child(j, 0)
                for k in range(object_item.rowCount()):
                    rel_cls_item = object_item.child(k, 0)
                    db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
                    if db_map not in db_map_dict:
                        continue
                    rel_cls = db_map_dict[db_map]
                    rel_cls_id = rel_cls['id']
                    if rel_cls_id not in relationship_dict:
                        continue
                    class_relationship_dict = relationship_dict[rel_cls_id]
                    existing_rows = [
                        [rel_cls_item.child(k, 0), rel_cls_item.child(k, 1)] for k in range(rel_cls_item.rowCount())
                    ]
                    existing_row_d = {row[0].text(): row for row in existing_rows}
                    removed_rows = []
                    for l in range(rel_cls_item.rowCount()):
                        relationship_item = rel_cls_item.child(l, 0)
                        db_map_dict = relationship_item.data(Qt.UserRole + 1)
                        if db_map not in db_map_dict:
                            continue
                        relationship = db_map_dict[db_map]
                        relationship_id = relationship['id']
                        if relationship_id not in class_relationship_dict:
                            continue
                        upd_relationship = class_relationship_dict[relationship_id]
                        if upd_relationship.object_id_list != relationship['object_id_list']:
                            # Object id list changed, we don't know if the item belongs here anymore
                            removed_rows.append(j)
                            relationships_to_add.add(upd_relationship)
                        elif upd_relationship.object_name_list in existing_row_d:
                            # Already in model
                            removed_rows.append(j)
                            relationship_item, db_item = existing_row_d[upd_relationship.object_name_list]
                            db_map_dict = relationship_item.data(Qt.UserRole + 1)
                            db_map_dict[db_map] = upd_relationship._asdict()
                            databases = db_item.data(Qt.DisplayRole)
                            databases += "," + self._parent.db_map_to_name[db_map]
                            db_item.setData(databases, Qt.DisplayRole)
                        else:
                            db_map_dict[db_map] = upd_relationship._asdict()
                    self.remove_relationship_rows(db_map, removed_rows, rel_cls_item)
        self.add_relationships(db_map, relationships_to_add)

    def remove_object_class_rows(self, db_map, removed_rows):
        for row in sorted(removed_rows, reverse=True):
            object_class_item = self.root_item.child(row, 0)
            db_map_dict = object_class_item.data(Qt.UserRole + 1)
            del db_map_dict[db_map]
            if not db_map_dict:
                self.root_item.removeRow(row)
            else:
                db_item = self.root_item.child(row, 1)
                databases = db_item.data(Qt.DisplayRole).split(",")
                databases.remove(self._parent.db_map_to_name[db_map])
                db_item.setData(",".join(databases), Qt.DisplayRole)
                self.remove_object_rows(db_map, range(object_class_item.rowCount()), object_class_item)

    def remove_object_rows(self, db_map, removed_rows, object_class_item):
        for row in sorted(removed_rows, reverse=True):
            object_item = object_class_item.child(row, 0)
            db_map_dict = object_item.data(Qt.UserRole + 1)
            del db_map_dict[db_map]
            if not db_map_dict:
                object_class_item.removeRow(row)
            else:
                db_item = object_class_item.child(row, 1)
                databases = db_item.data(Qt.DisplayRole).split(",")
                databases.remove(self._parent.db_map_to_name[db_map])
                db_item.setData(",".join(databases), Qt.DisplayRole)
                self.remove_relationship_class_rows(db_map, range(object_item.rowCount()), object_item)

    def remove_relationship_class_rows(self, db_map, removed_rows, object_item):
        for row in sorted(removed_rows, reverse=True):
            rel_cls_item = object_item.child(row, 0)
            db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
            del db_map_dict[db_map]
            if not db_map_dict:
                object_item.removeRow(row)
            else:
                db_item = object_item.child(row, 1)
                databases = db_item.data(Qt.DisplayRole).split(",")
                databases.remove(self._parent.db_map_to_name[db_map])
                db_item.setData(",".join(databases), Qt.DisplayRole)
                self.remove_relationship_rows(db_map, range(rel_cls_item.rowCount()), rel_cls_item)

    def remove_relationship_rows(self, db_map, removed_rows, rel_cls_item):
        for row in sorted(removed_rows, reverse=True):
            relationship_item = rel_cls_item.child(row, 0)
            db_map_dict = relationship_item.data(Qt.UserRole + 1)
            del db_map_dict[db_map]
            if not db_map_dict:
                rel_cls_item.removeRow(row)
            else:
                db_item = rel_cls_item.child(row, 1)
                databases = db_item.data(Qt.DisplayRole).split(",")
                databases.remove(self._parent.db_map_to_name[db_map])
                db_item.setData(",".join(databases), Qt.DisplayRole)

    def remove_object_classes(self, db_map, removed_ids):
        """Remove object classes and their childs."""
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        removed_object_class_rows = []
        removed_relationship_class_row_d = {}
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type not in ('object_class', 'relationship_class'):
                continue
            # Get visited
            db_map_dict = visited_item.data(Qt.UserRole + 1)
            visited = db_map_dict.get(db_map)
            if not visited:
                continue
            if visited_type == 'object_class':
                visited_id = visited['id']
                if visited_id in removed_ids:
                    removed_object_class_rows.append(visited_item.row())
            elif visited_type == 'relationship_class':
                object_class_id_list = visited['object_class_id_list']
                if any(str(id) in object_class_id_list.split(',') for id in removed_ids):
                    visited_index = self.indexFromItem(visited_item.parent())
                    removed_relationship_class_row_d.setdefault(visited_index, []).append(visited_item.row())
        for object_index, rows in removed_relationship_class_row_d.items():
            object_item = self.itemFromIndex(object_index)
            self.remove_relationship_class_rows(db_map, rows, object_item)
        self.remove_object_class_rows(db_map, removed_object_class_rows)

    def remove_objects(self, db_map, removed_ids):
        """Remove objects and their childs."""
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        removed_object_row_d = {}
        removed_relationship_row_d = {}
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type not in ('object', 'relationship'):
                continue
            # Get visited
            db_map_dict = visited_item.data(Qt.UserRole + 1)
            visited = db_map_dict.get(db_map)
            if not visited:
                continue
            visited_index = self.indexFromItem(visited_item)
            if visited_type == 'object':
                visited_id = visited['id']
                if visited_id in removed_ids:
                    removed_object_row_d.setdefault(visited_index.parent(), []).append(visited_index.row())
            elif visited_type == 'relationship':
                object_id_list = visited['object_id_list']
                if any(id in [int(x) for x in object_id_list.split(',')] for id in removed_ids):
                    removed_relationship_row_d.setdefault(visited_index.parent(), []).append(visited_index.row())
        for rel_cls_index, rows in removed_relationship_row_d.items():
            rel_cls_item = self.itemFromIndex(rel_cls_index)
            self.remove_relationship_rows(db_map, rows, rel_cls_item)
        for obj_cls_index, rows in removed_object_row_d.items():
            obj_cls_item = self.itemFromIndex(obj_cls_index)
            self.remove_object_rows(db_map, rows, obj_cls_item)

    def remove_relationship_classes(self, db_map, removed_ids):
        """Remove relationship classes and their childs."""
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        removed_relationship_row_d = {}
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type != 'relationship_class':
                continue
            # Get visited
            db_map_dict = visited_item.data(Qt.UserRole + 1)
            visited = db_map_dict.get(db_map)
            if not visited:
                continue
            if visited['id'] in removed_ids:
                visited_index = self.indexFromItem(visited_item)
                removed_relationship_row_d.setdefault(visited_index.parent(), []).append(visited_index.row())
        for object_index, rows in removed_relationship_class_row_d.items():
            object_item = self.itemFromIndex(object_index)
            self.remove_relationship_class_rows(db_map, rows, object_item)

    def remove_relationships(self, db_map, removed_ids):
        """Remove relationships."""
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        removed_relationship_row_d = {}
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type != 'relationship':
                continue
            # Get visited
            db_map_dict = visited_item.data(Qt.UserRole + 1)
            visited = db_map_dict.get(db_map)
            if not visited:
                continue
            if visited['id'] in removed_ids:
                visited_index = self.indexFromItem(visited_item)
                removed_relationship_row_d.setdefault(visited_index.parent(), []).append(visited_index.row())
        for rel_cls_index, rows in removed_relationship_row_d.items():
            rel_cls_item = self.itemFromIndex(rel_cls_index)
            self.remove_relationship_rows(db_map, rows, rel_cls_item)

    def next_relationship_index(self, index):
        """Find and return next ocurrence of relationship item."""
        if index.data(Qt.UserRole) != 'relationship':
            return None
        object_name_list = index.data(Qt.DisplayRole)
        class_name = index.parent().data(Qt.DisplayRole)
        object_class_name_list = index.parent().data(Qt.ToolTipRole)
        items = [
            item
            for item in self.findItems(object_name_list, Qt.MatchExactly | Qt.MatchRecursive, column=0)
            if item.parent().data(Qt.DisplayRole) == class_name
            and item.parent().data(Qt.ToolTipRole) == object_class_name_list
        ]
        position = None
        for i, item in enumerate(items):
            if index == self.indexFromItem(item):
                position = i
                break
        if position is None:
            return None
        position = (position + 1) % len(items)
        return self.indexFromItem(items[position])


class RelationshipTreeModel(QStandardItemModel):
    """A class to display Spine data structure in a treeview
    with relationship classes at the outer level.
    """

    def __init__(self, parent):
        """Initialize class"""
        super().__init__(parent)
        self._parent = parent
        self.db_maps = parent.db_maps
        self.root_item = None
        self.bold_font = QFont()
        self.bold_font.setBold(True)
        self._fetched = set()

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index."""
        if index.column() != 0:
            return super().data(index, role)
        if role == Qt.ForegroundRole:
            item_type = index.data(Qt.UserRole)
            if item_type.endswith('class') and not self.hasChildren(index):
                return QBrush(Qt.gray)
        if role == Qt.DecorationRole:
            item_type = index.data(Qt.UserRole)
            if item_type == 'root':
                return QIcon(":/symbols/Spine_symbol.png")
            if item_type == 'relationship_class':
                return self._parent.icon_mngr.relationship_icon(index.data(Qt.ToolTipRole))
            if item_type == 'relationship':
                return self._parent.icon_mngr.relationship_icon(index.parent().data(Qt.ToolTipRole))
        return super().data(index, role)

    def hasChildren(self, parent):
        """Return True if not fetched, so the user can try and expand it."""
        if not parent.isValid():
            return super().hasChildren(parent)
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return super().hasChildren(parent)
        if parent_type == 'relationship':
            return False
        if parent in self._fetched:
            return super().hasChildren(parent)
        return True

    def canFetchMore(self, parent):
        """Return True if not fetched."""
        if not parent.isValid():
            return True
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return True
        return parent not in self._fetched

    @busy_effect
    def fetchMore(self, parent):
        """Build the deeper level of the tree"""
        if not parent.isValid():
            return False
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return False
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'relationship_class':
            parent_db_map_dict = parent.data(Qt.UserRole + 1)
            rel_cls_item = self.itemFromIndex(parent)
            for db_map, relationship_class in parent_db_map_dict.items():
                relationships = db_map.wide_relationship_list(class_id=relationship_class['id'])
                self.add_relationships_to_class(db_map, relationships, rel_cls_item)
            self._fetched.add(parent)
        self.dataChanged.emit(parent, parent)

    def build_tree(self):
        """Build the first level of the tree"""
        self.clear()
        self.setHorizontalHeaderLabels(["item", "databases"])
        self._fetched = set()
        self.root_item = QStandardItem('root')
        self.root_item.setData('root', Qt.UserRole)
        db_item = QStandardItem(", ".join([self._parent.db_map_to_name[x] for x in self.db_maps]))
        for db_map in self.db_maps:
            self.add_relationship_classes(db_map, db_map.wide_relationship_class_list())
        self.appendRow([self.root_item, db_item])

    def new_relationship_class_row(self, db_map, relationship_class):
        """Returns new relationship class item."""
        relationship_class_item = QStandardItem(relationship_class.name)
        relationship_class_item.setData('relationship_class', Qt.UserRole)
        relationship_class_item.setData({db_map: relationship_class._asdict()}, Qt.UserRole + 1)
        relationship_class_item.setData(relationship_class.object_class_name_list, Qt.ToolTipRole)
        relationship_class_item.setData(self.bold_font, Qt.FontRole)
        db_item = QStandardItem(self._parent.db_map_to_name[db_map])
        return [relationship_class_item, db_item]

    def new_relationship_row(self, db_map, relationship):
        """Returns new relationship item."""
        relationship_item = QStandardItem(relationship.object_name_list)
        relationship_item.setData('relationship', Qt.UserRole)
        relationship_item.setData({db_map: relationship._asdict()}, Qt.UserRole + 1)
        db_item = QStandardItem(self._parent.db_map_to_name[db_map])
        return [relationship_item, db_item]

    def add_relationship_classes(self, db_map, relationship_classes):
        """Add relationship class items to the model."""
        existing_rows = [
            [self.root_item.child(j, 0), self.root_item.child(j, 1)] for j in range(self.root_item.rowCount())
        ]
        existing_row_d = {(row[0].text(), row[0].data(Qt.ToolTipRole)): row for row in existing_rows}
        new_rows = []
        for rel_cls in relationship_classes:
            if (rel_cls.name, rel_cls.object_class_name_list) in existing_row_d:
                # Already in model, append db_map information
                rel_cls_item, db_item = existing_row_d[rel_cls.name, rel_cls.object_class_name_list]
                db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
                db_map_dict[db_map] = rel_cls._asdict()
                databases = db_item.data(Qt.DisplayRole)
                databases += "," + self._parent.db_map_to_name[db_map]
                db_item.setData(databases, Qt.DisplayRole)
            else:
                new_rows.append(self.new_relationship_class_row(db_map, rel_cls))
        for row in new_rows:
            self.root_item.appendRow(row)

    def add_relationships(self, db_map, relationships):
        """Add relationship items to model."""
        relationship_dict = {}
        for relationship in relationships:
            relationship_dict.setdefault(relationship.class_id, list()).append(relationship)
        for i in range(self.root_item.rowCount()):
            rel_cls_item = self.root_item.child(i, 0)
            rel_cls_index = self.indexFromItem(rel_cls_item)
            if self.canFetchMore(rel_cls_index):
                continue
            db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
            if db_map not in db_map_dict:
                # Can someone be adding relationships to a class that doesn't exist in the same db?
                continue
            relationship_class = db_map_dict[db_map]
            relationship_class_id = relationship_class['id']
            if relationship_class_id not in relationship_dict:
                continue
            relationships = relationship_dict[relationship_class_id]
            self.add_relationships_to_class(db_map, relationships, rel_cls_item)

    def add_relationships_to_class(self, db_map, relationships, rel_cls_item):
        existing_rows = [[rel_cls_item.child(j, 0), rel_cls_item.child(j, 1)] for j in range(rel_cls_item.rowCount())]
        existing_row_d = {row[0].text(): row for row in existing_rows}
        new_rows = []
        for relationship in relationships:
            if relationship.object_name_list in existing_row_d:
                # Already in model, append db_map information
                relationship_item, db_item = existing_row_d[relationship.object_name_list]
                db_map_dict = relationship_item.data(Qt.UserRole + 1)
                db_map_dict[db_map] = relationship._asdict()
                databases = db_item.data(Qt.DisplayRole)
                databases += "," + self._parent.db_map_to_name[db_map]
                db_item.setData(databases, Qt.DisplayRole)
            else:
                new_rows.append(self.new_relationship_row(db_map, relationship))
        for row in new_rows:
            rel_cls_item.appendRow(row)

    def update_object_classes(self, db_map, object_classes):
        """Update object classes in the model.
        This just means updating the object class name in relationship class items.
        """
        object_class_d = {x.id: x.name for x in object_classes}
        for i in range(self.root_item.rowCount()):
            rel_cls_item = self.root_item.child(i, 0)
            db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
            if db_map not in db_map_dict:
                continue
            rel_cls = db_map_dict[db_map]
            obj_cls_name_list = rel_cls['object_class_name_list'].split(',')
            obj_cls_id_list = [int(x) for x in rel_cls['object_class_id_list'].split(',')]
            for k, id_ in enumerate(obj_cls_id_list):
                if id_ in object_class_d:
                    obj_cls_name_list[k] = object_class_d[id_]
            rel_cls['object_class_name_list'] = ",".join(obj_cls_name_list)
            rel_cls_item.setData(",".join(obj_cls_name_list), Qt.ToolTipRole)

    def update_objects(self, db_map, objects):
        """Update object in the model.
        This just means updating the object name in relationship items.
        """
        object_d = {x.id: x.name for x in objects}
        for i in range(self.root_item.rowCount()):
            relationship_class_item = self.root_item.child(i)
            for j in range(relationship_class_item.rowCount()):
                relationship_item = relationship_class_item.child(j)
                db_map_dict = relationship_item.data(Qt.UserRole + 1)
                if db_map not in db_map_dict:
                    continue
                relationship = db_map_dict[db_map]
                object_id_list = [int(x) for x in relationship['object_id_list'].split(",")]
                object_name_list = relationship['object_name_list'].split(",")
                for k, id_ in enumerate(object_id_list):
                    if id_ in object_d:
                        object_name_list[k] = object_d[id_]
                str_object_name_list = ",".join(object_name_list)
                relationship['object_name_list'] = str_object_name_list
                relationship_item.setData(str_object_name_list, Qt.DisplayRole)

    def update_relationship_classes(self, db_map, relationship_classes):
        """Update relationship classes in the model."""
        rel_cls_d = {x.id: x for x in relationship_classes}
        existing_rows = [
            [self.root_item.child(j, 0), self.root_item.child(j, 1)] for j in range(self.root_item.rowCount())
        ]
        existing_row_d = {(row[0].text(), row[0].data(Qt.ToolTipRole)): row for row in existing_rows}
        removed_rows = []
        for i in range(self.root_item.rowCount()):
            rel_cls_item = self.root_item.child(i)
            db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
            if db_map not in db_map_dict:
                continue
            rel_cls = db_map_dict[db_map]
            rel_cls_id = rel_cls['id']
            upd_rel_cls = rel_cls_d.pop(rel_cls_id, None)
            if not upd_rel_cls:
                continue
            rel_cls_key = (upd_rel_cls.name, upd_rel_cls.object_class_name_list)
            if rel_cls_key in existing_row_d:
                # Already in model
                removed_rows.append(i)
                rel_cls_item, db_item = existing_row_d[rel_cls_key]
                db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
                db_map_dict[db_map] = upd_rel_cls._asdict()
                databases = db_item.data(Qt.DisplayRole)
                databases += "," + self._parent.db_map_to_name[db_map]
                db_item.setData(databases, Qt.DisplayRole)
                # Add relationships from this db if fetched
                rel_cls_index = self.indexFromItem(rel_cls_item)
                if not self.canFetchMore(rel_cls_index):
                    relationships = db_map.wide_relationship_list(class_id=rel_cls_id)
                    self.add_relationships_to_class(db_map, relationships, rel_cls_item)
            else:
                db_map_dict[db_map] = upd_rel_cls._asdict()
                rel_cls_item.setData(upd_rel_cls.name, Qt.DisplayRole)
                rel_cls_item.setData(upd_rel_cls.object_class_name_list, Qt.ToolTipRole)
        self.remove_relationship_class_rows(db_map, removed_rows)

    def update_relationships(self, db_map, relationships):
        """Update relationships in the model."""
        relationship_d = {}
        for rel in relationships:
            relationship_d.setdefault(rel.class_id, {}).update({rel.id: rel})
        for i in range(self.root_item.rowCount()):
            rel_cls_item = self.root_item.child(i)
            db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
            if db_map not in db_map_dict:
                continue
            rel_cls = db_map_dict[db_map]
            rel_cls_id = rel_cls['id']
            class_relationship_dict = relationship_d.pop(rel_cls_id, None)
            if not class_relationship_dict:
                continue
            existing_rows = [
                [rel_cls_item.child(j, 0), rel_cls_item.child(j, 1)] for j in range(rel_cls_item.rowCount())
            ]
            existing_row_d = {row[0].text(): row for row in existing_rows}
            removed_rows = []
            for j in range(rel_cls_item.rowCount()):
                relationship_item = rel_cls_item.child(j)
                db_map_dict = relationship_item.data(Qt.UserRole + 1)
                if db_map not in db_map_dict:
                    continue
                relationship = db_map_dict[db_map]
                relationship_id = relationship['id']
                upd_relationship = class_relationship_dict.pop(relationship_id, None)
                if not upd_relationship:
                    continue
                if upd_relationship.object_name_list in existing_row_d:
                    # Already in model
                    removed_rows.append(j)
                    relationship_item, db_item = existing_row_d[upd_relationship.object_name_list]
                    db_map_dict = relationship_item.data(Qt.UserRole + 1)
                    db_map_dict[db_map] = upd_relationship._asdict()
                    databases = db_item.data(Qt.DisplayRole)
                    databases += "," + self._parent.db_map_to_name[db_map]
                    db_item.setData(databases, Qt.DisplayRole)
                else:
                    db_map_dict[db_map] = upd_relationship._asdict()
                    relationship_item.setData(upd_relationship.object_name_list, Qt.DisplayRole)
            self.remove_relationship_rows(db_map, removed_rows, rel_cls_item)

    def remove_relationship_class_rows(self, db_map, removed_rows):
        for row in sorted(removed_rows, reverse=True):
            rel_cls_item = self.root_item.child(row, 0)
            db_map_dict = rel_cls_item.data(Qt.UserRole + 1)
            del db_map_dict[db_map]
            if not db_map_dict:
                self.root_item.removeRow(row)
            else:
                db_item = self.root_item.child(row, 1)
                databases = db_item.data(Qt.DisplayRole).split(",")
                databases.remove(self._parent.db_map_to_name[db_map])
                db_item.setData(",".join(databases), Qt.DisplayRole)
                self.remove_relationship_rows(db_map, range(rel_cls_item.rowCount()), rel_cls_item)

    def remove_relationship_rows(self, db_map, removed_rows, rel_cls_item):
        for row in sorted(removed_rows, reverse=True):
            relationship_item = rel_cls_item.child(row, 0)
            db_map_dict = relationship_item.data(Qt.UserRole + 1)
            del db_map_dict[db_map]
            if not db_map_dict:
                rel_cls_item.removeRow(row)
            else:
                db_item = rel_cls_item.child(row, 1)
                databases = db_item.data(Qt.DisplayRole).split(",")
                databases.remove(self._parent.db_map_to_name[db_map])
                db_item.setData(",".join(databases), Qt.DisplayRole)

    def remove_object_classes(self, db_map, removed_ids):
        """Remove object classes and their childs."""
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        removed_relationship_class_rows = []
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type != 'relationship_class':
                continue
            # Get visited
            db_map_dict = visited_item.data(Qt.UserRole + 1)
            visited = db_map_dict.get(db_map)
            if not visited:
                continue
            object_class_id_list = visited['object_class_id_list']
            if any(str(id) in object_class_id_list.split(',') for id in removed_ids):
                removed_relationship_class_rows.append(visited_item.row())
        self.remove_relationship_class_rows(db_map, removed_relationship_class_rows)

    def remove_objects(self, db_map, removed_ids):
        """Remove objects and their childs."""
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        removed_relationship_row_d = {}
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type != 'relationship':
                continue
            # Get visited
            db_map_dict = visited_item.data(Qt.UserRole + 1)
            visited = db_map_dict.get(db_map)
            if not visited:
                continue
            object_id_list = visited['object_id_list']
            if any(str(id) in object_id_list.split(',') for id in removed_ids):
                visited_index = self.indexFromItem(visited_item)
                removed_relationship_row_d.setdefault(visited_index.parent(), []).append(visited_index.row())
        for rel_cls_index, rows in removed_relationship_row_d.items():
            rel_cls_item = self.itemFromIndex(rel_cls_index)
            self.remove_relationship_rows(db_map, rows, object_item)

    def remove_relationship_classes(self, db_map, removed_ids):
        """Remove relationship classes and their childs."""
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        removed_relationship_class_rows = []
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type != 'relationship_class':
                continue
            # Get visited
            db_map_dict = visited_item.data(Qt.UserRole + 1)
            visited = db_map_dict.get(db_map)
            if not visited:
                continue
            visited_id = visited['id']
            if visited_id in removed_ids:
                visited_index = self.indexFromItem(visited_item)
                removed_relationship_class_rows.append(visited_index.row())
        self.remove_relationship_class_rows(db_map, removed_relationship_class_rows)

    def remove_relationships(self, db_map, removed_ids):
        """Remove relationships."""
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        removed_relationship_row_d = {}
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type != 'relationship':
                continue
            # Get visited
            db_map_dict = visited_item.data(Qt.UserRole + 1)
            visited = db_map_dict.get(db_map)
            if not visited:
                continue
            if visited['id'] in removed_ids:
                visited_index = self.indexFromItem(visited_item)
                removed_relationship_row_d.setdefault(visited_index.parent(), []).append(visited_index.row())
        for rel_cls_index, rows in removed_relationship_row_d.items():
            rel_cls_item = self.itemFromIndex(rel_cls_index)
            self.remove_relationship_rows(db_map, rows, rel_cls_item)


class SubParameterModel(MinimalTableModel):
    """A parameter model which corresponds to a slice of the entire table.
    The idea is to combine several of these into one big model.
    Allows specifying set of columns that are non-editable (e.g., object_class_name)
    TODO: how column insertion/removal impacts fixed_columns?
    """

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self.gray_brush = QGuiApplication.palette().button()
        self.error_log = []
        self.updated_count = 0

    def flags(self, index):
        """Make fixed indexes non-editable."""
        flags = super().flags(index)
        if index.column() in self._parent.fixed_columns:
            return flags & ~Qt.ItemIsEditable
        return flags

    def data(self, index, role=Qt.DisplayRole):
        """Paint background of fixed indexes gray."""
        if role != Qt.BackgroundRole:
            return super().data(index, role)
        if index.column() in self._parent.fixed_columns:
            return self.gray_brush
        return super().data(index, role)

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        Try and update data in the database first, and if successful set data in the model.
        """
        self.error_log = []
        self.updated_count = 0
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        items_to_update = self.items_to_update(indexes, data)
        upd_ids = self.update_items_in_db(items_to_update)
        header = self._parent.horizontal_header_labels()
        id_column = header.index('id')
        db_column = header.index('database')
        for k, index in enumerate(indexes):
            db_name = self._main_data[index.row()][db_column]
            db_map = self._parent.db_name_to_map[db_name]
            id_ = self._main_data[index.row()][id_column]
            if (db_map, id_) not in upd_ids:
                continue
            self._main_data[index.row()][index.column()] = data[k]
        return True

    def items_to_update(self, indexes, data):
        """A list of items (dict) to update in the database."""
        raise NotImplementedError()

    def update_items_in_db(self, items_to_update):
        """A list of ids of items updated in the database."""
        raise NotImplementedError()


class SubParameterValueModel(SubParameterModel):
    """A parameter model which corresponds to a slice of an entire parameter value table.
    The idea is to combine several of these into one big model.
    """

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_update(self, indexes, data):
        """A list of items (dict) for updating in the database."""
        items_to_update = dict()
        header = self._parent.horizontal_header_labels()
        db_column = header.index('database')
        id_column = header.index('id')
        for k, index in enumerate(indexes):
            row = index.row()
            db_name = index.sibling(row, db_column).data(Qt.EditRole)
            db_map = self._parent.db_name_to_map[db_name]
            id_ = index.sibling(row, id_column).data(Qt.EditRole)
            if not id_:
                continue
            field_name = header[index.column()]
            if field_name != "value":
                continue
            value = data[k]
            if value == index.data(Qt.EditRole):
                # nothing to do really
                continue
            item = {"id": id_, "value": value}
            items_to_update.setdefault(db_map, {}).setdefault(id_, {}).update(item)
        return {db_map: list(item_d.values()) for db_map, item_d in items_to_update.items()}

    @busy_effect
    def update_items_in_db(self, items_to_update):
        """Try and update parameter values in database."""
        upd_ids = []
        for db_map, items in items_to_update.items():
            upd_items, error_log = db_map.update_parameter_values(*items)
            self.updated_count += upd_items.count()
            self.error_log += error_log
            upd_ids += [(db_map, x.id) for x in upd_items]
        return upd_ids

    def data(self, index, role=Qt.DisplayRole):
        """Limit the display of json array data."""
        if role == Qt.ToolTipRole and self._parent.header[index.column()] == 'value':
            return strip_json_data(super().data(index, Qt.DisplayRole), 256)
        if role == Qt.DisplayRole and self._parent.header[index.column()] == 'value':
            return strip_json_data(super().data(index, Qt.DisplayRole), 16)
        return super().data(index, role)


class SubParameterDefinitionModel(SubParameterModel):
    """A parameter model which corresponds to a slice of an entire parameter definition table.
    The idea is to combine several of these into one big model.
    """

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_update(self, indexes, data):
        """A list of items (dict) for updating in the database."""
        items_to_update = dict()
        header = self._parent.horizontal_header_labels()
        db_column = header.index('database')
        id_column = header.index('id')
        parameter_tag_id_list_column = header.index('parameter_tag_id_list')
        value_list_id_column = header.index('value_list_id')
        parameter_tag_dict = {}
        parameter_value_list_dict = {}
        new_indexes = []
        new_data = []
        for index, value in zip(indexes, data):
            row = index.row()
            db_name = index.sibling(row, db_column).data(Qt.EditRole)
            db_map = self._parent.db_name_to_map[db_name]
            id_ = index.sibling(row, id_column).data(Qt.EditRole)
            if not id_:
                continue
            field_name = header[index.column()]
            item = {"id": id_}
            # Handle changes in parameter tag list: update tag id list accordingly
            if field_name == "parameter_tag_list":
                split_parameter_tag_list = value.split(",") if value else []
                d = parameter_tag_dict.setdefault(db_map, {x.tag: x.id for x in db_map.parameter_tag_list()})
                try:
                    parameter_tag_id_list = ",".join(str(d[x]) for x in split_parameter_tag_list)
                    new_indexes.append(index.sibling(row, parameter_tag_id_list_column))
                    new_data.append(parameter_tag_id_list)
                    item.update({'parameter_tag_id_list': parameter_tag_id_list})
                except KeyError as e:
                    self.error_log.append("Invalid parameter tag '{}'.".format(e))
            # Handle changes in value_list name: update value_list id accordingly
            elif field_name == "value_list_name":
                value_list_name = value
                d = parameter_value_list_dict.setdefault(
                    db_map, {x.name: x.id for x in db_map.wide_parameter_value_list_list()}
                )
                try:
                    value_list_id = d[value_list_name]
                    new_indexes.append(index.sibling(row, value_list_id_column))
                    new_data.append(value_list_id)
                    item.update({'parameter_value_list_id': value_list_id})
                except KeyError:
                    self.error_log.append("Invalid value list '{}'.".format(value_list_name))
            elif field_name == "parameter_name":
                item.update({"name": value})
            elif field_name == "default_value":
                default_value = value
                if default_value != index.data(Qt.EditRole):
                    item.update({"default_value": default_value})
            items_to_update.setdefault(db_map, {}).setdefault(id_, {}).update(item)
        indexes.extend(new_indexes)
        data.extend(new_data)
        return {db_map: list(item_d.values()) for db_map, item_d in items_to_update.items()}

    @busy_effect
    def update_items_in_db(self, items_to_update):
        """Try and update parameter definitions in database."""
        upd_ids = []
        for db_map, items in items_to_update.items():
            tag_dict = dict()
            for item in items:
                parameter_tag_id_list = item.pop("parameter_tag_id_list", None)
                if parameter_tag_id_list is None:
                    continue
                tag_dict[item["id"]] = parameter_tag_id_list
            upd_def_tag_list, def_tag_error_log = db_map.set_parameter_definition_tags(tag_dict)
            upd_params, param_error_log = db_map.update_parameters(*items)
            self.updated_count += len(upd_def_tag_list) + upd_params.count()
            self.error_log += def_tag_error_log + param_error_log
            upd_ids += [(db_map, x.parameter_definition_id) for x in upd_def_tag_list]
            upd_ids += [(db_map, x.id) for x in upd_params]
        return upd_ids

    def data(self, index, role=Qt.DisplayRole):
        """Limit the display of json array data."""
        if role == Qt.ToolTipRole and self._parent.header[index.column()] == 'default_value':
            return strip_json_data(super().data(index, Qt.DisplayRole), 256)
        if role == Qt.DisplayRole and self._parent.header[index.column()] == 'default_value':
            return strip_json_data(super().data(index, Qt.DisplayRole), 16)
        return super().data(index, role)


class EmptyParameterModel(EmptyRowModel):
    """An empty parameter model.
    It implements `bath_set_data` for all 'EmptyParameter' models.
    """

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent
        self.error_log = []
        self.added_rows = []

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        Set data in model first, then check if the database needs to be updated as well.
        Extend set of indexes as additional data is set (for emitting dataChanged at the end).
        """
        # TODO: emit dataChanged? Perhaps we need to call `super().batch_set_data` at the end
        self.error_log = []
        self.added_rows = []
        if not super().batch_set_data(indexes, data):
            return False
        items_to_add = self.items_to_add(indexes)
        self.add_items_to_db(items_to_add)
        return True

    def items_to_add(self, indexes):
        raise NotImplementedError()

    def add_items_to_db(self, items_to_add):
        raise NotImplementedError()


class EmptyParameterValueModel(EmptyParameterModel):
    """An empty parameter value model.
    Implements `add_items_to_db` for both EmptyObjectParameterValueModel
    and EmptyRelationshipParameterValueModel.
    """

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    @busy_effect
    def add_items_to_db(self, items_to_add):
        """Add parameter values to database.
        """
        for db_map, row_dict in items_to_add.items():
            items = list(row_dict.values())
            parameter_values, error_log = db_map.add_parameter_values(*items)
            self.added_rows = list(row_dict.keys())
            id_column = self._parent.horizontal_header_labels().index('id')
            for i, parameter_value in enumerate(parameter_values):
                self._main_data[self.added_rows[i]][id_column] = parameter_value.id
            self.error_log.extend(error_log)


class EmptyObjectParameterValueModel(EmptyParameterValueModel):
    """An empty object parameter value model.
    Implements `items_to_add`.
    """

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_add(self, indexes):
        """A dictionary of rows (int) to items (dict) to add to the db.
        Extend set of indexes as additional data is set."""
        items_to_add = dict()
        # Get column numbers
        header_index = self._parent.horizontal_header_labels().index
        db_column = header_index('database')
        object_class_id_column = header_index('object_class_id')
        object_class_name_column = header_index('object_class_name')
        object_id_column = header_index('object_id')
        object_name_column = header_index('object_name')
        parameter_id_column = header_index('parameter_id')
        parameter_name_column = header_index('parameter_name')
        value_column = header_index('value')
        # Lookup dicts (these are filled below as needed with data from the db corresponding to each row)
        object_class_dict = {}
        object_class_name_dict = {}
        object_dict = {}
        parameter_dict = {}
        unique_rows = {ind.row() for ind in indexes}
        for row in unique_rows:
            db_name = self.index(row, db_column).data(Qt.DisplayRole)
            db_map = self._parent.db_name_to_map[db_name]
            object_class_name = self.index(row, object_class_name_column).data(Qt.DisplayRole)
            object_name = self.index(row, object_name_column).data(Qt.DisplayRole)
            parameter_name = self.index(row, parameter_name_column).data(Qt.DisplayRole)
            object_class_id = None
            object_ = None
            parameter = None
            if object_class_name:
                d = object_class_dict.setdefault(db_map, {x.name: x.id for x in db_map.object_class_list()})
                try:
                    object_class_id = d[object_class_name]
                    self._main_data[row][object_class_id_column] = object_class_id
                except KeyError:
                    self.error_log.append("Invalid object class '{}'".format(object_class_name))
            if object_name:
                d = object_dict.setdefault(
                    db_map, {x.name: {'id': x.id, 'class_id': x.class_id} for x in db_map.object_list()}
                )
                try:
                    object_ = d[object_name]
                    self._main_data[row][object_id_column] = object_['id']
                except KeyError:
                    self.error_log.append("Invalid object '{}'".format(object_name))
            if parameter_name:
                d = parameter_dict.setdefault(db_map, {})
                for x in db_map.object_parameter_definition_list():
                    d.setdefault(x.parameter_name, {}).update(
                        {x.object_class_id: {'id': x.id, 'object_class_id': x.object_class_id}}
                    )
                try:
                    dup_parameters = d[parameter_name]
                    if len(dup_parameters) == 1:
                        parameter = list(dup_parameters.values())[0]
                    elif object_class_id in dup_parameters:
                        parameter = dup_parameters[object_class_id]
                    if parameter is not None:
                        self._main_data[row][parameter_id_column] = parameter['id']
                except KeyError:
                    self.error_log.append("Invalid parameter '{}'".format(parameter_name))
            if object_class_id is None:
                d = object_class_name_dict.setdefault(db_map, {x.id: x.name for x in db_map.object_class_list()})
                if object_ is not None:
                    object_class_id = object_['class_id']
                    object_class_name = d[object_class_id]
                    self._main_data[row][object_class_id_column] = object_class_id
                    self._main_data[row][object_class_name_column] = object_class_name
                    indexes.append(self.index(row, object_class_name_column))
                elif parameter is not None:
                    object_class_id = parameter['object_class_id']
                    object_class_name = d[object_class_id]
                    self._main_data[row][object_class_id_column] = object_class_id
                    self._main_data[row][object_class_name_column] = object_class_name
                    indexes.append(self.index(row, object_class_name_column))
            if object_ is None or parameter is None:
                continue
            value = self.index(row, value_column).data(Qt.DisplayRole)
            item = {"object_id": object_['id'], "parameter_definition_id": parameter['id'], "value": value}
            items_to_add.setdefault(db_map, {})[row] = item
        return items_to_add


class EmptyRelationshipParameterValueModel(EmptyParameterValueModel):
    """An empty relationship parameter value model.
    Reimplements alsmot all methods from the super class EmptyParameterModel.
    """

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        A little different from the base class implementation,
        since here we need to support creating relationships on the fly.
        """
        self.error_log = []
        self.added_rows = []
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        for k, index in enumerate(indexes):
            self._main_data[index.row()][index.column()] = data[k]
        relationships_on_the_fly = self.relationships_on_the_fly(indexes)
        items_to_add = self.items_to_add(indexes, relationships_on_the_fly)
        self.add_items_to_db(items_to_add)
        # Find square envelope of indexes to emit dataChanged
        top = min(ind.row() for ind in indexes)
        bottom = max(ind.row() for ind in indexes)
        left = min(ind.column() for ind in indexes)
        right = max(ind.column() for ind in indexes)
        self.dataChanged.emit(self.index(top, left), self.index(bottom, right))
        return True

    def relationships_on_the_fly(self, indexes):
        """A dict of row (int) to relationship item (KeyedTuple),
        which can be either retrieved or added on the fly.
        Extend set of indexes as additional data is set.
        """
        relationships_on_the_fly = dict()
        relationships_to_add = dict()
        # Get column numbers
        header_index = self._parent.horizontal_header_labels().index
        db_column = header_index('database')
        relationship_class_id_column = header_index('relationship_class_id')
        relationship_class_name_column = header_index('relationship_class_name')
        object_class_id_list_column = header_index('object_class_id_list')
        object_class_name_list_column = header_index('object_class_name_list')
        object_id_list_column = header_index('object_id_list')
        object_name_list_column = header_index('object_name_list')
        parameter_id_column = header_index('parameter_id')
        parameter_name_column = header_index('parameter_name')
        # Lookup dicts (these are filled below as needed with data from the db corresponding to each row)
        relationship_class_dict = {}
        relationship_class_name_dict = {}
        parameter_dict = {}
        relationship_dict = {}
        object_dict = {}
        unique_rows = {ind.row() for ind in indexes}
        for row in unique_rows:
            db_name = self.index(row, db_column).data(Qt.DisplayRole)
            db_map = self._parent.db_name_to_map[db_name]
            relationship_class_name = self.index(row, relationship_class_name_column).data(Qt.DisplayRole)
            parameter_name = self.index(row, parameter_name_column).data(Qt.DisplayRole)
            object_name_list = self.index(row, object_name_list_column).data(Qt.DisplayRole)
            relationship_class_id = None
            object_id_list = None
            parameter = None
            if relationship_class_name:
                d = relationship_class_dict.setdefault(
                    db_map,
                    {
                        x.name: {
                            "id": x.id,
                            "object_class_id_list": x.object_class_id_list,
                            "object_class_name_list": x.object_class_name_list,
                        }
                        for x in db_map.wide_relationship_class_list()
                    },
                )
                try:
                    relationship_class = d[relationship_class_name]
                    relationship_class_id = relationship_class['id']
                    object_class_id_list = relationship_class['object_class_id_list']
                    object_class_name_list = relationship_class['object_class_name_list']
                    self._main_data[row][relationship_class_id_column] = relationship_class_id
                    self._main_data[row][object_class_id_list_column] = object_class_id_list
                    self._main_data[row][object_class_name_list_column] = object_class_name_list
                    indexes.append(self.index(row, object_class_name_list_column))
                except KeyError:
                    self.error_log.append("Invalid relationship class '{}'".format(relationship_class_name))
            if object_name_list:
                d = object_dict.setdefault(db_map, {x.name: x.id for x in db_map.object_list()})
                try:
                    object_id_list = [d[x] for x in object_name_list.split(",")]
                    join_object_id_list = ",".join(str(x) for x in object_id_list)
                    self._main_data[row][object_id_list_column] = join_object_id_list
                except KeyError as e:
                    self.error_log.append("Invalid object '{}'".format(e))
            if parameter_name:
                d = parameter_dict.setdefault(db_map, {})
                for x in db_map.relationship_parameter_definition_list():
                    d.setdefault(x.parameter_name, {}).update(
                        {x.relationship_class_id: {'id': x.id, 'relationship_class_id': x.relationship_class_id}}
                    )
                try:
                    dup_parameters = d[parameter_name]
                    if len(dup_parameters) == 1:
                        parameter = list(dup_parameters.values())[0]
                    elif relationship_class_id in dup_parameters:
                        parameter = dup_parameters[relationship_class_id]
                    if parameter is not None:
                        self._main_data[row][parameter_id_column] = parameter['id']
                except KeyError:
                    self.error_log.append("Invalid parameter '{}'".format(parameter_name))
            if relationship_class_id is None and parameter is not None:
                relationship_class_id = parameter['relationship_class_id']
                d1 = relationship_class_name_dict.setdefault(
                    db_map, {x.id: x.name for x in db_map.wide_relationship_class_list()}
                )
                d2 = relationship_class_dict.setdefault(
                    db_map,
                    {
                        x.name: {
                            "id": x.id,
                            "object_class_id_list": x.object_class_id_list,
                            "object_class_name_list": x.object_class_name_list,
                        }
                        for x in db_map.wide_relationship_class_list()
                    },
                )
                relationship_class_name = d1[relationship_class_id]
                relationship_class = d2[relationship_class_name]
                object_class_id_list = relationship_class['object_class_id_list']
                object_class_name_list = relationship_class['object_class_name_list']
                self._main_data[row][relationship_class_id_column] = relationship_class_id
                self._main_data[row][relationship_class_name_column] = relationship_class_name
                self._main_data[row][object_class_id_list_column] = object_class_id_list
                self._main_data[row][object_class_name_list_column] = object_class_name_list
                indexes.append(self.index(row, relationship_class_name_column))
                indexes.append(self.index(row, object_class_name_list_column))
            if relationship_class_id is None or object_id_list is None:
                continue
            d = relationship_dict.setdefault(
                db_map, {(x.class_id, x.object_id_list): x.id for x in db_map.wide_relationship_list()}
            )
            try:
                relationship_id = d[relationship_class_id, join_object_id_list]
                relationships_on_the_fly[row] = relationship_id
            except KeyError:
                relationship_name = relationship_class_name + "_" + object_name_list.replace(",", "__")
                relationship = {
                    "name": relationship_name,
                    "object_id_list": object_id_list,
                    "class_id": relationship_class_id,
                }
                relationships_to_add.setdefault(db_map, {})[row] = relationship
        added_relationships = self.add_relationships(relationships_to_add)
        if added_relationships:
            relationships_on_the_fly.update(added_relationships)
        return relationships_on_the_fly

    def add_relationships(self, relationships_to_add):
        """Add relationships to database on the fly and return them."""
        added_relationships = {}
        for db_map, row_dict in relationships_to_add.items():
            items = list(row_dict.values())
            rows = list(row_dict.keys())
            added, error_log = db_map.add_wide_relationships(*items)
            self._parent._parent.object_tree_model.add_relationships(db_map, added)
            self._parent._parent.relationship_tree_model.add_relationships(db_map, added)
            added_ids = [x.id for x in added]
            self.error_log.extend(error_log)
            added_relationships.update(dict(zip(rows, added_ids)))
        return added_relationships

    def items_to_add(self, indexes, relationships_on_the_fly):
        """A dictionary of rows (int) to items (dict) to add to the db.
        Extend set of indexes as additional data is set."""
        items_to_add = dict()
        # Get column numbers
        header_index = self._parent.horizontal_header_labels().index
        db_column = header_index('database')
        relationship_id_column = header_index('relationship_id')
        parameter_id_column = header_index('parameter_id')
        parameter_name_column = header_index('parameter_name')
        value_column = header_index('value')
        unique_rows = {ind.row() for ind in indexes}
        for row in unique_rows:
            db_name = self.index(row, db_column).data(Qt.DisplayRole)
            db_map = self._parent.db_name_to_map[db_name]
            parameter_id = self.index(row, parameter_id_column).data(Qt.DisplayRole)
            if parameter_id is None:
                continue
            relationship_id = relationships_on_the_fly.get(row, None)
            if not relationship_id:
                continue
            self._main_data[row][relationship_id_column] = relationship_id
            value = self.index(row, value_column).data(Qt.DisplayRole)
            item = {"relationship_id": relationship_id, "parameter_definition_id": parameter_id, "value": value}
            items_to_add.setdefault(db_map, {})[row] = item
        return items_to_add


class EmptyParameterDefinitionModel(EmptyParameterModel):
    """An empty parameter definition model."""

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    @busy_effect
    def add_items_to_db(self, items_to_add):
        """Add parameter definitions to database.
        """
        for db_map, row_dict in items_to_add.items():
            items = list(row_dict.values())
            name_tag_dict = dict()
            for item in items:
                parameter_tag_id_list = item.pop("parameter_tag_id_list", None)
                if parameter_tag_id_list is None:
                    continue
                name_tag_dict[item["name"]] = parameter_tag_id_list
            par_defs, error_log = db_map.add_parameter_definitions(*items)
            self.added_rows = list(row_dict.keys())
            self.error_log.extend(error_log)
            id_column = self._parent.horizontal_header_labels().index('id')
            tag_dict = dict()
            for i, par_def in enumerate(par_defs):
                if par_def.name in name_tag_dict:
                    tag_dict[par_def.id] = name_tag_dict[par_def.name]
                self._main_data[self.added_rows[i]][id_column] = par_def.id
            _, def_tag_error_log = db_map.set_parameter_definition_tags(tag_dict)
            self.error_log.extend(def_tag_error_log)


class EmptyObjectParameterDefinitionModel(EmptyParameterDefinitionModel):
    """An empty object parameter definition model."""

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_add(self, indexes):
        """Return a dictionary of rows (int) to items (dict) to add to the db."""
        items_to_add = dict()
        # Get column numbers
        header_index = self._parent.horizontal_header_labels().index
        db_column = header_index('database')
        object_class_id_column = header_index('object_class_id')
        object_class_name_column = header_index('object_class_name')
        parameter_name_column = header_index('parameter_name')
        parameter_tag_list_column = header_index('parameter_tag_list')
        parameter_tag_id_list_column = header_index('parameter_tag_id_list')
        value_list_id_column = header_index('value_list_id')
        value_list_name_column = header_index('value_list_name')
        default_value_column = header_index('default_value')
        # Lookup dicts (these are filled below as needed with data from the db corresponding to each row)
        object_class_dict = {}
        parameter_tag_dict = {}
        parameter_value_list_dict = {}
        for row in {ind.row() for ind in indexes}:
            db_name = self.index(row, db_column).data(Qt.DisplayRole)
            db_map = self._parent.db_name_to_map[db_name]
            object_class_name = self.index(row, object_class_name_column).data(Qt.DisplayRole)
            parameter_name = self.index(row, parameter_name_column).data(Qt.DisplayRole)
            parameter_tag_list = self.index(row, parameter_tag_list_column).data(Qt.DisplayRole)
            value_list_name = self.index(row, value_list_name_column).data(Qt.DisplayRole)
            object_class_id = None
            item = {"name": parameter_name}
            if object_class_name:
                d = object_class_dict.setdefault(db_map, {x.name: x.id for x in db_map.object_class_list()})
                try:
                    object_class_id = d[object_class_name]
                except KeyError:
                    self.error_log.append("Invalid object class '{}'".format(object_class_name))
                self._main_data[row][object_class_id_column] = object_class_id
                item["object_class_id"] = object_class_id
            if parameter_tag_list:
                d = parameter_tag_dict.setdefault(db_map, {x.tag: x.id for x in db_map.parameter_tag_list()})
                split_parameter_tag_list = parameter_tag_list.split(",")
                try:
                    parameter_tag_id_list = ",".join(str(d[x]) for x in split_parameter_tag_list)
                except KeyError as e:
                    self.error_log.append("Invalid parameter tag '{}'".format(e))
                self._main_data[row][parameter_tag_id_list_column] = parameter_tag_id_list
                item["parameter_tag_id_list"] = parameter_tag_id_list
            if value_list_name:
                d = parameter_value_list_dict.setdefault(
                    db_map, {x.name: x.id for x in db_map.wide_parameter_value_list_list()}
                )
                try:
                    value_list_id = d[value_list_name]
                except KeyError:
                    self.error_log.append("Invalid value list '{}'".format(value_list_name))
                self._main_data[row][value_list_id_column] = value_list_id
                item["parameter_value_list_id"] = value_list_id
            if not parameter_name or not object_class_id:
                continue
            default_value = self.index(row, default_value_column).data(Qt.DisplayRole)
            item["default_value"] = default_value
            items_to_add.setdefault(db_map, {})[row] = item
        return items_to_add


class EmptyRelationshipParameterDefinitionModel(EmptyParameterDefinitionModel):
    """An empty relationship parameter definition model."""

    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_add(self, indexes):
        """Return a dictionary of rows (int) to items (dict) to add to the db.
        Extend set of indexes as additional data is set."""
        items_to_add = dict()
        # Get column numbers
        header_index = self._parent.horizontal_header_labels().index
        db_column = header_index('database')
        relationship_class_id_column = header_index('relationship_class_id')
        relationship_class_name_column = header_index('relationship_class_name')
        object_class_id_list_column = header_index('object_class_id_list')
        object_class_name_list_column = header_index('object_class_name_list')
        parameter_name_column = header_index('parameter_name')
        parameter_tag_list_column = header_index('parameter_tag_list')
        parameter_tag_id_list_column = header_index('parameter_tag_id_list')
        value_list_id_column = header_index('value_list_id')
        value_list_name_column = header_index('value_list_name')
        default_value_column = header_index('default_value')
        # Lookup dicts (these are filled below as needed with data from the db corresponding to each row)
        relationship_class_dict = {}
        parameter_tag_dict = {}
        parameter_value_list_dict = {}
        unique_rows = {ind.row() for ind in indexes}
        for row in unique_rows:
            db_name = self.index(row, db_column).data(Qt.DisplayRole)
            db_map = self._parent.db_name_to_map[db_name]
            relationship_class_name = self.index(row, relationship_class_name_column).data(Qt.DisplayRole)
            object_class_name_list = self.index(row, object_class_name_list_column).data(Qt.DisplayRole)
            parameter_name = self.index(row, parameter_name_column).data(Qt.DisplayRole)
            parameter_tag_list = self.index(row, parameter_tag_list_column).data(Qt.DisplayRole)
            value_list_name = self.index(row, value_list_name_column).data(Qt.DisplayRole)
            relationship_class_id = None
            item = {"name": parameter_name}
            if relationship_class_name:
                d = relationship_class_dict.setdefault(
                    db_map,
                    {
                        x.name: {
                            'id': x.id,
                            'object_class_id_list': x.object_class_id_list,
                            'object_class_name_list': x.object_class_name_list,
                        }
                        for x in db_map.wide_relationship_class_list()
                    },
                )
                try:
                    relationship_class = d[relationship_class_name]
                except KeyError:
                    self.error_log.append("Invalid relationship class '{}'".format(relationship_class_name))
                relationship_class_id = relationship_class['id']
                object_class_id_list = relationship_class['object_class_id_list']
                object_class_name_list = relationship_class['object_class_name_list']
                self._main_data[row][relationship_class_id_column] = relationship_class_id
                self._main_data[row][object_class_id_list_column] = object_class_id_list
                self._main_data[row][object_class_name_list_column] = object_class_name_list
                indexes.append(self.index(row, object_class_name_list_column))
                item["relationship_class_id"] = relationship_class_id
            if parameter_tag_list:
                d = parameter_tag_dict.setdefault(db_map, {x.tag: x.id for x in db_map.parameter_tag_list()})
                split_parameter_tag_list = parameter_tag_list.split(",")
                try:
                    parameter_tag_id_list = ",".join(str(d[x]) for x in split_parameter_tag_list)
                except KeyError as e:
                    self.error_log.append("Invalid tag '{}'".format(e))
                self._main_data[row][parameter_tag_id_list_column] = parameter_tag_id_list
                item["parameter_tag_id_list"] = parameter_tag_id_list
            if value_list_name:
                d = parameter_value_list_dict.setdefault(
                    db_map, {x.name: x.id for x in db_map.wide_parameter_value_list_list()}
                )
                try:
                    value_list_id = d[value_list_name]
                except KeyError:
                    self.error_log.append("Invalid value list '{}'".format(value_list_name))
                self._main_data[row][value_list_id_column] = value_list_id
                item["parameter_value_list_id"] = value_list_id
            if not parameter_name or not relationship_class_id:
                continue
            default_value = self.index(row, default_value_column).data(Qt.DisplayRole)
            item["default_value"] = default_value
            items_to_add.setdefault(db_map, {})[row] = item
        return items_to_add


class ObjectParameterModel(MinimalTableModel):
    """A model that concatenates several 'sub' object parameter models,
    one per object class.
    """

    def __init__(self, parent=None):
        """Init class."""
        super().__init__(parent)
        self._parent = parent
        self.db_maps = parent.db_maps
        self.db_name_to_map = parent.db_name_to_map
        self.sub_models = []
        self.empty_row_model = None
        self.fixed_columns = list()
        self.filtered_out = dict()
        self.italic_font = QFont()
        self.italic_font.setItalic(True)

    def flags(self, index):
        """Return flags for given index.
        Depending on the index's row we will land on a specific model.
        Models whose object class id is not selected are skipped.
        """
        row = index.row()
        column = index.column()
        selected_object_class_ids = self._parent.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models:
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            if row < model.rowCount():
                return model.index(row, column).flags()
            row -= model.rowCount()
        return self.empty_row_model.index(row, column).flags()

    def data(self, index, role=Qt.DisplayRole):
        """Return data for given index and role.
        Depending on the index's row we will land on a specific model.
        Models whose object class id is not selected are skipped.
        """
        row = index.row()
        column = index.column()
        selected_object_class_ids = self._parent.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models:
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            if row < model.rowCount():
                if role == Qt.DecorationRole and column == self.object_class_name_column:
                    object_class_name = model.index(row, column).data(Qt.DisplayRole)
                    return self._parent.icon_mngr.object_icon(object_class_name)
                return model.index(row, column).data(role)
            row -= model.rowCount()
        if role == Qt.DecorationRole and column == self.object_class_name_column:
            object_class_name = self.empty_row_model.index(row, column).data(Qt.DisplayRole)
            return self._parent.icon_mngr.object_icon(object_class_name)
        return self.empty_row_model.index(row, column).data(role)

    def rowCount(self, parent=QModelIndex()):
        """Return the sum of rows in all models.
        Skip models whose object class id is not selected.
        """
        count = 0
        selected_object_class_ids = self._parent.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models:
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            count += model.rowCount()
        count += self.empty_row_model.rowCount()
        return count

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        Distribute indexes and data among the different submodels
        and call batch_set_data on each of them."""
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        model_indexes = {}
        model_data = {}
        selected_object_class_ids = self._parent.all_selected_object_class_ids()
        for k, index in enumerate(indexes):
            if not index.isValid():
                continue
            row = index.row()
            column = index.column()
            for object_class_id, model in self.sub_models:
                if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                    continue
                if row < model.rowCount():
                    model_indexes.setdefault(model, list()).append(model.index(row, column))
                    model_data.setdefault(model, list()).append(data[k])
                    break
                row -= model.rowCount()
            else:
                model = self.empty_row_model
                model_indexes.setdefault(model, list()).append(model.index(row, column))
                model_data.setdefault(model, list()).append(data[k])
        updated_count = 0
        update_error_log = []
        for _, model in self.sub_models:
            model.batch_set_data(model_indexes.get(model, list()), model_data.get(model, list()))
            updated_count += model.sourceModel().updated_count
            update_error_log += model.sourceModel().error_log
        model = self.empty_row_model
        model.batch_set_data(model_indexes.get(model, list()), model_data.get(model, list()))
        add_error_log = model.error_log
        added_rows = model.added_rows
        # Find square envelope of indexes to emit dataChanged
        top = min(ind.row() for ind in indexes)
        bottom = max(ind.row() for ind in indexes)
        left = min(ind.column() for ind in indexes)
        right = max(ind.column() for ind in indexes)
        self.dataChanged.emit(self.index(top, left), self.index(bottom, right))
        if added_rows:
            self.move_rows_to_sub_models(added_rows)
            self._parent.commit_available.emit(True)
            self._parent.msg.emit("Successfully added entries.")
        if updated_count:
            self._parent.commit_available.emit(True)
            self._parent.msg.emit("Successfully updated entries.")
        error_log = add_error_log + update_error_log
        if error_log:
            msg = format_string_list(error_log)
            self._parent.msg_error.emit(msg)
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-model (or the empty model) and call insertRows on it."""
        selected_object_class_ids = self._parent.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models:
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            if row < model.rowCount():
                return model.insertRows(row, count)
            row -= model.rowCount()
        return self.empty_row_model.insertRows(row, count)

    def removeRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-models (or empty model) and call removeRows on them."""
        if row < 0 or row + count - 1 >= self.rowCount():
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        selected_object_class_ids = self._parent.all_selected_object_class_ids()
        model_row_sets = dict()
        for i in range(row, row + count):
            for object_class_id, model in self.sub_models:
                if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                    continue
                if i < model.rowCount():
                    model_row_sets.setdefault(model, set()).add(i)
                    break
                i -= model.rowCount()
            else:
                model_row_sets.setdefault(self.empty_row_model, set()).add(i)
        for _, model in self.sub_models:
            try:
                row_set = model_row_sets[model]
                min_row = min(row_set)
                max_row = max(row_set)
                model.removeRows(min_row, max_row - min_row + 1)
            except KeyError:
                pass
        try:
            row_set = model_row_sets[self.empty_row_model]
            min_row = min(row_set)
            max_row = max(row_set)
            self.empty_row_model.removeRows(min_row, max_row - min_row + 1)
        except KeyError:
            pass
        self.endRemoveRows()
        return True

    @Slot("QModelIndex", "int", "int", name="_handle_empty_rows_inserted")
    def _handle_empty_rows_inserted(self, parent, first, last):
        offset = self.rowCount() - self.empty_row_model.rowCount()
        self.rowsInserted.emit(QModelIndex(), offset + first, offset + last)

    def invalidate_filter(self):
        """Invalidate filter."""
        self.layoutAboutToBeChanged.emit()
        for _, model in self.sub_models:
            model.invalidateFilter()
        self.layoutChanged.emit()

    @busy_effect
    def auto_filter_values(self, column):
        """Return values to populate the auto filter of given column.
        Each 'row' in the returned value consists of:
        1) The 'checked' state, True if the value *hasn't* been filtered out
        2) The value itself (an object name, a parameter name, a numerical value...)
        3) A set of object class ids where the value is found.
        """
        values = dict()
        selected_object_class_ids = self._parent.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models:
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            data = model.sourceModel()._main_data
            row_count = model.sourceModel().rowCount()
            for i in range(row_count):
                if not model.main_filter_accepts_row(i, None):
                    continue
                if not model.auto_filter_accepts_row(i, None, ignored_columns=[column]):
                    continue
                values.setdefault(data[i][column], set()).add(object_class_id)
        filtered_out = self.filtered_out.get(column, [])
        return [[val not in filtered_out, val, obj_cls_id_set] for val, obj_cls_id_set in values.items()]

    def set_filtered_out_values(self, column, values):
        """Set values that need to be filtered out."""
        filtered_out = [val for obj_cls_id, values in values.items() for val in values]
        self.filtered_out[column] = filtered_out
        for object_class_id, model in self.sub_models:
            model.set_filtered_out_values(column, values.get(object_class_id, {}))
        if filtered_out:
            self.setHeaderData(column, Qt.Horizontal, self.italic_font, Qt.FontRole)
        else:
            self.setHeaderData(column, Qt.Horizontal, None, Qt.FontRole)

    def clear_filtered_out_values(self):
        """Clear the set of values that need to be filtered out."""
        for column in self.filtered_out:
            self.setHeaderData(column, Qt.Horizontal, None, Qt.FontRole)
        self.filtered_out = dict()

    def rename_object_classes(self, db_map, object_classes):
        """Rename object classes in model."""
        object_class_name_column = self.header.index("object_class_name")
        object_class_id_name = {(db_map, x.id): x.name for x in object_classes}
        for object_class_id, model in self.sub_models:
            if object_class_id not in object_class_id_name:
                continue
            object_class_name = object_class_id_name[object_class_id]
            for row_data in model.sourceModel()._main_data:
                row_data[object_class_name_column] = object_class_name

    def rename_parameter_tags(self, parameter_tags):
        """Rename parameter tags in model."""
        parameter_tag_list_column = self.header.index("parameter_tag_list")
        parameter_tag_id_list_column = self.header.index("parameter_tag_id_list")
        parameter_tag_dict = {x.id: x.tag for x in parameter_tags}
        for _, model in self.sub_models:
            for row_data in model.sourceModel()._main_data:
                parameter_tag_id_list = row_data[parameter_tag_id_list_column]
                parameter_tag_list = row_data[parameter_tag_list_column]
                if not parameter_tag_id_list:
                    continue
                split_parameter_tag_id_list = [int(x) for x in parameter_tag_id_list.split(",")]
                split_parameter_tag_list = parameter_tag_list.split(",")
                found = False
                for k, tag_id in enumerate(split_parameter_tag_id_list):
                    if tag_id in parameter_tag_dict:
                        new_tag = parameter_tag_dict[tag_id]
                        split_parameter_tag_list[k] = new_tag
                        found = True
                if not found:
                    continue
                row_data[parameter_tag_list_column] = ",".join(split_parameter_tag_list)

    def remove_object_classes(self, db_map, object_classes):
        """Remove object classes from model."""
        self.layoutAboutToBeChanged.emit()
        object_class_ids = [(db_map, x['id']) for x in object_classes]
        for i, (object_class_id, _) in reversed(list(enumerate(self.sub_models))):
            if object_class_id in object_class_ids:
                self.sub_models.pop(i)
        self.layoutChanged.emit()

    def remove_parameter_tags(self, parameter_tag_ids):
        """Remove parameter tags from model."""
        parameter_tag_list_column = self.header.index("parameter_tag_list")
        parameter_tag_id_list_column = self.header.index("parameter_tag_id_list")
        for _, model in self.sub_models:
            for row_data in model.sourceModel()._main_data:
                parameter_tag_id_list = row_data[parameter_tag_id_list_column]
                parameter_tag_list = row_data[parameter_tag_list_column]
                if not parameter_tag_id_list:
                    continue
                split_parameter_tag_id_list = [int(x) for x in parameter_tag_id_list.split(",")]
                split_parameter_tag_list = parameter_tag_list.split(",")
                found = False
                for k, tag_id in enumerate(split_parameter_tag_id_list):
                    if tag_id in parameter_tag_ids:
                        del split_parameter_tag_list[k]
                        found = True
                if not found:
                    continue
                row_data[parameter_tag_list_column] = ",".join(split_parameter_tag_list)


class ObjectParameterValueModel(ObjectParameterModel):
    """A model that concatenates several 'sub' object parameter value models,
    one per object class.
    """

    def __init__(self, parent=None):
        """Init class."""
        super().__init__(parent)
        self.empty_row_model = EmptyObjectParameterValueModel(self)
        self.empty_row_model.rowsInserted.connect(self._handle_empty_rows_inserted)

    def reset_model(self):
        """Reset model data. Each sub-model is filled with parameter value data
        for a different object class."""
        self.beginResetModel()
        self.sub_models = []
        header = self.db_maps[0].object_parameter_value_fields() + ["database"]
        self.fixed_columns = [
            header.index(x) for x in ('object_class_name', 'object_name', 'parameter_name', "database")
        ]
        self.object_class_name_column = header.index('object_class_name')
        parameter_definition_id_column = header.index('parameter_id')
        object_id_column = header.index('object_id')
        db_column = header.index('database')
        self.set_horizontal_header_labels(header)
        data_dict = {}
        for db_map in self.db_maps:
            for parameter_value in db_map.object_parameter_value_list():
                object_class_id = (db_map, parameter_value.object_class_id)
                data_dict.setdefault(object_class_id, list()).append(
                    list(parameter_value) + [self._parent.db_map_to_name[db_map]]
                )
        for object_class_id, data in data_dict.items():
            source_model = SubParameterValueModel(self)
            source_model.reset_model([list(x) for x in data])
            model = ObjectParameterValueFilterProxyModel(
                self, parameter_definition_id_column, object_id_column, db_column
            )
            model.setSourceModel(source_model)
            self.sub_models.append((object_class_id, model))
        self.empty_row_model.set_horizontal_header_labels(header)
        self.empty_row_model.clear()
        self.endResetModel()

    def update_filter(self):
        """Update filter."""
        self.layoutAboutToBeChanged.emit()
        selected_parameter_definition_ids = self._parent.selected_obj_parameter_definition_ids
        selected_object_ids = self._parent.selected_object_ids
        for object_class_id, model in self.sub_models:
            parameter_definition_ids = selected_parameter_definition_ids.get(object_class_id, {})
            object_ids = selected_object_ids.get(object_class_id, {})
            model.update_filter(parameter_definition_ids, object_ids)
            model.clear_filtered_out_values()
        self.clear_filtered_out_values()
        self.layoutChanged.emit()

    def rename_objects(self, db_map, objects):
        """Rename objects in model."""
        object_id_column = self.header.index("object_id")
        object_name_column = self.header.index("object_name")
        object_dict = {}
        for object_ in objects:
            object_dict.setdefault((db_map, object_.class_id), {}).update({object_.id: object_.name})
        for object_class_id, model in self.sub_models:
            if object_class_id not in object_dict:
                continue
            object_id_name = object_dict[object_class_id]
            source_model = model.sourceModel()
            for row_data in source_model._main_data:
                object_id = row_data[object_id_column]
                if object_id in object_id_name:
                    row_data[object_name_column] = object_id_name[object_id]

    def rename_parameter(self, parameter_id, object_class_id, new_name):
        """Rename single parameter in model."""
        parameter_id_column = self.header.index("parameter_id")
        parameter_name_column = self.header.index("parameter_name")
        for model_object_class_id, model in self.sub_models:
            if model_object_class_id != object_class_id:
                continue
            for row_data in model.sourceModel()._main_data:
                if row_data[parameter_id_column] == parameter_id:
                    row_data[parameter_name_column] = new_name

    def remove_objects(self, db_map, objects):
        """Remove objects from model."""
        object_id_column = self.header.index("object_id")
        object_ids = {}
        for object_ in objects:
            object_ids.setdefault((db_map, object_['class_id']), set()).add(object_['id'])
        for object_class_id, model in self.sub_models:
            if object_class_id not in object_ids:
                continue
            class_object_ids = object_ids[object_class_id]
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                object_id = source_model._main_data[row][object_id_column]
                if object_id in class_object_ids:
                    source_model.removeRows(row, 1)

    def remove_parameters(self, parameter_dict):
        """Remove parameters from model."""
        parameter_id_column = self.header.index("parameter_id")
        for object_class_id, model in self.sub_models:
            if object_class_id not in parameter_dict:
                continue
            parameter_ids = parameter_dict[object_class_id]
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                parameter_id = source_model._main_data[row][parameter_id_column]
                if parameter_id in parameter_ids:
                    source_model.removeRows(row, 1)

    def move_rows_to_sub_models(self, rows):
        """Move rows from empty row model to the a new sub_model.
        Called when the empty row model succesfully inserts new data in the db.
        """
        db_column = self.header.index('database')
        object_class_id_column = self.header.index("object_class_id")
        parameter_definition_id_column = self.header.index('parameter_id')
        object_id_column = self.header.index("object_id")
        model_data_dict = {}
        for row in rows:
            row_data = self.empty_row_model._main_data[row]
            object_class_id = row_data[object_class_id_column]
            db_map = self.db_name_to_map[row_data[db_column]]
            model_data_dict.setdefault((db_map, object_class_id), list()).append(row_data)
        for object_class_id, data in model_data_dict.items():
            source_model = SubParameterValueModel(self)
            source_model.reset_model(data)
            model = ObjectParameterValueFilterProxyModel(
                self, parameter_definition_id_column, object_id_column, db_column
            )
            model.setSourceModel(source_model)
            self.sub_models.append((object_class_id, model))
        for row in reversed(rows):
            self.empty_row_model.removeRows(row, 1)
        self.invalidate_filter()


class ObjectParameterDefinitionModel(ObjectParameterModel):
    """A model that concatenates several object parameter definition models
    (one per object class) vertically.
    """

    def __init__(self, parent=None):
        """Init class."""
        super().__init__(parent)
        self.empty_row_model = EmptyObjectParameterDefinitionModel(self)
        self.empty_row_model.rowsInserted.connect(self._handle_empty_rows_inserted)

    def reset_model(self):
        """Reset model data. Each sub-model is filled with parameter definition data
        for a different object class."""
        self.beginResetModel()
        self.sub_models = []
        header = self.db_maps[0].object_parameter_definition_fields() + ["database"]
        self.fixed_columns = [header.index('object_class_name'), header.index('database')]
        self.object_class_name_column = header.index('object_class_name')
        parameter_definition_id_column = header.index('id')
        self.set_horizontal_header_labels(header)
        data_dict = {}
        for db_map in self.db_maps:
            for parameter_definition in db_map.object_parameter_definition_list():
                object_class_id = (db_map, parameter_definition.object_class_id)
                data_dict.setdefault(object_class_id, list()).append(
                    list(parameter_definition) + [self._parent.db_map_to_name[db_map]]
                )
        for object_class_id, data in data_dict.items():
            source_model = SubParameterDefinitionModel(self)
            source_model.reset_model([list(x) for x in data])
            model = ObjectParameterDefinitionFilterProxyModel(self, parameter_definition_id_column)
            model.setSourceModel(source_model)
            self.sub_models.append((object_class_id, model))
        self.empty_row_model.set_horizontal_header_labels(header)
        self.empty_row_model.clear()
        self.endResetModel()

    def update_filter(self):
        """Update filter."""
        self.layoutAboutToBeChanged.emit()
        selected_parameter_definition_ids = self._parent.selected_obj_parameter_definition_ids
        for object_class_id, model in self.sub_models:
            model.update_filter(selected_parameter_definition_ids.get(object_class_id, {}))
            model.clear_filtered_out_values()
        self.clear_filtered_out_values()
        self.layoutChanged.emit()

    def move_rows_to_sub_models(self, rows):
        """Move rows from empty row model to a new sub_model.
        Called when the empty row model succesfully inserts new data in the db.
        """
        db_column = self.header.index("database")
        object_class_id_column = self.header.index("object_class_id")
        parameter_definition_id_column = self.header.index('id')
        model_data_dict = {}
        for row in rows:
            row_data = self.empty_row_model._main_data[row]
            object_class_id = row_data[object_class_id_column]
            db_map = self.db_name_to_map[row_data[db_column]]
            model_data_dict.setdefault((db_map, object_class_id), list()).append(row_data)
        for object_class_id, data in model_data_dict.items():
            source_model = SubParameterDefinitionModel(self)
            source_model.reset_model(data)
            model = ObjectParameterDefinitionFilterProxyModel(self, parameter_definition_id_column)
            model.setSourceModel(source_model)
            self.sub_models.append((object_class_id, model))
        for row in reversed(rows):
            self.empty_row_model.removeRows(row, 1)
        self.invalidate_filter()

    def clear_parameter_value_lists(self, value_list_ids):
        """Clear parameter value_lists from model."""
        value_list_id_column = self.header.index("value_list_id")
        value_list_name_column = self.header.index("value_list_name")
        for _, model in self.sub_models:
            for row_data in model.sourceModel()._main_data:
                value_list_id = row_data[value_list_id_column]
                if value_list_id in value_list_ids:
                    row_data[value_list_id_column] = None
                    row_data[value_list_name_column] = None
        self.dataChanged.emit(
            self.index(0, value_list_name_column),
            self.index(self.rowCount() - 1, value_list_name_column),
            [Qt.DisplayRole],
        )

    def rename_parameter_value_lists(self, value_lists):
        """Rename parameter value_lists in model."""
        value_list_id_column = self.header.index("value_list_id")
        value_list_name_column = self.header.index("value_list_name")
        value_list_dict = {x.id: x.name for x in value_lists}
        for _, model in self.sub_models:
            for row_data in model.sourceModel()._main_data:
                value_list_id = row_data[value_list_id_column]
                if value_list_id in value_list_dict:
                    row_data[value_list_name_column] = value_list_dict[value_list_id]
        self.dataChanged.emit(
            self.index(0, value_list_name_column),
            self.index(self.rowCount() - 1, value_list_name_column),
            [Qt.DisplayRole],
        )


class RelationshipParameterModel(MinimalTableModel):
    """A model that combines several relationship parameter models
    (one per relationship class), one on top of the other.
    """

    def __init__(self, parent=None):
        """Init class."""
        super().__init__(parent)
        self._parent = parent
        self.db_maps = parent.db_maps
        self.db_name_to_map = parent.db_name_to_map
        self.sub_models = []
        self.object_class_id_lists = {}
        self.empty_row_model = EmptyRowModel(self)
        self.fixed_columns = list()
        self.filtered_out = dict()
        self.italic_font = QFont()
        self.italic_font.setItalic(True)

    def add_object_class_id_lists(self, db_map, wide_relationship_class_list):
        """Populate a dictionary of object class id lists per relationship class."""
        # NOTE: this must be called when adding new relationship classes
        self.object_class_id_lists.update(
            {
                (db_map, x.id): [(db_map, int(x)) for x in x.object_class_id_list.split(",")]
                for x in wide_relationship_class_list
            }
        )

    def flags(self, index):
        """Return flags for given index.
        Depending on the index's row we will land on a specific model.
        Models whose relationship class id is not selected are skipped.
        Models whose object class id list doesn't intersect the selected ones are also skipped.
        """
        row = index.row()
        column = index.column()
        selected_object_class_ids = self._parent.selected_object_class_ids
        selected_relationship_class_ids = self._parent.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models:
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            if row < model.rowCount():
                return model.index(row, column).flags()
            row -= model.rowCount()
        return self.empty_row_model.index(row, column).flags()

    def data(self, index, role=Qt.DisplayRole):
        """Return data for given index and role.
        Depending on the index's row we will land on a specific model.
        Models whose relationship class id is not selected are skipped.
        Models whose object class id list doesn't intersect the selected ones are also skipped.
        """
        row = index.row()
        column = index.column()
        selected_object_class_ids = self._parent.selected_object_class_ids
        selected_relationship_class_ids = self._parent.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models:
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            if row < model.rowCount():
                if role == Qt.DecorationRole and column == self.relationship_class_name_column:
                    object_class_name_list = model.index(row, self.object_class_name_list_column).data(Qt.DisplayRole)
                    return self._parent.icon_mngr.relationship_icon(object_class_name_list)
                return model.index(row, column).data(role)
            row -= model.rowCount()
        if role == Qt.DecorationRole and column == self.relationship_class_name_column:
            object_class_name_list = self.empty_row_model.index(row, self.object_class_name_list_column).data(
                Qt.DisplayRole
            )
            return self._parent.icon_mngr.relationship_icon(object_class_name_list)
        return self.empty_row_model.index(row, column).data(role)

    def rowCount(self, parent=QModelIndex()):
        """Return the sum of rows in all models.
        Models whose relationship class id is not selected are skipped.
        Models whose object class id list doesn't intersect the selected ones are also skipped.
        """
        count = 0
        selected_object_class_ids = self._parent.selected_object_class_ids
        selected_relationship_class_ids = self._parent.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models:
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            count += model.rowCount()
        count += self.empty_row_model.rowCount()
        return count

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        Distribute indexes and data among the different submodels
        and call batch_set_data on each of them."""
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        model_indexes = {}
        model_data = {}
        selected_object_class_ids = self._parent.selected_object_class_ids
        selected_relationship_class_ids = self._parent.all_selected_relationship_class_ids()
        for k, index in enumerate(indexes):
            if not index.isValid():
                continue
            row = index.row()
            column = index.column()
            for relationship_class_id, model in self.sub_models:
                if selected_object_class_ids:
                    object_class_id_list = self.object_class_id_lists[relationship_class_id]
                    if not selected_object_class_ids.intersection(object_class_id_list):
                        continue
                if selected_relationship_class_ids:
                    if relationship_class_id not in selected_relationship_class_ids:
                        continue
                if row < model.rowCount():
                    model_indexes.setdefault(model, list()).append(model.index(row, column))
                    model_data.setdefault(model, list()).append(data[k])
                    break
                row -= model.rowCount()
            else:
                model = self.empty_row_model
                model_indexes.setdefault(model, list()).append(model.index(row, column))
                model_data.setdefault(model, list()).append(data[k])
        updated_count = 0
        update_error_log = []
        for _, model in self.sub_models:
            model.batch_set_data(model_indexes.get(model, list()), model_data.get(model, list()))
            updated_count += model.sourceModel().updated_count
            update_error_log += model.sourceModel().error_log
        model = self.empty_row_model
        model.batch_set_data(model_indexes.get(model, list()), model_data.get(model, list()))
        add_error_log = model.error_log
        added_rows = model.added_rows
        # Find square envelope of indexes to emit dataChanged
        top = min(ind.row() for ind in indexes)
        bottom = max(ind.row() for ind in indexes)
        left = min(ind.column() for ind in indexes)
        right = max(ind.column() for ind in indexes)
        self.dataChanged.emit(self.index(top, left), self.index(bottom, right))
        if added_rows:
            self.move_rows_to_sub_models(added_rows)
            self._parent.commit_available.emit(True)
            self._parent.msg.emit("Successfully added entries.")
        if updated_count:
            self._parent.commit_available.emit(True)
            self._parent.msg.emit("Successfully updated entries.")
        error_log = add_error_log + update_error_log
        if error_log:
            msg = format_string_list(error_log)
            self._parent.msg_error.emit(msg)
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-model (or the empty model) and call insertRows on it."""
        selected_object_class_ids = self._parent.selected_object_class_ids
        selected_relationship_class_ids = self._parent.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models:
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            if row < model.rowCount():
                return model.insertRows(row, count)
            row -= model.rowCount()
        return self.empty_row_model.insertRows(row, count)

    def removeRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-models (or empty model) and call removeRows on them."""
        if row < 0 or row + count - 1 >= self.rowCount():
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        selected_object_class_ids = self._parent.selected_object_class_ids
        selected_relationship_class_ids = self._parent.all_selected_relationship_class_ids()
        model_row_sets = {}
        for i in range(row, row + count):
            for relationship_class_id, model in self.sub_models:
                if selected_object_class_ids:
                    object_class_id_list = self.object_class_id_lists[relationship_class_id]
                    if not selected_object_class_ids.intersection(object_class_id_list):
                        continue
                if selected_relationship_class_ids:
                    if relationship_class_id not in selected_relationship_class_ids:
                        continue
                if i < model.rowCount():
                    model_row_sets.setdefault(model, set()).add(i)
                    break
                i -= model.rowCount()
            else:
                model_row_sets.setdefault(self.empty_row_model, set()).add(i)
        for _, model in self.sub_models:
            try:
                row_set = model_row_sets[model]
                min_row = min(row_set)
                max_row = max(row_set)
                model.removeRows(min_row, max_row - min_row + 1)
            except KeyError:
                pass
        try:
            row_set = model_row_sets[self.empty_row_model]
            min_row = min(row_set)
            max_row = max(row_set)
            self.empty_row_model.removeRows(min_row, max_row - min_row + 1)
        except KeyError:
            pass
        self.endRemoveRows()
        return True

    @Slot("QModelIndex", "int", "int", name="_handle_empty_rows_inserted")
    def _handle_empty_rows_inserted(self, parent, first, last):
        offset = self.rowCount() - self.empty_row_model.rowCount()
        self.rowsInserted.emit(QModelIndex(), offset + first, offset + last)

    def invalidate_filter(self):
        """Invalidate filter."""
        self.layoutAboutToBeChanged.emit()
        for _, model in self.sub_models:
            model.invalidateFilter()
        self.layoutChanged.emit()

    @busy_effect
    def auto_filter_values(self, column):
        """Return values to populate the auto filter of given column.
        Each 'row' in the returned value consists of:
        1) The 'checked' state, True if the value *hasn't* been filtered out
        2) The value itself (an object name, a parameter name, a numerical value...)
        3) A set of relationship class ids where the value is found.
        """
        values = dict()
        selected_object_class_ids = self._parent.selected_object_class_ids
        selected_relationship_class_ids = self._parent.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models:
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            data = model.sourceModel()._main_data
            row_count = model.sourceModel().rowCount()
            for i in range(row_count):
                if not model.main_filter_accepts_row(i, None):
                    continue
                if not model.auto_filter_accepts_row(i, None, ignored_columns=[column]):
                    continue
                values.setdefault(data[i][column], set()).add(relationship_class_id)
        filtered_out = self.filtered_out.get(column, [])
        return [[val not in filtered_out, val, rel_cls_id_set] for val, rel_cls_id_set in values.items()]

    def set_filtered_out_values(self, column, values):
        """Set values that need to be filtered out."""
        filtered_out = [val for rel_cls_id, values in values.items() for val in values]
        self.filtered_out[column] = filtered_out
        for relationship_class_id, model in self.sub_models:
            model.set_filtered_out_values(column, values.get(relationship_class_id, {}))
        if filtered_out:
            self.setHeaderData(column, Qt.Horizontal, self.italic_font, Qt.FontRole)
        else:
            self.setHeaderData(column, Qt.Horizontal, None, Qt.FontRole)

    def clear_filtered_out_values(self):
        """Clear the set of filtered out values."""
        for column in self.filtered_out:
            self.setHeaderData(column, Qt.Horizontal, None, Qt.FontRole)
        self.filtered_out = dict()

    def rename_object_classes(self, db_map, object_classes):
        """Rename object classes in model."""
        object_class_name_list_column = self.header.index("object_class_name_list")
        object_class_d = {(db_map, x.id): x.name for x in object_classes}
        for relationship_class_id, model in self.sub_models:
            object_class_id_list = self.object_class_id_lists[relationship_class_id]
            obj_cls_name_d = {
                k: object_class_d[id_] for k, id_ in enumerate(object_class_id_list) if id_ in object_class_d
            }
            if not obj_cls_name_d:
                continue
            for row_data in model.sourceModel()._main_data:
                object_class_name_list = row_data[object_class_name_list_column].split(',')
                for k, new_name in obj_cls_name_d.items():
                    object_class_name_list[k] = new_name
                row_data[object_class_name_list_column] = ",".join(object_class_name_list)

    def rename_relationship_classes(self, db_map, relationship_classes):
        """Rename relationship classes in model."""
        relationship_class_name_column = self.header.index("relationship_class_name")
        relationship_class_id_name = {(db_map, x.id): x.name for x in relationship_classes}
        for relationship_class_id, model in self.sub_models:
            if relationship_class_id not in relationship_class_id_name:
                continue
            relationship_class_name = relationship_class_id_name[relationship_class_id]
            for row_data in model.sourceModel()._main_data:
                row_data[relationship_class_name_column] = relationship_class_name

    def rename_parameter_tags(self, parameter_tags):
        """Rename parameter tags in model."""
        parameter_tag_list_column = self.header.index("parameter_tag_list")
        parameter_tag_id_list_column = self.header.index("parameter_tag_id_list")
        parameter_tag_dict = {x.id: x.tag for x in parameter_tags}
        for _, model in self.sub_models:
            for row_data in model.sourceModel()._main_data:
                parameter_tag_id_list = row_data[parameter_tag_id_list_column]
                parameter_tag_list = row_data[parameter_tag_list_column]
                if not parameter_tag_id_list:
                    continue
                split_parameter_tag_id_list = [int(x) for x in parameter_tag_id_list.split(",")]
                split_parameter_tag_list = parameter_tag_list.split(",")
                found = False
                for k, tag_id in enumerate(split_parameter_tag_id_list):
                    if tag_id in parameter_tag_dict:
                        new_tag = parameter_tag_dict[tag_id]
                        split_parameter_tag_list[k] = new_tag
                        found = True
                if not found:
                    continue
                row_data[parameter_tag_list_column] = ",".join(split_parameter_tag_list)

    def remove_object_classes(self, db_map, object_classes):
        """Remove object classes from model."""
        self.layoutAboutToBeChanged.emit()
        object_class_ids = {(db_map, x['id']) for x in object_classes}
        for i, (relationship_class_id, _) in reversed(list(enumerate(self.sub_models))):
            object_class_id_list = self.object_class_id_lists[relationship_class_id]
            if object_class_ids.intersection(object_class_id_list):
                self.sub_models.pop(i)
        self.layoutChanged.emit()

    def remove_relationship_classes(self, relationship_classes):
        """Remove relationship classes from model."""
        self.layoutAboutToBeChanged.emit()
        relationship_class_ids = [(db_map, x['id']) for x in relationship_classes]
        for i, (relationship_class_id, _) in reversed(list(enumerate(self.sub_models))):
            if relationship_class_id in relationship_class_ids:
                self.sub_models.pop(i)
        self.layoutChanged.emit()

    def remove_parameter_tags(self, parameter_tag_ids):
        """Remove parameter tags from model."""
        parameter_tag_list_column = self.header.index("parameter_tag_list")
        parameter_tag_id_list_column = self.header.index("parameter_tag_id_list")
        for _, model in self.sub_models:
            for row_data in model.sourceModel()._main_data:
                parameter_tag_id_list = row_data[parameter_tag_id_list_column]
                parameter_tag_list = row_data[parameter_tag_list_column]
                if not parameter_tag_id_list:
                    continue
                split_parameter_tag_id_list = [int(x) for x in parameter_tag_id_list.split(",")]
                split_parameter_tag_list = parameter_tag_list.split(",")
                found = False
                for k, tag_id in enumerate(split_parameter_tag_id_list):
                    if tag_id in parameter_tag_ids:
                        del split_parameter_tag_list[k]
                        found = True
                if not found:
                    continue
                row_data[parameter_tag_list_column] = ",".join(split_parameter_tag_list)


class RelationshipParameterValueModel(RelationshipParameterModel):
    """A model that combines several relationship parameter value models
    (one per relationship class), one on top of the other.
    """

    def __init__(self, parent=None):
        """Init class."""
        super().__init__(parent)
        self.empty_row_model = EmptyRelationshipParameterValueModel(self)
        self.empty_row_model.rowsInserted.connect(self._handle_empty_rows_inserted)

    def reset_model(self):
        """Reset model data. Each sub-model is filled with parameter value data
        for a different relationship class."""
        self.beginResetModel()
        self.sub_models = []
        for db_map in self.db_maps:
            self.add_object_class_id_lists(db_map, db_map.wide_relationship_class_list())
        header = self.db_maps[0].relationship_parameter_value_fields() + ["database"]
        self.fixed_columns = [
            header.index(x) for x in ('relationship_class_name', 'object_name_list', 'parameter_name', "database")
        ]
        self.relationship_class_name_column = header.index('relationship_class_name')
        self.object_class_name_list_column = header.index('object_class_name_list')
        parameter_definition_id_column = header.index('parameter_id')
        object_id_list_column = header.index('object_id_list')
        db_column = header.index('database')
        self.set_horizontal_header_labels(header)
        data_dict = {}
        for db_map in self.db_maps:
            for parameter_value in db_map.relationship_parameter_value_list():
                relationship_class_id = (db_map, parameter_value.relationship_class_id)
                data_dict.setdefault(relationship_class_id, list()).append(
                    list(parameter_value) + [self._parent.db_map_to_name[db_map]]
                )
        for relationship_class_id, data in data_dict.items():
            source_model = SubParameterValueModel(self)
            source_model.reset_model([list(x) for x in data])
            model = RelationshipParameterValueFilterProxyModel(
                self, parameter_definition_id_column, object_id_list_column, db_column
            )
            model.setSourceModel(source_model)
            self.sub_models.append((relationship_class_id, model))
        self.empty_row_model.set_horizontal_header_labels(header)
        self.empty_row_model.clear()
        self.endResetModel()

    def update_filter(self):
        """Update filter."""
        self.layoutAboutToBeChanged.emit()
        selected_parameter_definition_ids = self._parent.selected_rel_parameter_definition_ids
        selected_object_ids = self._parent.selected_object_ids
        selected_object_id_lists = self._parent.selected_object_id_lists
        for relationship_class_id, model in self.sub_models:
            parameter_definition_ids = selected_parameter_definition_ids.get(relationship_class_id, {})
            object_class_id_list = self.object_class_id_lists[relationship_class_id]
            object_ids = set(y for x in object_class_id_list for y in selected_object_ids.get(x, {}))
            object_id_lists = selected_object_id_lists.get(relationship_class_id, {})
            model.update_filter(parameter_definition_ids, object_ids, object_id_lists)
            model.clear_filtered_out_values()
        self.clear_filtered_out_values()
        self.layoutChanged.emit()

    def move_rows_to_sub_models(self, rows):
        """Move rows from empty row model to a new sub_model.
        Called when the empty row model succesfully inserts new data in the db.
        """
        db_column = self.header.index("database")
        relationship_class_id_column = self.header.index("relationship_class_id")
        parameter_definition_id_column = self.header.index('parameter_id')
        object_id_list_column = self.header.index('object_id_list')
        model_data_dict = {}
        for row in rows:
            row_data = self.empty_row_model._main_data[row]
            relationship_class_id = row_data[relationship_class_id_column]
            db_map = self.db_name_to_map[row_data[db_column]]
            model_data_dict.setdefault((db_map, relationship_class_id), list()).append(row_data)
        for relationship_class_id, data in model_data_dict.items():
            source_model = SubParameterValueModel(self)
            source_model.reset_model(data)
            model = RelationshipParameterValueFilterProxyModel(
                self, parameter_definition_id_column, object_id_list_column, db_column
            )
            model.setSourceModel(source_model)
            self.sub_models.append((relationship_class_id, model))
        for row in reversed(rows):
            self.empty_row_model.removeRows(row, 1)
        self.invalidate_filter()

    def rename_objects(self, db_map, objects):
        """Rename objects in model."""
        object_id_list_column = self.header.index("object_id_list")
        object_name_list_column = self.header.index("object_name_list")
        object_id_name = {x.id: x.name for x in objects}
        for relationship_class_id, model in self.sub_models:
            if relationship_class_id[0] != db_map:
                continue
            for row_data in model.sourceModel()._main_data:
                object_id_list = [int(x) for x in row_data[object_id_list_column].split(',')]
                object_name_list = row_data[object_name_list_column].split(',')
                for i, object_id in enumerate(object_id_list):
                    if object_id in object_id_name:
                        object_name_list[i] = object_id_name[object_id]
                row_data[object_name_list_column] = ",".join(object_name_list)

    def remove_objects(self, db_map, objects):
        """Remove objects from model."""
        object_id_list_column = self.header.index("object_id_list")
        object_ids = {x['id'] for x in objects}
        for relationship_class_id, model in self.sub_models:
            if relationship_class_id[0] != db_map:
                continue
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                object_id_list = source_model._main_data[row][object_id_list_column]
                if object_ids.intersection(int(x) for x in object_id_list.split(',')):
                    source_model.removeRows(row, 1)

    def remove_relationships(self, db_map, relationships):
        """Remove relationships from model."""
        relationship_id_column = self.header.index("relationship_id")
        relationship_ids = {}
        for relationship in relationships:
            relationship_ids.setdefault((db_map, relationship['class_id']), set()).add(relationship['id'])
        for relationship_class_id, model in self.sub_models:
            if relationship_class_id not in relationship_ids:
                continue
            class_relationship_ids = relationship_ids[relationship_class_id]
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                relationship_id = source_model._main_data[row][relationship_id_column]
                if relationship_id in class_relationship_ids:
                    source_model.removeRows(row, 1)

    def rename_parameter(self, parameter_id, relationship_class_id, new_name):
        """Rename single parameter in model."""
        parameter_id_column = self.header.index("parameter_id")
        parameter_name_column = self.header.index("parameter_name")
        for model_relationship_class_id, model in self.sub_models:
            if model_relationship_class_id != relationship_class_id:
                continue
            for row_data in model.sourceModel()._main_data:
                if row_data[parameter_id_column] == parameter_id:
                    row_data[parameter_name_column] = new_name

    def remove_parameters(self, parameter_dict):
        """Remove parameters from model."""
        parameter_id_column = self.header.index("parameter_id")
        for relationship_class_id, model in self.sub_models:
            if relationship_class_id not in parameter_dict:
                continue
            parameter_ids = parameter_dict[relationship_class_id]
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                parameter_id = source_model._main_data[row][parameter_id_column]
                if parameter_id in parameter_ids:
                    source_model.removeRows(row, 1)


class RelationshipParameterDefinitionModel(RelationshipParameterModel):
    """A model that combines several relationship parameter definition models
    (one per relationship class), one on top of the other.
    """

    def __init__(self, parent=None):
        """Init class."""
        super().__init__(parent)
        self.empty_row_model = EmptyRelationshipParameterDefinitionModel(self)
        self.empty_row_model.rowsInserted.connect(self._handle_empty_rows_inserted)

    def reset_model(self):
        """Reset model data. Each sub-model is filled with parameter definition data
        for a different relationship class."""
        self.beginResetModel()
        self.sub_models = []
        for db_map in self.db_maps:
            self.add_object_class_id_lists(db_map, db_map.wide_relationship_class_list())
        header = self.db_maps[0].relationship_parameter_definition_fields() + ["database"]
        self.fixed_columns = [
            header.index(x) for x in ('relationship_class_name', 'object_class_name_list', 'database')
        ]
        self.relationship_class_name_column = header.index('relationship_class_name')
        self.object_class_name_list_column = header.index('object_class_name_list')
        parameter_definition_id_column = header.index('id')
        self.set_horizontal_header_labels(header)
        data_dict = {}
        for db_map in self.db_maps:
            for parameter_definition in db_map.relationship_parameter_definition_list():
                relationship_class_id = (db_map, parameter_definition.relationship_class_id)
                data_dict.setdefault(relationship_class_id, list()).append(
                    list(parameter_definition) + [self._parent.db_map_to_name[db_map]]
                )
        for relationship_class_id, data in data_dict.items():
            source_model = SubParameterDefinitionModel(self)
            source_model.reset_model([list(x) for x in data])
            model = RelationshipParameterDefinitionFilterProxyModel(self, parameter_definition_id_column)
            model.setSourceModel(source_model)
            self.sub_models.append((relationship_class_id, model))
        self.empty_row_model.set_horizontal_header_labels(header)
        self.empty_row_model.clear()
        self.endResetModel()

    def update_filter(self):
        """Update filter."""
        self.layoutAboutToBeChanged.emit()
        selected_parameter_definition_ids = self._parent.selected_rel_parameter_definition_ids
        for relationship_class_id, model in self.sub_models:
            parameter_definition_ids = selected_parameter_definition_ids.get(relationship_class_id, {})
            model.update_filter(parameter_definition_ids)
            model.clear_filtered_out_values()
        self.clear_filtered_out_values()
        self.layoutChanged.emit()

    def move_rows_to_sub_models(self, rows):
        """Move rows from empty row model to a new sub_model.
        Called when the empty row model succesfully inserts new data in the db.
        """
        db_column = self.header.index("database")
        relationship_class_id_column = self.header.index("relationship_class_id")
        parameter_definition_id_column = self.header.index('id')
        model_data_dict = {}
        for row in rows:
            row_data = self.empty_row_model._main_data[row]
            relationship_class_id = row_data[relationship_class_id_column]
            db_map = self.db_name_to_map[row_data[db_column]]
            model_data_dict.setdefault((db_map, relationship_class_id), list()).append(row_data)
        for relationship_class_id, data in model_data_dict.items():
            source_model = SubParameterDefinitionModel(self)
            source_model.reset_model(data)
            model = RelationshipParameterDefinitionFilterProxyModel(self, parameter_definition_id_column)
            model.setSourceModel(source_model)
            self.sub_models.append((relationship_class_id, model))
        for row in reversed(rows):
            self.empty_row_model.removeRows(row, 1)
        self.invalidate_filter()

    def clear_parameter_value_lists(self, value_list_ids):
        """Clear parameter value_lists from model."""
        value_list_id_column = self.header.index("value_list_id")
        value_list_name_column = self.header.index("value_list_name")
        for _, model in self.sub_models:
            for row_data in model.sourceModel()._main_data:
                value_list_id = row_data[value_list_id_column]
                if value_list_id in value_list_ids:
                    row_data[value_list_id_column] = None
                    row_data[value_list_name_column] = None
        self.dataChanged.emit(
            self.index(0, value_list_name_column),
            self.index(self.rowCount() - 1, value_list_name_column),
            [Qt.DisplayRole],
        )

    def rename_parameter_value_lists(self, value_lists):
        """Rename parameter value_lists in model."""
        value_list_id_column = self.header.index("value_list_id")
        value_list_name_column = self.header.index("value_list_name")
        parameter_value_list_dict = {x.id: x.name for x in value_lists}
        for _, model in self.sub_models:
            for row_data in model.sourceModel()._main_data:
                value_list_id = row_data[value_list_id_column]
                if value_list_id in parameter_value_list_dict:
                    row_data[value_list_name_column] = parameter_value_list_dict[value_list_id]
        self.dataChanged.emit(
            self.index(0, value_list_name_column),
            self.index(self.rowCount() - 1, value_list_name_column),
            [Qt.DisplayRole],
        )


class ObjectParameterDefinitionFilterProxyModel(QSortFilterProxyModel):
    """A filter proxy model for object parameter models."""

    def __init__(self, parent, parameter_definition_id_column):
        """Init class."""
        super().__init__(parent)
        self.parameter_definition_ids = set()
        self.parameter_definition_id_column = parameter_definition_id_column
        self.filtered_out = dict()

    def update_filter(self, parameter_definition_ids):
        """Update filter."""
        if parameter_definition_ids == self.parameter_definition_ids:
            return
        self.parameter_definition_ids = parameter_definition_ids
        self.invalidateFilter()

    def set_filtered_out_values(self, column, values):
        """Set values that need to be filtered out."""
        if values == self.filtered_out.get(column, {}):
            return
        self.filtered_out[column] = values
        self.invalidateFilter()

    def clear_filtered_out_values(self):
        """Clear the filtered out values."""
        if not self.filtered_out:
            return
        self.filtered_out = dict()
        self.invalidateFilter()

    def auto_filter_accepts_row(self, source_row, source_parent, ignored_columns=None):
        """Accept or reject row."""
        if ignored_columns is None:
            ignored_columns = []
        for column, values in self.filtered_out.items():
            if column in ignored_columns:
                continue
            if self.sourceModel()._main_data[source_row][column] in values:
                return False
        return True

    def main_filter_accepts_row(self, source_row, source_parent):
        """Accept or reject row."""
        if self.parameter_definition_ids:
            parameter_definition_id = self.sourceModel()._main_data[source_row][self.parameter_definition_id_column]
            return parameter_definition_id in self.parameter_definition_ids
        return True

    def filterAcceptsRow(self, source_row, source_parent):
        """Accept or reject row."""
        if not self.main_filter_accepts_row(source_row, source_parent):
            return False
        if not self.auto_filter_accepts_row(source_row, source_parent):
            return False
        return True

    def batch_set_data(self, indexes, data):
        source_indexes = [self.mapToSource(x) for x in indexes]
        return self.sourceModel().batch_set_data(source_indexes, data)


class ObjectParameterValueFilterProxyModel(ObjectParameterDefinitionFilterProxyModel):
    """A filter proxy model for object parameter value models."""

    def __init__(self, parent, parameter_definition_id_column, object_id_column, db_column):
        """Init class."""
        super().__init__(parent, parameter_definition_id_column)
        self.object_ids = set()
        self.object_id_column = object_id_column
        self.db_column = db_column

    def update_filter(self, parameter_definition_ids, object_ids):
        """Update filter."""
        if parameter_definition_ids == self.parameter_definition_ids and object_ids == self.object_ids:
            return
        self.parameter_definition_ids = parameter_definition_ids
        self.object_ids = object_ids
        self.invalidateFilter()

    def main_filter_accepts_row(self, source_row, source_parent):
        """Accept or reject row."""
        if not super().main_filter_accepts_row(source_row, source_parent):
            return False
        if self.object_ids:
            db = self.sourceModel()._main_data[source_row][self.db_column]
            object_id = self.sourceModel()._main_data[source_row][self.object_id_column]
            return (db, object_id) in self.object_ids
        return True


class RelationshipParameterDefinitionFilterProxyModel(QSortFilterProxyModel):
    """A filter proxy model for relationship parameter definition models."""

    def __init__(self, parent, parameter_definition_id_column):
        """Init class."""
        super().__init__(parent)
        self.parameter_definition_ids = set()
        self.parameter_definition_id_column = parameter_definition_id_column
        self.filtered_out = dict()

    def update_filter(self, parameter_definition_ids):
        """Update filter."""
        if parameter_definition_ids == self.parameter_definition_ids:
            return
        self.parameter_definition_ids = parameter_definition_ids
        self.invalidateFilter()

    def set_filtered_out_values(self, column, values):
        """Set values that need to be filtered out."""
        if values == self.filtered_out.get(column, {}):
            return
        self.filtered_out[column] = values
        self.invalidateFilter()

    def clear_filtered_out_values(self):
        """Clear the set of values that need to be filtered out."""
        if not self.filtered_out:
            return
        self.filtered_out = dict()
        self.invalidateFilter()

    def auto_filter_accepts_row(self, source_row, source_parent, ignored_columns=None):
        """Accept or reject row."""
        if ignored_columns is None:
            ignored_columns = list()
        for column, values in self.filtered_out.items():
            if column in ignored_columns:
                continue
            if self.sourceModel()._main_data[source_row][column] in values:
                return False
        return True

    def main_filter_accepts_row(self, source_row, source_parent):
        """Accept or reject row."""
        if self.parameter_definition_ids:
            parameter_definition_id = self.sourceModel()._main_data[source_row][self.parameter_definition_id_column]
            return parameter_definition_id in self.parameter_definition_ids
        return True

    def filterAcceptsRow(self, source_row, source_parent):
        """Accept or reject row."""
        if not self.main_filter_accepts_row(source_row, source_parent):
            return False
        if not self.auto_filter_accepts_row(source_row, source_parent):
            return False
        return True

    def batch_set_data(self, indexes, data):
        source_indexes = [self.mapToSource(x) for x in indexes]
        return self.sourceModel().batch_set_data(source_indexes, data)


class RelationshipParameterValueFilterProxyModel(RelationshipParameterDefinitionFilterProxyModel):
    """A filter proxy model for relationship parameter value models."""

    def __init__(self, parent, parameter_definition_id_column, object_id_list_column, db_column):
        """Init class."""
        super().__init__(parent, parameter_definition_id_column)
        self.object_ids = dict()
        self.object_id_lists = set()
        self.object_id_list_column = object_id_list_column
        self.db_column = db_column

    def update_filter(self, parameter_definition_ids, object_ids, object_id_lists):
        """Update filter."""
        if (
            parameter_definition_ids == self.parameter_definition_ids
            and object_ids == self.object_ids
            and object_id_lists == self.object_id_lists
        ):
            return
        self.parameter_definition_ids = parameter_definition_ids
        self.object_ids = object_ids
        self.object_id_lists = object_id_lists
        self.invalidateFilter()

    def main_filter_accepts_row(self, source_row, source_parent):
        """Accept or reject row."""
        if not super().main_filter_accepts_row(source_row, source_parent):
            return False
        object_id_list = self.sourceModel()._main_data[source_row][self.object_id_list_column]
        db = self.sourceModel()._main_data[source_row][self.db_column]
        if self.object_id_lists:
            return (db, object_id_list) in self.object_id_lists
        if self.object_ids:
            return len(self.object_ids.intersection((db, int(x)) for x in object_id_list.split(","))) > 0
        return True


class TreeNode:
    """A helper class to use as the internalPointer of indexes in ParameterValueListModel.

    Attributes
        parent (TreeNode): the parent node
        row (int): the row, needed in ParameterValueListModel.parent()
        text (str, NoneType): the text to show
        id (int, NoneType): the id from the db table
    """

    def __init__(self, parent, row, text=None, id=None):
        self.parent = parent
        self.row = row
        self.child_nodes = list()
        self.text = text
        self.id = id


class ParameterValueListModel(QAbstractItemModel):
    """A class to display parameter value list data in a treeview."""

    def __init__(self, parent):
        """Initialize class"""
        super().__init__(parent)
        self._parent = parent
        self.db_map = parent.db_map
        self.bold_font = QFont()
        self.bold_font.setBold(True)
        gray_color = QGuiApplication.palette().text().color()
        gray_color.setAlpha(128)
        self.gray_brush = QBrush(gray_color)
        self.empty_list = "Type new list name here..."
        self.empty_value = "Type new list value here..."
        self._root_nodes = list()
        self.dataChanged.connect(self._handle_data_changed)

    def build_tree(self):
        """Initialize the internal data structure of TreeNode instances."""
        self.beginResetModel()
        self._root_nodes = list()
        i = 0
        for wide_value_list in self.db_map.wide_parameter_value_list_list():
            root_node = TreeNode(None, i, text=wide_value_list.name, id=wide_value_list.id)
            i += 1
            self._root_nodes.append(root_node)
            j = 0
            for value in wide_value_list.value_list.split(","):
                child_node = TreeNode(root_node, j, text=value)
                j += 1
                root_node.child_nodes.append(child_node)
            root_node.child_nodes.append(TreeNode(root_node, j, text=self.empty_value))
        self._root_nodes.append(TreeNode(None, i, text=self.empty_list))
        self.endResetModel()

    def index(self, row, column, parent=QModelIndex()):
        """Returns the index of the item in the model specified by the given row, column and parent index.
        Toplevel indexes get their pointer from the `_root_nodes` attribute;
        whereas inner indexes get their pointer from the `child_nodes` attribute of the parent node.
        """
        if not parent.isValid():
            return self.createIndex(row, column, self._root_nodes[row])
        parent_node = parent.internalPointer()
        return self.createIndex(row, column, parent_node.child_nodes[row])

    def parent(self, index):
        """Returns the parent of the model item with the given index.
        Use the internal pointer to retrieve the parent node and use it
        to create the parent index.
        """
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        return self.createIndex(node.parent.row, 0, node.parent)

    def rowCount(self, parent=QModelIndex()):
        """Returns the number of rows under the given parent.
        Get it from the lenght of the appropriate list.
        """
        if not parent.isValid():
            return len(self._root_nodes)
        node = parent.internalPointer()
        return len(node.child_nodes)

    def columnCount(self, parent=QModelIndex()):
        """Returns the number of columns under the given parent. Always 1.
        """
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index.
        Bold toplevel items. Get the DisplayRole from the `text` attribute of the internal pointer.
        """
        if not index.isValid():
            return None
        if role == Qt.FontRole and not index.parent().isValid():
            # Bold top-level items
            return self.bold_font
        if role == Qt.ForegroundRole and index.row() == self.rowCount(index.parent()) - 1:
            # Paint gray last item in each level
            return self.gray_brush
        if role in (Qt.DisplayRole, Qt.EditRole):
            text = index.internalPointer().text
            # Deserialize value (so we don't see e.g. quotes around strings)
            if role == Qt.DisplayRole and index.parent().isValid() and index.row() != self.rowCount(index.parent()) - 1:
                text = json.loads(text)
            return text
        return None

    def flags(self, index):
        """Returns the item flags for the given index.
        """
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role=Qt.EditRole):
        """Sets the role data for the item at index to value.
        Returns True if successful; otherwise returns False.
        Basically just update the `text` attribute of the internal pointer.
        """
        if not index.isValid():
            return False
        if role != Qt.EditRole:
            return False
        node = index.internalPointer()
        if index.parent().isValid():
            # list values are stored as json (list *names*, as normal python types)
            value = json.dumps(value)
        if value == node.text:
            return False
        node.text = value
        self.dataChanged.emit(index, index, [role])
        return True

    def appendRows(self, count, parent=QModelIndex()):
        """Append count rows into the model.
        Items in the new row will be children of the item represented by the parent model index.
        """
        row = self.rowCount(parent)
        self.beginInsertRows(parent, row, row + count - 1)
        if not parent.isValid():
            self._root_nodes.append(TreeNode(None, row, text=self.empty_list))
        else:
            root_node = parent.internalPointer()
            root_node.child_nodes.append(TreeNode(root_node, row, text=self.empty_value))
        self.endInsertRows()

    @Slot("QModelIndex", "QModelIndex", "QVector", name="_handle_data_changed")
    def _handle_data_changed(self, top_left, bottom_right, roles=None):
        """Called when data in the model changes.
        """
        if roles is None:
            roles = list()
        if Qt.EditRole not in roles:
            return
        parent = self.parent(top_left)
        if parent != self.parent(bottom_right):
            return
        self.append_empty_rows(bottom_right, parent)
        to_add, to_update = self.items_to_add_and_update(top_left.row(), bottom_right.row(), parent)
        self._parent.add_parameter_value_lists(*to_add)
        self._parent.update_parameter_value_lists(*to_update)

    def append_empty_rows(self, index, parent):
        """Append emtpy rows if index is the last children, so the user can continue editing the model.
        The argument `parent` is given for convenience.
        """
        if self.rowCount(parent) == index.row() + 1:
            self.appendRows(1, parent)
            if not parent.isValid():
                self.appendRows(1, index)

    def items_to_add_and_update(self, first, last, parent):
        """Return list of items to add and update in the db.
        """
        to_add = list()
        to_update = list()
        if not parent.isValid():
            # The changes correspond to list *names*.
            # We need to check them all
            for row in range(first, last + 1):
                index = self.index(row, 0, parent)
                node = index.internalPointer()
                id = node.id
                name = node.text
                if id:
                    # Update
                    to_update.append(dict(id=id, name=name))
                else:
                    # Add
                    value_list = [
                        self.index(i, 0, index).internalPointer().text for i in range(self.rowCount(index) - 1)
                    ]
                    if value_list:
                        to_add.append(dict(parent=index, name=name, value_list=value_list))
        else:
            # The changes correspond to list *values*, so it's enough to check the parent
            value_list = [
                str(self.index(i, 0, parent).internalPointer().text) for i in range(self.rowCount(parent) - 1)
            ]
            id = parent.internalPointer().id
            if id:
                # Update
                to_update.append(dict(id=id, value_list=value_list))
            else:
                # Add
                name = parent.internalPointer().text
                to_add.append(dict(parent=parent, name=name, value_list=value_list))
        return to_add, to_update

    def batch_set_data(self, indexes, values):
        """Set edit role for indexes to values in batch."""
        # NOTE: Not in use at the moment
        parented_rows = dict()
        for index, value in zip(indexes, values):
            index.internalPointer().text = value
            parent = self.parent(index)
            parented_rows.setdefault(parent, list()).append(index.row())
        # Emit dataChanged parent-wise
        for parent, rows in parented_rows.items():
            top_left = self.index(min(rows), 0, parent)
            bottom_right = self.index(max(rows), 0, parent)
            self.dataChanged.emit(top_left, bottom_right, [Qt.EditRole])

    def removeRow(self, row, parent=QModelIndex()):
        """Remove row under parent, but never the last row (which is the empty one)"""
        if row == self.rowCount(parent) - 1:
            return
        self.beginRemoveRows(parent, row, row)
        if not parent.isValid():
            # Row is at the top level
            self._root_nodes.pop(row)
            # Update row attribute of tail items. This is awful but we need it.
            for r in range(row, len(self._root_nodes)):
                node = self._root_nodes[r]
                node.row = r
        else:
            # Row is at the low level
            parent_node = parent.internalPointer()
            child_nodes = parent_node.child_nodes
            child_nodes.pop(row)
            # We don't need to update the row attribute of the childs, since they're not used.
        self.endRemoveRows()


class LazyLoadingArrayModel(EmptyRowModel):
    """A model of array data, used by TreeViewForm.

    Attributes:
        parent (JSONEditor): the parent widget
        stride (int): The number of elements to fetch
    """

    def __init__(self, parent, stride=256):
        """Initialize class"""
        super().__init__(parent)
        self._orig_data = []
        self._stride = stride
        self.set_horizontal_header_labels("json")
        self._wrong_data = False

    def reset_model(self, arr):
        """Store given array into the `_orig_data` attribute.
        Initialize first `_stride` rows of the model.
        """
        if arr is None:
            arr = []
        self._orig_data = arr
        if not isinstance(self._orig_data, list):
            return
        data = list()
        for i in range(self._stride):
            try:
                data.append([self._orig_data.pop(0)])
            except IndexError:
                break
        super().reset_model(data)

    def canFetchMore(self, parent):
        if isinstance(self._orig_data, list):
            return len(self._orig_data) > 0
        return False

    def fetchMore(self, parent):
        """Pop data from the _orig_data attribute and add it to the model."""
        data = list()
        for i in range(self._stride):
            try:
                data.append([self._orig_data.pop(0)])
            except IndexError:
                break
        count = len(data)
        last_data_row = self.rowCount() - 1
        self.insertRows(last_data_row, count)
        indexes = [self.index(last_data_row + i, 0) for i in range(count)]
        self.batch_set_data(indexes, data)

    def all_data(self):
        """Return all data into a list."""
        if not isinstance(self._orig_data, list):
            return self._orig_data
        last_data_row = self.rowCount() - 1
        all_data = [self._main_data[i][0] for i in range(last_data_row)]
        all_data.extend(self._orig_data)  # Whatever remains unfetched
        return all_data
