from cocotb_test.simulator import run
import pytest
import os
import glob

current_dir = os.path.dirname(__file__)
vhdl_srcs = glob.glob(os.path.join(current_dir, "../src/*.vhd"))
vhdl_srcs += glob.glob("../node_modules/@curbeloangles-dev/asymmetric_fifo/src/*.vhd")

@pytest.mark.parametrize(
    "parameters", [
                    {"g_input_width": "8",    "g_output_width": "8",    "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "8",    "g_output_width": "32",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "8",   "g_AXIS_TID_WIDTH"  : "20",  "g_AXIS_TDEST_WIDTH" : "32"},
                    {"g_input_width": "32",   "g_output_width": "8",    "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "16",  "g_AXIS_TID_WIDTH"  : "128", "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "8",    "g_output_width": "16",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "8",   "g_AXIS_TDEST_WIDTH" : "100"},
                    {"g_input_width": "16",   "g_output_width": "8",    "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "9",   "g_AXIS_TID_WIDTH"  : "15",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "8",    "g_output_width": "64",   "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "64",   "g_output_width": "8",    "g_DEPTH": "32",  "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "8",   "g_AXIS_TDEST_WIDTH" : "100"},
                    {"g_input_width": "8",    "g_output_width": "128",  "g_DEPTH": "64",  "g_AXIS_TUSER_WIDTH" : "2",   "g_AXIS_TID_WIDTH"  : "6",   "g_AXIS_TDEST_WIDTH" : "50"},
                    {"g_input_width": "128",  "g_output_width": "8",    "g_DEPTH": "128", "g_AXIS_TUSER_WIDTH" : "125", "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "10"},
                    {"g_input_width": "8",    "g_output_width": "256",  "g_DEPTH": "64",  "g_AXIS_TUSER_WIDTH" : "15",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "23"},
                    {"g_input_width": "256",  "g_output_width": "8",    "g_DEPTH": "128", "g_AXIS_TUSER_WIDTH" : "2",   "g_AXIS_TID_WIDTH"  : "3",   "g_AXIS_TDEST_WIDTH" : "4"},
                    {"g_input_width": "512",  "g_output_width": "8",    "g_DEPTH": "256", "g_AXIS_TUSER_WIDTH" : "8",   "g_AXIS_TID_WIDTH"  : "5",   "g_AXIS_TDEST_WIDTH" : "90"},
                    {"g_input_width": "8",    "g_output_width": "512",  "g_DEPTH": "128", "g_AXIS_TUSER_WIDTH" : "16",  "g_AXIS_TID_WIDTH"  : "4",   "g_AXIS_TDEST_WIDTH" : "32"},
                    {"g_input_width": "16",   "g_output_width": "16",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "16",   "g_output_width": "32",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "8",   "g_AXIS_TID_WIDTH"  : "20",  "g_AXIS_TDEST_WIDTH" : "32"},
                    {"g_input_width": "32",   "g_output_width": "16",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "16",  "g_AXIS_TID_WIDTH"  : "128", "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "16",   "g_output_width": "64",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "64",   "g_output_width": "16",   "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "8",   "g_AXIS_TDEST_WIDTH" : "100"},
                    {"g_input_width": "16",   "g_output_width": "128",  "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "2",   "g_AXIS_TID_WIDTH"  : "6",   "g_AXIS_TDEST_WIDTH" : "50"},
                    {"g_input_width": "128",  "g_output_width": "16",   "g_DEPTH": "32",  "g_AXIS_TUSER_WIDTH" : "125", "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "10"},
                    {"g_input_width": "16",   "g_output_width": "256",  "g_DEPTH": "32",  "g_AXIS_TUSER_WIDTH" : "15",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "23"},
                    {"g_input_width": "256",  "g_output_width": "16",   "g_DEPTH": "64",  "g_AXIS_TUSER_WIDTH" : "2",   "g_AXIS_TID_WIDTH"  : "3",   "g_AXIS_TDEST_WIDTH" : "4"},
                    {"g_input_width": "512",  "g_output_width": "16",   "g_DEPTH": "128", "g_AXIS_TUSER_WIDTH" : "8",   "g_AXIS_TID_WIDTH"  : "5",   "g_AXIS_TDEST_WIDTH" : "90"},
                    {"g_input_width": "16",   "g_output_width": "512",  "g_DEPTH": "64",  "g_AXIS_TUSER_WIDTH" : "16",  "g_AXIS_TID_WIDTH"  : "4",   "g_AXIS_TDEST_WIDTH" : "32"},
                    {"g_input_width": "32",   "g_output_width": "32",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "32",   "g_output_width": "64",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "64",   "g_output_width": "32",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "8",   "g_AXIS_TDEST_WIDTH" : "100"},
                    {"g_input_width": "32",   "g_output_width": "128",  "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "2",   "g_AXIS_TID_WIDTH"  : "6",   "g_AXIS_TDEST_WIDTH" : "50"},
                    {"g_input_width": "128",  "g_output_width": "32",   "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "125", "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "10"},
                    {"g_input_width": "32",   "g_output_width": "256",  "g_DEPTH": "32",  "g_AXIS_TUSER_WIDTH" : "15",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "23"},
                    {"g_input_width": "256",  "g_output_width": "32",   "g_DEPTH": "32",  "g_AXIS_TUSER_WIDTH" : "2",   "g_AXIS_TID_WIDTH"  : "3",   "g_AXIS_TDEST_WIDTH" : "4"},
                    {"g_input_width": "512",  "g_output_width": "32",   "g_DEPTH": "64",  "g_AXIS_TUSER_WIDTH" : "8",   "g_AXIS_TID_WIDTH"  : "5",   "g_AXIS_TDEST_WIDTH" : "90"},
                    {"g_input_width": "32",   "g_output_width": "512",  "g_DEPTH": "32",  "g_AXIS_TUSER_WIDTH" : "16",  "g_AXIS_TID_WIDTH"  : "4",   "g_AXIS_TDEST_WIDTH" : "32"},
                    {"g_input_width": "64",   "g_output_width": "64",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "64",   "g_output_width": "128",  "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "2",   "g_AXIS_TID_WIDTH"  : "6",   "g_AXIS_TDEST_WIDTH" : "50"},
                    {"g_input_width": "128",  "g_output_width": "64",   "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "125", "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "10"},
                    {"g_input_width": "64",   "g_output_width": "256",  "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "15",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "23"},
                    {"g_input_width": "256",  "g_output_width": "64",   "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "2",   "g_AXIS_TID_WIDTH"  : "3",   "g_AXIS_TDEST_WIDTH" : "4"},
                    {"g_input_width": "512",  "g_output_width": "64",   "g_DEPTH": "32",  "g_AXIS_TUSER_WIDTH" : "8",   "g_AXIS_TID_WIDTH"  : "5",   "g_AXIS_TDEST_WIDTH" : "90"},
                    {"g_input_width": "64",   "g_output_width": "512",  "g_DEPTH": "32",  "g_AXIS_TUSER_WIDTH" : "16",  "g_AXIS_TID_WIDTH"  : "4",   "g_AXIS_TDEST_WIDTH" : "32"},
                    {"g_input_width": "128",  "g_output_width": "128",  "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "128",  "g_output_width": "256",  "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "15",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "23"},
                    {"g_input_width": "256",  "g_output_width": "128",  "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "2",   "g_AXIS_TID_WIDTH"  : "3",   "g_AXIS_TDEST_WIDTH" : "4"},
                    {"g_input_width": "512",  "g_output_width": "128",  "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "8",   "g_AXIS_TID_WIDTH"  : "5",   "g_AXIS_TDEST_WIDTH" : "90"},
                    {"g_input_width": "128",  "g_output_width": "512",  "g_DEPTH": "16",  "g_AXIS_TUSER_WIDTH" : "16",  "g_AXIS_TID_WIDTH"  : "4",   "g_AXIS_TDEST_WIDTH" : "32"},
                    {"g_input_width": "256",  "g_output_width": "256",  "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "512",  "g_output_width": "256",  "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "8",   "g_AXIS_TID_WIDTH"  : "5",   "g_AXIS_TDEST_WIDTH" : "90"},
                    {"g_input_width": "256",  "g_output_width": "512",  "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "16",  "g_AXIS_TID_WIDTH"  : "4",   "g_AXIS_TDEST_WIDTH" : "32"},
                    {"g_input_width": "512",  "g_output_width": "512",  "g_DEPTH": "8",   "g_AXIS_TUSER_WIDTH" : "32",  "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"},
                    {"g_input_width": "96",   "g_output_width": "32",   "g_DEPTH": "66",  "g_AXIS_TUSER_WIDTH" : "8",   "g_AXIS_TID_WIDTH"  : "24",  "g_AXIS_TDEST_WIDTH" : "64"}
                    ])
@pytest.mark.skipif(os.getenv("SIM") != "ghdl", reason="")
def test_axi_stream_width_converter(parameters):
    run(
        vhdl_sources=vhdl_srcs,                     # vhdl sources
        toplevel="axi_stream_width_converter",      # top level HDL
        module="axi_stream_width_converter_tb",     # name of cocotb test module
        toplevel_lang="vhdl",
        parameters=parameters,
        extra_env=parameters, 
        sim_build="sim_build"
    )