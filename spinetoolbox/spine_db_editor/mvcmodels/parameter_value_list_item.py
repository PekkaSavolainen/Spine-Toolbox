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
Tree items for parameter_value lists.

:authors: M. Marin (KTH)
:date:   28.6.2019
"""

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from spinedb_api import from_database
from spinetoolbox.mvcmodels.shared import PARSED_ROLE
from .tree_item_utility import (
    EmptyChildMixin,
    GrayIfLastMixin,
    BoldTextMixin,
    EditableMixin,
    StandardDBItem,
    FetchMoreMixin,
    SortsChildrenMixin,
    LeafItem,
)
from ...helpers import CharIconEngine, rows_to_row_count_tuples


class DBItem(EmptyChildMixin, FetchMoreMixin, StandardDBItem):
    """An item representing a db."""

    @property
    def item_type(self):
        return "db"

    @property
    def fetch_item_type(self):
        return "parameter_value_list"

    def empty_child(self):
        return ListItem()

    def remove_wip_items(self, names):
        removed_rows = [
            row for row, list_item in enumerate(self.children[:-1]) if list_item.id is None and list_item.name in names
        ]
        for row, count in sorted(rows_to_row_count_tuples(removed_rows), reverse=True):
            self.remove_children(row, count)


class ListItem(GrayIfLastMixin, EditableMixin, EmptyChildMixin, BoldTextMixin, SortsChildrenMixin, LeafItem):
    """A parameter value list item."""

    def __init__(self, identifier=None, name=None):
        super().__init__(identifier=identifier)
        self._name = name

    @property
    def item_type(self):
        return "parameter_value_list"

    def _make_item_data(self):
        return {"name": "Type new list name here..." if self._name is None else self._name}

    def collect_values(self):
        """Collects parameter value list values from child items.

        Returns:
            list: list of values
        """
        return [child.data(0, PARSED_ROLE) for child in self._children[:-1]]

    # pylint: disable=no-self-use
    def empty_child(self):
        return ValueItem(self.id)

    def data(self, column, role=Qt.DisplayRole):
        if role == Qt.DecorationRole:
            engine = CharIconEngine("\uf022", 0)
            return QIcon(engine.pixmap())
        return super().data(column, role)

    def set_data(self, column, value, role=Qt.EditRole):
        if role != Qt.EditRole or value == self.data(column, role):
            return False
        if self.id:
            db_item = self._make_item_to_update(column, value)
            self.update_item_in_db(db_item)
            return True
        # Don't add item to db. Items are only added when the first list value is set.
        # Instead, insert a wip list item with just a name, and no values yet
        self.parent_item.insert_children(self.child_number(), [ListItem(name=value)])
        return True

    def add_item_to_db(self, db_item):
        raise NotImplementedError()

    def update_item_in_db(self, db_item):
        self.db_mngr.update_parameter_value_lists({self.db_map: [db_item]})

    def handle_updated_in_db(self):
        value_count = self.db_mngr.get_parameter_value_list_length(self.db_map, self.id)
        curr_value_count = self.child_count() - 1
        if value_count > curr_value_count:
            added_count = value_count - curr_value_count
            children = [ValueItem(self.id) for _ in range(added_count)]
            self.insert_children(curr_value_count, children)
        elif curr_value_count > value_count:
            removed_count = curr_value_count - value_count
            self.remove_children(value_count, removed_count)

    @staticmethod
    def _sort_key(child):
        return int(child.id.split(",")[1])


class ValueItem(GrayIfLastMixin, EditableMixin, LeafItem):
    @property
    def item_type(self):
        return "list_value"

    @property
    def value(self):
        return self.db_mngr.get_value_list_item(self.db_map, self.id, self.child_number(), Qt.EditRole)

    @property
    def item_data(self):
        if not self.id:
            return self._make_item_data()
        return self.db_mngr.get_item(self.db_map, self.parent_item.item_type, self.id)

    def data(self, column, role=Qt.DisplayRole):
        if role in (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole, PARSED_ROLE):
            if not self.id:
                return "Enter new list value here..." if role != PARSED_ROLE else None
            return self.db_mngr.get_value_list_item(self.db_map, self.id, role=role)
        return super().data(column, role)

    def _make_item_to_add(self, value):
        value_list = self.parent_item.collect_values()
        try:
            value_list[self.child_number()] = value
        except IndexError:
            value_list.append(value)
        return [(self.parent_item.name, value) for value in value_list]

    def make_item_to_add(self, db_value):
        # Needed for parameter value editor.
        return self._make_item_to_add(from_database(db_value))

    def _make_item_to_update(self, _column, value):
        return self._make_item_to_add(value)

    def add_item_to_db(self, db_item):
        self.db_mngr.import_data({self.db_map: {"parameter_value_lists": db_item}})

    def update_item_in_db(self, db_item):
        self.add_item_to_db(db_item)
