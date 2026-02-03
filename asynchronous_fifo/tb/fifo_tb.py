import  cocotb
from    cocotb.triggers import RisingEdge, Join
from    cocotb.result   import TestFailure
from    cocotb.clock    import Clock
import  numpy           as np

# Constants
c_CLK_PERIOD_RD = 5 #ns
c_CLK_PERIOD_WR = 10 #ns
#========================================================================================#
async def write_data(dut, data):
    for i in range(len(data)):
        if int(dut.o_FULL_FLAG) != 1:
            dut.i_INC_WR.value = 1
            dut.i_DAT_WR.value = int(data[i])
            dut._log.info("Write data: %s" % hex(data[i]))
        else:
            dut.i_INC_WR = 0
        # One packet each 16 cycles
        for i in range(16):
            await RisingEdge(dut.i_CLK_WR)
            dut.i_INC_WR.value = 0
    dut.i_INC_WR.value = 0
    return 0  
#========================================================================================#
async def read_data(dut,data):
    while True:
        await RisingEdge(dut.i_CLK_RD)
        if int(dut.o_EMPTY_FLAG.value) == 0:
            dut.i_INC_RD.value = 1
        if int(dut.o_DAT_VALID.value) == 1:
            rd_data = int(dut.o_DAT_RD.value)
            data += [rd_data]
            dut._log.info("Read data: %s" % hex(rd_data))

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
    get_data = cocotb.start_soon(read_data(dut,output_data))

    yield Join(gen_data)

    # Compare
    for h in range(len(output_data)-1):
        if input_data[h] != output_data[h+1]:
            raise TestFailure("Input data = " + str(hex(input_data[h])) +" != Output data = " + str(hex(output_data[h+1])))
        else:
            dut._log.info("Input data = " + str(hex(input_data[h])) +" = Output data = " + str(hex(output_data[h+1])))
    dut._log.info("All data is correct!")

            
