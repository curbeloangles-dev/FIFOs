import  cocotb
import logging
from    cocotb.triggers import Timer, RisingEdge, FallingEdge, First
from cocotb.result import TestFailure
from    cocotb.clock    import Clock
from cocotb_coverage.coverage import *
import random
import os


c_CLK_PERIOD = 10 #ns
input_data_length = 2000
RAM_DEPTH = 512
# ==============================================================================
# Functional coverage definition
# ==============================================================================

fill_count_all_counts = coverage_section(
    CoverPoint(
        "bram.fill_count.all_counts",
        vname="fill_count",
        bins=list(range(0, RAM_DEPTH-1)),
    )
)
empty_flag_set = coverage_section(
    CoverCheck(
        "bram.empty.empty_flag_set",
        f_fail=lambda empty: empty == 0,
        f_pass=lambda empty: empty == 1,
    )
)
empty_flag_clear = coverage_section(
    CoverCheck(
        "bram.empty.empty_flag_clear",
        f_fail=lambda empty: empty == 1,
        f_pass=lambda empty: empty == 0,
    )
)
empty_next_flag_set = coverage_section(
    CoverCheck(
        "bram.empty.empty_next_flag_set",
        f_fail=lambda empty_next: empty_next == 0,
        f_pass=lambda empty_next: empty_next == 1,
    )
)
empty_next_flag_clear = coverage_section(
    CoverCheck(
        "bram.empty.empty_next_flag_clear",
        f_fail=lambda empty_next: empty_next == 1,
        f_pass=lambda empty_next: empty_next == 0,
    )
)
full_flag_set = coverage_section(
    CoverCheck(
        "bram.full.full_flag_set",
        f_fail=lambda full: full == 0,
        f_pass=lambda full: full == 1,
    )
)
full_flag_clear = coverage_section(
    CoverCheck(
        "bram.full.full_flag_clear",
        f_fail=lambda full: full == 1,
        f_pass=lambda full: full == 0,
    )
)
full_next_flag_set = coverage_section(
    CoverCheck(
        "bram.full.full_next_flag_set",
        f_fail=lambda full_next: full_next == 0,
        f_pass=lambda full_next: full_next == 1,
    )
)
full_next_flag_clear = coverage_section(
    CoverCheck(
        "bram.full.full_next_flag_clear",
        f_fail=lambda full_next: full_next == 1,
        f_pass=lambda full_next: full_next == 0,
    )
)
def fail_callback():
    raise TestFailure("Signal not detected!")

coverage_db["bram.empty.empty_flag_set"].add_bins_callback(fail_callback, "FAIL")
coverage_db["bram.empty.empty_next_flag_set"].add_bins_callback(fail_callback, "FAIL")
coverage_db["bram.empty.empty_flag_clear"].add_bins_callback(fail_callback, "FAIL")
coverage_db["bram.empty.empty_next_flag_clear"].add_bins_callback(fail_callback, "FAIL")
coverage_db["bram.full.full_flag_set"].add_bins_callback(fail_callback, "FAIL")
coverage_db["bram.full.full_next_flag_set"].add_bins_callback(fail_callback, "FAIL")
coverage_db["bram.full.full_flag_clear"].add_bins_callback(fail_callback, "FAIL")
coverage_db["bram.full.full_next_flag_clear"].add_bins_callback(fail_callback, "FAIL")


