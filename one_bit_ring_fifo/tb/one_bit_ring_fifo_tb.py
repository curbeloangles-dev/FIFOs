import  numpy                       as np
import  random
import  os
import  cocotb
from    cocotb.triggers             import Timer, RisingEdge
from    cocotb.clock                import Clock
from    cocotb_coverage.coverage    import *

# addata_ing fw_libs to the system path
import os
import sys
# os.path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'node_modules/@quside/qvm/src'))
import test_utils
from    functional_coverage_tb  import FC

# Constants
# Clock Period
c_CLK_PERIOD = 10       # ns

# ==============================================================================
class TB(object):
    def __init__(self, dut):
        self.dut = dut       

        # Set clock
        clk_100MHz = Clock(dut.clk, c_CLK_PERIOD, units='ns')
        cocotb.start_soon(clk_100MHz.start(start_high=True))

        # Initial values
        self.dut.data_in.value = 0
        self.dut.data_valid_in.value = 0
        self.dut.data_out_ready.value = 1
        
        # Helper variables  
        self.ring_buffer_wr_index = 0
        self.r0_one_bit_ring_fifo_array = int(self.dut.g_fifo_depth) * [0]
        self.r1_one_bit_ring_fifo_array = int(self.dut.g_fifo_depth) * [0]
        self.ring_buffer_rd_index = 0
        self.ring_buffer_data_ctr = 0
        self.data_out_value_array = []
        self.expected_data_out_value_array = []

        # Functional coverage functions  
        self.fc = FC(dut)
        cocotb.start_soon(self.fc.run_empty_coverage())
        cocotb.start_soon(self.fc.run_full_coverage())

    # data_out_ready signal control
    async def control_data_out_ready(self, randomize = False):
        if randomize:
            length_pattern = 100
            random_pattern = [random.randint(0, 1) for _ in range(length_pattern)]
            while True:
                for i in range(length_pattern):
                    await RisingEdge(self.dut.clk)
                    self.dut.data_out_ready.value = random_pattern[i]
        else:
            self.dut.data_out_ready.value = 1

    # Update ring buffer golden model
    async def run_ring_buffer_golden_model(self):
        while True:
            await RisingEdge(self.dut.clk)
            if self.ring_buffer_data_ctr >= int(self.dut.g_data_out_width) and (self.dut.data_out_valid.value == 1 and self.dut.data_out_ready.value == 1):
                await self.read_ring_buffer_golden_model()        

            self.r1_one_bit_ring_fifo_array = self.r0_one_bit_ring_fifo_array.copy()

            if self.dut.data_valid_in.value == 1:
                data_to_write = int(self.dut.data_in.value)
                await self.write_ring_buffer_golden_model(data_to_write)

    # Read ring buffer golden model
    async def read_ring_buffer_golden_model(self):
        data_out_width = int(self.dut.g_data_out_width)
        # read data_out_width bits from the ring buffer starting from the current read index
        data_out_bin = ''.join(str(self.r1_one_bit_ring_fifo_array[(self.ring_buffer_rd_index + i) % int(self.dut.g_fifo_depth)]) for i in range(data_out_width))
        # convert binary string to integer
        data_out_value = int(data_out_bin[::-1], 2)  # Reverse back to original order for conversion
        self.expected_data_out_value_array.append(data_out_value)        
        # update the ring buffer index
        self.ring_buffer_rd_index = (self.ring_buffer_rd_index + data_out_width) % int(self.dut.g_fifo_depth)
        # update the ring buffer data counter (minimum is 0)
        self.ring_buffer_data_ctr = max(self.ring_buffer_data_ctr - data_out_width, 0)

    # Write ring buffer golden model
    async def write_ring_buffer_golden_model(self, data_in_value):
        data_in_width = int(self.dut.g_data_in_width)
        # convert data_in_value to binary string and pad with leading zeros
        data_in_bin = bin(data_in_value)[2:].zfill(data_in_width)[::-1]  # Reverse the string to match LSB to MSB order
        # update the ring buffer array bit by bit
        for i in range(data_in_width):
            self.r0_one_bit_ring_fifo_array[(self.ring_buffer_wr_index+i) % int(self.dut.g_fifo_depth)] = int(data_in_bin[i])
        # update the ring buffer index
        self.ring_buffer_wr_index = (self.ring_buffer_wr_index + data_in_width) % int(self.dut.g_fifo_depth)
        # update the ring buffer data counter (maximum is fifo_depth)
        self.ring_buffer_data_ctr = min(self.ring_buffer_data_ctr + data_in_width, int(self.dut.g_fifo_depth))

    # Read ring buffer
    async def read_dut(self):
        while True:
            await RisingEdge(self.dut.clk)
            if self.dut.data_out_valid.value == 1 and self.dut.data_out_ready.value == 1:
                self.data_out_value_array.append(int(self.dut.data_out.value))

    # Write ring buffer
    async def write_dut(self, total_writes, fixed_cycle_wait = False, cycles_between_writes = 5):        
        data_in_width = int(self.dut.g_data_in_width)
        for i in range(total_writes):
            # generate random data_in value (works for any data_in_width)
            random_bits = np.random.randint(0, 2, size=data_in_width, dtype=np.uint8)
            data_in_value = int(''.join(map(str, random_bits)), 2)
            # write data_in value
            await RisingEdge(self.dut.clk)
            self.dut.data_in.value = data_in_value
            self.dut.data_valid_in.value = 1
            # waiting time between writes
            if fixed_cycle_wait:
                # wait for a fixed number of cycles
                for j in range(cycles_between_writes):
                    await RisingEdge(self.dut.clk)
                    self.dut.data_valid_in.value = 0
            else:
                # wait random number of cycles between 0 and 20
                wait_cycles = np.random.randint(0, 20)
                for j in range(wait_cycles):
                    await RisingEdge(self.dut.clk)
                    self.dut.data_valid_in.value = 0
        # deactivate data_valid_in
        await RisingEdge(self.dut.clk)
        self.dut.data_valid_in.value = 0

    # Check data
    async def check_data(self, total_reads):
        for i in range(total_reads):
            assert self.expected_data_out_value_array[i] == self.data_out_value_array[i], "Data expected is %s and read is %s" % (hex(self.expected_data_out_value_array[i]), hex(self.data_out_value_array[i]))

