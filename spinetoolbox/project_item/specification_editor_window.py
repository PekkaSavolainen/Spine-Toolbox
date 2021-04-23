######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains SpecificationEditorWindowBase and ChangeSpecPropertyCommand

:author: M. Marin (KTH), P. Savolainen (VTT)
:date:   12.4.2018
"""

from PySide2.QtGui import QGuiApplication, QKeySequence, QIcon
from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QUndoStack,
    QLabel,
    QWidget,
    QToolBar,
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QAction,
    QMenu,
    QLineEdit,
    QCheckBox,
    QUndoCommand,
    QErrorMessage,
)
from spinetoolbox.config import STATUSBAR_SS
from spinetoolbox.widgets.notification import ChangeNotifier
from spinetoolbox.helpers import ensure_window_is_on_screen, CharIconEngine


class ChangeSpecPropertyCommand(QUndoCommand):
    """Command to set specification properties."""

    def __init__(self, callback, new_value, old_value, cmd_name):
        """
        Args:
            callback (function): Function to call to set the spec property.
            new_value (any): new value
            old_value (any): old value
            cmd_name (str): command name
        """
        super().__init__()
        self._callback = callback
        self._new_value = new_value
        self._old_value = old_value
        self.setText(cmd_name)
        self.setObsolete(new_value == old_value)

    def redo(self):
        self._callback(self._new_value)

    def undo(self):
        self._callback(self._old_value)


class SpecificationEditorWindowBase(QMainWindow):
    def __init__(self, toolbox, specification=None, item=None):
        """Base class for spec editors.

        Args:
            toolbox (ToolboxUI): QMainWindow instance
            specification (ProjectItemSpecification, optional): If given, the form is pre-filled with this specification
            item (ProjectItem, optional): Sets the spec for this item if accepted
        """
        super().__init__(parent=toolbox)  # Inherit stylesheet from ToolboxUI
        # Class attributes
        self._toolbox = toolbox
        self._original_spec_name = None if specification is None else specification.name
        self.specification = specification
        self.item = item
        self._app_settings = toolbox.qsettings()
        # Setup UI from Qt Designer file
        self._ui = self._make_ui()
        self._ui.setupUi(self)
        self._ui_error = QErrorMessage(self)
        self._ui_error.setWindowTitle("Error")
        self._ui_error.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(specification.name if specification else "")
        # Restore ui
        self._restore_dock_widgets()
        restore_ui(self, self._app_settings, self.settings_group)
        # Setup undo stack and change notifier
        self._undo_stack = QUndoStack(self)
        self._change_notifier = ChangeNotifier(self, self._undo_stack, self._app_settings, "appSettings/specShowUndo")
        # Setup toolbar
        self._spec_toolbar = _SpecNameDescriptionToolbar(self, specification, self._undo_stack)
        self.addToolBar(Qt.TopToolBarArea, self._spec_toolbar)
        self._ui.statusbar.setStyleSheet(STATUSBAR_SS)
        self._populate_main_menu()
        self._spec_toolbar.save_action.triggered.connect(self._save)
        self._spec_toolbar.close_action.triggered.connect(self.close)
        self._undo_stack.cleanChanged.connect(self._update_window_modified)

    @property
    def settings_group(self):
        """Returns the settings group for this spec type.

        Returns
            str
        """
        raise NotImplementedError()

    def _make_ui(self):
        """Returns the ui object from Qt designer.

        Returns
            object
        """
        raise NotImplementedError()

    def _restore_dock_widgets(self):
        """Restores dockWidgets to some default state. Called in the constructor, before restoring the ui from settings.
        Reimplement in subclasses if needed."""

    def _make_new_specification(self, spec_name):
        """Returns a ProjectItemSpecification from current form settings.

        Args:
            spec_name (str): Name of the spec

        Returns:
            ProjectItemSpecification
        """
        raise NotImplementedError()

    @Slot(str)
    def _show_error(self, message):
        self._ui_error.showMessage(message)

    def _show_status_bar_msg(self, msg):
        word_count = len(msg.split(" "))
        mspw = 60000 / 140  # Assume we can read ~140 words per minute
        duration = mspw * word_count
        self._ui.statusbar.showMessage(msg, duration)

    def _populate_main_menu(self):
        undo_action = self._undo_stack.createUndoAction(self)
        redo_action = self._undo_stack.createRedoAction(self)
        undo_action.setShortcuts(QKeySequence.Undo)
        redo_action.setShortcuts(QKeySequence.Redo)
        self._spec_toolbar.menu.insertActions(self._spec_toolbar.save_action, [redo_action, undo_action])
        self._spec_toolbar.menu.insertSeparator(self._spec_toolbar.save_action)

    @Slot(bool)
    def _update_window_modified(self, clean):
        self.setWindowModified(not clean)
        self._spec_toolbar.save_action.setEnabled(not clean)
        self.setWindowTitle(self._spec_toolbar.name())
        self.windowTitleChanged.emit(self.windowTitle())

    def _save(self):
        """Saves spec."""
        name = self._spec_toolbar.name()
        if not name:
            self._show_error("Please enter a name for the specification.")
            return False
        new_spec = self._make_new_specification(name)
        if new_spec is None:
            return False
        update_existing = new_spec.name == self._original_spec_name
        if not self._toolbox.add_specification(new_spec, update_existing, self):
            return False
        self._undo_stack.setClean()
        if self.item:
            self.item.set_specification(new_spec)
        self.specification = new_spec
        self.setWindowTitle(self.specification.name)
        return True

    def tear_down(self):
        if self.focusWidget():
            self.focusWidget().clearFocus()
        if not self._undo_stack.isClean() and not prompt_to_save_changes(self, self._toolbox.qsettings(), self._save):
            return False
        self._undo_stack.cleanChanged.disconnect(self._update_window_modified)
        save_ui(self, self._app_settings, self.settings_group)
        return True

    def closeEvent(self, event):
        if not self.tear_down():
            event.ignore()
            return
        super().closeEvent(event)


class _SpecNameDescriptionToolbar(QToolBar):
    """A QToolBar to let users set name and description for an Spec."""

    def __init__(self, parent, spec, undo_stack):
        """

        Args:
            parent (QMainWindow): QMainWindow instance
            spec (ProjectItemSpecification): specification that is being edited
            undo_stack (QUndoStack): an undo stack
        """
        super().__init__("Specification name and description", parent=parent)
        self._parent = parent
        self._undo_stack = undo_stack
        self._current_name = ""
        self._current_description = ""
        self._line_edit_name = QLineEdit()
        self._line_edit_description = QLineEdit()
        self._line_edit_name.setPlaceholderText("Enter specification name here...")
        self._line_edit_description.setPlaceholderText("Enter specification description here...")
        self.setAllowedAreas(Qt.TopToolBarArea)
        self.setFloatable(False)
        self.setMovable(False)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self._line_edit_name)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self._line_edit_description)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setStretchFactor(self._line_edit_name, 1)
        layout.setStretchFactor(self._line_edit_description, 3)
        self.addWidget(widget)
        self.menu = self._make_main_menu()
        self.save_action = self.menu.addAction("Save")
        self.save_action.setEnabled(False)
        self.close_action = self.menu.addAction("Close")
        self.save_action.setShortcut(QKeySequence.Save)
        self.close_action.setShortcut(QKeySequence.Close)
        self.setObjectName("_SpecNameDescriptionToolbar")
        if spec:
            self.do_set_name(spec.name)
            self.do_set_description(spec.description)
        self._line_edit_name.editingFinished.connect(self._set_name)
        self._line_edit_description.editingFinished.connect(self._set_description)

    def _make_main_menu(self):
        menu = QMenu(self)
        menu_action = self.addAction(QIcon(CharIconEngine("\uf0c9")), "")
        menu_action.setMenu(menu)
        menu_button = self.widgetForAction(menu_action)
        menu_button.setPopupMode(menu_button.InstantPopup)
        action = QAction(self)
        action.triggered.connect(menu_button.showMenu)
        keys = [QKeySequence(Qt.ALT + Qt.Key_F), QKeySequence(Qt.ALT + Qt.Key_E)]
        action.setShortcuts(keys)
        self._parent.addAction(action)
        keys_str = ", ".join([key.toString() for key in keys])
        menu_button.setToolTip(f"<p>Main menu ({keys_str})</p>")
        return menu

    @Slot()
    def _set_name(self):
        if self.name() == self._current_name:
            return
        self._undo_stack.push(
            ChangeSpecPropertyCommand(self.do_set_name, self.name(), self._current_name, "change specification name")
        )

    @Slot()
    def _set_description(self):
        if self.description() == self._current_description:
            return
        self._undo_stack.push(
            ChangeSpecPropertyCommand(
                self.do_set_description,
                self.description(),
                self._current_description,
                "change specification description",
            )
        )

    def do_set_name(self, name):
        self._current_name = name
        self._line_edit_name.setText(name)

    def do_set_description(self, description):
        self._current_description = description
        self._line_edit_description.setText(description)

    def name(self):
        return self._line_edit_name.text()

    def description(self):
        return self._line_edit_description.text()


def prompt_to_save_changes(parent, settings, save_callback):
    """Prompts to save changes.

    Args:
        parent (QWidget): Spec editor widget
        settings (QSettings): Toolbox settings
        save_callback (Callable): A function to call if the user chooses Save.
            It must return True or False depending on the outcome of the 'saving'.

    Returns:
        bool: False if the user chooses to cancel, in which case we don't close the form.
    """
    save_spec = int(settings.value("appSettings/saveSpecBeforeClosing", defaultValue="1"))
    if save_spec == 0:
        return True
    if save_spec == 2:
        return save_callback()
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle(parent.windowTitle())
    msg.setText("Do you want to save your changes to the specification?")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
    chkbox = QCheckBox()
    chkbox.setText("Do not ask me again")
    msg.setCheckBox(chkbox)
    answer = msg.exec_()
    if answer == QMessageBox.Cancel:
        return False
    if chkbox.checkState() == 2:
        # Save preference
        preference = "2" if answer == QMessageBox.Yes else "0"
        settings.setValue("appSettings/saveSpecBeforeClosing", preference)
    if answer == QMessageBox.Yes:
        return save_callback()
    return True


def restore_ui(window, app_settings, settings_group):
    """Restores UI state from previous session.

    Args:
        window (QMainWindow)
        app_settings (QSettings)
        settings_group (str)
    """
    app_settings.beginGroup(settings_group)
    window_size = app_settings.value("windowSize")
    window_pos = app_settings.value("windowPosition")
    window_state = app_settings.value("windowState")
    window_maximized = app_settings.value("windowMaximized", defaultValue='false')
    n_screens = app_settings.value("n_screens", defaultValue=1)
    app_settings.endGroup()
    original_size = window.size()
    if window_size:
        window.resize(window_size)
    if window_pos:
        window.move(window_pos)
    if window_state:
        window.restoreState(window_state, version=1)  # Toolbar and dockWidget positions
    # noinspection PyArgumentList
    if len(QGuiApplication.screens()) < int(n_screens):
        # There are less screens available now than on previous application startup
        window.move(0, 0)  # Move this widget to primary screen position (0,0)
    ensure_window_is_on_screen(window, original_size)
    if window_maximized == 'true':
        window.setWindowState(Qt.WindowMaximized)


def save_ui(window, app_settings, settings_group):
    """Saves UI state for next session.

    Args:
        window (QMainWindow)
        app_settings (QSettings)
        settings_group (str)
    """
    app_settings.beginGroup(settings_group)
    app_settings.setValue("windowSize", window.size())
    app_settings.setValue("windowPosition", window.pos())
    app_settings.setValue("windowState", window.saveState(version=1))
    app_settings.setValue("windowMaximized", window.windowState() == Qt.WindowMaximized)
    app_settings.setValue("n_screens", len(QGuiApplication.screens()))
    app_settings.endGroup()