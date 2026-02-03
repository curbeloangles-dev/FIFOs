import pytest
import os
import glob
from cocotb_test.simulator import run

current_dir = os.path.dirname(__file__)
vhdl_src = glob.glob(os.path.join(current_dir, "../src/*.vhd"))

@pytest.mark.parametrize(
    "parameters", [
                    {"g_input_width": "2",   "g_output_width": "128", "g_depth": "64"}, 
                    {"g_input_width": "2",   "g_output_width": "64",  "g_depth": "64"}, 
                    {"g_input_width": "2",   "g_output_width": "32",  "g_depth": "64"}, 
                    {"g_input_width": "2",   "g_output_width": "16",  "g_depth": "64"},
                    {"g_input_width": "2",   "g_output_width": "8",   "g_depth": "64"},
                    {"g_input_width": "2",   "g_output_width": "4",   "g_depth": "64"}, 
                    {"g_input_width": "2",   "g_output_width": "2",   "g_depth": "64"},
                    {"g_input_width": "4",   "g_output_width": "128", "g_depth": "64"}, 
                    {"g_input_width": "4",   "g_output_width": "64",  "g_depth": "64"},
                    {"g_input_width": "4",   "g_output_width": "32",  "g_depth": "64"},
                    {"g_input_width": "4",   "g_output_width": "16",  "g_depth": "64"},
                    {"g_input_width": "4",   "g_output_width": "8",   "g_depth": "64"},
                    {"g_input_width": "4",   "g_output_width": "4",   "g_depth": "64"},
                    {"g_input_width": "4",   "g_output_width": "2",   "g_depth": "64"},
                    {"g_input_width": "8",   "g_output_width": "128", "g_depth": "64"},
                    {"g_input_width": "8",   "g_output_width": "64",  "g_depth": "64"},
                    {"g_input_width": "8",   "g_output_width": "32",  "g_depth": "64"},
                    {"g_input_width": "8",   "g_output_width": "16",  "g_depth": "64"},
                    {"g_input_width": "8",   "g_output_width": "8",   "g_depth": "64"},
                    {"g_input_width": "8",   "g_output_width": "4",   "g_depth": "64"},
                    {"g_input_width": "8",   "g_output_width": "2",   "g_depth": "64"},
                    {"g_input_width": "16",  "g_output_width": "128", "g_depth": "64"},
                    {"g_input_width": "16",  "g_output_width": "64",  "g_depth": "64"},
                    {"g_input_width": "16",  "g_output_width": "32",  "g_depth": "64"},
                    {"g_input_width": "16",  "g_output_width": "16",  "g_depth": "64"},
                    {"g_input_width": "16",  "g_output_width": "8",   "g_depth": "64"},
                    {"g_input_width": "16",  "g_output_width": "4",   "g_depth": "64"},
                    {"g_input_width": "16",  "g_output_width": "2",   "g_depth": "64"},
                    {"g_input_width": "32",  "g_output_width": "128", "g_depth": "64"},
                    {"g_input_width": "32",  "g_output_width": "64",  "g_depth": "64"},
                    {"g_input_width": "32",  "g_output_width": "32",  "g_depth": "64"},
                    {"g_input_width": "32",  "g_output_width": "16",  "g_depth": "64"},
                    {"g_input_width": "32",  "g_output_width": "8",   "g_depth": "64"},
                    {"g_input_width": "32",  "g_output_width": "4",   "g_depth": "64"},
                    {"g_input_width": "32",  "g_output_width": "2",   "g_depth": "64"},
                    {"g_input_width": "64",  "g_output_width": "128", "g_depth": "64"},
                    {"g_input_width": "64",  "g_output_width": "64",  "g_depth": "64"},
                    {"g_input_width": "64",  "g_output_width": "32",  "g_depth": "64"},
                    {"g_input_width": "64",  "g_output_width": "16",  "g_depth": "64"},
                    {"g_input_width": "64",  "g_output_width": "8",   "g_depth": "64"},
                    {"g_input_width": "64",  "g_output_width": "4",   "g_depth": "64"},
                    {"g_input_width": "64",  "g_output_width": "2",   "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "128", "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "64",  "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "32",  "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "16",  "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "8",   "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "4",   "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "2",   "g_depth": "64"},
                    {"g_input_width": "256", "g_output_width": "128", "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "256", "g_depth": "64"},
                    {"g_input_width": "32",  "g_output_width": "256", "g_depth": "64"},
                    {"g_input_width": "256", "g_output_width": "32",  "g_depth": "64"},
                    {"g_input_width": "256", "g_output_width": "64",  "g_depth": "64"},
                    {"g_input_width": "64",  "g_output_width": "256", "g_depth": "64"},
                    {"g_input_width": "96",  "g_output_width": "32",  "g_depth": "64"},
                    {"g_input_width": "192", "g_output_width": "64",  "g_depth": "64"}
                   ]
)
@pytest.mark.skipif(os.getenv("SIM") != "ghdl", reason="")
def test_asymmetric_sync_fifo(parameters):
    run(
        vhdl_sources=vhdl_src,                          # sources
        toplevel="asymmetric_sync_fifo",                # top level HDL
        module="asymmetric_sync_fifo_tb",               # name of cocotb test module
        toplevel_lang="vhdl",
        parameters=parameters,
        extra_env=parameters, 
        sim_build="sim_build"
    )