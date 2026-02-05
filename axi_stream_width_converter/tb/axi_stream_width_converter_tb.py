# Libraries
# =============================================================================
import cocotb
import logging
import itertools
import random
from cocotb.triggers    import RisingEdge, ClockCycles
from cocotb.clock       import Clock
from cocotbext.axi      import AxiStreamFrame
from cocotbext.axi      import AxiStreamBus
from cocotbext.axi      import AxiStreamSource
from cocotbext.axi      import AxiStreamSink

# Constants
#==============================================================================
CLK_PERIOD      = 10     # ns

# Testbench class
#==============================================================================
class Frame:
    def __init__(self, tdata, tkeep, tid, tuser, tdest):
        self.tdata = tdata
        self.tkeep = tkeep
        self.tid = tid
        self.tuser = tuser
        self.tdest = tdest
        
class TB(object):
    def __init__(self, dut):
        self.dut = dut

        log = logging.getLogger("cocotb.tb")
        #Set clock
        axis_clk_100MHz = Clock(self.dut.axis_aclk, CLK_PERIOD, units='ns')
        cocotb.start_soon(axis_clk_100MHz.start(start_high=False))
    
        self.axis_source = AxiStreamSource(AxiStreamBus.from_prefix(self.dut, "s_axis"), self.dut.axis_aclk, self.dut.axis_aresetn, reset_active_level=False)
        self.axis_sink = AxiStreamSink(AxiStreamBus.from_prefix(self.dut, "m_axis"), self.dut.axis_aclk, self.dut.axis_aresetn, reset_active_level=False)

    async def reset(self):
        self.dut.axis_aresetn.setimmediatevalue(1)
        await RisingEdge(self.dut.axis_aclk)
        self.dut.axis_aresetn.value = 0
        await RisingEdge(self.dut.axis_aclk)
        self.dut.axis_aresetn.value = 1
        await RisingEdge(self.dut.axis_aclk)

    def insert_idle_list(self, cycle_list = None):
        if type(cycle_list) is not list:
            print ("Cycle List needs to be a list")
        self.axis_source.set_pause_generator(itertools.cycle(cycle_list))

    def insert_backpressure_list(self, cycle_list = None):
        if type(cycle_list) is not list:
            print ("Cycle List needs to be a list")
        self.axis_sink.set_pause_generator(itertools.cycle(cycle_list))

    def compare(self, a, b):
        assert len(a) == len(b)
        self.dut._log.info("Input len %d" % (len(a)))
        self.dut._log.info("Expected input len %d" % (len(b)))
        # print(a)
        # print(b)
        for i in range(len(a)):
            assert a[i] == b[i]

    def strip_invalid_bytes(self, tdata, tkeep):
        """Remove bytes from tdata where tkeep=0"""
        return [d for d, k in zip(tdata, tkeep) if k == 1]


#================================================================================= 
@cocotb.coroutine
async def receive_data(tb, capture_size):
    """
    Read AXI-Stream frames from sink and return a list of dictionaries
    with full fields (tdata, tkeep, tid, tuser, tdest).
    """
    output = []
    #Reading
    for _ in range(capture_size):
        rframe = await tb.axis_sink.recv(compact=False) # Disable compact mode to get full fields
        # These values are lists of repeated values (see cocotb-axi documentation), so we take the first element
        frame_info = Frame(
            tdata = rframe.tdata,
            tkeep = rframe.tkeep if hasattr(rframe, 'tkeep') else None,     # Check if tkeep exists
            tid = [rframe.tid[0]] if hasattr(rframe, 'tid') else [0],       # Check if tid exists, default to [0]
            tuser = [rframe.tuser[0]] if hasattr(rframe, 'tuser') else [0], # Check if tuser exists, default to [0]
            tdest = [rframe.tdest[0]] if hasattr(rframe, 'tdest') else [0], # Check if tdest exists, default to [0]
        )

        output.append(frame_info)
        await RisingEdge(tb.dut.axis_aclk)

    return output      
