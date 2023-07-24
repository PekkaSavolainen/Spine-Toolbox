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
"""This module contains a Toolbox wrapper for project items."""
from PySide6.QtCore import QObject, Signal


class ToolboxProjectItem(QObject):
    """A Wrapper that glues project item into Toolbox GUI.

    Attributes:
        x (float): horizontal position on Design View
        y (float): vertical position on Design View
    """

    resources_to_predecessors_changed = Signal(object)
    resources_to_predecessors_replaced = Signal(object, list, list)
    resources_to_successors_changed = Signal(object)
    resources_to_successors_replaced = Signal(object, list, list)
    notification_set_on = Signal(int, str)
    notification_set_off = Signal(int)

    def __init__(self, project_item, x, y, parent):
        """
        Args:
            project_item (ProjectItem): project item to wrap
            x (float): item's horizontal coordinate on Design View
            y (float): item's vertical coordinate on Design View
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._item = project_item
        self.x = x
        self.y = y

    @property
    def project_item(self):
        """Returns the wrapped project item."""
        return self._item

    def handle_execution_successful(self, execution_direction, engine_state):
        """Performs item dependent actions after the execution item has finished successfully.

        Args:
            execution_direction (str): "FORWARD" or "BACKWARD"
            engine_state: engine state after item's execution
        """

    def resources_for_direct_successors(self):
        """
        Returns resources for direct successors.

        These resources can include transient files that don't exist yet, or filename patterns.
        The default implementation returns an empty list.

        Returns:
            list: a list of ProjectItemResources
        """
        return []

    def resources_for_direct_predecessors(self):
        """
        Returns resources for direct predecessors.

        These resources can include transient files that don't exist yet, or filename patterns.
        The default implementation returns an empty list.

        Returns:
            list: a list of ProjectItemResources
        """
        return list()

    def upstream_resources_updated(self, resources):
        """Notifies item that resources from direct predecessors have changed.

        Args:
            resources (list of ProjectItemResource): new resources from upstream
        """

    def replace_resources_from_upstream(self, old, new):
        """Replaces existing resources from direct predecessor by a new ones.

        Args:
            old (list of ProjectItemResource): old resources
            new (list of ProjectItemResource): new resources
        """

    def downstream_resources_updated(self, resources):
        """Notifies item that resources from direct successors have changed.

        Args:
            resources (list of ProjectItemResource): new resources from downstream
        """

    def replace_resources_from_downstream(self, old, new):
        """Replaces existing resources from direct successor by a new ones.

        Args:
            old (list of ProjectItemResource): old resources
            new (list of ProjectItemResource): new resources
        """

