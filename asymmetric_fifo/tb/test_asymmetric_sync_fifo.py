from cocotb_test.simulator import run
import pytest
import os
import glob

dir = os.path.dirname(__file__)

@pytest.mark.parametrize(
    "parameters", [
                    {"g_input_width": "2", "g_output_width": "128", "g_depth": "64"}, {"g_input_width": "2", "g_output_width": "64", "g_depth": "64"}, 
                    {"g_input_width": "2", "g_output_width": "32", "g_depth": "64"}, {"g_input_width": "2", "g_output_width": "16", "g_depth": "64"},
                    {"g_input_width": "2", "g_output_width": "8", "g_depth": "64"},
                    {"g_input_width": "2", "g_output_width": "4", "g_depth": "64"}, 
                    {"g_input_width": "2", "g_output_width": "2", "g_depth": "64"},
                    {"g_input_width": "4", "g_output_width": "128", "g_depth": "64"}, {"g_input_width": "4", "g_output_width": "64", "g_depth": "64"},
                    {"g_input_width": "4", "g_output_width": "32", "g_depth": "64"}, {"g_input_width": "4", "g_output_width": "16", "g_depth": "64"},
                    {"g_input_width": "4", "g_output_width": "8", "g_depth": "64"},
                    {"g_input_width": "4", "g_output_width": "4", "g_depth": "64"},
                    {"g_input_width": "4", "g_output_width": "2", "g_depth": "64"},
                    {"g_input_width": "8", "g_output_width": "128", "g_depth": "64"}, {"g_input_width": "8", "g_output_width": "64", "g_depth": "64"},
                    {"g_input_width": "8", "g_output_width": "32", "g_depth": "64"}, {"g_input_width": "8", "g_output_width": "16", "g_depth": "64"},
                    {"g_input_width": "8", "g_output_width": "8", "g_depth": "64"},
                    {"g_input_width": "8", "g_output_width": "4", "g_depth": "64"},
                    {"g_input_width": "8", "g_output_width": "2", "g_depth": "64"},
                    {"g_input_width": "16", "g_output_width": "128", "g_depth": "64"}, {"g_input_width": "16", "g_output_width": "64", "g_depth": "64"},
                    {"g_input_width": "16", "g_output_width": "32", "g_depth": "64"}, {"g_input_width": "16", "g_output_width": "16", "g_depth": "64"},
                    {"g_input_width": "16", "g_output_width": "8", "g_depth": "64"},
                    {"g_input_width": "16", "g_output_width": "4", "g_depth": "64"},
                    {"g_input_width": "16", "g_output_width": "2", "g_depth": "64"},
                    {"g_input_width": "32", "g_output_width": "128", "g_depth": "64"}, {"g_input_width": "32", "g_output_width": "64", "g_depth": "64"},
                    {"g_input_width": "32", "g_output_width": "32", "g_depth": "64"}, {"g_input_width": "32", "g_output_width": "16", "g_depth": "64"},
                    {"g_input_width": "32", "g_output_width": "8", "g_depth": "64"}, {"g_input_width": "32", "g_output_width": "4", "g_depth": "64"},
                    {"g_input_width": "32", "g_output_width": "2", "g_depth": "64"},
                    {"g_input_width": "64", "g_output_width": "128", "g_depth": "64"}, {"g_input_width": "64", "g_output_width": "64", "g_depth": "64"},
                    {"g_input_width": "64", "g_output_width": "32", "g_depth": "64"}, {"g_input_width": "64", "g_output_width": "16", "g_depth": "64"},
                    {"g_input_width": "64", "g_output_width": "8", "g_depth": "64"}, {"g_input_width": "64", "g_output_width": "4", "g_depth": "64"},
                    {"g_input_width": "64", "g_output_width": "2", "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "128", "g_depth": "64"}, {"g_input_width": "128", "g_output_width": "64", "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "32", "g_depth": "64"}, {"g_input_width": "128", "g_output_width": "16", "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "8", "g_depth": "64"}, {"g_input_width": "128", "g_output_width": "4", "g_depth": "64"},
                    {"g_input_width": "128", "g_output_width": "2", "g_depth": "64"},
                    {"g_input_width": "256", "g_output_width": "128", "g_depth": "64"}, {"g_input_width": "128", "g_output_width": "256", "g_depth": "64"},
                    {"g_input_width": "32", "g_output_width": "256", "g_depth": "64"}, {"g_input_width": "256", "g_output_width": "32", "g_depth": "64"},
                    {"g_input_width": "256", "g_output_width": "64", "g_depth": "64"}, {"g_input_width": "64", "g_output_width": "256", "g_depth": "64"},
                    {"g_input_width": "96", "g_output_width": "32", "g_depth": "64"},
                    {"g_input_width": "1344", "g_output_width": "192", "g_depth": "64"},
                    {"g_input_width": "192", "g_output_width": "64","g_depth": "64"}
                   ]
)
@pytest.mark.skipif(os.getenv("SIM") != "ghdl", reason="")
def test_asymmetric_sync_fifo(parameters):
    run(
        vhdl_sources=[os.path.join(dir, "..","..","src","asymmetric_sync_fifo_up.vhd"),
                      os.path.join(dir, "..","..","src","asymmetric_sync_fifo_down.vhd"),
                      os.path.join(dir, "..","..","src","asymmetric_sync_fifo.vhd")], # sources
        toplevel="asymmetric_sync_fifo",            # top level HDL
        module="asymmetric_sync_fifo_tb",        # name of cocotb test module
        toplevel_lang="vhdl",
        compile_args=["--ieee=synopsys","--std=08"],
        parameters=parameters,
        extra_env=parameters, 
        sim_build="sim_build/test_vhdl" + "_".join(("{}={}".format(*i) for i in parameters.items())),
        sim_args=["--wave=wave.ghw"]
    )

src_v     = glob.glob("../../src/*.v")

@pytest.mark.skipif(os.getenv("SIM") != "icarus", reason="")
def test_async_fifo_verilog():
    run(
        verilog_sources=[os.path.join(dir, file) for file in src_v],      # verilog sources
        toplevel_lang="verilog",
        toplevel="asymmetric_sync_fifo",                                             # top level HDL
        module="asymmetric_sync_fifo_tb",                                            # name of cocotb test module
        timescale= "1ns/1ps",
        sim_build="sim_build/test_verilog"
    )