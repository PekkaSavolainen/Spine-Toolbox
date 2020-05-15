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
Animation class for the Exporter and Importer items.

:authors: M. Marin (KTH)
:date:   12.11.2019
"""

import random
from PySide2.QtGui import QFont, QPainterPath
from PySide2.QtCore import Slot, QTimeLine, QPointF
from PySide2.QtWidgets import QGraphicsOpacityEffect, QGraphicsTextItem


class ImporterExporterAnimation:
    def __init__(self, item, duration=2000, count=5, percentage_size=0.24, x_shift=0):
        """Initializes animation stuff.

        Args:
            item (QGraphicsItem): The item on top of which the animation should play.
        """
        self._item = item
        self._count = count
        self._x_shift = x_shift
        self.cubes = [QGraphicsTextItem("\uf1b2", item) for i in range(count)]
        self.effects = [QGraphicsOpacityEffect() for i in range(count)]
        self.opacity_at_value_path = QPainterPath(QPointF(0.0, 0.0))
        self.opacity_at_value_path.lineTo(QPointF(0.01, 1.0))
        self.opacity_at_value_path.lineTo(QPointF(0.5, 1.0))
        self.opacity_at_value_path.lineTo(QPointF(1.0, 0.0))
        self.time_line = QTimeLine()
        self.time_line.setLoopCount(0)  # loop forever
        self.time_line.setFrameRange(0, 10)
        self.time_line.setDuration(duration)
        self.time_line.setCurveShape(QTimeLine.LinearCurve)
        self.time_line.valueChanged.connect(self._handle_time_line_value_changed)
        font = QFont('Font Awesome 5 Free Solid')
        item_rect = item.rect()
        self.cube_size = percentage_size * 0.875 * item_rect.height()
        font.setPixelSize(self.cube_size)
        rect = item_rect.translated(-0.5 * self.cube_size + x_shift, -self.cube_size)
        end = rect.center()
        ctrl = end - QPointF(0, 0.6 * rect.height())
        lower, upper = 0.2, 0.8
        starts = [lower + i * (upper - lower) / count for i in range(count)]
        starts = [rect.topLeft() + QPointF(start * rect.width(), 0) for start in starts]
        self.paths = [QPainterPath(start) for start in starts]
        for path in self.paths:
            path.quadTo(ctrl, end)
        self.offsets = [i / count for i in range(count)]
        for cube, effect in zip(self.cubes, self.effects):
            cube.setFont(font)
            cube.setDefaultTextColor("#003333")
            cube.setGraphicsEffect(effect)
            effect.setOpacity(0.0)
            cube.setTransformOriginPoint(cube.boundingRect().center())

    @Slot(float)
    def _handle_time_line_value_changed(self, value):
        for cube, effect, offset, path in zip(self.cubes, self.effects, self.offsets, self.paths):
            value = (offset + value) % 1.0
            opacity = self.opacity_at_value_path.pointAtPercent(value).y()
            effect.setOpacity(opacity)
            percent = self.percent(value)
            point = path.pointAtPercent(percent)
            angle = percent * 360.0
            cube.setPos(point)
            cube.setRotation(angle)

    def start(self):
        """Starts the animation."""
        if self.time_line.state() == QTimeLine.Running:
            return
        for cube in self.cubes:
            cube.show()
        random.shuffle(self.offsets)
        self.time_line.start()

    @staticmethod
    def percent(value):
        raise NotImplementedError()

    def stop(self):
        """Stops the animation"""
        self.time_line.stop()
        for cube in self.cubes:
            cube.hide()
        self.time_line.setCurrentTime(999)


class ImporterAnimation(ImporterExporterAnimation):
    @staticmethod
    def percent(value):
        return value


class ExporterAnimation(ImporterExporterAnimation):
    @staticmethod
    def percent(value):
        return 1.0 - value
