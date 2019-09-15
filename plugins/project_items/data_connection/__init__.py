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
Data connection plugin.

:author: M. Marin (KTH)
:date:   12.9.2019
"""

from .data_connection import DataConnection
from .data_connection_icon import DataConnectionIcon
from .widgets.data_connection_properties_widget import DataConnectionPropertiesWidget
from .widgets.add_data_connection_widget import AddDataConnectionWidget

item_rank = 1
item_category = "Data Connections"
item_type = "Data Connection"
item_icon = ":/icons/project_item_icons/file-alt.svg"
item_maker = DataConnection
icon_maker = DataConnectionIcon
properties_widget_maker = DataConnectionPropertiesWidget
add_form_maker = AddDataConnectionWidget
