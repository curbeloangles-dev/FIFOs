library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;


--! - **Name:** axi_stream_fifo
--!
--! - **Human Name:** Asynchronous Axi stream FIFO
--!
--! - **One-line Description:**   Asynchronous Axi stream FIFO
--!
--! - **One-paragraph Description:**  Asynchronous FIFO is inside this wrapper. The wrapper convert the FIFO interfaces into AXI-Stream interfaces.
--!
--! - **Block diagram:** 
--!
--!
--! ### Features
--! 
--! **Generic accepted values**
--!    - g_DATA_WIDTH:  Multiple of 8 bits
--!    - g_DEPTH: 32 - x 
--!    - g_AXIS_TUSER_WIDTH  : Any accepted value, but standard recommends to be no more than 8
--!    - g_AXIS_TID_WIDTH    : Any accepted value, but standard recommends be an integer multiple of g_DATA_WIDTH/8
--!    - g_AXIS_TDEST_WIDTH  : Any accepted value, but standard recommends to be no more than 8

--! 
--! **Latency**
--!   - Clock cycles: TBD
--!
--! **Running mode**
--!   - Pipelined: Yes
--! 
--! **Corner cases**
--!   - Just one data is written and read.
--!   - Fifo is full tready is low.
--!   - Fifo is empty tready is high.
--!   - Fifo is full and write data: when the fifo is full and the tvalid is set, the fifo is not written. terady is low.
--!   - Fifo is empty and read data: when the fifo is empty and the tready is set, the fifo is not read. tvalid is low.
--!   
--!  ### Future improvements
--! - Axis registers to improve timing and routing.

entity axi_stream_fifo is
  generic (
    g_DATA_WIDTH        : integer := 32;  --! Data width
    g_DEPTH             : integer := 256; --! FIFO depth
    g_AXIS_TUSER_WIDTH  : integer := 8; --! AXI-Stream tuser width
    g_AXIS_TID_WIDTH    : integer := 8; --! AXI-Stream tid width
    g_AXIS_TDEST_WIDTH  : integer := 8 --! AXI-Stream tdest width
  );
  port (
    -- common
    s_axis_aclk    : in std_logic; --! AXI-Stream clock
    s_axis_aresetn : in std_logic; --! AXI-Stream resetn. Resets write side (S_AXIS). This means write pointer will be back at index 0
    m_axis_aclk    : in std_logic; --! AXI-Stream clock
    m_axis_aresetn : in std_logic; --! AXI-Stream resetn. Resets read side (M_AXIS). This means read pointer will be back at index 0
    -- AXI-Stream Slave Interface 
    s_axis_tdata  : in std_logic_vector(g_DATA_WIDTH - 1 downto 0); --! AXI-Stream Slave tdata signal
    s_axis_tvalid : in std_logic;                                    --! AXI-Stream Slave tvalid signal
    s_axis_tready : out std_logic;                                   --! AXI-Stream Slave tready signal
    s_axis_tkeep  : in std_logic_vector((g_DATA_WIDTH / 8) - 1 downto 0)       := (others => '1');
    s_axis_tuser  : in std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0)        := (others => '0');
    s_axis_tid    : in std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0)          := (others => '0');
    s_axis_tdest  : in std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0)        := (others => '0');
    s_axis_tlast  : in std_logic                                                := '1'; 
    -- AXI-Stream Master Interface 
    m_axis_tdata  : out std_logic_vector(g_DATA_WIDTH - 1 downto 0); --! AXI-Stream Master tdata signal
    m_axis_tvalid : out std_logic;                                     --! AXI-Stream Master tvalid signal
    m_axis_tready : in std_logic;                                       --! AXI-Stream Master tready signal
    m_axis_tkeep  : out std_logic_vector((g_DATA_WIDTH / 8) - 1 downto 0);
    m_axis_tuser  : out std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0);
    m_axis_tid    : out std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0);
    m_axis_tdest  : out std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0);
    m_axis_tlast  : out std_logic
  
    );
end;

architecture rtl of axi_stream_fifo is
  -- constants
  constant c_ADDR_WIDTH     : natural := integer(ceil(log2(real(g_DEPTH)))); -- Asynchronous FIFO Depth = 16 words
  constant c_data_width_mod : integer := (g_DATA_WIDTH mod 8);
  -- signals
  signal s_s_axis_areset    : std_logic;
  signal s_m_axis_areset    : std_logic;
  signal s_async_full       : std_logic;

  signal s_s_axis_tlast     : std_logic_vector(0 downto 0);
  signal s_m_axis_tlast     : std_logic_vector(0 downto 0);