# ==============================================================================
@cocotb.coroutine
async def send_data(tb, data_list):
    """
    Send AXI-Stream frames defined inside object data_list (class Frame)
    AXI parameters (tdata, tkeep, tid, tuser, tdest) are sent if defined inside data_list
    """
    for data in data_list:
        frame = AxiStreamFrame(data.tdata)

        # Assign only when the field is defined (not None)
        if hasattr(data, "tkeep") and data.tkeep is not None:
            frame.tkeep = data.tkeep

        if hasattr(data, "tid") and data.tid is not None:
            frame.tid = data.tid

        if hasattr(data, "tuser") and data.tuser is not None:
            frame.tuser = data.tuser

        if hasattr(data, "tdest") and data.tdest is not None:
            frame.tdest = data.tdest

        await tb.axis_source.send(frame)

#=============================================================================
@cocotb.test(skip = False, stage = 1)
async def test_continuos(dut):
    tb = TB(dut)
    await tb.reset()
    
    num_transfers_total = 10
    num_frames = 10
    data_width = int(dut.g_input_width)//8
    data_tid_width = int(dut.g_AXIS_TID_WIDTH)
    data_tdest_width = int(dut.g_AXIS_TDEST_WIDTH)
    data_tuser_width = int(dut.g_AXIS_TUSER_WIDTH)

    for num_transfers in range(1,num_transfers_total):
        ##################### W/R AXI-STREAM ############################## 
        # Expected output
        stream_frames = [] # List to store AxiStreamFrame objects
        for i in range(num_frames):
            frame_data = []
            frame_tkeep = []
            for _ in range(num_transfers):
                tdata_chunk = [random.randint(0, 255) for _ in range(data_width)]
                frame_data.extend(tdata_chunk)
                tkeep_chunk = [random.randint(0,1) for _ in range(data_width)]
                frame_tkeep.extend(tkeep_chunk)
                
            frame_tid = [random.randint(0, 2**data_tid_width - 1)]
            frame_tuser = [random.randint(0, 2**data_tuser_width - 1)]
            frame_tdest = [random.randint(0, 2**data_tdest_width - 1)]
            stream_frame = AxiStreamFrame(frame_data,
                                          tkeep=frame_tkeep, 
                                          tdest=frame_tdest,
                                          tid=frame_tid,
                                          tuser=frame_tuser)
            stream_frames.append(stream_frame)

        cocotb.start_soon(send_data(tb, stream_frames))
        recv_task = cocotb.start_soon(receive_data(tb, num_frames))
        dut_output = await recv_task.join()

        for i in range(num_frames):
            tdata_expected = tb.strip_invalid_bytes(stream_frames[i].tdata, stream_frames[i].tkeep)
            tdata_received = tb.strip_invalid_bytes(dut_output[i].tdata, dut_output[i].tkeep)
            tdest_expected = tb.strip_invalid_bytes(stream_frames[i].tdest, stream_frames[i].tkeep)
            tdest_received = tb.strip_invalid_bytes(dut_output[i].tdest, dut_output[i].tkeep)
            tid_expected = tb.strip_invalid_bytes(stream_frames[i].tid, stream_frames[i].tkeep)
            tid_received = tb.strip_invalid_bytes(dut_output[i].tid, dut_output[i].tkeep)
            tuser_expected = tb.strip_invalid_bytes(stream_frames[i].tuser, stream_frames[i].tkeep)
            tuser_received = tb.strip_invalid_bytes(dut_output[i].tuser, dut_output[i].tkeep)
            tdest_expected = tb.strip_invalid_bytes(stream_frames[i].tdest, stream_frames[i].tkeep)
            tdest_received = tb.strip_invalid_bytes(dut_output[i].tdest, dut_output[i].tkeep)
            tb.compare(tdata_received, tdata_expected)
            tb.compare(tdest_received, tdest_expected)
            tb.compare(tid_received, tid_expected)
            tb.compare(tuser_received, tuser_expected)
            
