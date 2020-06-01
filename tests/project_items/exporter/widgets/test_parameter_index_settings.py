######################################################################################################################
# Copyright (C) 2017-2019 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Tests for ParameterIndexSettings widget and its models.

:author: A. Soininen (VTT)
:date:   17.12.2019
"""

import unittest
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtWidgets import QApplication
from spinedb_api.parameter_value import Map, TimePattern
import spinetoolbox.spine_io.exporters.gdx as gdx
from spinetoolbox.project_items.exporter.widgets.parameter_index_settings import (
    _IndexingTableModel,
    ParameterIndexSettings,
)


_ERROR_PREFIX = "<span style='color:#ff3333;white-space: pre-wrap;'>"
_ERROR_SUFFIX = "</span>"


class TestParameterIndexSettings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_domain_name_clash_warning(self):
        value = Map(["s1", "s2"], [-1.1, -2.2])
        parameter = gdx.Parameter(["domain name"], [("key_1",)], [value])
        indexing_setting = gdx.IndexingSetting(parameter, "set name")
        existing_domains = {"domain name": [("key_1",)]}
        new_domains = {}
        settings_widget = ParameterIndexSettings(
            "parameter name", indexing_setting, existing_domains, new_domains, None
        )
        settings_widget._ui.create_domain_radio_button.click()
        settings_widget._ui.extract_indexes_button.click()
        settings_widget._ui.domain_name_edit.setText("domain name")
        self.assertEqual(
            settings_widget._ui.message_label.text(),
            _ERROR_PREFIX + "Domain name already exists. Choose another name." + _ERROR_SUFFIX,
        )


class TestIndexingTableModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        time_series1 = TimePattern(["s1", "s2"], [-1.1, -2.2])
        time_series2 = TimePattern(["t1", "t2"], [1.1, 2.2])
        parameter = gdx.Parameter(["domain1", "domain2"], [("A1", "B1"), ("A2", "B2")], [time_series1, time_series2])
        self._model = _IndexingTableModel(parameter)

    def test_IndexingTableModel_construction(self):
        self.assertEqual(self._model.indexes, [])
        self.assertEqual(self._model.index_selection, [])
        self.assertEqual(self._model.columnCount(), 3)
        self.assertEqual(self._model.rowCount(), 0)
        self.assertEqual(self._model.headerData(1, Qt.Horizontal), "A1, B1")
        self.assertEqual(self._model.headerData(2, Qt.Horizontal), "A2, B2")

    def test_set_indexes(self):
        self._model.set_indexes(["i1", "i2"])
        self._model.fetchMore(QModelIndex())
        self.assertEqual(self._model.rowCount(), 2)
        self.assertEqual(self._model.indexes, ["i1", "i2"])
        self.assertEqual(self._model.index_selection, [True, True])
        self.assertEqual(self._model.index(0, 0).data(), "i1")
        self.assertEqual(self._model.index(1, 0).data(), "i2")
        self.assertEqual(self._model.index(0, 1).data(), "-1.1")
        self.assertEqual(self._model.index(1, 1).data(), "-2.2")
        self.assertEqual(self._model.index(0, 2).data(), "1.1")
        self.assertEqual(self._model.index(1, 2).data(), "2.2")

    def test_set_selection(self):
        self._model.set_indexes(["i1", "i2", "i3"])
        selected = [True, False, True]
        self._model.set_selection(selected)
        self._model.fetchMore(QModelIndex())
        self.assertEqual(self._model.rowCount(), 3)
        self.assertEqual(self._model.index(0, 0).data(), "i1")
        self.assertEqual(self._model.index(1, 0).data(), "i2")
        self.assertEqual(self._model.index(2, 0).data(), "i3")
        self.assertEqual(self._model.index(0, 1).data(), "-1.1")
        self.assertEqual(self._model.index(1, 1).data(), None)
        self.assertEqual(self._model.index(2, 1).data(), "-2.2")
        self.assertEqual(self._model.index(0, 2).data(), "1.1")
        self.assertEqual(self._model.index(1, 2).data(), None)
        self.assertEqual(self._model.index(2, 2).data(), "2.2")
        self.assertEqual(self._model.mapped_values_balance(), 0)
        self.assertEqual(self._model.index_selection, [True, False, True])

    def test_reorder_indexes(self):
        self._model.set_indexes(["i1", "i2"])
        self._model.set_selection([True, True])
        self._model.reorder_indexes(0, 0, 1)
        self._model.fetchMore(QModelIndex())
        self.assertEqual(self._model.rowCount(), 2)
        self.assertEqual(self._model.index(0, 0).data(), "i2")
        self.assertEqual(self._model.index(1, 0).data(), "i1")
        self.assertEqual(self._model.index(0, 1).data(), "-1.1")
        self.assertEqual(self._model.index(1, 1).data(), "-2.2")
        self.assertEqual(self._model.index(0, 2).data(), "1.1")
        self.assertEqual(self._model.index(1, 2).data(), "2.2")


if __name__ == '__main__':
    unittest.main()
