import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ClockCycles, Join
from cocotb.result import TestFailure
from cocotb.clock import Clock
from cocotb import coroutine
import numpy as np

# Constants
c_CLK_PERIOD_RD = 4 #ns
c_CLK_PERIOD_WR = 10 #ns
#========================================================================================#
async def write_data(dut, data):
    i = 0
    await RisingEdge(dut.i_CLK_WR)
    done = 0
    while done == 0:
        dut.i_INC_WR.value = 1
        dut.i_DAT_WR.value = int(data[i])
        await RisingEdge(dut.i_CLK_WR)
        if int(dut.o_FULL_FLAG.value) == 0:
            i = i+1
        if i == len(data):
            done = 1
    dut.i_INC_WR.value = 0
    return 0  
#========================================================================================#
async def read_data(dut,data):
    await RisingEdge(dut.i_CLK_RD)
    dut.i_INC_RD.value = 1
    while True:
        if int(dut.o_DAT_VALID) == 1 and dut.i_INC_RD.value == 1:
            rd_data = int(dut.o_DAT_RD)
            data += [rd_data]
            dut._log.info("Data read: " +hex(rd_data))
        await RisingEdge(dut.i_CLK_RD)
#========================================================================================#
@cocotb.test(skip = False, stage = 1)
def fifo_tb(dut):
    # Setting up clocks
    clk_rd_100MHz = Clock(dut.i_CLK_RD, c_CLK_PERIOD_RD, units='ns')
    cocotb.start_soon(clk_rd_100MHz.start(start_high=False))
    clk_wr_200MHz = Clock(dut.i_CLK_WR, c_CLK_PERIOD_WR, units='ns')
    cocotb.start_soon(clk_wr_200MHz.start(start_high=False))

    # Setting init values
    dut.i_RST_WR.value = 1
    dut.i_RST_RD.value = 1
    dut.i_INC_RD.value = 0
    dut.i_INC_WR.value = 0
    dut.i_DAT_WR.value = 0

    # Deactivate reset
    yield RisingEdge(dut.i_CLK_WR)
    dut.i_RST_WR.value = 0
    dut.i_RST_RD.value = 0

    # Gen data
    yield RisingEdge(dut.i_CLK_RD)
    input_data = np.random.randint(0,2**32-1,10000)
    output_data = []
    gen_data = cocotb.start_soon(write_data(dut,input_data))
    yield Timer(500, units='ns')
    out_data = cocotb.start_soon(read_data(dut,output_data))

    yield Join(gen_data)
    yield Timer(1, units='us')
    out_data.kill()
    dut.i_INC_RD.value = 0

    # Compare
    for h in range(len(output_data)):
        if input_data[h] != output_data[h]:
            raise TestFailure("Input data = " + str(hex(input_data[h])) +" != Output data = " + str(hex(output_data[h])))
        else:
            dut._log.info("Input data = " + str(hex(input_data[h])) +" = Output data = " + str(hex(output_data[h])))
    dut._log.info("All data is correct!")

