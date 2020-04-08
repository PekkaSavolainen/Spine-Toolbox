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
Widget shown to user when a new View is created.

:author: P. Savolainen (VTT)
:date:   19.1.2017
"""

from spinetoolbox.widgets.add_project_item_widget import AddProjectItemWidget
from ..view import View


class AddViewWidget(AddProjectItemWidget):
    """A widget to query user's preferences for a new item.

    Attributes:
        toolbox (ToolboxUI): Parent widget
        x (int): X coordinate of new item
        y (int): Y coordinate of new item
    """

    def __init__(self, toolbox, x, y, spec=""):
        """Initialize class."""
        initial_name = toolbox.propose_item_name(View.default_name_prefix())
        super().__init__(toolbox, x, y, initial_name)
        self.setWindowTitle(f"Add View")

    def call_add_item(self):
        """Creates new Item according to user's selections."""
        item = dict(name=self.name, description=self.description, x=self._x, y=self._y)
        self._project.add_project_items("Views", item, set_selected=True)