# ==============================================================================
class TB(object):
    def __init__(self, dut):
        self.dut = dut

        logging.getLogger("cocotb.tb")

        # set inmediate value for reset
        self.dut.rst.setimmediatevalue(1)

        # Set clock
        clk_100MHz = Clock(dut.clk, c_CLK_PERIOD, units='ns')
        cocotb.start_soon(clk_100MHz.start(start_high=True))

        # Functional coverage
        cocotb.start_soon(self.fill_count_coverage())

    async def reset(self, aclk, aresetn, active_level=0):

        self.dut.rd_en.value = 0
        self.dut.wr_en.value = 0
        self.dut.wr_data.value = 0
        
        aresetn.value = active_level
        await RisingEdge(aclk)
        await RisingEdge(aclk)
        aresetn.value =  not active_level
        await RisingEdge(aclk)
        await RisingEdge(aclk)    

    # Write data function
    async def write_data(self, data, continuous_input = True):
        length = len(data)
        for i in range(length):
            if continuous_input == False:
                write_period = random.randint(1, 5)
                for x in range(write_period):
                    await RisingEdge(self.dut.clk)
            # Write data to FIFO
            while self.dut.full_next.value == 1:
                await RisingEdge(self.dut.clk)
            self.dut.wr_data.value = data[i]
            self.dut.wr_en.value = 1
            # Wait for rising edge of clk
            await RisingEdge(self.dut.clk)
            self.dut.wr_en.value = 0

    async def single_write_data(self, data):
        await RisingEdge(self.dut.clk)
        self.dut.wr_data.value = data
        self.dut.wr_en.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.wr_en.value = 0

    # Read data function
    async def read_data(self,data_length, continuous_read = True):
        data = []
        counter = 0
        while counter < data_length:
            while self.dut.empty.value == 1:
                await RisingEdge(self.dut.clk)
            if continuous_read == False:
                read_period = random.randint(1, 5)
                for i in range(read_period):
                    await RisingEdge(self.dut.clk)
            self.dut.rd_en.value = 1
            # Wait for rising edge of clk
            await RisingEdge(self.dut.clk)
            if self.dut.rd_valid.value == 1:
                # Append data to list
                data.append(int(str(self.dut.rd_data.value), 2))
                counter += 1
            self.dut.rd_en.value = 0
        return data

    async def single_read_data(self):
        await RisingEdge(self.dut.clk)
        self.dut.rd_en.value = 1
        await RisingEdge(self.dut.clk)
        if self.dut.rd_valid.value == 1:
            return int(str(self.dut.rd_data.value), 2)
        self.dut.rd_en.value = 0
        return None

    def test_data(self, data, output_data):
        for i in range(len(data)):
            # print("index: ", i, "data read:", output_data[i],"data expected:", data[i])
            assert data[i] == output_data[i]
        assert data == output_data

    async def fill_count_coverage(self):
        @fill_count_all_counts
        def sample(fill_count):
            pass
        while True:
            await RisingEdge(self.dut.clk)
            fill_count = self.dut.fill_count.value
            sample(fill_count)

    def assert_empty_flag(self):
        @empty_flag_set
        def sample(empty_flag):
            pass

        empty = self.dut.empty.value
        sample(empty)

    def assert_empty_clear(self):
        @empty_flag_clear
        def sample(empty_flag):
            pass

        empty = self.dut.empty.value
        sample(empty)

    def assert_empty_next_flag(self):
        @empty_next_flag_set
        def sample(empty_flag):
            pass

        empty = self.dut.empty_next.value
        sample(empty)

    def assert_empty_next_clear(self):
        @empty_next_flag_clear
        def sample(empty_flag):
            pass

        empty = self.dut.empty_next.value
        sample(empty)

    def assert_full_flag(self):
        @full_flag_set
        def sample(full_flag):
            pass
        
        full = self.dut.full.value
        sample(full)

    def assert_full_clear(self):
        @full_flag_clear
        def sample(full_flag):
            pass
        
        full = self.dut.full.value
        sample(full)

    def assert_full_next_flag(self):
        @full_next_flag_set
        def sample(full_flag):
            pass
        
        full = self.dut.full_next.value
        sample(full)

    def assert_full_next_clear(self):
        @full_next_flag_clear
        def sample(full_flag):
            pass
        
        full = self.dut.full_next.value
        sample(full)
#=========================================================================================
@cocotb.test(skip = False, stage = 1, timeout_time=0.2, timeout_unit='ms')
async def continuous_input(dut):
    tb = TB(dut)

    await tb.reset(dut.clk, dut.rst, active_level=1)

    # Generate a vector with random integers
    data = [random.randint(0, 2**32 - 1) for _ in range(input_data_length)]
    # Write data to FIFO
    cocotb.start_soon(tb.write_data(data,continuous_input = True) )
    # Read data from FIFO
    output_data = await tb.read_data(input_data_length,continuous_read= True)

    # compare two list: data and output_data
    tb.test_data(data, output_data)

    # Wait for 10 rising edges of clk
    await Timer(10*c_CLK_PERIOD, 'ns')

@cocotb.test(skip = False, stage = 2, timeout_time=0.2, timeout_unit='ms')
async def random_input(dut):
    tb = TB(dut)

    await tb.reset(dut.clk, dut.rst, active_level=1)

    # Generate a vector with random integers
    data = [random.randint(0, 2**32 - 1) for _ in range(input_data_length)]
    # Write data to FIFO
    cocotb.start_soon(tb.write_data(data,continuous_input = False) )
    # Read data from FIFO
    output_data = await tb.read_data(input_data_length, continuous_read= True)

    # compare two list: data and output_data
    tb.test_data(data, output_data)

    # Wait for 10 rising edges of clk
    await Timer(10*c_CLK_PERIOD, 'ns')

