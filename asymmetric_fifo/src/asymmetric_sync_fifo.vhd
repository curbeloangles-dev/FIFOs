library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;


--! - **Name:** asymmetric_sync_fifo  
--!
--! - **Human Name:** Asymmetric Synchronous FIFO
--!
--! - **One-line Description:**   Asymmetric Synchronous FIFO
--!
--! - **One-paragraph Description:**  Asymmetric synchronous FIFO allows to transfer data from one input size to a different output size. The FIFO can be configured to be up or down. The depth of the FIFO is deffined by g_depth.
--! Where g_depth is the depth in number of output words of the bigger width (input or output).
--! the relation between input and output width can be any integer ratio (2:1, 4:1, 1:2, 1:4, 3:1, 1:3, etc). If the ratio is not a number of base 2 the FIFO will use some extra logic to handle the non power of 2 ratio. 
--!
--! - **Block diagram:** 
--!
--!
--! ### Features
--! 
--! **Generic accepted values**
--!    - g_input_width:  2 - 256
--!    - g_output_width: 2 - 256
--!    - g_depth:        >= 2 * max(g_OUTPUT_WIDTH, g_INPUT_WIDTH)
--! 
--! **Latency**
--!   - Clock cycles: TBD
--!
--! **Running mode**
--!   - Pipelined: Yes
--! 
--! **Corner cases**
--!   - Fifo is empty: before reset, the fifo fill count is zero, all data has been read.
--!   - Fifo is full: when the fifo fill count is equal to the fifo depth - 1.
--!   - Fifo is almost full: when the fifo fill count is equal or more than the fifo depth - 2.
--!   - Fifo is almost empty: when the fifo fill count is equal to 1 or less.
--!   - Fifo is full and write data: when the fifo is full and the write enable is set, the fifo is not written.
--!   - Fifo is empty and read data: when the fifo is empty and the read enable is set, the fifo is not read.
--!   - Signal behavior when heap and tail counters overflows
--! 
--!  ### Future improvements
--!  - Add generic to select the memory read and write latency.

entity asymmetric_sync_fifo is
  generic (
    g_input_width  : natural := 32; --! input_width
    g_output_width : natural := 128; --! output_width
    g_depth        : natural := 128 --! depth of the FIFO in number of max(input,output) words
  );
  port (
    clk : in std_logic;
    rst : in std_logic;

    -- Write port
    wr_en   : in std_logic;
    wr_data : in std_logic_vector(g_input_width - 1 downto 0);

    -- Read port
    rd_en    : in std_logic;
    rd_valid : out std_logic;
    rd_data  : out std_logic_vector(g_output_width - 1 downto 0);

    -- Flags
    empty      : out std_logic;
    empty_next : out std_logic;
    full       : out std_logic;
    full_next  : out std_logic
  );
end asymmetric_sync_fifo;

architecture rtl of asymmetric_sync_fifo is

  -- Function to determine which FIFO to use. True = Up, False = Down
  function up_or_down(
    input_width  : natural;
    output_width : natural) return boolean is
  begin
    if input_width <= output_width then
      return True;
    else
      return False;
    end if;
  end function;

  -- Constants
  constant c_up_or_down : boolean := up_or_down(g_input_width, g_output_width);

begin

  UP_FIFO : if c_up_or_down = True generate
    asymmetric_sync_fifo_up_inst : entity work.asymmetric_sync_fifo_up
      generic map(
        g_input_width  => g_input_width,
        g_output_width => g_output_width,
        g_depth        => g_depth
      )
      port map(
        clk        => clk,
        rst        => rst,
        wr_en      => wr_en,
        wr_data    => wr_data,
        rd_en      => rd_en,
        rd_valid   => rd_valid,
        rd_data    => rd_data,
        empty      => empty,
        empty_next => empty_next,
        full       => full,
        full_next  => full_next
      );
  end generate;

  DOWN_FIFO : if c_up_or_down = False generate
    asymmetric_sync_fifo_down_inst : entity work.asymmetric_sync_fifo_down
      generic map(
        g_input_width  => g_input_width,
        g_output_width => g_output_width,
        g_depth        => g_depth
      )
      port map(
        clk        => clk,
        rst        => rst,
        wr_en      => wr_en,
        wr_data    => wr_data,
        rd_en      => rd_en,
        rd_valid   => rd_valid,
        rd_data    => rd_data,
        empty      => empty,
        empty_next => empty_next,
        full       => full,
        full_next  => full_next
      );
  end generate;
end architecture;