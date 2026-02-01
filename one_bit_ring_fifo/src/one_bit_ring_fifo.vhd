library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use	ieee.math_real.all;

--! - **Name:** one_bit_ring_fifo
--!
--! - **Human Name:** One Bit Ring FIFO
--!
--! - **One-line Description:** One Bit Ring FIFO
--!
--! - **One-paragraph Description:** One Bit Ring FIFO. This module implements a one-bit wide ring FIFO buffer. It allows for the storage and retrieval of data in a circular manner, with a configurable depth and data width.
--!
--! - **Block diagram:** N/A
--!
--! ### Features
--! 
--! **Generic accepted values**
--!   - g_data_in_width: Width of the input data bus (default: 10)
--!   - g_data_out_width: Width of the output data bus (default: 32)
--!   - g_fifo_depth: Depth of the FIFO buffer (default: 64, power of 2 and higher than g_data_in_width and g_data_out_width)
--! 
--! **Latency**
--!   N/A
--!
--! **Running mode**
--!   - Sequential
--! 
--! **Corner cases**
--!   - Continuous writing data
--!   - Input or output data with same width than FIFO depth
--! 
--!  ### Future improvements
--!  - None

entity one_bit_ring_fifo is
  generic (
    g_data_in_width   : integer := 10;
    g_data_out_width  : integer := 32;
    g_fifo_depth      : integer := 64   -- power of 2 and higher than g_data_in_width and g_data_out_width
  );  
  port (  
    clk               : in  std_logic;
    rstn              : in  std_logic;
    data_in           : in  std_logic_vector(g_data_in_width-1 downto 0);
    data_valid_in     : in  std_logic;
    data_out          : out std_logic_vector(g_data_out_width-1 downto 0);
    data_out_valid    : out std_logic;
    data_out_ready    : in  std_logic;
    full_out          : out std_logic;
    empty_out         : out std_logic
  );
end entity;

architecture rtl of one_bit_ring_fifo is

  constant c_addr_width     : integer := integer(ceil(log2(real(g_fifo_depth))));

  type mem_type is array (g_fifo_depth-1 downto 0) of std_logic;
  signal mem                : mem_type;
  signal r0_unread_bits_ctr : integer range 0 to g_fifo_depth;

  -- read reconstruction signals
  signal r0_data_out        : std_logic_vector(g_data_out_width-1 downto 0);
  signal r0_data_out_valid  : std_logic;
  signal r0_overflow_fifo   : std_logic;

begin

  -- parallel write logic - writes all data_in bits in one clock cycle
  write_p : process(clk)   
    variable v_wr_ptr : unsigned(c_addr_width-1 downto 0); 
  begin
    if rising_edge(clk) then
      if rstn = '0' then
        v_wr_ptr   := (others => '0');
      else
        if data_valid_in = '1' then
          -- Write all bits of data_in in parallel
          for i in 0 to g_data_in_width-1 loop
            mem((to_integer(v_wr_ptr) + i) mod g_fifo_depth) <= data_in(i);
          end loop;
          -- Update write pointer
          v_wr_ptr   := v_wr_ptr + g_data_in_width;
        end if;
      end if;
    end if;
  end process;

  -- parallel read logic - reads all data_out_width bits in one clock cycle
  read_p : process(clk)
    variable v_rd_ptr     : unsigned(c_addr_width-1 downto 0);
  begin
    if rising_edge(clk) then
      if rstn = '0' then
        v_rd_ptr          := (others => '0');
        r0_data_out       <= (others => '0');
        r0_data_out_valid <= '0';
      else
        -- Update read pointer when theres is a handshake at the output
        if (r0_data_out_valid = '1' and data_out_ready = '1') then
          v_rd_ptr := v_rd_ptr + g_data_out_width;
        end if;
        -- Read all bits of data_out_width in parallel
        if r0_unread_bits_ctr >= g_data_out_width then
          if (r0_data_out_valid = '1' and data_out_ready = '1') then
            -- enough data for next read
            if r0_unread_bits_ctr - g_data_out_width >= g_data_out_width then
              r0_data_out_valid <= '1';
              for i in 0 to g_data_out_width-1 loop
                r0_data_out(i)  <= mem((to_integer(v_rd_ptr) + i) mod g_fifo_depth);
              end loop;
            -- not enough data for next read
            else
              r0_data_out_valid <= '0';
            end if;
          else           
            r0_data_out_valid <= '1';
            for i in 0 to g_data_out_width-1 loop
              r0_data_out(i)  <= mem((to_integer(v_rd_ptr) + i) mod g_fifo_depth);
            end loop;
          end if;
        else
          r0_data_out_valid <= '0';
        end if;
      end if;
    end if;
  end process;

  -- r0_unread_bits_ctr logic
  bits_ctr_p : process(clk)
  begin
    if rising_edge(clk) then
      if rstn = '0' then
        r0_unread_bits_ctr <= 0;
        r0_overflow_fifo   <= '0';
      else
        -- Simultaneous write and read
        if data_valid_in = '1' and (r0_data_out_valid = '1' and data_out_ready = '1') then

          if r0_overflow_fifo = '1' then 
            if g_data_in_width >= g_data_out_width then
              r0_unread_bits_ctr <= g_fifo_depth;
            else
              r0_unread_bits_ctr <= g_fifo_depth - g_data_out_width + g_data_in_width;
              r0_overflow_fifo   <= '0';
            end if;            
          elsif r0_unread_bits_ctr + g_data_in_width - g_data_out_width <= g_fifo_depth  then
            r0_unread_bits_ctr <= r0_unread_bits_ctr + g_data_in_width - g_data_out_width;
          else  
            r0_unread_bits_ctr <= g_fifo_depth;
            r0_overflow_fifo   <= '1';
          end if;

        -- Write only
        elsif data_valid_in = '1' then
          if r0_unread_bits_ctr + g_data_in_width <= g_fifo_depth then
            r0_unread_bits_ctr <= r0_unread_bits_ctr + g_data_in_width;
          else
            -- r0_unread_bits_ctr stays at maximum capacity
            r0_unread_bits_ctr <= g_fifo_depth;
            r0_overflow_fifo   <= '1';
          end if;

        -- Read only
        elsif (r0_data_out_valid = '1' and data_out_ready = '1') then
          r0_unread_bits_ctr <= r0_unread_bits_ctr - g_data_out_width;
          if r0_overflow_fifo = '1' then
            r0_overflow_fifo   <= '0';
          end if;
        end if;
      end if;
    end if;
  end process;

  -- empty_out flag
  empty_out <= '1' when r0_unread_bits_ctr = 0 else '0';
  -- full_out flag
  full_out  <= '1' when r0_unread_bits_ctr = g_fifo_depth else '0';
    
  -- output data
  data_out        <= r0_data_out;
  data_out_valid  <= r0_data_out_valid;

end architecture;