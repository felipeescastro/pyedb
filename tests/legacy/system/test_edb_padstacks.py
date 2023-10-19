"""Tests related to Edb padstacks
"""

import pytest

pytestmark = pytest.mark.system

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = edbapp
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_get_pad_parameters(self):
        """Access to pad parameters."""
        pin = self.edbapp.components.get_pin_from_component("J1", pinName="1")
        parameters = self.edbapp.padstacks.get_pad_parameters(
            pin[0], "1_Top", self.edbapp.padstacks.pad_type.RegularPad
        )
        assert isinstance(parameters[1], list)
        assert isinstance(parameters[0], int)

    def test_get_vias_from_nets(self):
        """Use padstacks' get_via_instance_from_net method."""
        assert self.edbapp.padstacks.get_via_instance_from_net("GND")
        assert not self.edbapp.padstacks.get_via_instance_from_net(["GND2"])

    def test_create_with_packstack_name(self):
        """Create a padstack"""
        # Create myVia
        self.edbapp.padstacks.create(padstackname="myVia")
        assert "myVia" in list(self.edbapp.padstacks.definitions.keys())
        self.edbapp.padstacks.definitions["myVia"].hole_range = "begin_on_upper_pad"
        assert self.edbapp.padstacks.definitions["myVia"].hole_range == "begin_on_upper_pad"
        self.edbapp.padstacks.definitions["myVia"].hole_range = "through"
        assert self.edbapp.padstacks.definitions["myVia"].hole_range == "through"
        # Create myVia_vullet
        self.edbapp.padstacks.create(padstackname="myVia_bullet", antipad_shape="Bullet")
        assert "myVia_bullet" in list(self.edbapp.padstacks.definitions.keys())
    
        self.edbapp.add_design_variable("via_x", 5e-3)
        self.edbapp["via_y"] = "1mm"
        assert self.edbapp["via_y"].value == 1e-3
        assert self.edbapp["via_y"].value_string == "1mm"
        assert self.edbapp.padstacks.place(["via_x", "via_x+via_y"], "myVia", via_name="via_test1")
        assert self.edbapp.padstacks.place(["via_x", "via_x+via_y*2"], "myVia_bullet")
        self.edbapp.padstacks["via_test1"].net_name = "GND"
        assert self.edbapp.padstacks["via_test1"].net_name == "GND"
        padstack = self.edbapp.padstacks.place(["via_x", "via_x+via_y*3"], "myVia", is_pin=True)
        for test_prop in (self.edbapp.padstacks.padstack_instances, self.edbapp.padstacks.instances):
            padstack_instance = test_prop[padstack.id]
            assert padstack_instance.is_pin
            assert padstack_instance.position
            assert padstack_instance.start_layer in padstack_instance.layer_range_names
            assert padstack_instance.stop_layer in padstack_instance.layer_range_names
            padstack_instance.position = [0.001, 0.002]
            assert padstack_instance.position == [0.001, 0.002]
            assert padstack_instance.parametrize_position()
            assert isinstance(padstack_instance.rotation, float)
            self.edbapp.padstacks.create_circular_padstack(padstackname="mycircularvia")
            assert "mycircularvia" in list(self.edbapp.padstacks.definitions.keys())
            assert not padstack_instance.backdrill_top
            assert not padstack_instance.backdrill_bottom
            assert padstack_instance.delete()
            via = self.edbapp.padstacks.place([0, 0], "myVia")
            assert via.set_backdrill_top("Inner4(Sig2)", 0.5e-3)
            assert via.backdrill_top
            assert via.set_backdrill_bottom("16_Bottom", 0.5e-3)
            assert via.backdrill_bottom

    def test_padstacks_get_nets_from_pin_list(self):
        """Retrieve pin list from component and net."""
        cmp_pinlist = self.edbapp.padstacks.get_pinlist_from_component_and_net("U1", "GND")
        assert cmp_pinlist[0].GetNet().GetName()

    def test_padstack_properties_getter(self):
        """Evaluate properties"""
        for el in self.edbapp.padstacks.definitions:
            padstack = self.edbapp.padstacks.definitions[el]
            assert padstack.hole_plating_thickness is not None or False
            assert padstack.hole_properties is not None or False
            assert padstack.hole_plating_thickness is not None or False
            assert padstack.hole_plating_ratio is not None or False
            assert padstack.via_start_layer is not None or False
            assert padstack.via_stop_layer is not None or False
            assert padstack.material is not None or False
            assert padstack.hole_finished_size is not None or False
            assert padstack.hole_rotation is not None or False
            assert padstack.hole_offset_x is not None or False
            assert padstack.hole_offset_y is not None or False
            assert padstack.hole_type is not None or False
            pad = padstack.pad_by_layer[padstack.via_stop_layer]
            if not pad.shape == "NoGeometry":
                assert pad.parameters is not None or False
                assert pad.parameters_values is not None or False
                assert pad.offset_x is not None or False
                assert pad.offset_y is not None or False
                assert isinstance(pad.geometry_type, int)
            polygon = pad.polygon_data
            if polygon:
                assert polygon.GetBBox()

    def test_padstack_properties_setter(self):
        """Set padstack properties"""
        pad = self.edbapp.padstacks.definitions["c180h127"]
        hole_pad = 8
        tol = 1e-12
        pad.hole_properties = hole_pad
        pad.hole_offset_x = 0
        pad.hole_offset_y = 1
        pad.hole_rotation = 0
        pad.hole_plating_ratio = 90
        assert pad.hole_plating_ratio == 90
        pad.hole_plating_thickness = 0.3
        assert abs(pad.hole_plating_thickness - 0.3) <= tol
        pad.material = "copper"
        assert abs(pad.hole_properties[0] - hole_pad) < tol
        offset_x = 7
        offset_y = 1
        pad.pad_by_layer[pad.via_stop_layer].shape = "Circle"
        pad.pad_by_layer[pad.via_stop_layer].parameters = 7
        pad.pad_by_layer[pad.via_stop_layer].offset_x = offset_x
        pad.pad_by_layer[pad.via_stop_layer].offset_y = offset_y
        assert pad.pad_by_layer[pad.via_stop_layer].parameters["Diameter"].tofloat == 7
        assert pad.pad_by_layer[pad.via_stop_layer].offset_x == str(offset_x)
        assert pad.pad_by_layer[pad.via_stop_layer].offset_y == str(offset_y)
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"Diameter": 8}
        assert pad.pad_by_layer[pad.via_stop_layer].parameters["Diameter"].tofloat == 8
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"Diameter": 1}
        pad.pad_by_layer[pad.via_stop_layer].shape = "Square"
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"Size": 1}
        pad.pad_by_layer[pad.via_stop_layer].shape = "Rectangle"
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"XSize": 1, "YSize": 1}
        pad.pad_by_layer[pad.via_stop_layer].shape = "Oval"
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"XSize": 1, "YSize": 1, "CornerRadius": 1}
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"XSize": 1, "YSize": 1, "CornerRadius": 1}
        pad.pad_by_layer[pad.via_stop_layer].parameters = [1, 1, 1]
