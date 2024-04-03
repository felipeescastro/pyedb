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

"""
EDB: SYZ analysis
-------------------
This example shows how you can use PyAEDT to set up SYZ analysis on Serdes channel.
The input is the name of the differential nets. The positive net is PCIe_Gen4_TX3_CAP_P.
The negative net is PCIe_Gen4_TX3_CAP_N. The code will place ports on driver and
receiver components.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes importing a section.

import time

from pyaedt import Hfss3dLayout

import pyedb
from pyedb.generic.general_methods import generate_unique_folder_name
from pyedb.misc.downloads import download_file

###############################################################################
# Download file
# ~~~~~~~~~~~~~
# Download the AEDB file and copy it in the temporary folder.

temp_folder = generate_unique_folder_name()
targetfile = download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
time.sleep(5)

print(targetfile)

###############################################################################
# Configure EDB
# ~~~~~~~~~~~~~
# Launch the :class:`pyedb.Edb` class, using EDB 2023 R2.

edbapp = pyedb.Edb(edbpath=targetfile, edbversion="2024.1")

###############################################################################
# Generate extended nets
# ~~~~~~~~~~~~~~~~~~~~~~
# An extended net is a connection between two nets that are usually connected
# through a passive component like a resistor or capacitor.

edbapp.extended_nets.auto_identify_signal(resistor_below=10, inductor_below=1, capacitor_above=1e-9)

###############################################################################
# Review extended net properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Review extended net properties.

diff_p = edbapp.nets["PCIe_Gen4_TX3_CAP_P"]
diff_n = edbapp.nets["PCIe_Gen4_TX3_CAP_N"]

nets_p = list(diff_p.extended_net.nets.keys())
nets_n = list(diff_n.extended_net.nets.keys())

comp_p = list(diff_p.extended_net.components.keys())
comp_n = list(diff_n.extended_net.components.keys())

rlc_p = list(diff_p.extended_net.rlc.keys())
rlc_n = list(diff_n.extended_net.rlc.keys())

print(comp_p, rlc_p, comp_n, rlc_n, sep="\n")

###############################################################################
# Prepare input data for port creation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Prepare input data for port creation.

ports = []
for net_name, net_obj in diff_p.extended_net.nets.items():
    for comp_name, comp_obj in net_obj.components.items():
        if comp_obj.type not in ["Resistor", "Capacitor", "Inductor"]:
            ports.append(
                {"port_name": "{}_{}".format(comp_name, net_name), "comp_name": comp_name, "net_name": net_name}
            )

for net_name, net_obj in diff_n.extended_net.nets.items():
    for comp_name, comp_obj in net_obj.components.items():
        if comp_obj.type not in ["Resistor", "Capacitor", "Inductor"]:
            ports.append(
                {"port_name": "{}_{}".format(comp_name, net_name), "comp_name": comp_name, "net_name": net_name}
            )

print(*ports, sep="\n")

###############################################################################
# Create ports
# ~~~~~~~~~~~~
# Solder balls are generated automatically. The default port type is coax port.

for d in ports:
    port_name = d["port_name"]
    comp_name = d["comp_name"]
    net_name = d["net_name"]
    edbapp.components.create_port_on_component(component=comp_name, net_list=net_name, port_name=port_name)

###############################################################################
# Cutout
# ~~~~~~
# Delete all irrelevant nets.

nets = []
nets.extend(nets_p)
nets.extend(nets_n)

edbapp.cutout(signal_list=nets, reference_list=["GND"], extent_type="Bounding")


###############################################################################
# Create SYZ analysis setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Create SIwave SYZ setup.

setup = edbapp.create_siwave_syz_setup("setup1")
setup.add_frequency_sweep(
    frequency_sweep=[
        ["linear count", "0", "1kHz", 1],
        ["log scale", "1kHz", "0.1GHz", 10],
        ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
    ]
)

###############################################################################
# Save and close AEDT
# ~~~~~~~~~~~~~~~~~~~
# Close AEDT.

edbapp.save()
edbapp.close_edb()

###############################################################################
# Launch Hfss3dLayout
# ~~~~~~~~~~~~~~~~~~~
# To do SYZ analysis, you must launch HFSS 3D Layout and import EDB into it.

h3d = Hfss3dLayout(targetfile, specified_version="2024.1", new_desktop_session=True)

###############################################################################
# Set differential pair
# ~~~~~~~~~~~~~~~~~~~~~
# Set differential pair.

h3d.set_differential_pair(
    positive_terminal="U1_PCIe_Gen4_TX3_CAP_P", negative_terminal="U1_PCIe_Gen4_TX3_CAP_N", diff_name="PAIR_U1"
)
h3d.set_differential_pair(
    positive_terminal="X1_PCIe_Gen4_TX3_P", negative_terminal="X1_PCIe_Gen4_TX3_N", diff_name="PAIR_X1"
)

###############################################################################
# Solve and plot results
# ~~~~~~~~~~~~~~~~~~~~~~
# Solve and plot the results.

h3d.analyze(num_cores=4)

###############################################################################
# Create report outside AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a report.

h3d.post.create_report("dB(S(PAIR_U1,PAIR_U1))", context="Differential Pairs")

###############################################################################
# Close AEDT
# ~~~~~~~~~~
# Close AEDT.

h3d.save_project()
print("Project is saved to {}".format(h3d.project_path))
h3d.release_desktop(True, True)
