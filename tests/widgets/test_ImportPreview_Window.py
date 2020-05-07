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
Contains unit tests for the ImportPreviewWindow class.

:author: A. Soininen
:date:   16.3.2020
"""

import unittest
from unittest import mock
from PySide2.QtCore import QSettings
from PySide2.QtWidgets import QApplication, QWidget
from spinetoolbox.widgets.import_preview_window import ImportPreviewWindow
from spinetoolbox.spine_io.io_api import SourceConnection


class TestImportPreviewWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_closeEvent(self):
        importer = mock.NonCallableMagicMock()
        importer.name = mock.MagicMock(return_value="importer")
        toolbox = QWidget()
        toolbox.qsettings = mock.MagicMock(return_value=QSettings())
        widget = ImportPreviewWindow(importer, "", SourceConnection(), {}, toolbox)
        widget._qsettings = mock.NonCallableMagicMock()
        widget.closeEvent()
        widget._qsettings.beginGroup.assert_called_once_with("mappingPreviewWindow")
        widget._qsettings.endGroup.assert_called_once_with()
        qsettings_save_calls = widget._qsettings.setValue.call_args_list
        self.assertEqual(len(qsettings_save_calls), 9)
        saved_dict = {saved[0][0]: saved[0][1] for saved in qsettings_save_calls}
        self.assertIn("main_splitter_splitterState", saved_dict)
        self.assertIn("sources_splitter_splitterState", saved_dict)
        self.assertIn("mapping_splitter_splitterState", saved_dict)
        self.assertIn("top_source_splitter_splitterState", saved_dict)
        self.assertIn("windowSize", saved_dict)
        self.assertIn("windowPosition", saved_dict)
        self.assertIn("windowState", saved_dict)
        self.assertIn("windowMaximized", saved_dict)
        self.assertIn("n_screens", saved_dict)


if __name__ == '__main__':
    unittest.main()