#==============================================================================
@cocotb.test(skip = False, stage = 2)
async def test_back_preassure(dut):
    tb = TB(dut)
    await tb.reset()
    # Adjust sink back pressure here. 
    # This list is repeated during the current simulation
    num_clocks_down = 50
    num_clocks_up = 3
    num_clocks = 100
    t_ready_clocks = []
    for z in range(num_clocks_up):
        t_ready_clocks.append(0)
    for k in range(num_clocks_down):
        t_ready_clocks.append(1)
    # for z in range(num_clocks):
    #     t_ready_clocks.append(random.choice(range(2)))
    tb.insert_backpressure_list(t_ready_clocks)

    num_transfers_total = 10
    num_frames = 10
    data_width = int(dut.g_input_width)//8
    data_tid_width = int(dut.g_AXIS_TID_WIDTH)
    data_tdest_width = int(dut.g_AXIS_TDEST_WIDTH)
    data_tuser_width = int(dut.g_AXIS_TUSER_WIDTH)

    for num_transfers in range(1,num_transfers_total):
        ##################### W/R AXI-STREAM ############################## 
        # Expected output
        stream_frames = [] # List to store AxiStreamFrame objects
        for i in range(num_frames):
            frame_data = []
            frame_tkeep = []
            for _ in range(num_transfers):
                tdata_chunk = [random.randint(0, 255) for _ in range(data_width)]
                frame_data.extend(tdata_chunk)
                tkeep_chunk = [random.randint(0,1) for _ in range(data_width)]
                frame_tkeep.extend(tkeep_chunk)
                
            frame_tid = [random.randint(0, 2**data_tid_width - 1)]
            frame_tuser = [random.randint(0, 2**data_tuser_width - 1)]
            frame_tdest = [random.randint(0, 2**data_tdest_width - 1)]
            stream_frame = AxiStreamFrame(frame_data,
                                          tkeep=frame_tkeep, 
                                          tdest=frame_tdest,
                                          tid=frame_tid,
                                          tuser=frame_tuser)
            stream_frames.append(stream_frame)

        cocotb.start_soon(send_data(tb, stream_frames))
        recv_task = cocotb.start_soon(receive_data(tb, num_frames))
        dut_output = await recv_task.join()

        for i in range(num_frames):
            tdata_expected = tb.strip_invalid_bytes(stream_frames[i].tdata, stream_frames[i].tkeep)
            tdata_received = tb.strip_invalid_bytes(dut_output[i].tdata, dut_output[i].tkeep)
            tdest_expected = tb.strip_invalid_bytes(stream_frames[i].tdest, stream_frames[i].tkeep)
            tdest_received = tb.strip_invalid_bytes(dut_output[i].tdest, dut_output[i].tkeep)
            tid_expected = tb.strip_invalid_bytes(stream_frames[i].tid, stream_frames[i].tkeep)
            tid_received = tb.strip_invalid_bytes(dut_output[i].tid, dut_output[i].tkeep)
            tuser_expected = tb.strip_invalid_bytes(stream_frames[i].tuser, stream_frames[i].tkeep)
            tuser_received = tb.strip_invalid_bytes(dut_output[i].tuser, dut_output[i].tkeep)
            tdest_expected = tb.strip_invalid_bytes(stream_frames[i].tdest, stream_frames[i].tkeep)
            tdest_received = tb.strip_invalid_bytes(dut_output[i].tdest, dut_output[i].tkeep)
            tb.compare(tdata_received, tdata_expected)
            tb.compare(tdest_received, tdest_expected)
            tb.compare(tid_received, tid_expected)
            tb.compare(tuser_received, tuser_expected)

