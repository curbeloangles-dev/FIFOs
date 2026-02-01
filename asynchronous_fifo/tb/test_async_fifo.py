from cocotb_test.simulator import run
import pytest
import os
import glob

dir = os.path.dirname(__file__)
src_vhdl  = glob.glob("../../src/*.vhd")

@pytest.mark.skipif(os.getenv("SIM") != "ghdl", reason="")
def test_async_fifo_vhdl():
    run(
        vhdl_sources=[os.path.join(dir, file) for file in src_vhdl], # sources
        toplevel="async_fifo",            # top level HDL
        module="async_fifo_tb",        # name of cocotb test module
        toplevel_lang="vhdl",
        sim_build="sim_build/test_vhdl",
        compile_args=["--ieee=synopsys","--std=08"],
        sim_args=["--wave=wave.ghw"]
    )

@pytest.mark.skipif(os.getenv("SIM") != "ghdl", reason="")
def test_fifo_vhdl():
    run(
        vhdl_sources=[os.path.join(dir, file) for file in src_vhdl], # sources
        toplevel="async_fifo",            # top level HDL
        module="fifo_tb",        # name of cocotb test module
        toplevel_lang="vhdl",
        sim_build="sim_build/test_vhdl",
        compile_args=["--ieee=synopsys","--std=08"],
        sim_args=["--wave=wave.ghw"]
    )