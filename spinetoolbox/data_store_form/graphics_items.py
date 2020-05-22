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
Classes for drawing graphics items on graph view's QGraphicsScene.

:authors: M. Marin (KTH), P. Savolainen (VTT)
:date:   4.4.2018
"""
from PySide2.QtCore import Qt, Signal, Slot, QLineF
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
    QGraphicsSimpleTextItem,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
    QGraphicsLineItem,
    QStyle,
    QApplication,
    QMenu,
)
from PySide2.QtGui import QPen, QBrush, QPainterPath, QFont, QPalette, QGuiApplication


class EntityItem(QGraphicsPixmapItem):
    def __init__(self, data_store_form, x, y, extent, entity_id=None):
        """Initializes item

        Args:
            data_store_form (DataStoreForm): 'owner'
            x (float): x-coordinate of central point
            y (float): y-coordinate of central point
            extent (int): Preferred extent
            entity_id (int): The entity id
        """
        super().__init__()
        self._data_store_form = data_store_form
        self.db_mngr = data_store_form.db_mngr
        self.db_map = data_store_form.db_map
        self.entity_id = entity_id
        self.arc_items = list()
        self._extent = extent
        self.refresh_icon()
        self.setPos(x, y)
        rect = self.boundingRect()
        self.setOffset(-rect.width() / 2, -rect.height() / 2)
        self._moved_on_scene = False
        self._bg = None
        self._bg_brush = Qt.NoBrush
        self._init_bg()
        self._bg.setFlag(QGraphicsItem.ItemStacksBehindParent, enabled=True)
        self.setZValue(0)
        self.setFlag(QGraphicsItem.ItemIsSelectable, enabled=True)
        self.setFlag(QGraphicsItem.ItemIsMovable, enabled=True)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, enabled=True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, enabled=True)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.ArrowCursor)
        self._menu = self._make_menu()

    @property
    def entity_type(self):
        raise NotImplementedError()

    @property
    def entity_name(self):
        return self.db_mngr.get_item(self.db_map, self.entity_type, self.entity_id)["name"]

    @property
    def entity_class_type(self):
        return {"relationship": "relationship class", "object": "object class"}[self.entity_type]

    @property
    def entity_class_id(self):
        return self.db_mngr.get_item(self.db_map, self.entity_type, self.entity_id)["class_id"]

    @property
    def entity_class_name(self):
        return self.db_mngr.get_item(self.db_map, self.entity_class_type, self.entity_class_id)["name"]

    @property
    def first_db_map(self):
        return self.db_map

    @property
    def display_data(self):
        return self.entity_name

    @property
    def display_database(self):
        return self.db_map.codename

    @property
    def db_maps(self):
        return (self.db_map,)

    def db_map_data(self, _db_map):
        return self.db_mngr.get_item(self.db_map, self.entity_type, self.entity_id)

    def db_map_id(self, _db_map):
        return self.entity_id

    def boundingRect(self):
        return super().boundingRect() | self.childrenBoundingRect()

    def moveBy(self, dx, dy):
        super().moveBy(dx, dy)
        self.update_arcs_line()

    def _init_bg(self):
        self._bg = QGraphicsRectItem(self.boundingRect(), self)
        self._bg.setPen(Qt.NoPen)

    def refresh_icon(self):
        """Refreshes the icon."""
        pixmap = self.db_mngr.entity_class_icon(self.db_map, self.entity_class_type, self.entity_class_id).pixmap(
            self._extent
        )
        self.setPixmap(pixmap)

    def shape(self):
        """Returns a shape containing the entire bounding rect, to work better with icon transparency."""
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRect(self._bg.boundingRect())
        return path

    def paint(self, painter, option, widget=None):
        """Shows or hides the selection halo."""
        if option.state & (QStyle.State_Selected):
            self._paint_as_selected()
            option.state &= ~QStyle.State_Selected
        else:
            self._paint_as_deselected()
        super().paint(painter, option, widget)

    def _paint_as_selected(self):
        self._bg.setBrush(QGuiApplication.palette().highlight())

    def _paint_as_deselected(self):
        self._bg.setBrush(self._bg_brush)

    def add_arc_item(self, arc_item):
        """Adds an item to the list of arcs.

        Args:
            arc_item (ArcItem)
        """
        self.arc_items.append(arc_item)

    def apply_zoom(self, factor):
        """Applies zoom.

        Args:
            factor (float): The zoom factor.
        """
        if factor > 1:
            factor = 1
        self.setScale(factor)

    def apply_rotation(self, angle, center):
        """Applies rotation.

        Args:
            angle (float): The angle in degrees.
            center (QPoint): Rotates around this point.
        """
        line = QLineF(center, self.pos())
        line.setAngle(line.angle() + angle)
        self.setPos(line.p2())
        self.update_arcs_line()

    def block_move_by(self, dx, dy):
        self.moveBy(dx, dy)

    def mouseMoveEvent(self, event):
        """Moves the item and all connected arcs. Also checks for a merge target
        and sets an appropriate mouse cursor.

        Args:
            event (QGraphicsSceneMouseEvent)
        """
        if event.buttons() & Qt.LeftButton == 0:
            super().mouseMoveEvent(event)
            return
        move_by = event.scenePos() - event.lastScenePos()
        # Move selected items together
        for item in self.scene().selectedItems():
            if isinstance(item, (EntityItem)):
                item.block_move_by(move_by.x(), move_by.y())

    def update_arcs_line(self):
        """Moves arc items."""
        for item in self.arc_items:
            item.update_line()

    def itemChange(self, change, value):
        """
        Keeps track of item's movements on the scene.

        Args:
            change (GraphicsItemChange): a flag signalling the type of the change
            value: a value related to the change

        Returns:
            the same value given as input
        """
        if change == QGraphicsItem.ItemScenePositionHasChanged:
            self._moved_on_scene = True
        return value

    def set_all_visible(self, on):
        """Sets visibility status for this item and all arc items.

        Args:
            on (bool)
        """
        for item in self.arc_items:
            item.setVisible(on)
        self.setVisible(on)

    def wipe_out(self):
        """Removes this item and all its arc items from the scene."""
        self.scene().removeItem(self)
        for arc_item in self.arc_items:
            if arc_item.scene():
                arc_item.scene().removeItem(arc_item)
                other_item = arc_item.other_item(self)
                if other_item.is_wip:
                    other_item.wipe_out()

    def _make_menu(self):
        menu = QMenu(self._data_store_form)
        menu.addAction(self._data_store_form.ui.actionHide_selected)
        menu.addAction(self._data_store_form.ui.actionPrune_selected_entities)
        menu.addAction(self._data_store_form.ui.actionPrune_selected_classes)
        menu.addSeparator()
        menu.addAction(self._data_store_form.ui.actionEdit_selected)
        menu.addAction(self._data_store_form.ui.actionRemove_selected)
        return menu

    def contextMenuEvent(self, e):
        """Shows context menu.

        Args:
            e (QGraphicsSceneMouseEvent): Mouse event
        """
        e.accept()
        if not self.isSelected() and not e.modifiers() & Qt.ControlModifier:
            self.scene().clearSelection()
        self.setSelected(True)
        self._data_store_form._handle_menu_graph_about_to_show()
        self._menu.exec_(e.screenPos())


class RelationshipItem(EntityItem):
    """Relationship item to use with GraphViewForm."""

    @property
    def entity_type(self):
        return "relationship"

    @property
    def object_class_id_list(self):
        return self.db_mngr.get_item(self.db_map, "relationship class", self.entity_class_id).get(
            "object_class_id_list"
        )

    @property
    def object_name_list(self):
        return self.db_mngr.get_item(self.db_map, "relationship", self.entity_id).get("object_name_list")

    @property
    def object_id_list(self):
        return self.db_mngr.get_item(self.db_map, "relationship", self.entity_id).get("object_id_list")

    @property
    def db_representation(self):
        return dict(
            class_id=self.entity_class_id,
            id=self.entity_id,
            object_id_list=self.object_id_list,
            object_name_list=self.object_name_list,
        )

    def _init_bg(self):
        extent = self._extent
        self._bg = QGraphicsEllipseItem(-0.5 * extent, -0.5 * extent, extent, extent, self)
        self._bg.setPen(Qt.NoPen)
        bg_color = QGuiApplication.palette().color(QPalette.Normal, QPalette.Window)
        bg_color.setAlphaF(0.8)
        self._bg_brush = QBrush(bg_color)

    def _show_item_context_menu_in_parent(self, pos):
        self._data_store_form.show_relationship_item_context_menu(pos)

    def follow_object_by(self, dx, dy):
        factor = 1.0 / len(self.arc_items)
        self.moveBy(factor * dx, factor * dy)


class ObjectItem(EntityItem):
    def __init__(self, data_store_form, x, y, extent, entity_id=None):
        """Initializes the item.

        Args:
            data_store_form (GraphViewForm): 'owner'
            x (float): x-coordinate of central point
            y (float): y-coordinate of central point
            extent (int): preferred extent
            entity_id (int): object id
        """
        super().__init__(data_store_form, x, y, extent, entity_id=entity_id)
        self.setFlag(QGraphicsItem.ItemIsFocusable, enabled=True)
        self.label_item = EntityLabelItem(self)
        self.setZValue(0.5)
        self.update_name(self.entity_name)
        description = self.db_mngr.get_item(self.db_map, "object", self.entity_id).get("description")
        self.update_description(description)

    @property
    def entity_type(self):
        return "object"

    @property
    def db_representation(self):
        return dict(class_id=self.entity_class_id, id=self.entity_id, name=self.entity_name)

    def shape(self):
        path = super().shape()
        path.addPolygon(self.label_item.mapToItem(self, self.label_item.boundingRect()))
        return path

    def update_name(self, name):
        """Refreshes the name."""
        self.label_item.setPlainText(name)

    def update_description(self, description):
        self.setToolTip(f"<html>{description}</html>")

    def block_move_by(self, dx, dy):
        super().block_move_by(dx, dy)
        rel_items_follow = self._data_store_form.qsettings.value(
            "appSettings/relationshipItemsFollow", defaultValue="true"
        )
        if rel_items_follow == "false":
            return
        for arc_item in self.arc_items:
            arc_item.rel_item.follow_object_by(dx, dy)

    def _make_menu(self):
        menu = super()._make_menu()
        menu.addSeparator()
        menu.addAction("Add relationships...", self._start_relationship)
        return menu

    @Slot(bool)
    def _start_relationship(self, checked=False):
        self._data_store_form.start_relationship_from_object(self)


class RodObjectItem(ObjectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, enabled=False)

    @property
    def entity_class_name(self):
        return "?"

    @property
    def entity_name(self):
        return "?"

    def refresh_icon(self):
        """Refreshes the icon."""
        pixmap = self.db_mngr.icon_mngr[self.db_map].object_pixmap("").scaled(self._extent, self._extent)
        self.setPixmap(pixmap)

    def mouseMoveEvent(self, event):
        move_by = event.scenePos() - self.scenePos()
        self.block_move_by(move_by.x(), move_by.y())

    def contextMenuEvent(self, e):
        e.accept()


class RodRelationshipItem(RelationshipItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, enabled=False)

    def refresh_icon(self):
        """Refreshes the icon."""
        object_class_name_list = [arc_item.obj_item.entity_class_name for arc_item in self.arc_items]
        object_class_name_list = ",".join(object_class_name_list)
        pixmap = (
            self.db_mngr.icon_mngr[self.db_map]
            .relationship_pixmap(object_class_name_list)
            .scaled(self._extent, self._extent)
        )
        self.setPixmap(pixmap)

    def block_move_by(self, dx, dy):
        super().block_move_by(dx, dy)
        for arc_item in self.arc_items:
            arc_item.rel_item.follow_object_by(dx, dy)


class ArcItem(QGraphicsLineItem):
    """Arc item to use with GraphViewForm. Connects a RelationshipItem to an ObjectItem."""

    def __init__(self, rel_item, obj_item, width):
        """Initializes item.

        Args:
            rel_item (spinetoolbox.widgets.graph_view_graphics_items.RelationshipItem): relationship item
            obj_item (spinetoolbox.widgets.graph_view_graphics_items.ObjectItem): object item
            width (float): Preferred line width
        """
        super().__init__()
        self.rel_item = rel_item
        self.obj_item = obj_item
        self._width = float(width)
        self.update_line()
        self._pen = self._make_pen()
        self.setPen(self._pen)
        self.setZValue(-2)
        rel_item.add_arc_item(self)
        obj_item.add_arc_item(self)
        self.setCursor(Qt.ArrowCursor)

    def _make_pen(self):
        pen = QPen()
        pen.setWidth(self._width)
        color = QGuiApplication.palette().color(QPalette.Normal, QPalette.WindowText)
        color.setAlphaF(0.8)
        pen.setColor(color)
        pen.setStyle(Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)
        return pen

    def moveBy(self, dx, dy):
        """Does nothing. This item is not moved the regular way, but follows the EntityItems it connects."""

    def update_line(self):
        src_x = self.rel_item.x()
        src_y = self.rel_item.y()
        dst_x = self.obj_item.x()
        dst_y = self.obj_item.y()
        self.setLine(src_x, src_y, dst_x, dst_y)

    def mousePressEvent(self, event):
        """Accepts the event so it's not propagated."""
        event.accept()

    def other_item(self, item):
        return {self.rel_item: self.obj_item, self.obj_item: self.rel_item}.get(item)

    def apply_zoom(self, factor):
        """Applies zoom.

        Args:
            factor (float): The zoom factor.
        """
        if factor < 1:
            factor = 1
        scaled_width = self._width / factor
        self._pen.setWidthF(scaled_width)
        self.setPen(self._pen)

    def wipe_out(self):
        self.obj_item.arc_items.remove(self)
        self.rel_item.arc_items.remove(self)


