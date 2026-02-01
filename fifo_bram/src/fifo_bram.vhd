library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

--! - **Name:** fifo_bram  
--!
--! - **Human Name:** FIFO BRAM
--!
--! - **One-line Description:**   Fifo module working with BRAM memory
--!
--! - **One-paragraph Description:**  Fifo module that woks with BRAM memory. It has a write and read port, and flags to indicate if the fifo is empty or full.
--!    When wr_en and full is clear, the data is written to the fifo. When rd_en and empty is clear, the data is read from the fifo.
--!    When full is set, wr_en must be 0. And when empty is set, rd_en must be 0.
--!    The rd_valid output is set when there is data to read and rd_en is set. The fill_count output indicates the number of elements in the fifo. 
--!    The fifo has a depth of 511 and a width of 32 bits. 
--!    The fifo is pipelined and the latency is one clock cycle to write data and cero clock cycles to read data.

--!
--! - **Block diagram:** 
--! ![FIFO_BRAM](FIFO_BRAM.png)

--! ### Features
--! 
--! **Generic accepted values**
--!    - RAM_WIDTH: 32 
--!    - RAM_DEPTH: 512
--! 
--! **Latency**
--!   - Clock cycles: One cycle to write data and cero cycles to read data.
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

entity fifo_bram is
  generic (
    RAM_WIDTH : natural := 32;  --! Word width
    RAM_DEPTH : natural := 512  --! Depth of the FIFO + 1
  );
  port (
    clk : in std_logic; --! input clock
    rst : in std_logic; --! rest signal high active

    -- Write port
    wr_en   : in std_logic; --! write enable
    wr_data : in std_logic_vector(RAM_WIDTH - 1 downto 0); --! data input

    -- Read port
    rd_en    : in std_logic;  --! read enable
    rd_valid : out std_logic; --! read valid. There is data to read
    rd_data  : out std_logic_vector(RAM_WIDTH - 1 downto 0); --! data output

    -- Flags
    empty      : out std_logic; --! fifo is empty
    empty_next : out std_logic; --! fifo will be empty next cycle
    full       : out std_logic; --! fifo is full
    full_next  : out std_logic; --! fifo will be full next cycle

    -- The number of elements in the FIFO
    fill_count : out integer range RAM_DEPTH - 1 downto 0 --! Number of elements in the FIFO
  );
end fifo_bram;

architecture rtl of fifo_bram is

  type ram_type is array (0 to RAM_DEPTH - 1) of std_logic_vector(wr_data'range);
  signal ram : ram_type;

  signal head : integer range 0 to RAM_DEPTH - 1;
  signal tail : integer range 0 to RAM_DEPTH - 1;

  signal empty_i      : std_logic;
  signal full_i       : std_logic;
  signal fill_count_i : integer range 0 to RAM_DEPTH - 1;

  -- Increment and wrap
  procedure incr(signal index : inout integer range 0 to RAM_DEPTH - 1) is
  begin
    if index = RAM_DEPTH - 1 then
      index <= 0;
    else
      index <= index + 1;
    end if;
  end procedure;

begin

  empty      <= empty_i;
  full       <= full_i;
  fill_count <= fill_count_i;

  -- Set the flags
  empty_i    <= '1' when fill_count_i = 0 else '0';
  empty_next <= '1' when fill_count_i <= 1 else '0';
  full_i     <= '1' when fill_count_i >= RAM_DEPTH - 1 else '0';
  full_next  <= '1' when fill_count_i >= RAM_DEPTH - 2 else '0';
  rd_valid   <= '1' when fill_count_i > 0 else '0';

  -- Update the head pointer in write
  PROC_HEAD : process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        head <= 0;
      else

        if wr_en = '1' and full_i = '0' then
          incr(head);
        end if;

      end if;
    end if;
  end process;

  -- Update the tail pointer on read and pulse valid
  PROC_TAIL : process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        tail     <= 0;
      else
        if rd_en = '1' and empty_i = '0' then
          incr(tail);
        end if;

      end if;
    end if;
  end process;

  -- Write to and read from the RAM
  PROC_RAM : process (clk)
  begin
    if rising_edge(clk) then
      ram(head) <= wr_data;
    end if;
  end process;
  rd_data   <= ram(tail);

  -- Update the fill count
  PROC_COUNT : process (head, tail)
  begin
    if head < tail then
      fill_count_i <= head - tail + RAM_DEPTH;
    else
      fill_count_i <= head - tail;
    end if;
  end process;

end architecture;