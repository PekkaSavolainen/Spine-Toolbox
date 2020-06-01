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
Single models for parameter definitions and values (as 'for a single entity').

:authors: M. Marin (KTH)
:date:   28.6.2019
"""

from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtGui import QGuiApplication
from ...mvcmodels.minimal_table_model import MinimalTableModel
from ..mvcmodels.parameter_mixins import (
    ConvertToDBMixin,
    FillInParameterNameMixin,
    FillInValueListIdMixin,
    MakeParameterTagMixin,
)
from ...mvcmodels.shared import PARSED_ROLE


class SingleParameterModel(MinimalTableModel):
    """A parameter model for a single entity class to go in a CompoundParameterModel.
    Provides methods to associate the model to an entity class as well as
    to filter entities within the class.
    """

    def __init__(self, header, db_mngr, db_map, entity_class_id, lazy=False):
        """Init class.

        Args:
            header (list): list of field names for the header
        """
        super().__init__(header=header, lazy=lazy)
        self.db_mngr = db_mngr
        self.db_map = db_map
        self.entity_class_id = entity_class_id
        self._auto_filter = dict()
        self._filter_parameter_ids = dict()

    @property
    def item_type(self):
        """The item type, either 'parameter value' or 'parameter definition', required by the data method."""
        raise NotImplementedError()

    @property
    def entity_class_type(self):
        """The entity class type, either 'object class' or 'relationship class'."""
        raise NotImplementedError()

    @property
    def json_fields(self):
        return {"parameter definition": ["default_value"], "parameter value": ["value"]}[self.item_type]

    @property
    def fixed_fields(self):
        return {
            "object class": {
                "parameter definition": ["object_class_name", "database"],
                "parameter value": ["object_class_name", "object_name", "parameter_name", "database"],
            },
            "relationship class": {
                "parameter definition": ["relationship_class_name", "object_class_name_list", "database"],
                "parameter value": ["relationship_class_name", "object_name_list", "parameter_name", "database"],
            },
        }[self.entity_class_type][self.item_type]

    @property
    def group_fields(self):
        return {
            "object class": {"parameter definition": ["parameter_tag_list"], "parameter value": []},
            "relationship class": {
                "parameter definition": ["object_class_name_list", "parameter_tag_list"],
                "parameter value": ["object_name_list"],
            },
        }[self.entity_class_type][self.item_type]

    @property
    def parameter_definition_id_key(self):
        return {"parameter definition": "id", "parameter value": "parameter_id"}[self.item_type]

    @property
    def can_be_filtered(self):
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        """This model doesn't support row insertion."""
        return False

    def db_item(self, index):
        return self._db_item(index.row())

    def _db_item(self, row):
        id_ = self._main_data[row]
        return self.db_item_from_id(id_)

    def db_item_from_id(self, id_):
        return self.db_mngr.get_item(self.db_map, self.item_type, id_)

    def db_items(self):
        return [self._db_item(row) for row in range(self.rowCount())]

    def flags(self, index):
        """Make fixed indexes non-editable."""
        flags = super().flags(index)
        if self.header[index.column()] in self.fixed_fields:
            return flags & ~Qt.ItemIsEditable
        return flags

    def get_field_item_data(self, field):
        """Returns item data for given field.

        Args:
            field (str): A field from the header

        Returns:
            str, str
        """
        return {
            "object_class_name": ("object_class_id", "object class"),
            "relationship_class_name": ("relationship_class_id", "relationship class"),
            "object_class_name_list": ("relationship_class_id", "relationship class"),
            "object_name": ("object_id", "object"),
            "object_name_list": ("relationship_id", "relationship"),
            "parameter_name": (self.parameter_definition_id_key, "parameter definition"),
            "value_list_name": ("value_list_id", "parameter value list"),
            "description": ("id", "parameter definition"),
            "value": ("id", "parameter value"),
            "default_value": ("id", "parameter definition"),
            "database": ("database", None),
        }.get(field)

    def get_id_key(self, field):
        field_item_data = self.get_field_item_data(field)
        if field_item_data is None:
            return None
        return field_item_data[0]

    def get_field_item(self, field, db_item):
        """Returns a db item corresponding to the given field from the table header,
        or an empty dict if the field doesn't contain db items.
        """
        field_item_data = self.get_field_item_data(field)
        if field_item_data is None:
            return {}
        id_key, item_type = field_item_data
        item_id = db_item.get(id_key)
        return self.db_mngr.get_item(self.db_map, item_type, item_id)

    def data(self, index, role=Qt.DisplayRole):
        """Gets the id and database for the row, and reads data from the db manager
        using the item_type property.
        Paint the object class icon next to the name.
        Also paint background of fixed indexes gray and apply custom format to JSON fields."""
        field = self.header[index.column()]
        # Background role
        if role == Qt.BackgroundRole and field in self.fixed_fields:
            return QGuiApplication.palette().button()
        # Display, edit, tool tip role
        if role in (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole, Qt.TextAlignmentRole, PARSED_ROLE):
            if field == "database":
                return self.db_map.codename
            id_ = self._main_data[index.row()]
            if role == Qt.ToolTipRole:
                description = self._get_field_item(field, id_).get("description", None)
                if description not in (None, ""):
                    return description
            if field in self.json_fields:
                return self.db_mngr.get_value(self.db_map, self.item_type, id_, role)
            item = self.db_mngr.get_item(self.db_map, self.item_type, id_)
            if role == Qt.ToolTipRole:
                description = self.get_field_item(field, item).get("description", None)
                if description not in (None, ""):
                    return description
            data = item.get(field)
            if role == Qt.DisplayRole and data and field in self.group_fields:
                data = data.replace(",", self.db_mngr._GROUP_SEP)
            return data
        # Decoration role
        entity_class_name_field = {
            "object class": "object_class_name",
            "relationship class": "relationship_class_name",
        }[self.entity_class_type]
        if role == Qt.DecorationRole and field == entity_class_name_field:
            return self.db_mngr.entity_class_icon(self.db_map, self.entity_class_type, self.entity_class_id)
        return super().data(index, role)

    def batch_set_data(self, indexes, data):
        """Sets data for indexes in batch.
        Sets data directly in database using db mngr. If successful, updated data will be
        automatically seen by the data method.
        """
        if not indexes or not data:
            return False
        row_data = dict()
        for index, value in zip(indexes, data):
            row_data.setdefault(index.row(), {})[self.header[index.column()]] = value
        items = [dict(id=self._main_data[row], **data) for row, data in row_data.items()]
        self.update_items_in_db(items)
        return True

    def update_items_in_db(self, items):
        """Update items in db. Required by batch_set_data"""
        raise NotImplementedError()

    def _filter_accepts_row(self, row):
        return self._parameter_filter_accepts_row(row) and self._auto_filter_accepts_row(row)

    def _parameter_filter_accepts_row(self, row):
        """Returns the result of the parameter filter."""
        if not self._filter_parameter_ids:
            return True
        parameter_id = self.db_mngr.get_item(self.db_map, self.item_type, self._main_data[row])[
            self.parameter_definition_id_key
        ]
        return parameter_id in self._filter_parameter_ids.get((self.db_map, self.entity_class_id), set())

    def _auto_filter_accepts_row(self, row):
        """Returns the result of the auto filter."""
        if self._auto_filter is None:
            return False
        item_id = self._main_data[row]
        for valid_ids in self._auto_filter.values():
            if valid_ids and item_id not in valid_ids:
                return False
        return True

    def accepted_rows(self):
        """Returns a list of accepted rows, for convenience."""
        return [row for row in range(self.rowCount()) if self._filter_accepts_row(row)]

    def _get_field_item(self, field, id_):
        """Returns a item from the db_mngr.get_item depending on the
        field. If a field doesn't correspond to a item in the database then
        an empty dict is returned.
        """
        data = self.db_mngr.get_item(self.db_map, self.item_type, id_)
        header_to_id = {
            "object_class_name": ("entity_class_id", "object class"),
            "relationship_class_name": ("entity_class_id", "relationship class"),
            "object_name": ("entity_id", "object"),
            "object_name_list": ("entity_id", "relationship"),
            "parameter_name": (self.parameter_definition_id_key, "parameter definition"),
        }
        if field not in header_to_id:
            return {}
        id_field, item_type = header_to_id[field]
        item_id = data.get(id_field)
        return self.db_mngr.get_item(self.db_map, item_type, item_id)