#==============================================================================
@cocotb.test(skip = False, stage = 3)
async def test_starvation(dut):
    tb = TB(dut)
    await tb.reset()
    # Adjust source starvation here. 
    # This list is repeated during the current simulation
    num_clocks = 100
    t_valid_clocks = []
    for z in range(num_clocks):
        t_valid_clocks.append(random.choice(range(2)))

    tb.insert_idle_list(t_valid_clocks)

    num_transfers_total = 10
    num_frames = 10
    data_width = int(dut.g_input_width)//8
    data_tid_width = int(dut.g_AXIS_TID_WIDTH)
    data_tdest_width = int(dut.g_AXIS_TDEST_WIDTH)
    data_tuser_width = int(dut.g_AXIS_TUSER_WIDTH)

    for num_transfers in range(1,num_transfers_total):
        ##################### W/R AXI-STREAM ############################## 
        # Expected output
        stream_frames = [] # List to store AxiStreamFrame objects
        for i in range(num_frames):
            frame_data = []
            frame_tkeep = []
            for _ in range(num_transfers):
                tdata_chunk = [random.randint(0, 255) for _ in range(data_width)]
                frame_data.extend(tdata_chunk)
                tkeep_chunk = [random.randint(0,1) for _ in range(data_width)]
                frame_tkeep.extend(tkeep_chunk)
                
            frame_tid = [random.randint(0, 2**data_tid_width - 1)]
            frame_tuser = [random.randint(0, 2**data_tuser_width - 1)]
            frame_tdest = [random.randint(0, 2**data_tdest_width - 1)]
            stream_frame = AxiStreamFrame(frame_data,
                                          tkeep=frame_tkeep, 
                                          tdest=frame_tdest,
                                          tid=frame_tid,
                                          tuser=frame_tuser)
            stream_frames.append(stream_frame)

        cocotb.start_soon(send_data(tb, stream_frames))
        recv_task = cocotb.start_soon(receive_data(tb, num_frames))
        dut_output = await recv_task.join()

        for i in range(num_frames):
            tdata_expected = tb.strip_invalid_bytes(stream_frames[i].tdata, stream_frames[i].tkeep)
            tdata_received = tb.strip_invalid_bytes(dut_output[i].tdata, dut_output[i].tkeep)
            tdest_expected = tb.strip_invalid_bytes(stream_frames[i].tdest, stream_frames[i].tkeep)
            tdest_received = tb.strip_invalid_bytes(dut_output[i].tdest, dut_output[i].tkeep)
            tid_expected = tb.strip_invalid_bytes(stream_frames[i].tid, stream_frames[i].tkeep)
            tid_received = tb.strip_invalid_bytes(dut_output[i].tid, dut_output[i].tkeep)
            tuser_expected = tb.strip_invalid_bytes(stream_frames[i].tuser, stream_frames[i].tkeep)
            tuser_received = tb.strip_invalid_bytes(dut_output[i].tuser, dut_output[i].tkeep)
            tdest_expected = tb.strip_invalid_bytes(stream_frames[i].tdest, stream_frames[i].tkeep)
            tdest_received = tb.strip_invalid_bytes(dut_output[i].tdest, dut_output[i].tkeep)
            tb.compare(tdata_received, tdata_expected)
            tb.compare(tdest_received, tdest_expected)
            tb.compare(tid_received, tid_expected)
            tb.compare(tuser_received, tuser_expected)

