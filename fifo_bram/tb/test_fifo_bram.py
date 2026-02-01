from    cocotb_test.simulator   import run
import  pytest
import  os
import  glob

dir = os.path.dirname(__file__)
src_vhdl = glob.glob("../../src/*.vhd")

@pytest.mark.skipif(os.getenv("SIM") != "ghdl", reason="")
def test_fifo_bram_vhdl():
    run(
        vhdl_sources=[os.path.join(dir, file) for file in src_vhdl],      # vhdl sources
        toplevel="fifo_bram",                                             # top level HDL
        toplevel_lang="vhdl",
        module="fifo_bram_tb",                                            # name of cocotb test module
        compile_args=["--ieee=synopsys","--std=08"],
        sim_build="sim_build/test_vhdl",
        sim_args=["--wave=wave.ghw"]
    )