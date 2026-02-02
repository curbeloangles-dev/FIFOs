from    cocotb_test.simulator   import run
import  pytest
import  os
import  glob

current_dir = os.path.dirname(__file__)
vhdl_src = glob.glob(os.path.join(current_dir, "../src/*.vhd"))

@pytest.mark.parametrize(
    "parameters", [
                    {"g_data_in_width": "8",    "g_data_out_width": "64",   "g_fifo_depth": "64"},
                    {"g_data_in_width": "10",   "g_data_out_width": "32",   "g_fifo_depth": "64"},
                    {"g_data_in_width": "16",   "g_data_out_width": "20",   "g_fifo_depth": "32"},
                    {"g_data_in_width": "20",   "g_data_out_width": "16",   "g_fifo_depth": "32"},
                    {"g_data_in_width": "32",   "g_data_out_width": "10",   "g_fifo_depth": "128"},
                    {"g_data_in_width": "64",   "g_data_out_width": "8",    "g_fifo_depth": "256"}
                    ])
@pytest.mark.skipif(os.getenv("SIM") != "ghdl", reason="")
def test_one_bit_ring_fifo_tb_ghdl(parameters):
    run(
        vhdl_sources=vhdl_src,                  # vhdl sources
        toplevel="one_bit_ring_fifo",           # top level HDL
        module="one_bit_ring_fifo_tb",          # name of cocotb test module
        toplevel_lang="vhdl",
        parameters=parameters,
        extra_env=parameters, 
        sim_build="sim_build"
    )