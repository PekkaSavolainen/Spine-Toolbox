######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Unit tests for `pivot_table_models` module.
"""
import itertools
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from spinedb_api import Map
from tests.mock_helpers import fetch_model
from tests.spine_db_editor.widgets.helpers import TestBase


class TestParameterValuePivotTableModel(TestBase):
    def setUp(self):
        self._common_setup("sqlite://", create=True)

    def tearDown(self):
        self._common_tear_down()

    def _fill_model_with_data(self):
        data = {
            "entity_classes": (("class1",),),
            "parameter_definitions": (("class1", "parameter1"), ("class1", "parameter2")),
            "entities": (("class1", "object1"), ("class1", "object2")),
            "parameter_values": (
                ("class1", "object1", "parameter1", 1.0),
                ("class1", "object2", "parameter1", 3.0),
                ("class1", "object1", "parameter2", 5.0),
                ("class1", "object2", "parameter2", 7.0),
            ),
        }
        self._db_mngr.import_data({self._db_map: data})

    def _start(self):
        get_item_exceptions = []

        def guarded_get_item(db_map, item_type, id_):
            try:
                return db_map.get_item(item_type, id=id_)
            except Exception as error:
                get_item_exceptions.append(error)
                return None

        object_class_index = self._db_editor.entity_tree_model.index(0, 0)
        fetch_model(self._db_editor.entity_tree_model)
        index = self._db_editor.entity_tree_model.index(0, 0, object_class_index)
        self._db_editor._update_class_attributes(index)
        with patch.object(self._db_editor.ui.dockWidget_pivot_table, "isVisible") as mock_is_visible:
            mock_is_visible.return_value = True
            self._db_editor.do_reload_pivot_table()
        self._model = self._db_editor.pivot_table_model
        with patch.object(self._db_mngr, "get_item") as get_item:
            get_item.side_effect = guarded_get_item
            self._model.beginResetModel()
            self._model.endResetModel()
            qApp.processEvents()
            self.assertEqual(get_item_exceptions, [])

    def test_x_flag(self):
        self._fill_model_with_data()
        self._start()
        self.assertIsNone(self._model.plot_x_column)
        self._model.set_plot_x_column(1, True)
        self.assertEqual(self._model.plot_x_column, 1)
        self._model.set_plot_x_column(1, False)
        self.assertIsNone(self._model.plot_x_column)

    def test_header_name(self):
        self._fill_model_with_data()
        self._start()
        self.assertEqual(self._model.rowCount(), 5)
        self.assertEqual(self._model.columnCount(), 4)
        self.assertEqual(self._model.header_name(self._model.index(2, 0)), 'object1')
        self.assertEqual(self._model.header_name(self._model.index(0, 1)), 'parameter1')
        self.assertEqual(self._model.header_name(self._model.index(3, 0)), 'object2')
        self.assertEqual(self._model.header_name(self._model.index(0, 2)), 'parameter2')

    def test_data(self):
        self._fill_model_with_data()
        self._start()
        self.assertEqual(self._model.rowCount(), 5)
        self.assertEqual(self._model.columnCount(), 4)
        self.assertEqual(self._model.index(0, 0).data(), "parameter")
        self.assertEqual(self._model.index(1, 0).data(), "class1")
        self.assertEqual(self._model.index(2, 0).data(), "object1")
        self.assertEqual(self._model.index(3, 0).data(), "object2")
        self.assertIsNone(self._model.index(4, 0).data())
        self.assertEqual(self._model.index(0, 1).data(), "parameter1")
        self.assertIsNone(self._model.index(1, 1).data())
        self.assertEqual(self._model.index(2, 1).data(), str(1.0))
        self.assertEqual(self._model.index(3, 1).data(), str(3.0))
        self.assertIsNone(self._model.index(4, 1).data())
        self.assertEqual(self._model.index(0, 2).data(), "parameter2")
        self.assertIsNone(self._model.index(1, 2).data())
        self.assertEqual(self._model.index(2, 2).data(), str(5.0))
        self.assertEqual(self._model.index(3, 2).data(), str(7.0))
        self.assertIsNone(self._model.index(4, 2).data())
        self.assertIsNone(self._model.index(0, 3).data())
        self.assertIsNone(self._model.index(1, 3).data())
        self.assertIsNone(self._model.index(2, 3).data())
        self.assertIsNone(self._model.index(3, 3).data())
        self.assertIsNone(self._model.index(4, 3).data())

    def test_header_row_count(self):
        self._fill_model_with_data()
        self._start()
        self.assertEqual(self._model.headerRowCount(), 2)

    def test_model_works_even_without_entities(self):
        data = {
            "entity_classes": (("class1",),),
        }
        self._db_mngr.import_data({self._db_map: data})
        self._start()
        self.assertEqual(self._model.rowCount(), 3)
        self.assertEqual(self._model.columnCount(), 2)
        self.assertEqual(self._model.index(0, 0).data(), "parameter")
        self.assertEqual(self._model.index(1, 0).data(), "class1")
        self.assertIsNone(self._model.index(2, 0).data())
        self.assertIsNone(self._model.index(0, 1).data())
        self.assertIsNone(self._model.index(1, 1).data())
        self.assertIsNone(self._model.index(2, 1).data())

    def test_drag_and_drop_database_from_frozen_table(self):
        self._fill_model_with_data()
        self._start()
        for frozen_column in range(self._db_editor.frozen_table_model.columnCount()):
            frozen_index = self._db_editor.frozen_table_model.index(0, frozen_column)
            if frozen_index.data() == "database":
                break
        else:
            raise RuntimeError("No 'database' column found in frozen table")
        frozen_table_header_widget = self._db_editor.ui.frozen_table.indexWidget(frozen_index)
        for row, column in itertools.product(
            range(self._db_editor.pivot_table_proxy.rowCount()), range(self._db_editor.pivot_table_proxy.columnCount())
        ):
            index_widget = self._db_editor.ui.pivot_table.indexWidget(
                self._db_editor.pivot_table_proxy.index(row, column)
            )
            if index_widget.identifier == "parameter":
                break
        else:
            raise RuntimeError("No 'parameter' header found")
        self._db_editor.handle_header_dropped(frozen_table_header_widget, index_widget)
        QApplication.processEvents()
        self.assertEqual(self._model.rowCount(), 6)
        self.assertEqual(self._model.columnCount(), 4)
        expected = [
            ["database", self.db_codename, self.db_codename, self.db_codename, None],
            ["parameter", "parameter1", "parameter2", None],
            ["class1", None, None, None],
            ["object1", "1.0", "5.0", None],
            ["object2", "3.0", "7.0", None],
            [None, None, None, None],
        ]
        for row, column in itertools.product(range(self._model.rowCount()), range(self._model.columnCount())):
            with self.subTest(row=row, column=column):
                self.assertEqual(self._model.index(row, column).data(), expected[row][column])


class TestIndexExpansionPivotTableModel(TestBase):
    def setUp(self):
        self._common_setup("sqlite://", create=True)
        data = {
            "entity_classes": (("class1",),),
            "parameter_definitions": (("class1", "parameter1"), ("class1", "parameter2")),
            "entities": (("class1", "object1"), ("class1", "object2")),
            "parameter_values": (
                ("class1", "object1", "parameter1", Map(["A", "B"], [1.1, 2.1])),
                ("class1", "object2", "parameter1", Map(["C", "D"], [1.2, 2.2])),
                ("class1", "object1", "parameter2", Map(["C", "D"], [-1.1, -2.1])),
                ("class1", "object2", "parameter2", Map(["A", "B"], [-1.2, -2.2])),
            ),
        }
        self._db_mngr.import_data({self._db_map: data})
        object_class_index = self._db_editor.entity_tree_model.index(0, 0)
        fetch_model(self._db_editor.entity_tree_model)
        index = self._db_editor.entity_tree_model.index(0, 0, object_class_index)
        for action in self._db_editor.pivot_action_group.actions():
            if action.text() == self._db_editor._INDEX_EXPANSION:
                action.trigger()
                break
        self._db_editor._update_class_attributes(index)
        with patch.object(self._db_editor.ui.dockWidget_pivot_table, "isVisible") as mock_is_visible:
            mock_is_visible.return_value = True
            self._db_editor.do_reload_pivot_table()
        self._model = self._db_editor.pivot_table_model
        self._model.beginResetModel()
        self._model.endResetModel()
        qApp.processEvents()

    def tearDown(self):
        self._common_tear_down()

    def test_data(self):
        self.assertEqual(self._model.rowCount(), 11)
        self.assertEqual(self._model.columnCount(), 5)
        model_data = list()
        i = self._model.index
        for row in range(11):
            model_data.append(list(i(row, column).data() for column in range(5)))
        expected = [
            [None, "parameter", "parameter1", "parameter2", None],
            ["class1", "index", None, None, None],
            ["object1", "A", str(1.1), None, None],
            ["object1", "B", str(2.1), None, None],
            ["object1", "C", None, str(-1.1), None],
            ["object1", "D", None, str(-2.1), None],
            ["object2", "A", None, str(-1.2), None],
            ["object2", "B", None, str(-2.2), None],
            ["object2", "C", str(1.2), None, None],
            ["object2", "D", str(2.2), None, None],
            [None, None, None, None, None],
        ]
        self.assertEqual(model_data, expected)


if __name__ == '__main__':
    unittest.main()