#==============================================================================
@cocotb.test(skip = False, stage = 4)
async def test_Tready_Tvalid_random(dut):
    tb = TB(dut)
    await tb.reset()
    # Adjust source starvation here. 
    # This list is repeated during the current simulation
    num_clocks = 100
    t_valid_clocks = []
    t_ready_clocks = []
    for z in range(num_clocks):
        t_valid_clocks.append(random.choice(range(2)))
        t_ready_clocks.append(random.choice(range(2)))
    
    tb.insert_backpressure_list(t_ready_clocks)
    tb.insert_idle_list(t_valid_clocks)

    num_transfers_total = 10
    num_frames = 10
    data_width = int(dut.g_input_width)//8
    data_tid_width = int(dut.g_AXIS_TID_WIDTH)
    data_tdest_width = int(dut.g_AXIS_TDEST_WIDTH)
    data_tuser_width = int(dut.g_AXIS_TUSER_WIDTH)

    for num_transfers in range(1,num_transfers_total):
        ##################### W/R AXI-STREAM ############################## 
        # Expected output
        stream_frames = [] # List to store AxiStreamFrame objects
        for i in range(num_frames):
            frame_data = []
            frame_tkeep = []
            for _ in range(num_transfers):
                tdata_chunk = [random.randint(0, 255) for _ in range(data_width)]
                frame_data.extend(tdata_chunk)
                tkeep_chunk = [random.randint(0,1) for _ in range(data_width)]
                frame_tkeep.extend(tkeep_chunk)
                
            frame_tid = [random.randint(0, 2**data_tid_width - 1)]
            frame_tuser = [random.randint(0, 2**data_tuser_width - 1)]
            frame_tdest = [random.randint(0, 2**data_tdest_width - 1)]
            stream_frame = AxiStreamFrame(frame_data,
                                          tkeep=frame_tkeep, 
                                          tdest=frame_tdest,
                                          tid=frame_tid,
                                          tuser=frame_tuser)
            stream_frames.append(stream_frame)

        cocotb.start_soon(send_data(tb, stream_frames))
        recv_task = cocotb.start_soon(receive_data(tb, num_frames))
        dut_output = await recv_task.join()

        for i in range(num_frames):
            tdata_expected = tb.strip_invalid_bytes(stream_frames[i].tdata, stream_frames[i].tkeep)
            tdata_received = tb.strip_invalid_bytes(dut_output[i].tdata, dut_output[i].tkeep)
            tdest_expected = tb.strip_invalid_bytes(stream_frames[i].tdest, stream_frames[i].tkeep)
            tdest_received = tb.strip_invalid_bytes(dut_output[i].tdest, dut_output[i].tkeep)
            tid_expected = tb.strip_invalid_bytes(stream_frames[i].tid, stream_frames[i].tkeep)
            tid_received = tb.strip_invalid_bytes(dut_output[i].tid, dut_output[i].tkeep)
            tuser_expected = tb.strip_invalid_bytes(stream_frames[i].tuser, stream_frames[i].tkeep)
            tuser_received = tb.strip_invalid_bytes(dut_output[i].tuser, dut_output[i].tkeep)
            tdest_expected = tb.strip_invalid_bytes(stream_frames[i].tdest, stream_frames[i].tkeep)
            tdest_received = tb.strip_invalid_bytes(dut_output[i].tdest, dut_output[i].tkeep)
            tb.compare(tdata_received, tdata_expected)
            tb.compare(tdest_received, tdest_expected)
            tb.compare(tid_received, tid_expected)
            tb.compare(tuser_received, tuser_expected)

#==============================================================================
@cocotb.test(skip = False, stage = 5)
async def fifo_wr_when_full(dut):
    tb = TB(dut)
    await tb.reset()

    fifo_up = False
    if int(dut.g_input_width) > int(dut.g_output_width):
        c_io_factor = int(dut.g_input_width) / int(dut.g_output_width)
    else:
        c_io_factor = int(dut.g_output_width) / int(dut.g_input_width)
        fifo_up = True

    # Force m_axis_tready = 0 to avoid data to be read from FIFO
    fifo_size = int(dut.g_DEPTH) if fifo_up == False else int(dut.g_DEPTH) * c_io_factor
    num_clocks = int(fifo_size)
    t_ready_clocks = []
    for z in range(num_clocks):
        t_ready_clocks.append(1)
    tb.insert_backpressure_list(t_ready_clocks)

    data_width = int(dut.g_output_width) // 8 if fifo_up else int(dut.g_input_width) // 8

    #################### W/R AXI-STREAM ############################## 
    frame_data = []
    frame_tkeep = []
    for _ in range(int(fifo_size)):
        tdata_chunk = [random.randint(0, 255) for _ in range(data_width)]
        frame_data.extend(tdata_chunk)
        tkeep_chunk = [1] * data_width
        frame_tkeep.extend(tkeep_chunk)

    stream_frame = AxiStreamFrame(frame_data, tkeep=frame_tkeep)
    send_task = cocotb.start_soon(send_data(tb, [stream_frame]))

    await ClockCycles(tb.dut.axis_aclk, 2*num_clocks)
    
    # Check that fifo is full and no more data is accepted
    assert dut.s_axis_tready.value == 0
    await send_task

#==============================================================================
@cocotb.test(skip = False, stage = 6)
async def fifo_rd_when_empty(dut):
    tb = TB(dut)
    await tb.reset()

    for i in range(10000):
        # To be sure that is not accepted more data into fifo
        assert dut.m_axis_tvalid.value == 0
        await RisingEdge(dut.axis_aclk)