import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ClockCycles, Join
from cocotb.result import TestFailure
from cocotb.clock import Clock
from cocotb import coroutine
import numpy as np
from random import randint

# Constants
c_CLK_PERIOD_RD = 10 #ns

try :
    g_INPUT_WIDTH = dut.g_INPUT_WIDTH.value
except:
    g_INPUT_WIDTH = 128

try :
    g_OUTPUT_WIDTH = dut.g_OUTPUT_WIDTH.value
except:
    g_OUTPUT_WIDTH = 32

#========================================================================================#
async def write_data(dut, number):
    i = 0
    global input_data

    try :
        g_INPUT_WIDTH = dut.g_INPUT_WIDTH.value
    except:
        g_INPUT_WIDTH = 128

    try :
        g_OUTPUT_WIDTH = dut.g_OUTPUT_WIDTH.value
    except:
        g_OUTPUT_WIDTH = 32

    input_data = []
    await RisingEdge(dut.clk)
    done = 0
    while done == 0:
        if int(dut.full) == 0:
            random_num = randint(0,2**int(g_INPUT_WIDTH)-1)
            dut.wr_data.value = random_num
            dut.wr_en.value = 1
            i = i+1
        else:
            dut.wr_en.value = 0
        await RisingEdge(dut.clk)
        if int(dut.full) == 0 and dut.wr_en.value == 1:
            input_data.append(random_num)
        if i == number:
            done = 1
    dut.wr_en.value = 0
    return 0  
# ==============================================================================
async def random_rd_en(dut):
    while True:
        await RisingEdge(dut.clk)
        dut.rd_en.value = randint(0,1)
#========================================================================================#
async def read_data(dut,data):
    while True:
        await RisingEdge(dut.clk)
        if int(dut.rd_valid.value) == 1 and int(dut.rd_en.value) == 1:
            rd_data = int(dut.rd_data.value)
            data += [rd_data]
        
#========================================================================================#
@cocotb.test(skip = False, stage = 1, timeout_time=10000, timeout_unit='us')
def run_multiple_data_test(dut):

    try :
        g_INPUT_WIDTH = dut.g_INPUT_WIDTH.value
    except:
        g_INPUT_WIDTH = 128

    try :
        g_OUTPUT_WIDTH = dut.g_OUTPUT_WIDTH.value
    except:
        g_OUTPUT_WIDTH = 32

    c_OUTPUT_WIDTH = int(g_OUTPUT_WIDTH)
    c_INPUT_WIDTH = int(g_INPUT_WIDTH)
    if c_INPUT_WIDTH <= c_OUTPUT_WIDTH:
        up_or_down = True
    else:
        up_or_down = False
    # Setting up clocks
    clk_rd_100MHz = Clock(dut.clk, c_CLK_PERIOD_RD, units='ns')
    cocotb.start_soon(clk_rd_100MHz.start(start_high=False))


    # Setting init values
    dut.rst.value = 1
    dut.wr_en.value = 0
    dut.wr_data.value = 0
    dut.rd_en.value = 0

    output_data = []
    yield RisingEdge(dut.clk)
    rand_rd_en = cocotb.start_soon(random_rd_en(dut))
    out_data = cocotb.start_soon(read_data(dut,output_data))

    # Deactivate reset
    yield RisingEdge(dut.clk)
    dut.rst.value = 0

    # Gen data
    yield RisingEdge(dut.clk)
    gen_data = cocotb.start_soon(write_data(dut,10000))

    yield Join(gen_data)

    yield Timer(10, units='us')
    yield RisingEdge(dut.clk)
    out_data.kill()
    rand_rd_en.kill()
    dut.rd_en.value = 0
    yield RisingEdge(dut.clk)
    # Compare
    if up_or_down == True:
        for i in range(len(output_data)):
            input_number = 0
            for k in range(0,c_OUTPUT_WIDTH,c_INPUT_WIDTH):
                input_number = input_number + (int(input_data[(i*int(c_OUTPUT_WIDTH/c_INPUT_WIDTH))+int(k/c_INPUT_WIDTH)]) << k)
            assert input_number == output_data[i], "Input data: %s differs from ouput data %s" % (hex(input_number),hex(output_data[i]))
            dut._log.info("Input data: %s = Ouput data %s" % (hex(input_number),hex(output_data[i])))
        dut._log.info("All data is correct!")
    else:
        for i in range(int(len(output_data)/int(c_INPUT_WIDTH/c_OUTPUT_WIDTH))):
            output_number = 0
            for k in range(0,c_INPUT_WIDTH,c_OUTPUT_WIDTH):
                output_number = output_number + (int(output_data[(i*int(c_INPUT_WIDTH/c_OUTPUT_WIDTH))+int(k/c_OUTPUT_WIDTH)]) << k)
            assert output_number == input_data[i], "Input data: %s differs from ouput data %s" % (hex(input_data[i]),hex(output_number))
            dut._log.info("Input data: %s = Ouput data %s" % (hex(input_data[i]),hex(output_number)))
        dut._log.info("All data is correct!")
