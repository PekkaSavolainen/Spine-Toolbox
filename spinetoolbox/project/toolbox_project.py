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
"""This module contains a Toolbox wrapper for projects."""
from PySide6.QtCore import QObject


class ToolboxProject(QObject):
    """A Wrapper that glues project into Toolbox GUI."""

    def __init__(self, project, app_settings):
        """
        Args:
            project (Project): project to wrap around
            app_settings (QSettings): Toolbox settings
        """
        super().__init__()