begin

  assert c_data_width_mod = 0 report "ERROR - End of simulation: g_DATA_WIDTH must be multiple of 8!" severity failure ;

  -- Reset 
  s_s_axis_areset <= not(s_axis_aresetn);
  s_m_axis_areset <= not(m_axis_aresetn);

  -- Async FIFO
  async_fifo_tdata : entity work.async_fifo
    generic map(
      g_DATA_WIDTH => g_DATA_WIDTH,
      g_ADDR_WIDTH => c_ADDR_WIDTH
    )
    port map(
      i_CLK_WR     => s_axis_aclk,
      i_INC_WR     => s_axis_tvalid,
      i_RST_WR     => s_s_axis_areset,
      i_DAT_WR     => s_axis_tdata,
      o_FULL_FLAG  => s_async_full,
      i_CLK_RD     => m_axis_aclk,
      i_INC_RD     => m_axis_tready,
      i_RST_RD     => s_m_axis_areset,
      o_DAT_RD     => m_axis_tdata,
      o_DAT_VALID  => m_axis_tvalid,
      o_EMPTY_FLAG => open
    );

  async_fifo_tkeep : entity work.async_fifo
    generic map(
      g_DATA_WIDTH => g_DATA_WIDTH/8,
      g_ADDR_WIDTH => c_ADDR_WIDTH
    )
    port map(
      i_CLK_WR     => s_axis_aclk,
      i_INC_WR     => s_axis_tvalid,
      i_RST_WR     => s_s_axis_areset,
      i_DAT_WR     => s_axis_tkeep,
      o_FULL_FLAG  => open,
      i_CLK_RD     => m_axis_aclk,
      i_INC_RD     => m_axis_tready,
      i_RST_RD     => s_m_axis_areset,
      o_DAT_RD     => m_axis_tkeep,
      o_DAT_VALID  => open,
      o_EMPTY_FLAG => open
    );

  async_fifo_tlast : entity work.async_fifo
    generic map(
      g_DATA_WIDTH => 1,
      g_ADDR_WIDTH => c_ADDR_WIDTH
    )
    port map(
      i_CLK_WR     => s_axis_aclk,
      i_INC_WR     => s_axis_tvalid,
      i_RST_WR     => s_s_axis_areset,
      i_DAT_WR     => s_s_axis_tlast,
      o_FULL_FLAG  => open,
      i_CLK_RD     => m_axis_aclk,
      i_INC_RD     => m_axis_tready,
      i_RST_RD     => s_m_axis_areset,
      o_DAT_RD     => s_m_axis_tlast,
      o_DAT_VALID  => open,
      o_EMPTY_FLAG => open
    );
  s_s_axis_tlast(0) <= s_axis_tlast;
  m_axis_tlast      <= s_m_axis_tlast(0);

  async_fifo_tdest : entity work.async_fifo
    generic map(
      g_DATA_WIDTH => g_AXIS_TDEST_WIDTH,
      g_ADDR_WIDTH => c_ADDR_WIDTH
    )
    port map(
      i_CLK_WR     => s_axis_aclk,
      i_INC_WR     => s_axis_tvalid,
      i_RST_WR     => s_s_axis_areset,
      i_DAT_WR     => s_axis_tdest,
      o_FULL_FLAG  => open,
      i_CLK_RD     => m_axis_aclk,
      i_INC_RD     => m_axis_tready,
      i_RST_RD     => s_m_axis_areset,
      o_DAT_RD     => m_axis_tdest,
      o_DAT_VALID  => open,
      o_EMPTY_FLAG => open
    );

  async_fifo_tuser : entity work.async_fifo
    generic map(
      g_DATA_WIDTH => g_AXIS_TUSER_WIDTH,
      g_ADDR_WIDTH => c_ADDR_WIDTH
    )
    port map(
      i_CLK_WR     => s_axis_aclk,
      i_INC_WR     => s_axis_tvalid,
      i_RST_WR     => s_s_axis_areset,
      i_DAT_WR     => s_axis_tuser,
      o_FULL_FLAG  => open,
      i_CLK_RD     => m_axis_aclk,
      i_INC_RD     => m_axis_tready,
      i_RST_RD     => s_m_axis_areset,
      o_DAT_RD     => m_axis_tuser,
      o_DAT_VALID  => open,
      o_EMPTY_FLAG => open
    );

  async_fifo_tid : entity work.async_fifo
    generic map(
      g_DATA_WIDTH => g_AXIS_TID_WIDTH,
      g_ADDR_WIDTH => c_ADDR_WIDTH
    )
    port map(
      i_CLK_WR     => s_axis_aclk,
      i_INC_WR     => s_axis_tvalid,
      i_RST_WR     => s_s_axis_areset,
      i_DAT_WR     => s_axis_tid,
      o_FULL_FLAG  => open,
      i_CLK_RD     => m_axis_aclk,
      i_INC_RD     => m_axis_tready,
      i_RST_RD     => s_m_axis_areset,
      o_DAT_RD     => m_axis_tid,
      o_DAT_VALID  => open,
      o_EMPTY_FLAG => open
    );

  -- Assign tready output
  s_axis_tready <= not(s_async_full) and s_axis_aresetn;

end architecture;