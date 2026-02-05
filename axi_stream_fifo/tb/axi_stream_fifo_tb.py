import  cocotb
from    cocotb.triggers    import Timer, RisingEdge, Join
from    cocotb.clock       import Clock
from    random             import randint  

# ==============================================================================
async def write_data(dut,number):
    i = 0
    global input_data
    global in_init_time, in_last_time
    input_data = []
    init = 0
    
    await RisingEdge(dut.s_axis_aclk)
    done = 0
    while done == 0:
        random_num = randint(0,2**int(dut.g_DATA_WIDTH)-1)
        dut.s_axis_tdata.value = random_num
        dut.s_axis_tvalid.value = randint(0,1)
        await RisingEdge(dut.s_axis_aclk)
        if  dut.s_axis_tready.value == 1 and dut.s_axis_tvalid.value == 1: 
            input_data.append(random_num)
            i = i+1
            if init == 0:
                in_init_time = cocotb.utils.get_sim_time('ns')
                init = 1
            in_last_time = cocotb.utils.get_sim_time('ns')
        if i == number:
            done = 1
    dut.s_axis_tdata.value = 0
    dut.s_axis_tvalid.value = 0
    return 0  
# ==============================================================================
async def random_tready(dut):
    while True:
        await RisingEdge(dut.m_axis_aclk)
        dut.m_axis_tready.value = randint(0,1)

# ==============================================================================
async def read_data(dut):
    global output_data
    output_data = []
    global init_time, last_time
    init = 0
    await RisingEdge(dut.m_axis_aclk)
    while True:
        if dut.m_axis_tvalid.value == 1 and dut.m_axis_tready.value == 1:
            output_data.append(dut.m_axis_tdata.value)
            if init == 0:
                init_time = cocotb.utils.get_sim_time('ns')
                init = 1
            last_time = cocotb.utils.get_sim_time('ns')
        await RisingEdge(dut.m_axis_aclk)
        
# ==============================================================================
@cocotb.test(skip = False, stage = 1)
def axi_stream_fifo_slow_to_fast_tb(dut):
    # Constants
    c_CLK_PERIOD_WR = 10 #ns
    c_CLK_PERIOD_RD = 5 #ns

    # Setting up clocks
    s_axis_clk = Clock(dut.s_axis_aclk, c_CLK_PERIOD_WR, units='ns')
    cocotb.start_soon(s_axis_clk.start(start_high=True))
    m_axis_clk = Clock(dut.m_axis_aclk, c_CLK_PERIOD_RD, units='ns')
    cocotb.start_soon(m_axis_clk.start(start_high=True))
    # Setting init values
    dut.s_axis_aresetn.value = 0 
    dut.m_axis_aresetn.value = 0   
    dut.s_axis_tdata.value = 0  
    dut.s_axis_tvalid.value = 0  
    dut.m_axis_tready.value = 0 

    # Resetn
    yield Timer(2*c_CLK_PERIOD_WR, units='ns')
    yield RisingEdge(dut.s_axis_aclk)
    dut.s_axis_aresetn.value = 1  
    dut.m_axis_aresetn.value = 1 
     
    yield Timer(2*c_CLK_PERIOD_WR, units='ns')
    in_data = cocotb.start_soon(write_data(dut,10))
    out_data = cocotb.start_soon(read_data(dut))
    yield Timer(50*c_CLK_PERIOD_WR, units='ns')
    rand_tready = cocotb.start_soon(random_tready(dut))

    yield Join(in_data)

    yield Timer(10, units='us')
    out_data.kill()
    rand_tready.kill()
    dut.m_axis_tready.value = 0

    for i in range(len(output_data)):
        assert (input_data[i]) == output_data[i], "Input data: %s differs from ouput data %s" % (hex((input_data[i])),hex(output_data[i]))
        dut._log.info("Input data: %s = Ouput data %s" % (hex((input_data[i])),hex(output_data[i])))
    dut._log.info("All data is correct!")

    # Reset procedure
    yield RisingEdge(dut.s_axis_aclk)
    dut.s_axis_aresetn.value = 0 
    yield RisingEdge(dut.m_axis_aclk)
    dut.m_axis_aresetn.value = 0  

    yield Timer(c_CLK_PERIOD_WR, units='ns')

    yield RisingEdge(dut.s_axis_aclk)
    dut.s_axis_aresetn.value = 1
    yield RisingEdge(dut.m_axis_aclk)
    dut.m_axis_aresetn.value = 1

    yield Timer(2*c_CLK_PERIOD_WR, units='ns')
    in_data = cocotb.start_soon(write_data(dut,5000))
    out_data = cocotb.start_soon(read_data(dut))
    yield Timer(50*c_CLK_PERIOD_WR, units='ns')
    rand_tready = cocotb.start_soon(random_tready(dut))

    yield Join(in_data)

    yield Timer(10, units='us')
    out_data.kill()
    rand_tready.kill()
    dut.m_axis_tready.value = 0

    for i in range(len(output_data)):
        assert (input_data[i]) == output_data[i], "Input data: %s differs from ouput data %s" % (hex((input_data[i])),hex(output_data[i]))
        dut._log.info("Input data: %s = Ouput data %s" % (hex((input_data[i])),hex(output_data[i])))
    dut._log.info("All data is correct!")

    # Check input Throughput
    in_throughput = (len(input_data)*int(dut.g_DATA_WIDTH))/((in_last_time-in_init_time)*10**-9)/10**6
    cocotb.log.info("Input Throughput: %f Mbps" % (in_throughput))

    # Check output Throughput
    out_throughput = (len(output_data)*int(dut.g_DATA_WIDTH))/((last_time-init_time)*10**-9)/10**6
    cocotb.log.info("Output Throughput: %f Mbps" % (out_throughput))