#========================================================================================#        
@cocotb.test(skip = False, stage = 2, timeout_time=1000, timeout_unit='us')
def run_one_data_test(dut):

    try :
        g_INPUT_WIDTH = dut.g_INPUT_WIDTH.value
    except:
        g_INPUT_WIDTH = 128

    try :
        g_OUTPUT_WIDTH = dut.g_OUTPUT_WIDTH.value
    except:
        g_OUTPUT_WIDTH = 32
        
    c_OUTPUT_WIDTH = int(g_OUTPUT_WIDTH)
    c_INPUT_WIDTH = int(g_INPUT_WIDTH)
    if c_INPUT_WIDTH <= c_OUTPUT_WIDTH:
        up_or_down = True
        ratio = int(c_OUTPUT_WIDTH/c_INPUT_WIDTH)
    else:
        up_or_down = False
        ratio = int(c_INPUT_WIDTH/c_OUTPUT_WIDTH)
    # Setting up clocks
    clk_rd_100MHz = Clock(dut.clk, c_CLK_PERIOD_RD, units='ns')
    cocotb.start_soon(clk_rd_100MHz.start(start_high=False))


    # Setting init values
    dut.rst.value = 1
    dut.wr_en.value = 0
    dut.wr_data.value = 0
    dut.rd_en.value = 0

    output_data = []
    yield RisingEdge(dut.clk)
    rand_rd_en = cocotb.start_soon(random_rd_en(dut))
    out_data = cocotb.start_soon(read_data(dut,output_data))

    # Deactivate reset
    yield RisingEdge(dut.clk)
    dut.rst.value = 0

    # Gen data
    yield RisingEdge(dut.clk)
    gen_data = cocotb.start_soon(write_data(dut,ratio))

    yield Join(gen_data)

    yield Timer(10, units='us')
    yield RisingEdge(dut.clk)
    out_data.kill()
    rand_rd_en.kill()
    dut.rd_en.value = 0
    yield RisingEdge(dut.clk)
    # Compare
    if up_or_down == True:
        for i in range(len(output_data)):
            input_number = 0
            for k in range(0,c_OUTPUT_WIDTH,c_INPUT_WIDTH):
                input_number = input_number + (int(input_data[(i*int(c_OUTPUT_WIDTH/c_INPUT_WIDTH))+int(k/c_INPUT_WIDTH)]) << k)
            assert input_number == output_data[i], "Input data: %s differs from ouput data %s" % (hex(input_number),hex(output_data[i]))
            dut._log.info("Input data: %s = Ouput data %s" % (hex(input_number),hex(output_data[i])))
        dut._log.info("All data is correct!")
    else:
        for i in range(int(len(output_data)/int(c_INPUT_WIDTH/c_OUTPUT_WIDTH))):
            output_number = 0
            for k in range(0,c_INPUT_WIDTH,c_OUTPUT_WIDTH):
                output_number = output_number + (int(output_data[(i*int(c_INPUT_WIDTH/c_OUTPUT_WIDTH))+int(k/c_OUTPUT_WIDTH)]) << k)
            assert output_number == input_data[i], "Input data: %s differs from ouput data %s" % (hex(input_data[i]),hex(output_number))
            dut._log.info("Input data: %s = Ouput data %s" % (hex(input_data[i]),hex(output_number)))
        dut._log.info("All data is correct!")
#========================================================================================#
@cocotb.test(skip = False, stage = 3, timeout_time=1000, timeout_unit='us')
def run_test_flags(dut):
    # Setting up clocks
    clk_rd_100MHz = Clock(dut.clk, c_CLK_PERIOD_RD, units='ns')
    cocotb.start_soon(clk_rd_100MHz.start(start_high=False))


    # Setting init values
    yield RisingEdge(dut.clk)
    dut.rst.value = 1
    dut.wr_en.value = 0
    dut.wr_data.value = 0
    dut.rd_en.value = 0


    # Deactivate reset
    yield RisingEdge(dut.clk)
    dut.rst.value = 0

    # Gen data
    yield RisingEdge(dut.clk)
    output_data = []
    gen_data = cocotb.start_soon(write_data(dut,10000))
    yield RisingEdge(dut.full)
    assert dut.full.value == 1, "Error! Full must be 1"

    gen_data.kill()
    yield RisingEdge(dut.clk)
    dut.wr_en.value = 0
    dut.rd_en.value = 1

    store_data = cocotb.start_soon(read_data(dut,output_data))
    yield RisingEdge(dut.empty)
    assert dut.empty.value == 1, "Error! Empty must be 1"

    yield Timer(500, units='ns')
