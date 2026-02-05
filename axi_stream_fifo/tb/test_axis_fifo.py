from cocotb_test.simulator import run
import pytest
import os
import glob

current_dir = os.path.dirname(__file__)
vhdl_srcs = glob.glob(os.path.join(current_dir, "../src/*.vhd"))
vhdl_srcs += glob.glob("../node_modules/@curbeloangles-dev/asynchronous_fifo/src/*.vhd")

@pytest.mark.parametrize(
    "parameters", [{"g_DATA_WIDTH": "8"},
                   {"g_DATA_WIDTH": "16"},
                   {"g_DATA_WIDTH": "32"},
                   {"g_DATA_WIDTH": "64"},
                   {"g_DATA_WIDTH": "128"},
                   {"g_DATA_WIDTH": "256"}]
)
@pytest.mark.skipif(os.getenv("SIM") != "ghdl", reason="")
def test_axis_fifo_vhdl(parameters):
    run(
        vhdl_sources=vhdl_srcs,         # vhdl sources
        toplevel="axi_stream_fifo",     # top level HDL
        module="axi_stream_fifo_tb",    # name of cocotb test module
        toplevel_lang="vhdl",
        parameters=parameters,
        extra_env=parameters, 
        sim_build="sim_build"
    )