# ==============================================================================
@cocotb.test(skip = False, stage = 1)
def axi_stream_fifo_fast_to_slow_tb(dut):
    # Constants
    c_CLK_PERIOD_WR = 2.5 #ns
    c_CLK_PERIOD_RD = 5 #ns

    # Setting up clocks
    s_axis_clk = Clock(dut.s_axis_aclk, c_CLK_PERIOD_WR, units='ns')
    cocotb.start_soon(s_axis_clk.start(start_high=True))
    m_axis_clk = Clock(dut.m_axis_aclk, c_CLK_PERIOD_RD, units='ns')
    cocotb.start_soon(m_axis_clk.start(start_high=True))
    # Setting init values
    dut.s_axis_aresetn.value = 0 
    dut.m_axis_aresetn.value = 0   
    dut.s_axis_tdata.value = 0  
    dut.s_axis_tvalid.value = 0  
    dut.m_axis_tready.value = 0 

    # Resetn
    yield Timer(2*c_CLK_PERIOD_WR, units='ns')
    yield RisingEdge(dut.s_axis_aclk)
    dut.s_axis_aresetn.value = 1  
    dut.m_axis_aresetn.value = 1 
     
    yield Timer(2*c_CLK_PERIOD_WR, units='ns')
    in_data = cocotb.start_soon(write_data(dut,10))
    out_data = cocotb.start_soon(read_data(dut))
    yield Timer(50*c_CLK_PERIOD_WR, units='ns')
    rand_tready = cocotb.start_soon(random_tready(dut))

    yield Join(in_data)

    yield Timer(10, units='us')
    out_data.kill()
    rand_tready.kill()
    dut.m_axis_tready.value = 0

    for i in range(len(output_data)):
        assert (input_data[i]) == output_data[i], "Input data: %s differs from ouput data %s" % (hex((input_data[i])),hex(output_data[i]))
        dut._log.info("Input data: %s = Ouput data %s" % (hex((input_data[i])),hex(output_data[i])))
    dut._log.info("All data is correct!")

    # Reset procedure
    yield RisingEdge(dut.s_axis_aclk)
    dut.s_axis_aresetn.value = 0 
    yield RisingEdge(dut.m_axis_aclk)
    dut.m_axis_aresetn.value = 0  

    yield Timer(c_CLK_PERIOD_WR, units='ns')

    yield RisingEdge(dut.s_axis_aclk)
    dut.s_axis_aresetn.value = 1
    yield RisingEdge(dut.m_axis_aclk)
    dut.m_axis_aresetn.value = 1

    yield Timer(2*c_CLK_PERIOD_WR, units='ns')
    in_data = cocotb.start_soon(write_data(dut,5000))
    out_data = cocotb.start_soon(read_data(dut))
    yield Timer(50*c_CLK_PERIOD_WR, units='ns')
    rand_tready = cocotb.start_soon(random_tready(dut))

    yield Join(in_data)

    yield Timer(10, units='us')
    out_data.kill()
    rand_tready.kill()
    dut.m_axis_tready.value = 0

    for i in range(len(output_data)):
        assert (input_data[i]) == output_data[i], "Input data: %s differs from ouput data %s" % (hex((input_data[i])),hex(output_data[i]))
        dut._log.info("Input data: %s = Ouput data %s" % (hex((input_data[i])),hex(output_data[i])))
    dut._log.info("All data is correct!")

    # Check input Throughput
    in_throughput = (len(input_data)*int(dut.g_DATA_WIDTH))/((in_last_time-in_init_time)*10**-9)/10**6
    cocotb.log.info("Input Throughput: %f Mbps" % (in_throughput))

    # Check output Throughput
    out_throughput = (len(output_data)*int(dut.g_DATA_WIDTH))/((last_time-init_time)*10**-9)/10**6
    cocotb.log.info("Output Throughput: %f Mbps" % (out_throughput))