@cocotb.test(skip = False, stage = 3, timeout_time=0.2, timeout_unit='ms')
async def random_read(dut):
    tb = TB(dut)

    await tb.reset(dut.clk, dut.rst, active_level=1)

    # Generate a vector with random integers
    data = [random.randint(0, 2**32 - 1) for _ in range(input_data_length)]
    # Write data to FIFO
    cocotb.start_soon(tb.write_data(data,continuous_input = True) )
    # Read data from FIFO
    output_data = await tb.read_data(input_data_length, continuous_read= False)

    # compare two list: data and output_data
    tb.test_data(data, output_data)

    # Wait for 10 rising edges of clk
    await Timer(10*c_CLK_PERIOD, 'ns')

@cocotb.test(skip = False, stage = 4, timeout_time=0.2, timeout_unit='ms')
async def random_write_read(dut):
    tb = TB(dut)

    await tb.reset(dut.clk, dut.rst, active_level=1)

    # Generate a vector with random integers
    data = [random.randint(0, 2**32 - 1) for _ in range(input_data_length)]
    # Write data to FIFO
    cocotb.start_soon(tb.write_data(data,continuous_input = False))
    # Read data from FIFO
    output_data = await tb.read_data(input_data_length, continuous_read= False)

    # compare two list: data and output_data
    tb.test_data(data, output_data)

    # Wait for 10 rising edges of clk
    await Timer(10*c_CLK_PERIOD, 'ns')

@cocotb.test(skip = False, stage = 4, timeout_time=0.2, timeout_unit='ms')
async def fifo_full(dut):
    tb = TB(dut)

    await tb.reset(dut.clk, dut.rst, active_level=1)

    # Generate a vector with random integers
    data = [random.randint(0, 2**32 - 1) for _ in range(input_data_length)]
    # Write data to FIFO
    cocotb.start_soon(tb.write_data(data,continuous_input = True))

    # Read fifo full signal from FIFO
    while dut.full_next.value == 0:
        await RisingEdge(dut.clk)
    tb.assert_full_next_flag()
    tb.assert_full_clear()
    await RisingEdge(dut.clk)
    tb.assert_full_flag()

    # Force write when full
    await tb.single_write_data(0x1)

    await RisingEdge(dut.clk)
    tb.assert_full_flag()
    tb.assert_empty_clear()

    # Read two data to clear full flags
    await tb.single_read_data()
    await RisingEdge(dut.clk)
    tb.assert_full_clear()
    await tb.single_read_data()
    await RisingEdge(dut.clk)
    tb.assert_full_next_clear()

    # Wait for 10 rising edges of clk
    await Timer(10*c_CLK_PERIOD, 'ns')

@cocotb.test(skip = False, stage = 4, timeout_time=0.2, timeout_unit='ms')
async def fifo_empty(dut):
    tb = TB(dut)

    await tb.reset(dut.clk, dut.rst, active_level=1)

    tb.assert_empty_flag()
    tb.assert_empty_next_flag()
    # Generate a vector with random integers
    data = [random.randint(0, 2**32 - 1) for _ in range(input_data_length)]
    # Write data to FIFO
    cocotb.start_soon(tb.write_data(data,continuous_input = True))
    # Read all data from FIFO
    cocotb.start_soon(tb.read_data(input_data_length, continuous_read= True))
    await Timer(10*c_CLK_PERIOD, 'ns')
    # Read fifo empty signal from FIFO
    while dut.empty_next.value == 0:
        await RisingEdge(dut.clk)
    tb.assert_empty_next_flag()
    tb.assert_empty_clear()
    await RisingEdge(dut.clk)
    tb.assert_empty_flag()

    # Write two data to force clear empty flags
    await tb.single_write_data(0x1)
    await RisingEdge(dut.clk)
    tb.assert_empty_clear()
    await tb.single_write_data(0x2)
    await RisingEdge(dut.clk)
    tb.assert_empty_next_clear()

    # Wait for 10 rising edges of clk
    await Timer(10*c_CLK_PERIOD, 'ns')

    # Sets the coverage yml file
    cg_group = coverage_db["bram"]
    dut._log.info(f"Functional coverage percentage: {cg_group.cover_percentage:.2f}%")  # Log the coverage level of the whole covergroup

    coverage_file = os.path.join(
        os.getenv("RESULT_PATH", "../../../../doc/"), "functional_coverage.yml"
    )
    coverage_db.export_to_yaml(filename=coverage_file)
