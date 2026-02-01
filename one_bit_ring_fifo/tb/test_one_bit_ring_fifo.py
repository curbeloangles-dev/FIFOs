from    cocotb_test.simulator   import run
import  pytest
import  os
import  glob

dir = os.path.dirname(__file__)
src_vhdl = glob.glob("../src/*.vhd")

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
        vhdl_sources=[os.path.join(dir, file) for file in src_vhdl],    # vhdl sources
        toplevel="one_bit_ring_fifo",                                   # top level HDL
        module="one_bit_ring_fifo_tb",                                  # name of cocotb test module
        toplevel_lang="vhdl",
        parameters=parameters,
        extra_env=parameters, 
        compile_args=["--ieee=synopsys","--std=08"],
        sim_build="sim_build",
        sim_args=["--wave=wave.ghw"]
    )

@pytest.mark.parametrize(
    "parameters", [
                    {"index": 0, "g_data_in_width": "8",    "g_data_out_width": "64",   "g_fifo_depth": "64"},  
                    {"index": 1, "g_data_in_width": "10",   "g_data_out_width": "32",   "g_fifo_depth": "64"},
                    {"index": 2, "g_data_in_width": "16",   "g_data_out_width": "20",   "g_fifo_depth": "32"},  
                    {"index": 3, "g_data_in_width": "20",   "g_data_out_width": "16",   "g_fifo_depth": "32"},
                    {"index": 4, "g_data_in_width": "32",   "g_data_out_width": "10",   "g_fifo_depth": "128"}, 
                    {"index": 5, "g_data_in_width": "64",   "g_data_out_width": "8",    "g_fifo_depth": "256"},
                    {"index": 6, "g_data_in_width": "10",   "g_data_out_width": "31",   "g_fifo_depth": "32"}
                    ])
@pytest.mark.skipif(os.getenv("SIM") != "questa", reason="")
def test_one_bit_ring_fifo_tb_questa(parameters):
    index = parameters["index"]
    run(
        vhdl_sources=[os.path.join(dir, file) for file in src_vhdl],    # vhdl sources
        toplevel="one_bit_ring_fifo",                                   # top level HDL
        module="one_bit_ring_fifo_tb",                                  # name of cocotb test module
        toplevel_lang="vhdl",
        parameters=parameters,
        compile_args=["+cover=bcesf", "-autoorder", "-2008"],
        sim_args=["-coverage","-t", "1ps", "-do",f"coverage save -onexit ../../doc/report_{index}.ucdb"],
        force_compile=True
    )