class SingleObjectParameterMixin:
    """Associates a parameter model with a single object class."""

    @property
    def entity_class_type(self):
        return "object class"


class SingleRelationshipParameterMixin:
    """Associates a parameter model with a single relationship class."""

    @property
    def entity_class_type(self):
        return "relationship class"


class SingleParameterDefinitionMixin(FillInParameterNameMixin, FillInValueListIdMixin, MakeParameterTagMixin):
    """A parameter definition model for a single entity class."""

    @property
    def item_type(self):
        return "parameter definition"

    def update_items_in_db(self, items):
        """Update items in db.

        Args:
            item (list): dictionary-items
        """
        self.build_lookup_dictionary({self.db_map: items})
        param_defs = list()
        param_def_tags = list()
        error_log = list()
        for item in items:
            param_def, err1 = self._convert_to_db(item, self.db_map)
            param_def_tag, err2 = self._make_parameter_definition_tag(item, self.db_map)
            if param_def:
                param_defs.append(param_def)
            if param_def_tag:
                param_def_tags.append(param_def_tag)
            if err1 or err2:
                error_log += err1 + err2
        if param_def_tags:
            self.db_mngr.set_parameter_definition_tags({self.db_map: param_def_tags})
        if param_defs:
            self.db_mngr.update_parameter_definitions({self.db_map: param_defs})
        if error_log:
            self.db_mngr.error_msg({self.db_map: error_log})


