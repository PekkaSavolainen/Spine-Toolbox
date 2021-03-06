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
Spine Toolbox project class.

:authors: P. Savolainen (VTT), E. Rinne (VTT)
:date:   10.1.2018
"""

import os
import json
import logging
from PySide2.QtCore import Slot, Signal, QTimer
from PySide2.QtWidgets import QMessageBox
from spinetoolbox.metaobject import MetaObject
from spinetoolbox.helpers import create_dir, inverted, erase_dir
from .config import LATEST_PROJECT_VERSION, PROJECT_FILENAME
from .dag_handler import DirectedGraphHandler
from .project_tree_item import LeafProjectTreeItem
from .project_commands import (
    SetProjectNameCommand,
    SetProjectDescriptionCommand,
    AddProjectItemsCommand,
    RemoveProjectItemCommand,
    RemoveAllProjectItemsCommand,
)
from .spine_engine_worker import SpineEngineWorker


class SpineToolboxProject(MetaObject):
    """Class for Spine Toolbox projects."""

    dag_execution_finished = Signal()
    project_execution_about_to_start = Signal()
    """Emitted just before the entire project is executed."""
    project_execution_finished = Signal()
    """Emitted when the execution finishes, used in unit tests."""

    def __init__(
        self, toolbox, name, description, p_dir, project_item_model, settings, logger,
    ):

        """

        Args:
            toolbox (ToolboxUI): toolbox of this project
            name (str): Project name
            description (str): Project description
            p_dir (str): Project directory
            project_item_model (ProjectItemModel): project item tree model
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): a logger instance
        """
        super().__init__(name, description)
        self._toolbox = toolbox
        self._project_item_model = project_item_model
        self._logger = logger
        self._settings = settings
        self._dags_about_to_be_notified = set()
        self.dag_handler = DirectedGraphHandler()
        self._engine_workers = []
        self._execution_stopped = True
        self.project_dir = None  # Full path to project directory
        self.config_dir = None  # Full path to .spinetoolbox directory
        self.items_dir = None  # Full path to items directory
        self.specs_dir = None  # Full path to specs directory
        self.config_file = None  # Full path to .spinetoolbox/project.json file
        self._toolbox.undo_stack.clear()
        if not self._create_project_structure(p_dir):
            self._logger.msg_error.emit("Creating project directory structure in <b>{0}</b> failed".format(p_dir))

    def connect_signals(self):
        """Connect signals to slots."""
        self.dag_handler.dag_simulation_requested.connect(self.notify_changes_in_dag)

    def _create_project_structure(self, directory):
        """Makes the given directory a Spine Toolbox project directory.
        Creates directories and files that are common to all projects.

        Args:
            directory (str): Abs. path to a directory that should be made into a project directory

        Returns:
            bool: True if project structure was created successfully, False otherwise
        """
        self.project_dir = directory
        self.config_dir = os.path.abspath(os.path.join(self.project_dir, ".spinetoolbox"))
        self.items_dir = os.path.abspath(os.path.join(self.config_dir, "items"))
        self.specs_dir = os.path.abspath(os.path.join(self.config_dir, "specifications"))
        self.config_file = os.path.abspath(os.path.join(self.config_dir, PROJECT_FILENAME))
        for dir_ in (self.project_dir, self.config_dir, self.items_dir, self.specs_dir):
            try:
                create_dir(dir_)
            except OSError:
                self._logger.msg_error.emit("Creating directory {0} failed".format(dir_))
                return False
        return True

    def call_set_name(self, name):
        self._toolbox.undo_stack.push(SetProjectNameCommand(self, name))

    def call_set_description(self, description):
        self._toolbox.undo_stack.push(SetProjectDescriptionCommand(self, description))

    def set_name(self, name):
        """Changes project name.

        Args:
            name (str): New project name
        """
        super().set_name(name)
        self._toolbox.update_window_title()
        # Remove entry with the old name from File->Open recent menu
        self._toolbox.remove_path_from_recent_projects(self.project_dir)
        # Add entry with the new name back to File->Open recent menu
        self._toolbox.update_recent_projects()
        self._logger.msg.emit("Project name changed to <b>{0}</b>".format(self.name))

    def set_description(self, description):
        super().set_description(description)
        msg = "Project description "
        if description:
            msg += f"changed to <b>{description}</b>"
        else:
            msg += "cleared"
        self._logger.msg.emit(msg)

    def save(self, spec_paths):
        """Collects project information and objects
        into a dictionary and writes it to a JSON file.

        Args:
            spec_paths (dict): List of absolute paths to specification files keyed by item type

        Returns:
            bool: True or False depending on success
        """
        project_dict = dict()  # Dictionary for storing project info
        project_dict["version"] = LATEST_PROJECT_VERSION
        project_dict["name"] = self.name
        project_dict["description"] = self.description
        project_dict["specifications"] = spec_paths
        # Compute connections directly from Links on scene
        project_dict["connections"] = [link.to_dict() for link in self._toolbox.ui.graphicsView.links()]
        items_dict = dict()  # Dictionary for storing project items
        # Traverse all items in project model by category
        for category_item in self._project_item_model.root().children():
            category = category_item.name
            # Store item dictionaries with item name as key and item_dict as value
            for item in self._project_item_model.items(category):
                items_dict[item.name] = item.project_item.item_dict()
        # Save project to file
        saved_dict = dict(project=project_dict, items=items_dict)
        # Write into JSON file
        with open(self.config_file, "w") as fp:
            json.dump(saved_dict, fp, indent=4)
        return True

    def load(self, items_dict):
        """Populates project item model with items loaded from project file.

        Args:
            items_dict (dict): Dictionary containing all project items in JSON format

        Returns:
            bool: True if successful, False otherwise
        """
        self._logger.msg.emit("Loading project items...")
        if not items_dict:
            self._logger.msg_warning.emit("Project has no items")
        self.make_and_add_project_items(items_dict, verbosity=False)
        return True

    def add_project_items(self, items_dict, set_selected=False, verbosity=True):
        """Pushes an AddProjectItemsCommand to the toolbox undo stack.
        """
        if not items_dict:
            return
        self._toolbox.undo_stack.push(
            AddProjectItemsCommand(self, items_dict, set_selected=set_selected, verbosity=verbosity)
        )

    def make_project_tree_items(self, items_dict):
        """Creates and returns a dictionary mapping category indexes to a list of corresponding LeafProjectTreeItem instances.

        Args:
            items_dict (dict): a mapping from item name to item dict

        Returns:
            dict(QModelIndex, list(LeafProjectTreeItem))
        """
        project_items_by_category = {}
        for item_name, item_dict in items_dict.items():
            item_type = item_dict["type"]
            factory = self._toolbox.item_factories.get(item_type)
            if factory is None:
                self._logger.msg_error.emit(f"Unknown item type <b>{item_type}</b>")
                self._logger.msg_error.emit(f"Loading project item <b>{item_name}</b> failed")
                return {}
            try:
                project_item = factory.make_item(item_name, item_dict, self._toolbox, self, self._logger)
            except TypeError as error:
                self._logger.msg_error.emit(
                    f"Creating <b>{item_type}</b> project item <b>{item_name}</b> failed. "
                    "This is most likely caused by an outdated project file."
                )
                logging.debug(error)
                continue
            except KeyError as error:
                self._logger.msg_error.emit(
                    f"Creating <b>{item_type}</b> project item <b>{item_name}</b> failed. "
                    f"This is most likely caused by an outdated or corrupted project file "
                    f"(missing JSON key: {str(error)})."
                )
                logging.debug(error)
                continue
            original_data_dir = item_dict.get("original_data_dir")
            original_db_url = item_dict.get("original_db_url")
            if original_data_dir is not None and original_db_url is not None:
                project_item.copy_local_data(original_data_dir, original_db_url)
            project_items_by_category.setdefault(project_item.item_category(), list()).append(project_item)
        project_tree_items = {}
        for category, project_items in project_items_by_category.items():
            category_ind = self._project_item_model.find_category(category)
            # NOTE: category_ind might be None, and needs to be handled caller side
            project_tree_items[category_ind] = [
                LeafProjectTreeItem(project_item, self._toolbox) for project_item in project_items
            ]
        return project_tree_items

    def do_add_project_tree_items(self, category_ind, *project_tree_items, set_selected=False, verbosity=True):
        """Adds LeafProjectTreeItem instances to project.

        Args:
            category_ind (QModelIndex): The category index
            project_tree_items (LeafProjectTreeItem): one or more LeafProjectTreeItem instances to add
            set_selected (bool): Whether to set item selected after the item has been added to project
            verbosity (bool): If True, prints message
        """
        for project_tree_item in project_tree_items:
            project_item = project_tree_item.project_item
            self._project_item_model.insert_item(project_tree_item, category_ind)
            self._finish_project_item_construction(project_item)
            # Append new node to networkx graph
            self.add_to_dag(project_item.name)
            if verbosity:
                self._logger.msg.emit(
                    "{0} <b>{1}</b> added to project".format(project_item.item_type(), project_item.name)
                )
        if set_selected:
            item = list(project_tree_items)[-1]
            self.set_item_selected(item)

    def set_item_selected(self, item):
        """
        Selects the given item.

        Args:
            item (LeafProjectTreeItem)
        """
        ind = self._project_item_model.find_item(item.name)
        self._toolbox.ui.treeView_project.setCurrentIndex(ind)

    def make_and_add_project_items(self, items_dict, set_selected=False, verbosity=True):
        """Adds items to project at loading.

        Args:
            items_dict (dict): a mapping from item name to item dict
            set_selected (bool): Whether to set item selected after the item has been added to project
            verbosity (bool): If True, prints message
        """
        for category_ind, project_tree_items in self.make_project_tree_items(items_dict).items():
            self.do_add_project_tree_items(
                category_ind, *project_tree_items, set_selected=set_selected, verbosity=verbosity
            )

    def add_to_dag(self, item_name):
        """Add new node (project item) to the directed graph."""
        self.dag_handler.add_dag_node(item_name)

    def remove_all_items(self):
        """Pushes a RemoveAllProjectItemsCommand to the toolbox undo stack."""
        items_per_category = self._project_item_model.items_per_category()
        if not any(v for v in items_per_category.values()):
            self._logger.msg.emit("No project items to remove")
            return
        delete_data = int(self._settings.value("appSettings/deleteData", defaultValue="0")) != 0
        msg = "Remove all items from project?"
        if not delete_data:
            msg += "Item data directory will still be available in the project directory after this operation."
        else:
            msg += "<br><br><b>Warning: Item data will be permanently lost after this operation.</b>"
        message_box = QMessageBox(
            QMessageBox.Question,
            "Remove All Items",
            msg,
            buttons=QMessageBox.Ok | QMessageBox.Cancel,
            parent=self._toolbox,
        )
        message_box.button(QMessageBox.Ok).setText("Remove Items")
        answer = message_box.exec_()
        if answer != QMessageBox.Ok:
            return
        links = self._toolbox.ui.graphicsView.links()
        self._toolbox.undo_stack.push(
            RemoveAllProjectItemsCommand(self, items_per_category, links, delete_data=delete_data)
        )

    def remove_item(self, name, check_dialog=False):
        """Pushes a RemoveProjectItemCommand to the toolbox undo stack.

        Args:
            name (str): Item's name
            check_dialog (bool): If True, shows 'Are you sure?' message box
        """
        delete_data = int(self._settings.value("appSettings/deleteData", defaultValue="0")) != 0
        if check_dialog:
            msg = "Remove item <b>{}</b> from project? ".format(name)
            if not delete_data:
                msg += "Item data directory will still be available in the project directory after this operation."
            else:
                msg += "<br><br><b>Warning: Item data will be permanently lost after this operation.</b>"
            msg += "<br><br>Tip: Remove items by pressing 'Delete' key to bypass this dialog."
            # noinspection PyCallByClass, PyTypeChecker
            message_box = QMessageBox(
                QMessageBox.Question,
                "Remove Item",
                msg,
                buttons=QMessageBox.Ok | QMessageBox.Cancel,
                parent=self._toolbox,
            )
            message_box.button(QMessageBox.Ok).setText("Remove Item")
            answer = message_box.exec_()
            if answer != QMessageBox.Ok:
                return
        self._toolbox.undo_stack.push(RemoveProjectItemCommand(self, name, delete_data=delete_data))

    def do_remove_item(self, name):
        """Removes item from project given its name.
        This method is used when closing the existing project for opening a new one.

        Args:
            name (str): Item's name
        """
        ind = self._project_item_model.find_item(name)
        category_ind = ind.parent()
        item = self._project_item_model.item(ind)
        self._remove_item(category_ind, item)

    def _remove_item(self, category_ind, item, delete_data=False):
        """Removes LeafProjectTreeItem from project.

        Args:
            category_ind (QModelIndex): The category index
            item (LeafProjectTreeItem): the item to remove
            delete_data (bool): If set to True, deletes the directories and data associated with the item
        """
        try:
            data_dir = item.project_item.data_dir
        except AttributeError:
            data_dir = None
        # Remove item from project model
        if not self._project_item_model.remove_item(item, parent=category_ind):
            self._logger.msg_error.emit("Removing item <b>{0}</b> from project failed".format(item.name))
        # Remove item icon and connected links (QGraphicsItems) from scene
        icon = item.project_item.get_icon()
        self._toolbox.ui.graphicsView.remove_icon(icon)
        self.dag_handler.remove_node_from_graph(item.name)
        item.project_item.tear_down()
        if delete_data:
            if data_dir:
                # Remove data directory and all its contents
                self._logger.msg.emit("Removing directory <b>{0}</b>".format(data_dir))
                try:
                    if not erase_dir(data_dir):
                        self._logger.msg_error.emit("Directory does not exist")
                except OSError:
                    self._logger.msg_error.emit("[OSError] Removing directory failed. Check directory permissions.")
            self._logger.msg.emit("Item <b>{0}</b> removed from project".format(item.name))

    def execute_dags(self, dags, execution_permits):
        """Executes given dags.

        Args:
            dags (Sequence(DiGraph))
            execution_permits (Sequence(dict))
        """
        self._execution_stopped = False
        self._execute_dags(dags, execution_permits)

    def _get_node_successors(self, dag, dag_identifier):
        node_successors = self.dag_handler.node_successors(dag)
        if not node_successors:
            self._logger.msg_warning.emit("<b>Graph {0} is not a Directed Acyclic Graph</b>".format(dag_identifier))
            self._logger.msg.emit("Items in graph: {0}".format(", ".join(dag.nodes())))
            edges = ["{0} -> {1}".format(*edge) for edge in self.dag_handler.edges_causing_loops(dag)]
            self._logger.msg.emit(
                "Please edit connections in Design View to execute it. "
                "Possible fix: remove connection(s) {0}.".format(", ".join(edges))
            )
            return None
        return node_successors

    def _make_settings_dict(self):
        # XXX: We may want to introduce a new group "executionSettings", for more clarity
        settings = {}
        self._settings.beginGroup("appSettings")
        for key in self._settings.childKeys():
            value = self._settings.value(key)
            try:
                json.dumps(value)
            except (TypeError, json.decoder.JSONDecodeError):
                continue
            settings[f"appSettings/{key}"] = value
        self._settings.endGroup()
        return settings

    def _execute_dags(self, dags, execution_permits_list):
        if self._engine_workers:
            self._logger.msg_error.emit("Execution already in progress.")
            return
        settings = self._make_settings_dict()
        for k, (dag, execution_permits) in enumerate(zip(dags, execution_permits_list)):
            dag_identifier = f"{k + 1}/{len(dags)}"
            self._execute_dag(dag, execution_permits, dag_identifier, settings)

    def _execute_dag(self, dag, execution_permits, dag_identifier, settings):
        node_successors = self._get_node_successors(dag, dag_identifier)
        if node_successors is None:
            return
        project_items = {name: self._project_item_model.get_item(name).project_item for name in node_successors}
        items = {}
        specifications = {}
        for name, project_item in project_items.items():
            items[name] = project_item.item_dict()
            spec = project_item.specification()
            if spec is not None:
                specifications.setdefault(project_item.item_type(), list()).append(spec.to_dict())
        filter_stacks = {}
        for item in project_items.values():
            for link in item.get_icon().outgoing_links():
                filter_stacks.update(link.filter_stacks())
        data = {
            "items": items,
            "specifications": specifications,
            "node_successors": node_successors,
            "filter_stacks": filter_stacks,
            "execution_permits": execution_permits,
            "settings": settings,
            "project_dir": self.project_dir,
        }
        self._logger.msg.emit("<b>Starting DAG {0}</b>".format(dag_identifier))
        self._logger.msg.emit("Order: {0}".format(" -> ".join(list(node_successors))))
        worker = SpineEngineWorker(self._toolbox, data, dag, dag_identifier, project_items)
        self._engine_workers.append(worker)
        worker.finished.connect(lambda worker=worker: self._handle_engine_worker_finished(worker))
        worker.start()

    def _handle_engine_worker_finished(self, worker):
        finished_outcomes = {
            "USER_STOPPED": "stopped by the user",
            "FAILED": "failed",
            "COMPLETED": "completed successfully",
        }
        outcome = finished_outcomes.get(worker.engine_final_state())
        if outcome is not None:
            self._logger.msg.emit("<b>DAG {0} {1}</b>".format(worker.dag_identifier, outcome))
        if any(worker.engine_final_state() not in finished_outcomes for worker in self._engine_workers):
            return
        # Only after all workers have finished, notify changes and handle successful executions.
        # Doing it while executing leads to deadlocks in acquiring sqlalchemy's infamous _CONFIGURE_MUTEX lock,
        # needed to create DatabaseMapping instances. It seems that the lock gets confused when
        # being acquired by threads from different processes or maybe even different QThreads
        # Can't say I really understand it totally.
        for finished_worker in self._engine_workers:
            self.notify_changes_in_dag(finished_worker.dag)
            for item, direction, state in finished_worker.sucessful_executions:
                item.handle_execution_successful(direction, state)
            finished_worker.clean_up()
        self._engine_workers.clear()
        self.project_execution_finished.emit()

    def execute_selected(self):
        """Executes DAGs corresponding to all selected project items."""
        if not self.dag_handler.dags():
            self._logger.msg_warning.emit("Project has no items to execute")
            return
        # Get selected item
        selected_indexes = self._toolbox.ui.treeView_project.selectedIndexes()
        if not selected_indexes:
            self._logger.msg_warning.emit("Please select a project item and try again.")
            return
        dags = set()
        executable_item_names = list()
        for ind in selected_indexes:
            item = self._project_item_model.item(ind)
            executable_item_names.append(item.name)
            dag = self.dag_handler.dag_with_node(item.name)
            if not dag:
                self._logger.msg_error.emit(
                    "[BUG] Could not find a graph containing {0}. "
                    "<b>Please reopen the project.</b>".format(item.name)
                )
                continue
            dags.add(dag)
        execution_permit_list = list()
        for dag in dags:
            execution_permits = dict()
            for item_name in dag.nodes:
                execution_permits[item_name] = item_name in executable_item_names
            execution_permit_list.append(execution_permits)
        self._logger.msg.emit("")
        self._logger.msg.emit("-------------------------------------------------")
        self._logger.msg.emit("<b>Executing Selected Directed Acyclic Graphs</b>")
        self._logger.msg.emit("-------------------------------------------------")
        self.execute_dags(dags, execution_permit_list)

    def execute_project(self):
        """Executes all dags in the project."""
        self.project_execution_about_to_start.emit()
        dags = self.dag_handler.dags()
        if not dags:
            self._logger.msg_warning.emit("Project has no items to execute")
            return
        execution_permit_list = list()
        for dag in dags:
            execution_permit_list.append({item_name: True for item_name in dag.nodes})
        self._logger.msg.emit("")
        self._logger.msg.emit("--------------------------------------------")
        self._logger.msg.emit("<b>Executing All Directed Acyclic Graphs</b>")
        self._logger.msg.emit("--------------------------------------------")
        self.execute_dags(dags, execution_permit_list)

    def stop(self):
        """Stops execution. Slot for the main window Stop tool button in the toolbar."""
        if self._execution_stopped:
            self._logger.msg.emit("No execution in progress")
            return
        self._logger.msg.emit("Stopping...")
        self._execution_stopped = True
        # Stop experimental engines
        for worker in self._engine_workers:
            worker.stop_engine()

    def export_graphs(self):
        """Exports all valid directed acyclic graphs in project to GraphML files."""
        if not self.dag_handler.dags():
            self._logger.msg_warning.emit("Project has no graphs to export")
            return
        i = 0
        for g in self.dag_handler.dags():
            fn = str(i) + ".graphml"
            path = os.path.join(self.project_dir, fn)
            if not self.dag_handler.export_to_graphml(g, path):
                self._logger.msg_warning.emit("Exporting graph nr. {0} failed. Not a directed acyclic graph".format(i))
            else:
                self._logger.msg.emit("Graph nr. {0} exported to {1}".format(i, path))
            i += 1

    @Slot(object)
    def notify_changes_in_dag(self, dag):
        """Notifies the items in given dag that the dag has changed."""
        # We wait 100 msecs before do the notification. This is to avoid notifying multiple
        # times the same dag, when multiple items in that dag change.
        if dag in self._dags_about_to_be_notified:
            return
        self._dags_about_to_be_notified.add(dag)
        QTimer.singleShot(100, lambda dag=dag: self._do_notify_changes_in_dag(dag))

    def _do_notify_changes_in_dag(self, dag):
        self._dags_about_to_be_notified.remove(dag)
        node_successors = self.dag_handler.node_successors(dag)
        items = {item.name: item.project_item for item in self._project_item_model.items()}
        if not node_successors:
            # Not a dag, invalidate workflow
            edges = self.dag_handler.edges_causing_loops(dag)
            for node in dag.nodes():
                item = items[node].invalidate_workflow(edges)
            return
        # Make resource map and run simulation
        node_predecessors = inverted(node_successors)
        ranks = _ranks(node_successors)
        # Memoize resources, so we don't call multiple times the same function
        resources_for_direct_successors = {}
        resources_for_direct_predecessors = {}
        for item_name, child_names in node_successors.items():
            item = items[item_name]
            upstream_resources = []
            downstream_resources = []
            for parent_name in node_predecessors.get(item_name, set()):
                parent_item = items[parent_name]
                if parent_item not in resources_for_direct_successors:
                    resources_for_direct_successors[parent_item] = parent_item.resources_for_direct_successors()
                upstream_resources += resources_for_direct_successors[parent_item]
            for child_name in child_names:
                child_item = items[child_name]
                if child_item not in resources_for_direct_predecessors:
                    resources_for_direct_predecessors[child_item] = child_item.resources_for_direct_predecessors()
                downstream_resources += resources_for_direct_predecessors[child_item]
            item.handle_dag_changed(ranks[item_name], upstream_resources, downstream_resources)
            if item_name not in resources_for_direct_successors:
                resources_for_direct_successors[item_name] = item.resources_for_direct_successors()
            for link in item.get_icon().outgoing_links():
                link.handle_dag_changed(resources_for_direct_successors[item_name])

    def notify_changes_in_all_dags(self):
        """Notifies all items of changes in all dags in the project."""
        for g in self.dag_handler.dags():
            self.notify_changes_in_dag(g)

    def notify_changes_in_containing_dag(self, item):
        """Notifies items in dag containing the given item that the dag has changed."""
        dag = self.dag_handler.dag_with_node(item)
        # Some items trigger this method while they are being initialized
        # but before they have been added to any DAG.
        # In those cases we don't need to notify other items.
        if dag:
            self.notify_changes_in_dag(dag)

    @property
    def settings(self):
        return self._settings

    def _finish_project_item_construction(self, project_item):
        """
        Activates the given project item so it works with the given toolbox.
        This is mainly intended to facilitate adding items back with redo.

        Args:
            project_item (ProjectItem)
        """
        icon = project_item.get_icon()
        if icon is not None:
            icon.activate()
        else:
            icon = self._toolbox.project_item_icon(project_item.item_type())
            project_item.set_icon(icon)
        properties_ui = self._toolbox.project_item_properties_ui(project_item.item_type())
        project_item.set_properties_ui(properties_ui)
        project_item.create_data_dir()
        project_item.set_up()


def _ranks(node_successors):
    """
    Calculates node ranks.

    Args:
        node_successors (dict): a mapping from successor name to a list of predecessor names

    Returns:
        dict: a mapping from node name to rank
    """
    node_predecessors = dict()
    for predecessor, successors in node_successors.items():
        node_predecessors.setdefault(predecessor, list())
        for successor in successors:
            node_predecessors.setdefault(successor, list()).append(predecessor)
    ranking = []
    while node_predecessors:
        same_ranks = [node for node, predecessor in node_predecessors.items() if not predecessor]
        for ranked_node in same_ranks:
            del node_predecessors[ranked_node]
            for node, successors in node_predecessors.items():
                node_predecessors[node] = [s for s in successors if s != ranked_node]
        ranking.append(same_ranks)
    return {node: rank for rank, nodes in enumerate(ranking) for node in nodes}
