# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pyedb.configuration.cfg_boundaries import CfgBoundaries
from pyedb.configuration.cfg_components import CfgComponent
from pyedb.configuration.cfg_general import CfgGeneral
from pyedb.configuration.cfg_nets import CfgNets
from pyedb.configuration.cfg_padstacks import CfgPadstacks
from pyedb.configuration.cfg_pin_groups import CfgPinGroup
from pyedb.configuration.cfg_ports_sources import CfgPort, CfgSources
from pyedb.configuration.cfg_setup import CfgSetup
from pyedb.configuration.cfg_spice_models import CfgSpiceModel


class CfgData(object):
    """Manages configure data."""

    def __init__(self, pedb, **kwargs):
        self.pedb = pedb
        self.edb_comps = self.pedb.components.components
        self.general = CfgGeneral(self, kwargs.get("general", None))
        self.boundaries = {}
        if kwargs.get("boundaries", None):
            self.boundaries = CfgBoundaries(self, kwargs.get("boundaries", None))
        self.nets = CfgNets(self)
        if kwargs.get("nets"):
            self.nets = CfgNets(
                self, kwargs.get("nets", {}).get("signal_nets", []), kwargs.get("nets", {}).get("power_ground_nets", [])
            )
        self.components = [CfgComponent(self, **component) for component in kwargs.get("components", [])]
        self.padstacks = CfgPadstacks(self, kwargs.get("padstacks", None))
        self.pin_groups = [CfgPinGroup(self, pin_group) for pin_group in kwargs.get("pin_groups", [])]
        self.ports = [CfgPort(self, **port) for port in kwargs.get("ports", [])]
        self.sources = [CfgSources(self, **source) for source in kwargs.get("sources", [])]
        self.setups = [CfgSetup(self)]
        if kwargs.get("setups", None):
            self.setups = [CfgSetup(self, setup) for setup in kwargs.get("setups", [])]
        self.stackup = None
        self.s_parameters = None
        self.spice_models = [
            CfgSpiceModel(self, self.general.spice_model_library, spice_model)
            for spice_model in kwargs.get("spice_models", [])
        ]
        self.package_definition = None
        self.operations = None