class SingleParameterValueMixin(ConvertToDBMixin):
    """A parameter value model for a single entity class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._filter_entity_ids = dict()

    @property
    def item_type(self):
        return "parameter value"

    def _filter_accepts_row(self, row):
        """Reimplemented to also account for the entity filter."""
        return (
            self._parameter_filter_accepts_row(row)
            and self._entity_filter_accepts_row(row)
            and self._auto_filter_accepts_row(row)
        )

    def _entity_filter_accepts_row(self, row):
        """Returns the result of the entity filter."""
        if not self._filter_entity_ids:
            return True
        entity_id_key = {"object class": "object_id", "relationship class": "relationship_id"}[self.entity_class_type]
        entity_id = self.db_mngr.get_item(self.db_map, self.item_type, self._main_data[row])[entity_id_key]
        return entity_id in self._filter_entity_ids.get((self.db_map, self.entity_class_id), set())

    def update_items_in_db(self, items):
        """Update items in db.

        Args:
            item (list): dictionary-items
        """
        param_vals = list()
        error_log = list()
        for item in items:
            param_val, err = self._convert_to_db(item, self.db_map)
            if param_val:
                param_vals.append(param_val)
            if err:
                error_log += err
        if param_vals:
            self.db_mngr.update_parameter_values({self.db_map: param_vals})
        if error_log:
            self.db_mngr.error_msg({self.db_map: error_log})


class SingleObjectParameterDefinitionModel(
    SingleObjectParameterMixin, SingleParameterDefinitionMixin, SingleParameterModel
):
    """An object parameter definition model for a single object class."""


class SingleRelationshipParameterDefinitionModel(
    SingleRelationshipParameterMixin, SingleParameterDefinitionMixin, SingleParameterModel
):
    """A relationship parameter definition model for a single relationship class."""


class SingleObjectParameterValueModel(SingleObjectParameterMixin, SingleParameterValueMixin, SingleParameterModel):
    """An object parameter value model for a single object class."""


class SingleRelationshipParameterValueModel(
    SingleRelationshipParameterMixin, SingleParameterValueMixin, SingleParameterModel
):
    """A relationship parameter value model for a single relationship class."""
