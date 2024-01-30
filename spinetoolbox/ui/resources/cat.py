######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Toolbox contributors
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Meow.
"""

import random
from PySide6.QtCore import QLineF, QTimer, QRectF, QPointF
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QGraphicsSvgItem

class Cat(QGraphicsSvgItem):
    _CAT_DOWN_0_BYTES = b'<svg version="1.0" width="95.418" height="137.136" viewBox="0 0 71.563 102.852" xmlns="http://www.w3.org/2000/svg"><path d="M38.763.352c-1.9 1.3-5.6 10.2-6.7 16.5-.3 1.6-1 4.4-1.7 6.4-1.1 3.3-.8 8 .6 12.8.4 1.3-.1 2.9-1.4 4.4-1.2 1.3-2.1 3-2.1 3.7 0 .8-1.5 2.1-3.2 3-1.8.9-3.6 2.2-4 2.8-.4.6-.8.8-.8.3 0-1.1-3.7 2.8-5 5.4-1.1 2-1.3 2.1-2.2.5-1.6-2.9 0-8.5 5.9-20 5.5-10.9 6.3-14.3 4.9-21.4-.7-3.2-6.3-8.2-9.3-8.2-5.3 0-6.8 4.9-3.2 10.7l2.2 3.4-5.7 11.4c-6 12.3-7.4 16.9-7 22.8.5 5 3.6 12 7 15.3 2.8 2.9 4.4 7.1 4.4 11.5 0 1.9 1.1 3.5 3.8 5.5 2 1.5 3.9 3.1 4.2 3.4.3.3 2.1 1.6 4.1 2.8 2.7 1.6 4.3 2 6 1.4 4-1.4 5.3-.8 7.1 3 1.9 4 4.3 5.1 10.7 5.1 3.5 0 6.1-2.2 6.1-5.3 0-1.7-3.4-6.2-4.4-6-2.3.5-2.4-1-.2-3.4l2.4-2.9 1.2 4.4c1.4 5.6 3.1 9.9 3.9 10 3.4.7 8.9.2 9.9-.8 2.2-2.1 2.3-5.8.3-8-1.9-2-2.9-4.4-3.7-9-.3-1.6-.7-3.6-1-4.5-.3-.9.5-5.7 1.7-10.5 2.7-11 3.1-17.6 1.4-22.3-1.2-3.5-1.2-3.8.9-5 3.5-1.8 5.7-6.4 5.7-11.7-.1-11.4-1.1-25.7-1.9-26.5-.4-.4-1.8.1-3 1.2-1.1 1.1-2.4 2-2.7 2-.4 0-1.4.9-2.3 2-1.4 1.6-2.3 1.8-5.2 1.1-1.9-.4-5.1-.6-7-.5-3.2.3-3.8-.1-5.4-3.1-2-3.6-3.6-4.7-5.3-3.7z"/></svg>'
    _CAT_DOWN_1_BYTES = b'<svg version="1.0" width="125.308" height="138.423" viewBox="0 0 93.981 103.817" xmlns="http://www.w3.org/2000/svg"><path d="M10.369 1.613c-2.7 2.5-2.7 5.2 0 8.9l2.2 2.9-2.8 5.8c-1.6 3.2-3.9 7.4-5.1 9.3-4.1 6.4-5.6 14.5-4.1 22 .8 4.1 4.4 9 10.2 13.8 1.7 1.4 2.1 5.2.5 5.2-2 0-.9 5.9 2.5 13.4 2 4.2 4.2 7.7 5 7.7.8.1 2.1.2 2.8.3 3.8.6 6.2-5 4.1-9.9l-1.5-3.6 3.3.4c1.8.2 3.2.6 3.1 1-.1.4.4 2.5 1.2 4.7.8 2.2 1.4 4.4 1.5 4.8 0 .4.9 3.5 2.1 7 2.3 7 3.9 8.3 10.6 8.5 4.7.1 7.3-1.7 7.3-5.3 0-1.9-3.4-6.3-4.2-5.5-.6.6-3.1-2.2-3.5-3.9-.1-.6-1-3.7-1.9-6.8-1.5-5.1-1.5-5.8-.1-7.2 1.7-1.8 4.3-2.1 5.1-.7.4.5 1.5 5.4 2.6 10.8 2 9.8 3.7 15.2 4.9 15.4 3.4.7 8.9.2 9.9-.8 2.2-2.1 2.3-5.8.3-8-1.9-2-2.8-4.2-3.6-8.5-.3-1.3-.7-3.5-1.1-5-.9-4.6.3-6.9 3.4-6.2 6.4 1.3 10.6 1.5 12.6.6 1.1-.5 3.8-1.7 5.9-2.6 7.6-3.4 11.6-10.6 10.1-18.4-.4-2-.8-6.9-.9-10.7-.3-12.8-.3-12.7-2.4-11.5-1.1.5-2.5 1.6-3.3 2.3-3.3 3.2-6.1 4.5-8.2 3.8-1.1-.4-4-.7-6.4-.6-3.8.2-4.4-.1-5.7-2.6-.9-1.6-2.4-3.3-3.5-3.9-1.7-.9-2.3-.6-4 2.2-1.1 1.8-2 3.6-2 3.9 0 1.2-14.6.2-18-1.3-3.9-1.7-13.3-1.7-15.4.1-.7.6-1.5.8-1.8.5-.3-.3-2.9 1.7-5.7 4.5-2.8 2.7-5.1 4.8-5.1 4.7 0-1.6 3.7-9.6 7.4-16.1 3.7-6.5 4.6-8.9 4.6-12.8 0-10.3-7.5-17.6-12.9-12.6z"/></svg>'
    _CAT_DOWN_2_BYTES = b'<svg version="1.0" width="122.457" height="191.239" viewBox="0 0 91.843 143.429" xmlns="http://www.w3.org/2000/svg"><path d="M2.13 1.63c-3.4 3.1-2.7 6.4 1.9 9.3l4 2.5.1 7.3c.1 11.8 1.3 16.1 5.6 19.2 6.6 5 6.7 5 5.1 6.6-2.3 2.2-4 8.4-4 14.1.1 2.7.3 5.3.6 5.6.4.3-.1 1.3-1 2.3-.9 1-1.8 3.1-1.9 4.6-.2 1.5-.6 5.4-1 8.5-.5 4.9-.3 6 1.5 7.8 4.3 4.3 10 .9 10-5.8 0-2.1.3-4.1.6-4.5.3-.3 2.1.3 4 1.4 1.9 1 5.4 2 7.7 2.1l4.3.3-.2 4.6c-.3 6.3 2.5 12.1 7.8 15.9 2.4 1.6 5.3 3.8 6.6 4.7 4.1 3 6.5 9.1 6.9 17.3.2 6.2.6 7.8 2.4 9.2 1.2 1 2.5 1.6 3 1.3.4-.3 1.3.4 1.9 1.5.6 1.1.8 2 .4 2s.1.9 1.1 2 3.1 2 4.6 2c4.5 0 5.6-2.8 5.4-12.8-.4-13.9-.6-24.6-.6-26 .1-.7 1.3-1.8 2.9-2.4 4.7-2.1 9-7.5 9.8-12.4.3-2.4.3-5.2-.1-6.1-.4-1-.9-6.2-1-11.6-.1-5.4-.5-10-.8-10.4-.7-.7-7.7 3.8-7.7 4.9 0 1.6-2.9.7-3.5-1.1-.8-2.7-6.2-8-9.3-9.3-2.4-.9-4.5-1.3-8.9-1.7-.6-.1-1.6-1.6-2.2-3.4-1.6-4.6-6.4-10.1-10.8-12.3-2.6-1.3-6-1.9-10.8-1.9-6.3-.1-7.5-.4-11.8-3.3-2.6-1.8-4.7-4.1-4.8-5-.1-.9-.2-4.9-.3-8.7-.4-9.9-1.2-12.8-4.9-16.3-4.1-3.9-9.7-4.8-12.6-2z"/></svg>'
    _CAT_DOWN_3_BYTES = b'<svg version="1.0" width="121.881" height="185.793" viewBox="0 0 91.411 139.345" xmlns="http://www.w3.org/2000/svg"><path d="M2.1 2.041c-1.2 1.3-2.1 2.9-2.1 3.6 0 2.3 4.7 6.3 7.4 6.3 3.1 0 5.3 3 7.1 10 .7 2.8 1.9 5.8 2.6 6.6 1.5 1.8 6.3 4.4 9.1 4.9 3.1.6 3.1.9-.3 4.4-1.7 1.8-3.7 4.8-4.5 6.7-.8 1.9-1.6 3.4-1.8 3.4-.2 0-1.9-.7-3.9-1.5-3.2-1.3-3.7-1.3-6 .5-2.4 1.9-2.4 2.3-2.2 12.7.1 6 .5 11.6 1 12.6 1.6 3.6 6.7 4.4 10.2 1.5 1.1-.9 1.3-2.4.8-6.6-.8-6.2-.1-6.2 3.9.1 3 4.6 6.9 7.6 12.5 9.2 1.8.5 3.3 1.3 3.3 1.7-.1.4.5 2.2 1.3 4 1.1 2.7 1.1 3.6.1 5-2 2.8-1.1 11.6 2.3 22.7 3.3 10.6 3 10.2 13.9 21.7 2 2.1 6.2 2.8 9.4 1.6 2.5-.9 2.9-.8 4.5 1.8 2 3.5 4.8 4.8 9.3 4.3 3.7-.5 4.6-1.4 5.6-5.1.7-2.4-1.9-6.2-4.1-6.2-1.3 0-3.5-4.2-3.5-6.8 0-1.1 1.9-2.8 4.8-4.4 6.6-3.5 9.2-8.3 8.5-15.7-.2-3.1-.6-8.5-.7-12.1-.5-11.7-.5-12-2.1-12-.8 0-1.5.4-1.5 1 0 .5-.5 1-1 1-.6 0-2.2 1.1-3.6 2.5-4.5 4.5-5.9 3-5.9-6.6 0-6.4-.4-8.1-2.5-11.2-1.3-2-4.1-4.5-6.1-5.6-3.3-1.9-3.7-2.6-4.1-7.1-.9-8.9-8.8-17.9-17.1-19.4-5-.9-6.6-1.7-7.2-3.6-.6-2-5.6-4.7-10.3-5.6-2.5-.5-3.1-1.2-3.7-4.2-1.8-9.8-9.3-17.4-17.6-18.1-2.8-.2-4.2.3-5.8 2zm63.7 119.7c.2.7-.2 1-1.2.6-.9-.3-1.6-1.1-1.6-1.6 0-1.3 2.3-.5 2.8 1z"/></svg>'
    _CAT_DOWN_4_BYTES = b'<svg version="1.0" width="114.595" height="167.513" viewBox="0 0 85.946 125.635" xmlns="http://www.w3.org/2000/svg"><path d="M1.14 1.195c-1.6 1.6-1.5 6.8.2 10.9.8 1.9 4 6.3 7 9.8 3.1 3.6 5.6 7 5.6 7.7 0 .6.7 1.7 1.5 2.4.9.7 1.3 1.5 1.1 1.7-.3.3 0 1 .5 1.7.5.6 2.2 2.9 3.7 5.1l2.8 3.9-2.9 5.3c-1.6 2.9-2.6 5.3-2.2 5.3.3 0-.1 1.3-1 3-1.9 3.6-1.9 6.4-.1 8.2 2.9 2.9 4.7 7.8 4.1 11.1-.5 2.4.2 5 2.9 10.7 1.9 4.1 3.8 9.3 4.2 11.4.4 2.2 1.7 5 3 6.3 1.9 1.9 2.7 2.1 5 1.3 1.5-.6 3.3-1.8 4-2.8 1.2-1.6 1.3-1.6 1.4.3.1 3.1 4.2 11.9 7.2 15.5 4 4.9 13 5.3 13.5.7.2-1.8 1.1-1.7 1.7.1.8 2.5 4.7 5.2 7 4.8 2.4-.3 5.6-3.3 5.6-5.1 0-.9-.7-2.6-1.5-3.8-.8-1.3-1.7-4.2-1.9-6.6-.3-3.3 0-4.6 1.7-6.2 1.1-1 2.4-1.9 2.9-1.9 3 0 7.7-7.1 7.8-11.7.1-7-1.1-24.9-1.9-28.1-.1-.5-6.5 4.1-7.3 5.3-.7.8-.9-.1-.8-3 0-.3-.7-2-1.6-3.8-2.3-4.6-6.4-8.6-10.3-10.3-1.8-.8-5.3-3.4-7.6-5.9-5.3-5.5-8.2-6.8-16.2-6.9-7.4-.2-8.8-1.3-13.9-10.3-1.9-3.4-5.9-9.1-8.8-12.6-2.9-3.4-5.8-7.8-6.5-9.9-.7-2-1.9-3.9-2.7-4.2-2.5-1-5.9-.7-7.2.6zm37.7 88c0 2.7-.2 2.9-.8 1.3-.5-1.1-.6-2.6-.4-3.3.8-2.1 1.3-1.3 1.2 2zm19.6 16.8c2.9.7 3.5 1.5 3.5 5.1 0 3.7-.1 3.8-2.1 2.7-1.8-1.1-5.9-7.6-5.9-9.3 0-.3.8-.1 1.8.4.9.5 2.2 1 2.7 1.1z"/></svg>'
    _CAT_UP_0_BYTES = b'<svg version="1.0" width="90.925" height="140.717" viewBox="0 0 68.194 105.538" xmlns="http://www.w3.org/2000/svg"><path d="M35.579.638c-1.7 1.3-5.3 10.2-6.2 15.6-.3 1.8-1.2 4.8-1.9 6.5-1.4 3.3-1.1 10.5.5 12.1 1.4 1.4 1.1 2.9-.9 5.1-1.1 1.1-2.2 2.6-2.5 3.4-.3 1-.6.6-.7-1-.5-6-1.8-9-4.9-11.7-3.9-3.4-7.7-3-9.8 1.2-1.1 2.1-.2 5.8 1.6 7 2.2 1.3 1 5.6-4.6 17-6.9 14.1-7.8 20.7-3.8 28.8 2.3 4.8 7.4 11.1 8.3 10.2.3-.2 2.9 1.7 5.8 4.4 3.4 3.1 6.7 5.1 9.1 5.7 4 .8 10.5.8 13.8 0 1.1-.2 2.8-.5 3.7-.5.9-.1 2.9-1.2 4.5-2.5s3.7-2.6 4.8-2.8c1.1-.1 3.9-2.2 6.2-4.6 4.9-4.9 5.5-8.4 2.3-12.5-2.8-3.6-2.8-14.2.1-19.8 2.5-5 3.1-12.1 1.4-16.9-1.4-4-1-6 1.1-6 .8 0 1.4-.4 1.4-.9s.8-1.7 1.7-2.7c1.3-1.2 1.7-3.3 1.6-7.8-.2-17.7-.5-24-1.2-25.8-.7-1.8-.8-1.8-2.8-.1-6 5.2-7.6 6.1-9.7 5.6-1.1-.3-4.2-.5-6.9-.5-4.2.1-4.9-.2-6.1-2.7-2.2-4.2-3.9-5.3-5.9-3.8z"/></svg>'
    _CAT_UP_1_BYTES = b'<svg version="1.0" width="106.494" height="140.137" viewBox="0 0 79.871 105.102" xmlns="http://www.w3.org/2000/svg"><path d="M9.938 1.553c-2.1 2.1-2 5.6.3 8.5 2.4 3.2 1.8 6.3-2.7 14.5-8.1 14.9-9.4 22.9-5.2 32.4 1.9 4.2 2.4 6.9 2.3 11.5-.6 14.2-.7 14 2.3 18.6 6.9 10.6 11.4 14.7 15.5 14.4 1.7-.2 3.5-.9 4-1.6 1.5-2.4 1-6.5-1.1-8.4-2.5-2.2-2.6-3.4-.2-3 .9.2 2.7.4 3.8.4 1.7.1 2.2.9 2.7 4.1.6 5 2.9 8.5 6.8 10.9 6.7 4.1 12.5-2.7 7.4-8.7-1.3-1.5-2.6-4.4-3-6.5-.6-3.1-.3-4.2 1.9-6.7l2.5-3.1 1.2 4.4c1.1 4.7 3.8 7 7.4 6.3 1.1-.3 2.3-.5 2.6-.5 2.2-.3 3.9-10.4 1.8-11.6-1.2-.8-.7-4 2.8-15.5 4.6-15.6 6.5-19.6 10.3-21.8 5.1-2.9 6.8-6.6 6.5-13.7-.2-3.3-.4-10.2-.6-15.4-.3-6-.8-9.6-1.6-9.8-.6-.2-2.9 1.3-5.1 3.4-3.7 3.5-4.4 3.8-7.3 3-1.8-.5-5-.7-7-.5-3.3.3-3.8 0-5.8-3.4-3.3-5.7-6.7-4.6-8.7 2.7-.1.5-.9 3-1.8 5.4-.9 2.4-1.6 5.4-1.6 6.7 0 2.6-4.7 6.4-7.8 6.4-2.5 0-7.1 5.5-10.9 12.6-1.5 2.9-3.1 5.1-3.4 4.8-.4-.2-1.3.1-2.1.8-.7.7-2.1 1.9-3.1 2.7-1.5 1.2-1.7 1.1-1.4-.5 1-5 2.4-8.3 6.6-15.8 3.9-7 4.5-9 4.7-14.5.3-6.9-.5-9.3-4.3-12.9-2.8-2.6-6.5-2.9-8.7-.6z"/></svg>'
    _CAT_UP_2_BYTES = b'<svg version="1.0" width="128.334" height="189.753" viewBox="0 0 96.25 142.315" xmlns="http://www.w3.org/2000/svg"><path d="M61.074 4.7c-1.4 2.7-3 7.2-3.7 10.1-2.5 10.6-4.3 14.4-8 16.5-1.9 1-4.5 3.1-5.7 4.5-2.3 2.7-5.3 10.2-5.3 13.1 0 .9-1.4 2.3-3.2 3-4.4 2-9.9 7.8-12.2 12.8-1.6 3.6-2.1 4-4 3.3-2.2-.8-3.1-1-4.5-1-.5 0-1.4-1.4-2.1-3-1.2-2.9-1.1-4.4.5-17 1.1-8.2-4.6-13.6-10-9.6-1.5 1.1-2 2.8-2.2 7.7-.1 3.5-.4 9.1-.6 12.4-.9 14 6.4 21.8 20.6 22.4 1 .1 1.6.5 1.2 1-.3.5-.1 1.2.5 1.6.5.3 1 4.2 1 8.6 0 6.5-.3 8.2-2 9.9-3.3 3.3-3.5 6.6-.6 13.3 2.9 7 3.4 8.9 3.7 15.4.3 5.1 2.5 7.3 7.5 7.3 4.7 0 7.3-4.2 5.2-8.3-1-1.9-1.3-3-2.2-9.1-.3-2.1-1.3-5-2.1-6.6-.8-1.6-1.5-3.4-1.5-4.1 0-1.5 9.2-10.9 10.2-10.3 1 .7-.3 7.5-2 10.6-1.4 2.4-1.4 3 .1 6.5.9 2.1 1.8 7.4 2.1 11.8.5 9.1 1.6 12.9 4.3 14 3 1.3 4.7 1.1 6.6-1 1.5-1.6 1.8-2.9 1.2-7-1.8-13.3-1.6-17.2 1.4-22.8 3.2-6 6.1-14.2 6.1-16.9 0-1.1 1-3.4 2.3-5.1 3.6-4.9 4.4-7.7 4.5-14.5 0-3.5.3-6.6.6-7 .4-.3 1.7.5 2.9 1.9 2.3 2.6 6.7 3.5 11.7 2.4 2.6-.6 4.1-2.4 3.9-4.8 0-.5.8-1.6 1.9-2.5 4.4-3.9 6-12.6 2.9-16-1.9-2.1-5.7-2.3-8-.4-1.2 1-1.6.9-2.1-.4-.8-2.2-.1-3.1 4.2-5.1 7.8-3.6 11.1-9.7 9.8-18-.3-2.1-.7-7.9-.8-13-.3-8.3-1.4-12.7-2.5-9.6-.3.7-.9 1.3-1.5 1.3-.5 0-2.2 1.3-3.6 2.8-2.7 2.8-3.9 3.2-5.7 2-.5-.3-3.3-.5-6-.4-4.9.2-5.2.1-7.5-3.6-1.3-2.1-3-3.8-3.7-3.8-.7 0-2.3 2.1-3.6 4.7z"/></svg>'
    _CAT_UP_3_BYTES = b'<svg version="1.0" width="143.268" height="150.001" viewBox="0 0 107.451 112.501" xmlns="http://www.w3.org/2000/svg"><path d="M73.03 2.088c-.9 1.3-2.5 5.2-3.6 8.8-1.9 6.4-2.1 6.6-6.5 7.9-4.2 1.3-12.9 8.5-12 10 .5.8-2.3 4.7-3 4.2-.9-.7-7.4 1-7.4 1.9 0 .6-.7 1-1.5 1s-1.5.4-1.5 1c0 .5-.5 1-1.1 1-.7 0-1.7.7-2.3 1.6-.8 1.1-3.1 1.6-7.4 1.8-4.8.2-6.5.7-7.7 2.2-.8 1-1.5 2.3-1.5 2.7 0 1.4-2.8 3.7-4.3 3.7-.8 0-2.2-.9-3.2-2-3.2-3.5-9.2-1.9-10 2.8-.3 2.2 1.7 6.2 4.4 8.6 1.6 1.5 3.8 2 9.5 2.1 7.6.1 9.4-.5 11.4-4 1.2-2.2 1.1-2.3 3.1 5.8 1.4 5.9 1.4 8.7 0 8.7-.6 0-1.8.7-2.6 1.6-1.3 1.3-1.7 3.9-1.8 12.3-.2 16 2.2 22.6 7.6 21.6 4.6-.9 5-2.1 4.3-12.7l-.7-9.9 3.4-2.9c1.9-1.5 3.9-2.5 4.4-2.2.6.4 1.5.7 2 .7 1.1 0 1.2 6 .1 11.5-.4 1.9-.9 6.7-1.3 10.6-.5 6.9-.4 7.3 2 8.8 1.6 1.1 3.4 1.5 5.1 1 2.6-.6 3.2-1.6 4-6.9 1.7-11.5 1.6-11.1 4.4-11.3 4.6-.3 7.5-5.6 9.5-17.7.3-1.7 1.1-4.2 1.8-5.8 1.1-2.5 1.3-2.6 3-1.1 1.1 1 2.8 1.5 4.4 1.2 1.6-.3 3.2.1 4.1.9 2 2.1 7.5 2.4 9.9.7 1.5-1.1 1.9-2.4 1.7-5.7-.8-11.4-.6-23.2.3-23.2 2-.1 8.1-3.9 10.2-6.4 2.8-3.1 3.8-7.8 2.9-13.4-.3-2.3-.7-7.8-.7-12.1-.1-8-.5-10.6-1.8-10.6-.3 0-2.6 1.8-5.1 3.9-3.1 2.8-4.9 3.7-6 3.1-.8-.4-3.8-.7-6.7-.6-4.8.1-5.3-.1-6.9-2.9-2.9-5.1-4.5-5.6-6.9-2.3z"/></svg>'
    _CAT_UP_4_BYTES = b'<svg version="1.0" width="141.475" height="115.705" viewBox="0 0 106.106 86.779" xmlns="http://www.w3.org/2000/svg"><path d="M71.8 2.083c-.8 1.3-2.1 4-2.9 6-.7 2.1-2.2 4.1-3.3 4.4-1.1.4-3.7 2.4-5.8 4.6-2.1 2.2-5 4.1-6.5 4.4-5.8 1.1-14.5 8.1-16.5 13.4-.5 1.3-2.4 1.5-10.4 1.4-13-.1-12.7-.1-15.1-2.4-3.4-3.1-6.8-3.5-9.2-1.1-1.2 1.2-2.1 3-2.1 4.1 0 2.1 7 9.6 9.2 9.8.7 0 2.7.4 4.3.8 1.7.4 7.1.6 12 .6l9-.1 1.7 5.1c1.2 3.5 1.4 5.7.7 7.4-1 2.9.6 7.5 4.1 11.4 1.2 1.4 3.6 4.4 5.3 6.7 1.7 2.4 3.4 4.4 3.9 4.4 3.4.5 7.6.4 9-.3 1.2-.6 2.4-.1 4.2 1.7 3 3 6.3 3.2 8.6.5 2.2-2.5 1.7-7-1.1-11.9-1.1-1.8-1.8-3.5-1.6-3.8.3-.2 1.4 1.2 2.5 3.1 2.2 3.7 6.8 5.5 9.9 3.7 1.3-.7 2.2-.6 3.3.3 2 1.7 7.1 3.3 9.2 2.9.9-.2 2.1-1.7 2.8-3.3 1.3-3.2.3-6.2-2.8-7.9-1.4-.8-1.7-2.2-1.4-8.3.6-16.4.7-16.8 6.2-19.6 3.2-1.6 7-7.1 7.1-10.3.1-3.5-1.1-24.1-1.6-26.4-.2-1.1-.4-2.5-.5-3 0-.6-.7-.1-1.5.9-.8 1.1-1.5 1.6-1.5 1.2 0-.5-1.4.6-3.2 2.3-2.3 2.3-3.9 3-5.7 2.7-1.5-.2-4.6-.5-7.1-.5-4-.1-4.8-.5-6.8-3.6-2.6-4.1-4.4-4.4-6.4-1.3z"/></svg>'
    _CAT_SIDE_0_BYTES = b'<svg version="1.0" width="118.805" height="122.836" viewBox="0 0 89.104 92.127" xmlns="http://www.w3.org/2000/svg"><path d="M71.904 2.008c-1.4 1.2-4 3.3-5.8 4.7-6.3 4.7-12.1 10.4-13.5 12.9-1.7 3.1-11.8 14.1-13 14.1-.4 0-2.3 1.1-4.1 2.5-1.9 1.4-3.7 2.6-4.1 2.6-.5.1-1.7.6-2.8 1.2-1.1.6-2.4 1-2.8.9-.4-.1-1 .5-1.3 1.3-.4.8-1 1.5-1.6 1.5-.5 0-1.6.6-2.4 1.4-2 2.1-6.4 11-6.4 13.2-.1 1.8-.1 1.8-1.4.1-2.4-3.1-.8-12.4 3.2-19 6.4-10.4 8.4-17.6 6.8-24-1-4.3-5.4-8.7-8.6-8.7-5.5 0-7.9 5.6-4.1 9.9 2.7 3 2 6.8-2.7 14.7-5.2 8.8-7.3 14.9-7.3 21.9-.2 10.2 7.4 21 13.7 19.9 1.5-.3 2.4.2 2.8 1.3.3 1 1.8 3.1 3.2 4.6 2.4 2.6 3.1 4.2 3.3 7.4.2 2.2 4 3.4 11.7 3.8 4.2.3 9 .8 10.7 1.3 1.8.4 3.8.7 4.5.6.6-.1 1.8-.2 2.6-.3 1.3-.1 2.8-2.7 3.1-5.6.1-.6-.5-2.1-1.2-3.3-.8-1.3-1.3-2.6-1-2.8.3-.3 1.4 1 2.6 2.9 2.3 3.8 5.5 5.8 9.9 6.2 3.6.3 7.2-2.5 7.2-5.5 0-2.3-3.4-6-5.5-6-2.8 0-3.1-12.1-.6-27.1.8-5.2 6.4-12.9 9.2-12.9 2.1 0 6.9-2 8.5-3.5 1.4-1.3 4.4-7.1 4.4-8.4 0-.5-.7-1.7-1.6-2.5-.8-.9-1.7-2.6-1.9-3.8-.8-4-3.6-8.3-6.9-10.5-2.4-1.5-3.2-2.9-3.4-5.4-.1-1.8-.4-3.4-.5-3.6-.2-.1-1.4.8-2.9 2z"/></svg>'
    _CAT_SIDE_1_BYTES = b'<svg version="1.0" width="134.771" height="120.009" viewBox="0 0 101.079 90.007" xmlns="http://www.w3.org/2000/svg"><path d="M1.386 2.007c-2.2 3-2 3.8 2.2 11.7l3.9 7.2-2.5 5c-1.9 3.6-2.6 6.6-2.6 10.6 0 6.4 1.1 9 5.1 12.4 1.6 1.3 2.9 3.1 2.9 4 0 .9 1.2 3.6 2.6 6.1 2.1 3.7 2.3 4.8 1.3 6.6-1.9 3.7-.3 6.6 5.3 9.9 3.8 2.2 5.8 4.2 7.4 7.4 3.1 6.2 4.7 7.1 12.3 7.1 7-.1 9.4-1.2 10.3-4.8 1-3.5-2.1-6.5-7-6.7-2.3-.1-4.4-.4-4.5-.6-1.3-1.7-4.7-6.8-4.7-7.1 0-.1 1.7-.4 3.8-.6 4.9-.3 6.5-.6 7.9-1.5 1.1-.7 4.3 1.7 4.3 3.2 0 1.5 12.6 13.8 15.5 15.3 2.7 1.3 4 1.5 8.6 1 2.2-.3 3.8-4.2 2.8-7-.5-1.3-2.4-2.9-4.2-3.7-1.8-.7-5.4-3.7-8.1-6.5-4.2-4.5-4.6-5.3-3.4-6.8 2.4-3.1 3.6-4.2 4.7-4.2.6 0 1.1-.5 1.1-1 0-.6.5-1 1.1-1 .6 0 1.7-.7 2.6-1.6.9-.9 2.2-1.2 3.2-.8 2.7 1.2 19.1 1.5 19.1.3 0-.6.4-.8.8-.5 1.4.9 6-4.1 7.2-7.9 1.1-3.3 1-3.8-1.1-5.6-1.2-1-1.9-1.9-1.5-1.9 1.6 0-2.8-7.8-6.1-10.8-2.4-2.1-3.8-4.5-4.2-6.8l-.6-3.4-2.7 2.5c-1.5 1.4-3.1 2.5-3.5 2.5-.5 0-1.5.9-2.3 2-.8 1.1-2 2-2.7 2-.7 0-1.3.4-1.3.9 0 .6-1.2.6-3.2 0-4.2-1.2-9.5-1.2-10.2 0-.4.5-1.8.7-3.4.5-6.1-1-7.8-1.1-9.3-.3-.9.5-3.2.4-5-.2-4.2-1.2-16.4-1.2-16.4.1 0 .1-.8.3-1.8.5s-2.7 1.1-3.8 2.1c-1 .9-1.9 1.4-1.9 1 0-.4-1.1.5-2.5 1.9s-2.8 2.5-3 2.5c-.6 0 1.1-5.4 2.9-8.8 2.8-5.3 2-10.8-2.5-19.2-2.3-4.1-4.6-7.8-5.3-8.2-2.2-1.5-6.2-.8-7.6 1.2z"/></svg>'
    _CAT_SIDE_2_BYTES = b'<svg version="1.0" width="173.632" height="122.687" viewBox="0 0 130.224 92.015" xmlns="http://www.w3.org/2000/svg"><path d="M9.448.064c-.3.3-4.1 1.1-7 1.4-.6.1-1.9 3.2-2.4 5.8-.5 2.7 3 5 7.4 4.9 5.2-.2 9.6 1.7 10.9 4.7.5 1.2 1 4.4 1.2 7.2.1 2.7.7 6.7 1.2 8.7.9 3.6 4.9 7.8 7.3 7.8.7 0 1.9 2.8 2.8 6.2.9 3.5 1.9 7.2 2.3 8.3.6 1.9.2 2-4 1.7-3.1-.3-5.4.1-7.2 1.3l-2.6 1.7.6 10.7c.6 10 1.1 14.3 2.3 18.3.5 1.6 4.8 3.6 7.2 3.2.6-.1 2.3-.2 3.6-.3 2.3-.1 3.5-1.8 4.2-6 .1-.7-.8-2.4-2.1-3.7-2-2-3.5-6-4-10.9-.3-2.2.7-2.3 6.3-.7 3.1 1 6.4 1.7 7.2 1.6 4.4-.3 9.8-4.2 13-9.3 1.1-1.8 2.6-2.5 5.4-2.8 2.1-.1 4.5-.8 5.2-1.4.8-.6 1.4-.8 1.4-.4 0 .9 7.2-4.5 8.3-6.2.6-1 1.4-1 4 .4 2.1 1.1 5.9 1.7 11 1.8 4.3.1 8.2.6 8.7 1.1.5.5 1 2.4 1.2 4.1.3 4.3 6 7.3 8.7 4.6 1.1-1.2 1.6-1 3.2 1.6 2 3.3 2 3.3 6.1 3.6 2.1.2 3-.5 4.1-2.8 1.3-2.6 1.3-3.5.1-7.1-1.9-5.3-5.5-10.4-10.7-15.3l-4.2-3.8 6.1-.6c6.9-.6 10.7-2.9 12.6-7.4 1.8-4.2 1.8-5.3.2-6.6-.8-.6-1.8-2.8-2.4-4.9-1-3.8-5.9-10-7.9-10-.5 0-1.3-1.7-1.6-3.8-.4-2-.7-4-.8-4.4-.1-.5-1.4.2-2.8 1.5-1.5 1.2-4.1 3.3-5.9 4.7-1.8 1.4-5.4 4.4-7.9 6.7-3.7 3.4-5.1 4.1-7.1 3.6-4.5-1-17.1-.3-21.2 1.2-.9.4-2.7.1-4-.6-3.1-1.7-14.6-1.9-18.4-.3-1.7.7-3.4 1-3.8.7-.3-.4-.6-.1-.6.5 0 .7-.7 1.2-1.5 1.2s-1.5.5-1.5 1.2c0 .6-.3.8-.6.5-.4-.4-2.1.9-3.9 2.8-3.2 3.6-5.4 4.5-5.6 2.2-1-15.2-1.5-16.7-7.3-22.1-3-2.7-8.6-6.1-8.6-5.2 0 .3-1.3.1-2.9-.4-1.6-.4-3.1-.7-3.3-.5z"/></svg>'
    _CAT_SIDE_3_BYTES = b'<svg version="1.0" width="162.029" height="116.611" viewBox="0 0 121.522 87.458" xmlns="http://www.w3.org/2000/svg"><path d="M1.685 1.226c-.6.7-1.3 2.4-1.6 3.9-.6 3.5 2 5.7 7.4 6.3 5.3.6 6.1 1.2 12.3 10.5 2.7 4.1 5.8 8.4 6.7 9.5 1 1.1 2.1 4.2 2.6 7 1.1 7 1.1 7-1.1 7-4 .1-6.4 1.6-6.9 4.3-.9 4.9-.3 6.3 3.8 9.1 4.1 2.9 8.9 7.3 15.8 14.8 5.1 5.5 9.8 5.2 11.3-.8.4-1.7-.2-3.5-2-5.9l-2.6-3.5 6.6-.5c5.1-.4 7-1 8.1-2.4.8-1.1 1.4-2.3 1.4-2.8 0-.4.8-.8 1.8-.8s2.2-.4 2.8-.9c.5-.5 2.4-.7 4.2-.4 2.6.4 4 1.6 6.9 6.2 2.1 3.1 4.1 5.8 4.5 6.2.4.3 2.2 3.4 3.9 6.9 1.7 3.5 4.1 7.3 5.2 8.3 5.7 5 13.9 5.7 15.3 1.4 1.4-4.1 1.2-4.9-1.8-8-6.4-6.6-9.5-11.4-10.4-15.7l-1-4.5 8.9.2c9.1.2 11.6-.5 14.9-4.2 3.1-3.5 3.7-7.6 1.6-10.6-1.7-2.2-2.4-4.1-2.7-7-.2-1.3-5.9-6.9-7-6.9-1.1 0-2.8-5.5-2.3-7.3.4-1.4-2.9-.7-3.4.8-.4.8-1 1.5-1.5 1.5s-2.3 1.3-4.1 3c-3.6 3.5-3.9 3.5-7.8 1.5-1.7-.9-3-1.2-3-.8 0 .4-.5.2-1-.3-.6-.6-3.9-.9-7.6-.7-5.5.4-7 .1-8.8-1.5-5.1-4.7-10.5-6.4-19.5-6.3-9.3.2-13.1.8-13.1 2.3 0 .5-.4.7-.9.3-.6-.3-1.6.1-2.3.8-1 1.1-2 .2-5.7-5.7-5.3-8.3-9.1-12.1-13.9-14.2-4.3-1.7-12.6-1.8-14-.1z"/></svg>'
    _CAT_SIDE_4_BYTES = b'<svg version="1.0" width="169.273" height="103.749" viewBox="0 0 126.955 77.812" xmlns="http://www.w3.org/2000/svg"><path d="M104.526 6.11c-6.3 5.1-8.5 6.2-10.5 5.8-1.4-.3-5.6-.5-9.4-.4-3.8 0-7.5-.5-8.2-1.1-.8-.6-1.4-.9-1.4-.5s-1.2 0-2.7-.7c-1.6-.8-4.1-1.3-5.8-1.1-1.6.1-5.7.3-9 .5-6 .2-9.9 2-13.6 6.1-1.4 1.5-1.8 1.6-4.3.2-1.6-.7-3.5-1.4-4.2-1.4-.8 0-1.4-.3-1.4-.8 0-.4-2.5-1.8-5.5-3.2-3-1.4-5.5-2.8-5.5-3.1 0-.6-1.7-1.3-4-1.7-.3 0-1.8-.6-3.5-1.2-5-2-11.2-2-13.5 0-4.2 3.6-1.5 9.4 4.7 9.8 3.4.3 20 7.4 21.3 9.2.4.6 3.7 2.2 5 2.4 2.1.4 7 3 7 3.7v1.4c-.1 1.3 3.3 6.8 6.2 10 2.9 3.4 3.1 4.1 2.9 10.5-.2 6.4.1 7.3 3.9 14.2 5 8.9 6.6 10.5 11.5 12.3 3.3 1.1 4.2 1.1 6.1-.2 4.4-2.8 3.5-8.1-1.8-10.7-1.2-.6-3.2-2.9-4.5-5.1-1.2-2.2-2.5-4.5-3-5-1.1-1.5-1.4-3.5-.6-3.6.5-.1 2.1-.2 3.7-.4 1.6-.1 3.8-1.2 4.7-2.4 1.4-1.7 2.7-2.1 5.1-1.9 3 .3 3.3.6 4 4.7.4 2.5 1.1 4.7 1.6 5 1.4 1 7.2 10.4 7.2 11.6 0 2.1 4.9 6.2 8.3 7 4.4 1 5.9.7 7.9-1.6 2.5-2.9.7-8.9-2.8-8.9-.7 0-2.1-1.2-3-2.8-1-1.5-2.8-4.4-4.1-6.4-1.8-2.7-2.3-4.3-1.7-6 .4-1.3.9-2.5.9-2.8 1.5-6.3 2.8-8.9 4.8-9.5 1.2-.4 6.5-.8 11.7-.9 10.4-.1 12.3-.9 15.8-6 2.6-3.8 2.8-6.3.7-8.6-.9-1-1.7-2.7-2-3.8-.8-4.3-4.2-8.8-8.3-11.1-.7-.4-1.5-2.2-1.7-4.1-.3-1.8-.6-3.4-.7-3.5-.2-.2-3.9 2.6-8.3 6.1z"/></svg>'
    _STEP_SIZE = 15
    _STEP_COUNT = 4
    _TIME_TO_TEASE = 100
    _TIME_TO_STOP_TEASING = 5
    _TIME_TO_HIDE = 30
    _MIN_PLACES_TO_HIDE = 6

    class _State:
        HIDING = "HIDING"
        TEASING = "TEASING"
        SHOWING = "SHOWING"

    def __init__(self, scene):
        super().__init__(None)
        self.setParent(scene)
        self.setScale(0.4)
        self.setZValue(-1e6)
        self._scene = scene
        self._scene.addItem(self)
        self._down_renderers = [
            QSvgRenderer(self._CAT_DOWN_0_BYTES),
            QSvgRenderer(self._CAT_DOWN_1_BYTES),
            QSvgRenderer(self._CAT_DOWN_2_BYTES),
            QSvgRenderer(self._CAT_DOWN_3_BYTES),
            QSvgRenderer(self._CAT_DOWN_4_BYTES),
        ]
        self._up_renderers = [
            QSvgRenderer(self._CAT_UP_0_BYTES),
            QSvgRenderer(self._CAT_UP_1_BYTES),
            QSvgRenderer(self._CAT_UP_2_BYTES),
            QSvgRenderer(self._CAT_UP_3_BYTES),
            QSvgRenderer(self._CAT_UP_4_BYTES),
        ]
        self._side_renderers = [
            QSvgRenderer(self._CAT_SIDE_0_BYTES),
            QSvgRenderer(self._CAT_SIDE_1_BYTES),
            QSvgRenderer(self._CAT_SIDE_2_BYTES),
            QSvgRenderer(self._CAT_SIDE_3_BYTES),
            QSvgRenderer(self._CAT_SIDE_4_BYTES),
        ]
        self._current_renderers = self._down_renderers
        self._default_rect = QRectF(QPointF(0, 0), self.scale() * self._down_renderers[0].defaultSize())
        self._step = 0
        self._target = None
        self._line = QLineF()
        self._state = self._State.HIDING
        self._time = 0
        self._hiding_place = None
        self._reset_target_timer = QTimer(self)
        self._reset_target_timer.setInterval(5000)
        self._reset_target_timer.timeout.connect(self._reset_target)
        self._move_timer = QTimer(self)
        self._move_timer.setInterval(100)
        self._move_timer.timeout.connect(self._move)
        self._move_timer.start()
        self.setSharedRenderer(self._current_renderers[self._step])
        self.hide()
        self._scene.changed.connect(self._update_target)

    def _update_target(self, region):
        rects = [rect for rect in region if not rect.intersects(self.sceneBoundingRect())]
        if not rects:
            return
        rect = random.choice(rects)
        self._target = rect.center()
        self._reset_target_timer.start()

    def _reset_target(self):
        self._reset_target_timer.stop()
        rect = self._scene.sceneRect()
        self._target = 2 * min(
            (rect.topLeft(), rect.topRight(), rect.bottomRight(), rect.bottomLeft()),
            key=lambda p: (p - self.sceneBoundingRect().center()).manhattanLength(),
        )

    def _places_to_hide(self):
        for item in self._scene.items():
            if item is self or item.parentItem() is not None:
                continue
            self._default_rect.moveCenter(item.boundingRect().center())
            if item.shape().contains(self._default_rect):
                yield item

    def _update_state(self):
        self._time += 1
        if self._state == self._State.HIDING:
            if (
                self._time < self._TIME_TO_HIDE
                and self._hiding_place is not None
                and not self.collidesWithItem(self._hiding_place)
            ):
                self._go_to_showing()
            elif self._time == self._TIME_TO_TEASE:
                places = list(self._places_to_hide())
                if len(places) >= self._MIN_PLACES_TO_HIDE:
                    self._hiding_place = random.choice(places)
                    self._go_to_teasing()
                else:
                    self._hiding_place = None
                    self._go_to_hiding()
        elif self._state == self._State.TEASING:
            if self._time == self._TIME_TO_STOP_TEASING:
                self._go_to_hiding()
        elif self._state == self._State.SHOWING:
            if not self._scene.sceneRect().intersects(self.sceneBoundingRect()):
                self._go_to_hiding()

    def _go_to_hiding(self):
        self._time = 0
        self._state = self._State.HIDING
        self._current_renderers = self._down_renderers
        self._chill()
        self.resetTransform()
        self.setZValue(-1e6)
        self.hide()

    def _go_to_teasing(self):
        self._time = 0
        self._state = self._State.TEASING
        self.setPos(self._hiding_place.scenePos() - 0.52 * self.boundingRect().center())
        self.show()

    def _go_to_showing(self):
        self._time = 0
        self._state = self._State.SHOWING
        self._hiding_place = None
        self.setZValue(1e6)
        self.show()

    def _move(self):
        self._update_state()
        if self._state != self._State.SHOWING:
            return
        if self._target is None:
            self._chill()
            return
        self._time = 0
        distance = (self.scenePos() - self._target).manhattanLength()
        if distance < self._STEP_SIZE:
            self._chill()
            return
        if self._step == 0:
            self._update_line()
        self.setSharedRenderer(self._current_renderers[self._step])
        step_size = min(self._STEP_SIZE, distance)
        unit_line = self._line.unitVector()
        delta = step_size * (unit_line.p2() - unit_line.p1())
        self._step = (self._step + 1) % self._STEP_COUNT
        self.moveBy(delta.x(), delta.y())

    def _chill(self):
        self._step = 0
        self.setSharedRenderer(self._current_renderers[self._step])

    def _update_line(self):
        self._line.setP1(self.scenePos())
        self._line.setP2(self._target)
        angle = self._line.angle()
        facing_left = 90 < angle < 270
        facing_up = 30 < angle < 150
        facing_down = 210 < angle < 330
        if facing_up:
            # new_angle = 60
            self._current_renderers = self._up_renderers
        elif facing_down:
            # new_angle = -60
            self._current_renderers = self._down_renderers
        else:
            # new_angle = 0
            self._current_renderers = self._side_renderers
        self.resetTransform()
        if facing_left:
            # new_angle = 180 - new_angle
            self._flip_horizontal()
        # self._line.setAngle(new_angle)

    def _flip_horizontal(self):
        transform = self.transform()
        m11 = transform.m11()
        m12 = transform.m12()
        m13 = transform.m13()
        m21 = transform.m21()
        m22 = transform.m22()
        m23 = transform.m23()
        m31 = transform.m31()
        m32 = transform.m32()
        m33 = transform.m33()
        scale = m11 * self.scale()
        m11 = -m11
        if m31 > 0:
            m31 = 0
        else:
            m31 = self.boundingRect().width() * scale
        transform.setMatrix(m11, m12, m13, m21, m22, m23, m31, m32, m33)
        self.setTransform(transform)
