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
Unit tests for the TreeViewFormUpdateMixin.

:author: M. Marin (KTH)
:date:   6.12.2018
"""

import unittest
from unittest import mock
from PySide2.QtCore import Qt
from spinetoolbox.spine_db_editor.mvcmodels.compound_parameter_models import CompoundParameterModel


class TestSpineDBEditorUpdateMixin:
    def test_update_object_classes_in_object_tree_model(self):
        """Test that object classes are updated in the object tree model.
        """
        self.spine_db_editor.init_models()
        self.put_mock_object_classes_in_db_mngr()
        self.fetch_object_tree_model()
        self.fish_class = self._object_class(1, "octopus", "An octopus.", 1, None)
        self.db_mngr.object_classes_updated.emit({self.mock_db_map: [self.fish_class]})
        root_item = self.spine_db_editor.object_tree_model.root_item
        fish_item = root_item.child(0)
        self.assertEqual(fish_item.item_type, "object_class")
        self.assertEqual(fish_item.display_data, "octopus")

    def test_update_objects_in_object_tree_model(self):
        """Test that objects are updated in the object tree model."""
        self.spine_db_editor.init_models()
        self.put_mock_object_classes_in_db_mngr()
        self.put_mock_objects_in_db_mngr()
        self.fetch_object_tree_model()
        self.nemo_object = self._object(1, self.fish_class["id"], 'dory', 'The one that forgets.')
        self.db_mngr.objects_updated.emit({self.mock_db_map: [self.nemo_object]})
        root_item = self.spine_db_editor.object_tree_model.root_item
        fish_item = root_item.child(0)
        nemo_item = fish_item.child(0)
        self.assertEqual(nemo_item.item_type, "object")
        self.assertEqual(nemo_item.display_data, "dory")

    def test_update_relationship_classes_in_object_tree_model(self):
        """Test that relationship classes are updated in the object tree model."""
        self.spine_db_editor.init_models()
        self.put_mock_object_classes_in_db_mngr()
        self.put_mock_objects_in_db_mngr()
        self.put_mock_relationship_classes_in_db_mngr()
        self.fetch_object_tree_model()
        self.fish_dog_class = self._relationship_class(
            3, "octopus__dog", str(self.fish_class["id"]) + "," + str(self.dog_class["id"]), "octopus,dog"
        )
        self.db_mngr.relationship_classes_updated.emit({self.mock_db_map: [self.fish_dog_class]})
        root_item = self.spine_db_editor.object_tree_model.root_item
        dog_item = root_item.child(0)
        pluto_item = dog_item.child(0)
        pluto_fish_dog_item = pluto_item.child(0)
        self.assertEqual(pluto_fish_dog_item.item_type, "relationship_class")
        self.assertEqual(pluto_fish_dog_item.display_data, "octopus__dog")

    @unittest.skip("TODO")
    def test_update_relationships_in_object_tree_model(self):
        """Test that relationships are updated in the object tree model."""
        self.fail()

    def test_update_object_parameter_definitions_in_model(self):
        """Test that object parameter definitions are updated in the model."""
        model = self.spine_db_editor.object_parameter_definition_model
        model.init_model()
        self.put_mock_object_classes_in_db_mngr()
        self.put_mock_object_parameter_definitions_in_db_mngr()
        self.fetch_object_tree_model()
        self.water_parameter = self._object_parameter_definition(1, self.fish_class["id"], "fish", "fire")
        with mock.patch.object(CompoundParameterModel, "_modify_data_in_filter_menus"):
            self.db_mngr.parameter_definitions_updated.emit({self.mock_db_map: [self.water_parameter]})
        h = model.header.index
        parameters = []
        for row in range(model.rowCount()):
            parameters.append(
                (model.index(row, h("object_class_name")).data(), model.index(row, h("parameter_name")).data())
            )
        self.assertTrue(("fish", "fire") in parameters)

    def test_update_relationship_parameter_definitions_in_model(self):
        """Test that object parameter definitions are updated in the model."""
        model = self.spine_db_editor.relationship_parameter_definition_model
        model.init_model()
        self.put_mock_relationship_classes_in_db_mngr()
        self.put_mock_relationship_parameter_definitions_in_db_mngr()
        self.fetch_object_tree_model()
        self.relative_speed_parameter = self._relationship_parameter_definition(
            3,
            self.fish_dog_class["id"],
            "fish__dog",
            str(self.fish_class["id"]) + "," + str(self.dog_class["id"]),
            "fish,dog",
            "each_others_opinion",
        )
        with mock.patch.object(CompoundParameterModel, "_modify_data_in_filter_menus"):
            self.db_mngr.parameter_definitions_updated.emit({self.mock_db_map: [self.relative_speed_parameter]})
        h = model.header.index
        parameters = []
        for row in range(model.rowCount()):
            parameters.append(
                (model.index(row, h("relationship_class_name")).data(), model.index(row, h("parameter_name")).data())
            )
        self.assertTrue(("fish__dog", "each_others_opinion") in parameters)

    def test_update_object_parameter_values_in_model(self):
        """Test that object parameter values are updated in the model."""
        model = self.spine_db_editor.object_parameter_value_model
        model.init_model()
        self.put_mock_object_classes_in_db_mngr()
        self.put_mock_object_parameter_values_in_db_mngr()
        self.fetch_object_tree_model()
        self.nemo_water = self._object_parameter_value(
            1,
            self.fish_class["id"],
            "fish",
            self.nemo_object["id"],
            "nemo",
            self.water_parameter["id"],
            "water",
            '"pepper"',
        )
        with mock.patch.object(CompoundParameterModel, "_modify_data_in_filter_menus"):
            self.db_mngr.parameter_values_updated.emit({self.mock_db_map: [self.nemo_water]})
        h = model.header.index
        parameters = []
        for row in range(model.rowCount()):
            parameters.append(
                (
                    model.index(row, h("object_name")).data(),
                    model.index(row, h("parameter_name")).data(),
                    model.index(row, h("value")).data(),
                )
            )
        self.assertTrue(("nemo", "water", "pepper") in parameters)

    def test_update_relationship_parameter_values_in_model(self):
        """Test that relationship parameter values are updated in the model."""
        model = self.spine_db_editor.relationship_parameter_value_model
        model.init_model()
        self.put_mock_relationship_classes_in_db_mngr()
        self.put_mock_relationship_parameter_values_in_db_mngr()
        self.fetch_object_tree_model()
        self.nemo_pluto_relative_speed = self._relationship_parameter_value(
            4,
            self.fish_dog_class["id"],
            "fish__dog",
            str(self.fish_class["id"]) + "," + str(self.dog_class["id"]),
            "fish,dog",
            self.nemo_pluto_rel["id"],
            str(self.nemo_object["id"]) + "," + str(self.pluto_object["id"]),
            "nemo,pluto",
            self.relative_speed_parameter["id"],
            "relative_speed",
            "100",
        )
        with mock.patch.object(CompoundParameterModel, "_modify_data_in_filter_menus"):
            self.db_mngr.parameter_values_updated.emit({self.mock_db_map: [self.nemo_pluto_relative_speed]})
        h = model.header.index
        parameters = []
        for row in range(model.rowCount()):
            parameters.append(
                (
                    model.index(row, h("object_name_list")).data(Qt.EditRole),
                    model.index(row, h("parameter_name")).data(),
                    model.index(row, h("value")).data(),
                )
            )
        self.assertTrue(("nemo,pluto", "relative_speed", "100.0") in parameters)
