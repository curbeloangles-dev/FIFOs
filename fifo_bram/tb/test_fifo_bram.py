from    cocotb_test.simulator   import run
import  pytest
import  os
import  glob

current_dir = os.path.dirname(__file__)
vhdl_src = glob.glob(os.path.join(current_dir, "../src/*.vhd"))

@pytest.mark.skipif(os.getenv("SIM") != "ghdl", reason="")
def test_fifo_bram_vhdl():
    run(
        vhdl_sources=vhdl_src,      # vhdl sources
        toplevel="fifo_bram",       # top level HDL
        module="fifo_bram_tb",      # name of cocotb test module
        toplevel_lang="vhdl",
        sim_build="sim_build"
    )