class RodArcItem(ArcItem):
    def _make_pen(self):
        pen = super()._make_pen()
        pen.setStyle(Qt.DotLine)
        return pen


class EntityLabelItem(QGraphicsTextItem):
    """Label item for items in GraphViewForm."""

    entity_name_edited = Signal(str)

    def __init__(self, entity_item):
        """Initializes item.

        Args:
            entity_item (spinetoolbox.widgets.graph_view_graphics_items.EntityItem): The parent item.
        """
        super().__init__(entity_item)
        self.entity_item = entity_item
        self._font = QApplication.font()
        self._font.setPointSize(11)
        self.setFont(self._font)
        self.bg = QGraphicsRectItem(self)
        self.bg_color = QGuiApplication.palette().color(QPalette.Normal, QPalette.ToolTipBase)
        self.bg_color.setAlphaF(0.8)
        self.bg.setBrush(QBrush(self.bg_color))
        self.bg.setPen(Qt.NoPen)
        self.bg.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, enabled=False)
        self.setAcceptHoverEvents(False)
        self._cursor = self.textCursor()
        self._text_backup = None

    def setPlainText(self, text):
        """Set texts and resets position.

        Args:
            text (str)
        """
        super().setPlainText(text)
        self.reset_position()

    def reset_position(self):
        """Adapts item geometry so text is always centered."""
        rectf = self.boundingRect()
        x = -rectf.width() / 2
        y = rectf.height() + 4
        self.setPos(x, y)
        self.bg.setRect(self.boundingRect())


class OutlinedTextItem(QGraphicsSimpleTextItem):
    """Outlined text item."""

    def __init__(self, text, parent, font=QFont(), brush=QBrush(Qt.white), outline_pen=QPen(Qt.black, 3, Qt.SolidLine)):
        """Initializes item.

        Args:
            text (str): text to show
            font (QFont, optional): font to display the text
            brush (QBrush, optional)
            outline_pen (QPen, optional)
        """
        super().__init__(text, parent)
        font.setWeight(QFont.Black)
        self.setFont(font)
        self.setBrush(brush)
        self.setPen(outline_pen)