# ==============================================================================
@cocotb.test(skip = (os.getenv("TEST_NAME") not in ["master_random_valid_slave_always_ready", "test_all"]), stage = 1)
async def master_random_valid_slave_always_ready(dut):

    # TB class
    tb = TB(dut)
    await test_utils.reset(dut.clk, dut.rstn)

    # Run ring buffer golden model
    cocotb.start_soon(tb.control_data_out_ready(randomize = True))
    cocotb.start_soon(tb.run_ring_buffer_golden_model())

    # Read all ring buffer outputs
    cocotb.start_soon(tb.read_dut())

    # Write data to ring buffer
    total_writes = 5 * int(dut.g_fifo_depth)
    await tb.write_dut(total_writes)

    # Wait some time
    await Timer(50*c_CLK_PERIOD, 'ns')

    # Check data
    total_reads = len(tb.expected_data_out_value_array)
    await tb.check_data(total_reads)

    raise cocotb.result.TestSuccess("Test passed")

# ==============================================================================
@cocotb.test(skip = (os.getenv("TEST_NAME") not in ["master_random_valid_slave_random_ready", "test_all"]), stage = 2)
async def master_random_valid_slave_random_ready(dut):

    # TB class
    tb = TB(dut)
    await test_utils.reset(dut.clk, dut.rstn)

    # Run ring buffer golden model
    cocotb.start_soon(tb.control_data_out_ready(randomize = False))
    cocotb.start_soon(tb.run_ring_buffer_golden_model())

    # Read all ring buffer outputs
    cocotb.start_soon(tb.read_dut())

    # Write data to ring buffer
    total_writes = 5 * int(dut.g_fifo_depth)
    await tb.write_dut(total_writes)

    # Wait some time
    await Timer(50*c_CLK_PERIOD, 'ns')

    # Check data
    total_reads = len(tb.expected_data_out_value_array)
    await tb.check_data(total_reads)

    raise cocotb.result.TestSuccess("Test passed")

# ==============================================================================
@cocotb.test(skip = (os.getenv("TEST_NAME") not in ["master_always_valid_slave_always_ready", "test_all"]), stage = 3)
async def master_always_valid_slave_always_ready(dut):

    # TB class
    tb = TB(dut)
    await test_utils.reset(dut.clk, dut.rstn)

    # Run ring buffer golden model
    cocotb.start_soon(tb.control_data_out_ready(randomize = False))
    cocotb.start_soon(tb.run_ring_buffer_golden_model())

    # Read all ring buffer outputs
    cocotb.start_soon(tb.read_dut())

    # Write data to ring buffer
    total_writes = 3 * int(dut.g_fifo_depth) 
    await tb.write_dut(total_writes, fixed_cycle_wait = True, cycles_between_writes = 0)

    # Wait some time
    await Timer(50*c_CLK_PERIOD, 'ns')

    # Check data
    total_reads = len(tb.expected_data_out_value_array)
    await tb.check_data(total_reads)

# ==============================================================================
@cocotb.test(skip = (os.getenv("TEST_NAME") not in ["master_always_valid_slave_random_ready", "test_all"]), stage = 4)
async def master_always_valid_slave_random_ready(dut):

    # TB class
    tb = TB(dut)
    await test_utils.reset(dut.clk, dut.rstn)

    # Run ring buffer golden model
    cocotb.start_soon(tb.control_data_out_ready(randomize = True))
    cocotb.start_soon(tb.run_ring_buffer_golden_model())

    # Read all ring buffer outputs
    cocotb.start_soon(tb.read_dut())

    # Write data to ring buffer
    total_writes = 3 * int(dut.g_fifo_depth) 
    await tb.write_dut(total_writes, fixed_cycle_wait = True, cycles_between_writes = 0)

    # Wait some time
    await Timer(50*c_CLK_PERIOD, 'ns')

    # Check data
    total_reads = len(tb.expected_data_out_value_array)
    await tb.check_data(total_reads)
    

# ==============================================================================
@cocotb.test(skip = (os.getenv("TEST_NAME") not in ["functional_coverage", "test_all"]), stage = 5)
async def functional_coverage(dut):
    # Sets the coverage yml file
    cg_group = coverage_db["one_bit_ring_fifo"]
    dut._log.info(f"Functional coverage percentage: {cg_group.cover_percentage:.2f}%")  # Log the coverage level of the whole covergroup

    coverage_file = os.path.join(
        os.getenv("RESULT_PATH", "../doc/"), "functional_coverage.yml"
    )
    coverage_db.export_to_yaml(filename=coverage_file)

    raise cocotb.result.TestSuccess("Test passed")