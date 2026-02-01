library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity asymmetric_sync_fifo_up is
  generic (
    g_input_width  : natural := 32; -- input_width
    g_output_width : natural := 128; -- output_width
    g_depth        : natural := 4096 -- depth of the FIFO in number of output words
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
end asymmetric_sync_fifo_up;

architecture rtl of asymmetric_sync_fifo_up is

  -- Constants

  constant c_io_factor : integer := integer(floor(real(g_output_width)/real(g_input_width))); -- Input/Output width Ratio
  --
  type ram_type is array (0 to g_depth - 1) of std_logic_vector(g_input_width * c_io_factor - 1 downto 0);
  signal r_write_data : std_logic_vector(g_input_width * c_io_factor - 1 downto 0); -- Registered write data input
  signal ram : ram_type; -- RAM to store the data as blocks of output width
  attribute ram_style : string;
  attribute ram_style of ram : signal is "block";
  
  signal head         : integer range 0 to c_io_factor*g_depth - 1;
  signal tail         : integer range 0 to c_io_factor*g_depth - 1;
  signal rd_valid_i   : std_logic;
  signal empty_i      : std_logic;
  signal full_i       : std_logic;
  signal fill_count_i : integer range 0 to c_io_factor*g_depth - 1;

  signal r_rd_data,r_rd_data_fwft    : std_logic_vector(g_output_width - 1 downto 0) ;
  signal r_rd_valid, r_rd_data_fwft_valid   : std_logic   ;

  function next_index(
    index     : integer range 0 to c_io_factor*g_depth - 1;
    rd_en     : std_logic;
    empty     : std_logic) return integer is
  begin
    if rd_en = '1' and empty = '0' then
      if index = c_io_factor*g_depth - c_io_factor then
        return 0;
      else
        return index + c_io_factor;
      end if;
    end if;

    return index;
  end function;

  -- Increment and wrap
  procedure incr(signal index : inout integer range 0 to c_io_factor*g_depth - 1; constant increment : in integer) is
  begin
    if index = c_io_factor*g_depth - 1 then
      index <= 0;
    else
      index <= index + increment;
    end if;
  end procedure;

  -- Increment and wrap
  procedure incr_tail(signal index : inout integer range 0 to c_io_factor*g_depth - 1; constant increment : in integer) is
  begin
    if index = c_io_factor*g_depth - c_io_factor then
      index <= 0;
    else
      index <= index + increment;
    end if;
  end procedure;

begin

  -- Copy internal signals to output
  empty    <= empty_i;
  full     <= full_i;
  rd_data  <= r_rd_data when r_rd_data_fwft_valid = '0' else r_rd_data_fwft;
  rd_valid <= r_rd_valid;
  -- Set the flags
  empty_i <= '1' when fill_count_i < c_io_factor else '0';
  empty_next <= '1' when fill_count_i < c_io_factor * 2 else '0';
  full_i    <= '1' when fill_count_i >= c_io_factor*g_depth - 1 else '0';
  full_next <= '1' when fill_count_i >= c_io_factor*g_depth - 2 else '0';
  rd_valid_i <= '0' when fill_count_i < c_io_factor else '1';     -- strictly less so tvalid is asserted inmediatly after c_io_factor data have been written in ram 

  -- Update the head pointer in write
  PROC_HEAD : process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        head <= 0;
      else
        if wr_en = '1' and full_i = '0' then
          incr(head, 1);
        end if;
      end if;
    end if;
  end process;

  -- Update the tail pointer on read and pulse valid
  PROC_TAIL : process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        tail <= 0;
      else
        if rd_en = '1' and r_rd_valid = '1' then
          incr_tail(tail, c_io_factor);
        end if;
      end if;
    end if;
  end process;

  -- Write to the RAM
  WRITE_RAM : process (clk)
    variable v_quotient : integer:=0;
    variable i : integer:=0;
    variable v_write_data : std_logic_vector(g_input_width * c_io_factor - 1 downto 0);
  begin
    if rising_edge(clk) then
      if rst = '1' then
        r_write_data <= (others => '0');
      else
          v_quotient := head / c_io_factor;
          i := head - v_quotient * c_io_factor; -- get the lower bits to select the portion of data to write -- head mod c_io_factor
          v_write_data := r_write_data;
          v_write_data(g_input_width*(1+i)-1 downto g_input_width*i) := wr_data; -- insert new data in the correct portion
          r_write_data <= v_write_data; -- register the write data for next write
          ram(v_quotient) <= v_write_data;
      end if;
    end if;
  end process;

  -- Read from the RAM
  READ_RAM : process (clk)
    variable v_quotient : integer:=0;
  begin
    if rising_edge(clk) then
      if rst = '1' then
        r_rd_data <= (others => '0');
      else
        v_quotient := next_index(tail, rd_en, empty_i) / c_io_factor;
        r_rd_data <= ram(v_quotient);
      end if;
    end if;
  end process;

  -- FWFT behavior
  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        r_rd_data_fwft_valid <= '0';
        r_rd_data_fwft <= (others => '0');
      else
        if fill_count_i = c_io_factor and rd_en = '1' then -- output the registered write data when there is just one output word in the fifo to reduce latency (FWFT)
          r_rd_data_fwft <= r_write_data;
          r_rd_data_fwft_valid <= '1';
        else
          r_rd_data_fwft <= r_rd_data_fwft;
          r_rd_data_fwft_valid <= '0';
        end if;
      end if;
    end if;
  end process;

  -- TVALID handler
  TVALID_HANDLER : process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        r_rd_valid <= '0';
      else
        -- deassert tvalid/r_rd_valid if there is a complete output data written in ram and it is being read while the next output data is not completely written yet
        if r_rd_valid = '1' and rd_en = '1' and fill_count_i < 2*c_io_factor then
          r_rd_valid  <= '0';
        -- assert tvalid/r_rd_valid when r_valid_i = '1'. tvalid will be asserted when there are more than 2 output data completely written in ram or if there is just one but is no being currently read
        elsif rd_valid_i = '1' then                  
          r_rd_valid  <= '1';                                      
        else 
          r_rd_valid  <= r_rd_valid;     
        end if;  
      end if;
    end if;
  end process;

  -- Update the fill count
  PROC_COUNT : process (head, tail)
  begin
    if head < tail then
      fill_count_i <= head - tail + c_io_factor*g_depth;
    else
      fill_count_i <= head - tail;
    end if;
  end process;

end architecture;