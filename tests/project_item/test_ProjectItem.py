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
Unit tests for ProjectItem base class.

:author: A. Soininen (VTT)
:date:   4.10.2019
"""

import unittest
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide2.QtWidgets import QApplication
from spinetoolbox.project_item.project_item import ProjectItem
from ..mock_helpers import create_toolboxui_with_project, clean_up_toolboxui_with_project


class TestProjectItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        """Set up."""
        self.toolbox = create_toolboxui_with_project()
        self.project = self.toolbox.project()

    def tearDown(self):
        """Clean up."""
        self.project = None
        clean_up_toolboxui_with_project(self.toolbox)

    def test_notify_destination(self):
        item = ProjectItem("name", "description", 0.0, 0.0, self.project, self.toolbox)
        item.item_type = MagicMock(return_value="item_type")
        self.toolbox.msg_warning = MagicMock()
        item.notify_destination(item)
        self.toolbox.msg_warning.emit.assert_called_with(
            "Link established."
            " Interaction between a <b>item_type</b> and a <b>item_type</b> has not been implemented yet."
        )

    def test_item_dict(self):
        project = MagicMock()
        project.items_dir = "item_directory/"
        item = ProjectItem("item name", "Item's description.", -2.3, 5.5, project, None)
        item.item_type = MagicMock(return_value="item type")
        point = NonCallableMagicMock()
        point.x = MagicMock(return_value=-2.3)
        point.y = MagicMock(return_value=5.5)
        sceneBoundingRect = NonCallableMagicMock()
        sceneBoundingRect.center = MagicMock(return_value=point)
        icon = NonCallableMagicMock()
        icon.sceneBoundingRect = MagicMock(return_value=sceneBoundingRect)
        item.get_icon = MagicMock(return_value=icon)
        item_dict = item.item_dict()
        expected = {"type": "item type", "description": "Item's description.", "x": -2.3, "y": 5.5}
        self.assertEqual(item_dict, expected)


if __name__ == "__main__":
    unittest.main()
