import  collections
from    cocotb.triggers             import RisingEdge
from    cocotb.result               import TestFailure
from    cocotb_coverage.coverage    import *


class FC(object):
  def __init__(self, dut):
    self.dut = dut

    ############################################################
    #################### Auxiliar Functions ####################
    ############################################################
    #------------------ Transformations (xf) ------------------#
    #------------------ Relations (rel) ------------------#      

    ######################################################
    #################### Cover Points ####################
    ######################################################
    #------------------ Inputs ------------------#
    #------------------ Outputs ------------------#
    """
      empty_out coverage
    """
    self.empty_coverage = coverage_section(
      CoverPoint(
        name="one_bit_ring_fifo.empty",
        vname="empty",
        bins=[0, 1],
        bins_labels=["no_empty", "empty"],
      )
    )
    """
      full_out coverage
    """
    self.full_coverage = coverage_section(
      CoverPoint(
        name="one_bit_ring_fifo.full",
        vname="full",
        bins=[0, 1],
        bins_labels=["no_full", "full"],
      )
    )
    #------------------ FSMs ------------------#

    ######################################################
    #################### Cover Checks ####################
    ######################################################
    #------------------ Inputs ------------------#
    #------------------ Outputs ------------------#
    #------------------ FSMs ------------------#

  ######################################################
  ################## Cover Functions ###################
  ######################################################
  #------------------ Helpers ------------------#
  async def wait_for_resetn(self):
    await RisingEdge(self.dut.clk)
    while self.dut.rstn.value != 1:
      await RisingEdge(self.dut.clk)

  #------------------ Inputs ------------------#
  #------------------ Outputs ------------------#
  """
    Coverage of empty_out_out
  """
  async def run_empty_coverage(self):
    # call coverage point
    @self.empty_coverage
    def sample(empty):
      pass

    # start surveillance
    await self.wait_for_resetn()
    while True:
      await RisingEdge(self.dut.clk)
      empty = self.dut.empty_out.value
      sample(empty)
  """
    Coverage of full_out
  """
  async def run_full_coverage(self):
    # call coverage point
    @self.full_coverage
    def sample(full):
      pass

    # start surveillance
    await self.wait_for_resetn()
    while True:
      await RisingEdge(self.dut.clk)
      full = self.dut.full_out.value
      sample(full)
  #------------------ FSMs ------------------#