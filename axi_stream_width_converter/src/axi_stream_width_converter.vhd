library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;


--! - **Name:** axi_stream_width_converter
--!
--! - **Human Name:** Axistream Width Converter
--!
--! - **One-line Description:**   Convert data width from one AXI-Stream interface to another with different data width.
--!
--! - **One-paragraph Description:**  Convert data width from one AXI-Stream interface to another with different data width. The module has a FIFO to store the data when the input data width is greater than the output data width. The FIFO is implemented using the asymmetric_sync_fifo module. The module has a generic to set the input and output data width and the FIFO depth.
--!
--! - **Block diagram:** 
--!
--!
--! ### Features
--! 
--! **Generic accepted values**
--!    - g_INPUT_WIDTH:  Multiple of 8 bits
--!    - g_OUTPUT_WIDTH: Multiple of 8 bits
--!    - g_DEPTH:        >= 2 * max(g_OUTPUT_WIDTH, g_INPUT_WIDTH)/min(g_OUTPUT_WIDTH, g_INPUT_WIDTH)
--!    - g_AXIS_TUSER_WIDTH  : Any accepted value, but standard recommends to be no more than 8
--!    - g_AXIS_TID_WIDTH    : Any accepted value, but standard recommends be an integer multiple of g_INPUT_WIDTH/8
--!    - g_AXIS_TDEST_WIDTH  : Any accepted value, but standard recommends to be no more than 8
--! 
--! **Latency**
--!   - Clock cycles: TBD
--!
--! **Running mode**
--!   - Pipelined: Yes
--! 
--! **Corner cases**
--!  - The is just one data stored in the fifo. The data should came out in the next clock cycle.
--!  - The amount of input data is not enough to fill an output data. The output data should be empty.
--! 
--!  ### Future improvements
--!  - Add generic to put registers in the output and input interfaces to improve timing.
--!  - Add generic to select the memory implementation.

entity axi_stream_width_converter is
  generic (
    g_INPUT_WIDTH       : integer := 8; --! Input data width
    g_OUTPUT_WIDTH      : integer := 32;  --! Output data width
    g_DEPTH             : integer := 64;  --! FIFO depth in input words when input width < output width, in output words otherwise
    g_AXIS_TUSER_WIDTH  : integer := 8; --! AXI-Stream tuser width
    g_AXIS_TID_WIDTH    : integer := 8; --! AXI-Stream tid width
    g_AXIS_TDEST_WIDTH  : integer := 8 --! AXI-Stream tdest width
  );
  port (
    -- common
    axis_aclk    : in std_logic; --! AXI-Stream clock
    axis_aresetn : in std_logic; --! AXI-Stream resetn. This means FIFO will be empty 
    -- AXI-Stream Slave Interface 
    s_axis_tdata  : in std_logic_vector(g_INPUT_WIDTH - 1 downto 0); --! AXI-Stream Slave tdata signal
    s_axis_tvalid : in std_logic;                                    --! AXI-Stream Slave tvalid signal
    s_axis_tready : out std_logic;                                   --! AXI-Stream Slave tready signal
    s_axis_tkeep  : in std_logic_vector((g_INPUT_WIDTH / 8) - 1 downto 0)       := (others => '1');
    s_axis_tuser  : in std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0)        := (others => '0');
    s_axis_tid    : in std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0)          := (others => '0');
    s_axis_tdest  : in std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0)        := (others => '0');
    s_axis_tlast  : in std_logic                                                := '1'; 
    -- AXI-Stream Master Interface 
    m_axis_tdata  : out std_logic_vector(g_OUTPUT_WIDTH - 1 downto 0); --! AXI-Stream Master tdata signal
    m_axis_tvalid : out std_logic;                                     --! AXI-Stream Master tvalid signal
    m_axis_tready : in std_logic;                                       --! AXI-Stream Master tready signal
    m_axis_tkeep  : out std_logic_vector((g_OUTPUT_WIDTH / 8) - 1 downto 0);
    m_axis_tuser  : out std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0);
    m_axis_tid    : out std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0);
    m_axis_tdest  : out std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0);
    m_axis_tlast  : out std_logic
  
    );
end;

architecture rtl of axi_stream_width_converter is

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
  
  -- CONSTANTS
  constant c_subwords_down          : integer := g_INPUT_WIDTH / g_OUTPUT_WIDTH;
  constant c_subwords_up            : integer := g_OUTPUT_WIDTH / g_INPUT_WIDTH;
  constant c_tkeep_width            : integer := g_INPUT_WIDTH / 8;
  constant c_up_or_down             : boolean := up_or_down(g_input_width, g_output_width);
  constant c_input_width_mod        : integer := (g_INPUT_WIDTH mod 8);
  constant c_output_width_mod       : integer := (g_OUTPUT_WIDTH mod 8);

  -- COMMON SIGNALS
  signal s_axis_areset              : std_logic;
  signal s_tkeep_fifo_full          : std_logic;
  signal s_tdata_fifo_full          : std_logic;
  signal s_tkeep_fifo_rd_valid      : std_logic;
  signal s_tlast_fifo_rd_valid      : std_logic;

  -- PROCESS DOWN SIGNALS 
  signal s_tlast_expanded           : std_logic_vector(c_subwords_down-1 downto 0);
  signal s_tlast_fifo_down_rd_data  : std_logic_vector(0 downto 0);
  signal s_tdest_expanded : std_logic_vector((c_subwords_down * g_AXIS_TDEST_WIDTH) - 1 downto 0);
  signal s_tid_expanded   : std_logic_vector((c_subwords_down * g_AXIS_TID_WIDTH) - 1 downto 0);
  signal s_tuser_expanded : std_logic_vector((c_subwords_down * g_AXIS_TUSER_WIDTH) - 1 downto 0);


  -- PROCESS UP SIGNALS
  signal s_subword_count            : integer range 0 to c_subwords_up := 0;
  type t_store_state iS (RECEIVE_WORD, STORE_WORD);
  signal s_store_state              : t_store_state;

  -- FIFO UP SIGNALS
  signal r_fifo_tdata_wr_en         : std_logic;
  signal s_fifo_tdata_data          : std_logic_vector(g_INPUT_WIDTH - 1 downto 0);
  signal r_fifo_tkeep_wr_en         : std_logic;
  signal r_fifo_tdest_wr_en         : std_logic;
  signal s_fifo_tdest_data          : std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0);
  signal r_fifo_tid_wr_en           : std_logic;
  signal s_fifo_tid_data            : std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0);
  signal r_fifo_tuser_wr_en         : std_logic;
  signal s_fifo_tuser_data          : std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0);
  signal s_fifo_tkeep_data          : std_logic_vector((g_INPUT_WIDTH/8)-1 downto 0);
  signal r_fifo_tlast_wr_en         : std_logic;
  signal s_fifo_tlast_data          : std_logic_vector(0 downto 0);
  signal s_tdata_fifo_rd_valid      : std_logic;
  signal s_tlast_fifo_up_data       : std_logic_vector(c_subwords_up - 1 downto 0);
  signal s_tready                   : std_logic;
  signal s_fifo_tdata_wr_en         : std_logic;
  signal s_fifo_tkeep_wr_en         : std_logic;
  signal s_fifo_tlast_wr_en         : std_logic;
  signal s_fifo_tdest_wr_en         : std_logic;
  signal s_fifo_tid_wr_en           : std_logic;
  signal s_fifo_tuser_wr_en         : std_logic;

  signal s_tdest_fifo_rd_valid      : std_logic;
  signal s_tid_fifo_rd_valid        : std_logic;
  signal s_tuser_fifo_rd_valid      : std_logic;

  signal s_tdest_fifo_up_data       : std_logic_vector((c_subwords_up * g_AXIS_TDEST_WIDTH) - 1 downto 0);
  signal s_tid_fifo_up_data         : std_logic_vector((c_subwords_up * g_AXIS_TID_WIDTH) - 1 downto 0);
  signal s_tuser_fifo_up_data       : std_logic_vector((c_subwords_up * g_AXIS_TUSER_WIDTH) - 1 downto 0);

begin

  assert (c_input_width_mod = 0 and c_output_width_mod = 0) report "ERROR: g_INPUT_WIDTH and g_OUTPUT_WIDTH must be multiple of 8!" severity FAILURE;


  -- Reset
  s_axis_areset <= not(axis_aresetn);
---------------------------------------------------------------------------------
-------------------------------- FIFO DOWNSTREAM --------------------------------
---------------------------------------------------------------------------------
  --! Downstream conversion: This block is enabled when input width > output width.
  --! It uses asymmetric FIFOs to split a wide input word into multiple narrower output words.
  --! Each AXI-Stream channel (TDATA, TKEEP, TLAST, TDEST, TID, TUSER) has its own FIFO.
  --! The expanded signals replicate the input sideband signals for each output subword, to keep all the FIFOs alligned
  gen_down_conv: if (c_up_or_down = False and c_input_width_mod = 0 and c_output_width_mod = 0)  generate

    fifo_tdata : entity work.asymmetric_sync_fifo
      generic map(
        g_input_width   => g_INPUT_WIDTH,
        g_output_width  => g_OUTPUT_WIDTH,
        g_depth         => g_DEPTH
      )
      port map(
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_axis_tvalid,
        wr_data         => s_axis_tdata,
        rd_en           => m_axis_tready,
        rd_valid        => s_tdata_fifo_rd_valid,
        rd_data         => m_axis_tdata,
        empty           => open,
        empty_next      => open,
        full            => s_tdata_fifo_full,
        full_next       => open
      );

    fifo_tkeep : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => g_INPUT_WIDTH/8,
        g_output_width  => g_OUTPUT_WIDTH/8,
        g_depth         => g_DEPTH
      )
      port map (
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_axis_tvalid,
        wr_data         => s_axis_tkeep,
        rd_en           => m_axis_tready,
        rd_valid        => s_tkeep_fifo_rd_valid,
        rd_data         => m_axis_tkeep,
        empty           => open,
        empty_next      => open,
        full            => s_tkeep_fifo_full,
        full_next       => open
      );

    fifo_tlast : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => c_subwords_down,
        g_output_width  => 1,
        g_depth         => g_DEPTH
      )
      port map (
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_axis_tvalid,
        wr_data         => s_tlast_expanded,
        rd_en           => m_axis_tready,
        rd_valid        => s_tlast_fifo_rd_valid,
        rd_data         => s_tlast_fifo_down_rd_data,
        empty           => open,
        empty_next      => open,
        full            => open,
        full_next       => open
      );
  -- Replicate TLAST for each subword, so this FIFO will be alligned with TDATA and TKEEP FIFOs
    s_tlast_expanded(c_subwords_down-2 downto 0)  <= (others => '0');
    s_tlast_expanded(c_subwords_down-1)           <= s_axis_tlast;

    fifo_tdest : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => c_subwords_down * g_AXIS_TDEST_WIDTH,
        g_output_width  => g_AXIS_TDEST_WIDTH,
        g_depth         => g_DEPTH
      )
      port map (
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_axis_tvalid,
        wr_data         => s_tdest_expanded,
        rd_en           => m_axis_tready,
        rd_valid        => s_tdest_fifo_rd_valid,
        rd_data         => m_axis_tdest,
        empty           => open,
        empty_next      => open,
        full            => open,
        full_next       => open
      );  
    -- Replicate TDEST for each subword, so this FIFO will be alligned with TDATA and TKEEP FIFOs
    gen_expand_tdest: for i in 0 to c_subwords_down - 1 generate
      s_tdest_expanded((i+1)*g_AXIS_TDEST_WIDTH - 1 downto i*g_AXIS_TDEST_WIDTH) <= s_axis_tdest;
    end generate;

    fifo_tid : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => c_subwords_down * g_AXIS_TID_WIDTH,
        g_output_width  => g_AXIS_TID_WIDTH,
        g_depth         => g_DEPTH
      )
      port map (
        clk        => axis_aclk,
        rst        => s_axis_areset,
        wr_en      => s_axis_tvalid,
        wr_data    => s_tid_expanded,
        rd_en      => m_axis_tready,
        rd_valid   => s_tid_fifo_rd_valid,
        rd_data    => m_axis_tid,
        empty      => open,
        empty_next => open,
        full       => open,
        full_next  => open
      );
    -- Replicate TID for each subword, so this FIFO will be alligned with TDATA and TKEEP FIFOs
    gen_expand_tid: for i in 0 to c_subwords_down - 1 generate
      s_tid_expanded((i+1)*g_AXIS_TID_WIDTH - 1 downto i*g_AXIS_TID_WIDTH) <= s_axis_tid;   
    end generate;

    fifo_tuser : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => c_subwords_down * g_AXIS_TUSER_WIDTH,
        g_output_width  => g_AXIS_TUSER_WIDTH,
        g_depth         => g_DEPTH
      )
      port map (
        clk        => axis_aclk,
        rst        => s_axis_areset,
        wr_en      => s_axis_tvalid,
        wr_data    => s_tuser_expanded,
        rd_en      => m_axis_tready,
        rd_valid   => s_tuser_fifo_rd_valid,
        rd_data    => m_axis_tuser,
        empty      => open,
        empty_next => open,
        full       => open,
        full_next  => open
      );
    -- Replicate TDEST for each subword, so this FIFO will be alligned with TDATA and TKEEP FIFOs
    gen_expand_tuser: for i in 0 to c_subwords_down - 1 generate
      s_tuser_expanded((i+1)*g_AXIS_TUSER_WIDTH - 1 downto i*g_AXIS_TUSER_WIDTH) <= s_axis_tuser;
    end generate;
    -- Handshake and output assignments
    -- s_axis_tready is asserted when the FIFO is not full and reset is not active
    s_axis_tready <= not(s_tdata_fifo_full) and axis_aresetn;
    -- m_axis_tvalid is asserted when there is valid data to read from the FIFO    
    m_axis_tvalid <= s_tdata_fifo_rd_valid;
    -- m_axis_tlast is only asserted on the last subword of the burst
    m_axis_tlast  <= s_tlast_fifo_down_rd_data(0) when s_tdata_fifo_rd_valid = '1' and m_axis_tready = '1' else '0';
  end generate;

---------------------------------------------------------------------------------
--------------------------------- FIFO UPSTREAM ---------------------------------
---------------------------------------------------------------------------------
 --! Upstream conversion: This block is enabled when input width < output width.
  --! It uses asymmetric FIFOs to combine multiple narrow input words into a single wider output word.
  --! Each AXI-Stream channel (TDATA, TKEEP, TLAST, TDEST, TID, TUSER) has its own FIFO.
  --! The control logic ensures correct packing of input data and sideband signals into the wider output.
  gen_up_conv: if (c_up_or_down = True and c_input_width_mod = 0 and c_output_width_mod = 0) generate
  -- FIFO for TDATA: collects multiple input words and outputs them as a single wide word
    fifo_tdata : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => g_INPUT_WIDTH,
        g_output_width  => g_OUTPUT_WIDTH,
        g_depth         => g_DEPTH
      )
      port map (
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_fifo_tdata_wr_en,
        wr_data         => s_fifo_tdata_data,
        rd_en           => m_axis_tready,
        rd_valid        => s_tdata_fifo_rd_valid,
        rd_data         => m_axis_tdata,
        empty           => open,
        empty_next      => open,
        full            => s_tdata_fifo_full,
        full_next       => open
      );

    -- FIFO for TKEEP: collects multiple input tkeep and outputs as a single wide tkeep
    fifo_tkeep : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => g_INPUT_WIDTH/8,
        g_output_width  => g_OUTPUT_WIDTH/8,
        g_depth         => g_DEPTH
      )
      port map (
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_fifo_tkeep_wr_en,
        wr_data         => s_fifo_tkeep_data,
        rd_en           => m_axis_tready,
        rd_valid        => open,
        rd_data         => m_axis_tkeep,
        empty           => open,
        empty_next      => open,
        full            => s_tkeep_fifo_full,
        full_next       => open
      );

    -- FIFO for TLAST: collects TLAST from each input word and outputs a vector for the wide output
    fifo_tlast : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => 1,
        g_output_width  => c_subwords_up,
        g_depth         => g_DEPTH
      )
      port map (
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_fifo_tlast_wr_en,
        wr_data         => s_fifo_tlast_data,
        rd_en           => m_axis_tready,
        rd_valid        => s_tlast_fifo_rd_valid,
        rd_data         => s_tlast_fifo_up_data,
        empty           => open,
        empty_next      => open,
        full            => open,
        full_next       => open
      );

    -- FIFO for TDEST: collects multiple input TDEST and outputs as a wide vector
    fifo_tdest : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => g_AXIS_TDEST_WIDTH,
        g_output_width  => c_subwords_up * g_AXIS_TDEST_WIDTH,
        g_depth         => g_DEPTH
      )
      port map (
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_fifo_tdest_wr_en,
        wr_data         => s_fifo_tdest_data,
        rd_en           => m_axis_tready,
        rd_valid        => s_tdest_fifo_rd_valid,
        rd_data         => s_tdest_fifo_up_data,
        empty           => open,
        empty_next      => open,
        full            => open,
        full_next       => open
      );  

    -- FIFO for TID: collects multiple input TID and outputs as a wide vector
    fifo_tid : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => g_AXIS_TID_WIDTH,
        g_output_width  => c_subwords_up * g_AXIS_TID_WIDTH,
        g_depth         => g_DEPTH
      )
      port map (
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_fifo_tid_wr_en,
        wr_data         => s_fifo_tid_data,
        rd_en           => m_axis_tready,
        rd_valid        => s_tid_fifo_rd_valid,
        rd_data         => s_tid_fifo_up_data,
        empty           => open,
        empty_next      => open,
        full            => open,
        full_next       => open
      );  

    -- FIFO for TUSER: collects multiple input TUSER and outputs as a wide vector
    fifo_tuser : entity work.asymmetric_sync_fifo
      generic map (
        g_input_width   => g_AXIS_TUSER_WIDTH,
        g_output_width  => c_subwords_up * g_AXIS_TUSER_WIDTH,
        g_depth         => g_DEPTH
      )
      port map (
        clk             => axis_aclk,
        rst             => s_axis_areset,
        wr_en           => s_fifo_tuser_wr_en,
        wr_data         => s_fifo_tuser_data,
        rd_en           => m_axis_tready,
        rd_valid        => s_tuser_fifo_rd_valid,
        rd_data         => s_tuser_fifo_up_data,
        empty           => open,
        empty_next      => open,
        full            => open,
        full_next       => open
      );  
  -- Handshake and output assignments for the upstream conversion
  -- s_axis_tready is asserted when the up_process_gen process is ready to accept new input data and FIFO is not full
  s_axis_tready <= s_tready and not(s_tdata_fifo_full) ;
  -- m_axis_tvalid is asserted when there is valid data to read from the FIFO
  m_axis_tvalid <= s_tdata_fifo_rd_valid;
  -- Output sideband signals are assigned only when data is valid and ready, otherwise set to zero
  -- Only the lower g_AXIS_TUSER_WIDTH, g_AXIS_TID_WIDTH and g_AXIS_TDEST_WIDTH bits are valid for output
  m_axis_tuser  <= s_tuser_fifo_up_data(g_AXIS_TUSER_WIDTH - 1 downto 0) when s_tdata_fifo_rd_valid = '1' and m_axis_tready = '1' else (others=>'0');
  m_axis_tid    <= s_tid_fifo_up_data(g_AXIS_TID_WIDTH - 1 downto 0) when s_tdata_fifo_rd_valid = '1' and m_axis_tready = '1' else (others=>'0');
  m_axis_tdest  <= s_tdest_fifo_up_data(g_AXIS_TDEST_WIDTH - 1 downto 0) when s_tdata_fifo_rd_valid = '1' and m_axis_tready = '1' else (others=>'0');
  -- m_axis_tlast is asserted only on the last subword of the packed output 
  -- Only the upper bit is valid for output
  m_axis_tlast  <= s_tlast_fifo_up_data(c_subwords_up - 1) when s_tdata_fifo_rd_valid = '1' and m_axis_tready = '1' else '0';
end generate;

up_process_gen: if ((c_up_or_down = True and c_input_width_mod = 0 and c_output_width_mod = 0)) generate
 --! This process manages the packing of multiple narrow input words into a single wide output word for up-conversion.
  --! It controls the write enable signals for the FIFOs and tracks the number of subwords collected.
  --! It controls the s_axis_tready signal. If dummy data needs to be store inside the FIFOs, s_axis_tready=0 to avoid the master to send new data
  --! The state machine has two states:
  --!   - RECEIVE_WORD: Accepts new input words until c_subwords_up (g_OUTPUT_WIDTH/g_INPUT_WIDTH) words are collected or TLAST is received.
  --!   - STORE_WORD: Forces to write dummy data to the FIFOs if TLAST is received before the output word is full.
  process(axis_aclk)
  begin
    if rising_edge(axis_aclk) then
      if axis_aresetn = '0' then
        s_subword_count               <= 0;
        r_fifo_tdata_wr_en            <= '0';
        r_fifo_tkeep_wr_en            <= '0';
        r_fifo_tlast_wr_en            <= '0';
        r_fifo_tdest_wr_en            <= '0';
        r_fifo_tid_wr_en              <= '0';
        r_fifo_tuser_wr_en            <= '0';
        s_tready                      <= '0';
        s_store_state                 <= RECEIVE_WORD;
      else
          case s_store_state is 
            when RECEIVE_WORD =>
            -- Ready to accept new input AXI-Stream data
              s_tready <= '1';
              -- Increment subword counter or reset if output word is full
              if s_tready = '1' and s_axis_tvalid = '1' and s_tdata_fifo_full = '0' then
                 if s_subword_count = c_subwords_up - 1 then
                  s_subword_count     <= 0;
                else
                  s_subword_count     <= s_subword_count +1;
                end if;
              end if;            
            -- If TLAST is received before s_subword_count is reached, force a dummy data write and go to STORE_WORD
             if s_axis_tlast = '1' and s_subword_count < c_subwords_up -1 then
                r_fifo_tdata_wr_en    <= '1';
                r_fifo_tkeep_wr_en    <= '1';
                r_fifo_tlast_wr_en    <= '1';
                r_fifo_tdest_wr_en    <= '1';
                r_fifo_tuser_wr_en    <= '1';
                r_fifo_tid_wr_en      <= '1';
                s_tready <= '0';
                s_store_state         <= STORE_WORD;
              else
                s_store_state         <= RECEIVE_WORD;
              end if;

            -- Force write to FIFOs dummy data and wait until not full
            when STORE_WORD =>
              s_tready <= '0';
              r_fifo_tdata_wr_en      <= '1';
              r_fifo_tkeep_wr_en      <= '1';
              r_fifo_tlast_wr_en      <= '1';
              r_fifo_tdest_wr_en      <= '1';
              r_fifo_tuser_wr_en      <= '1';
              r_fifo_tid_wr_en      <= '1';

              if s_tdata_fifo_full = '0' then
                -- After writing, reset control signals and counters, and return to RECEIVE_WORD
                if s_subword_count = c_subwords_up - 1 then
                  r_fifo_tdata_wr_en  <= '0';
                  r_fifo_tkeep_wr_en  <= '0';
                  r_fifo_tlast_wr_en  <= '0';
                  r_fifo_tdest_wr_en  <= '0';
                  r_fifo_tuser_wr_en  <= '0';
                  r_fifo_tid_wr_en  <= '0';
                  s_tready <= '1';
                  s_subword_count     <= 0;
                  s_store_state       <= RECEIVE_WORD;
                else
                  s_subword_count     <= s_subword_count + 1;
                end if;
              else
                s_store_state         <= STORE_WORD;
              end if;

            when others =>  
              s_subword_count         <= 0;
              s_store_state           <= RECEIVE_WORD;           
        end case;

      end if;
    end if;
  end process;

  -- Assign write enable and data signals for each FIFO based on the state machine and input handshake.
  -- When s_tready is high, use input signals; otherwise, use registered control signals.
  -- wr_en and not s_tdata_fifo_full allows to write in the FIFOs only until s_tdata_fifo_full is deasserted
  s_fifo_tdata_wr_en    <= s_axis_tvalid when s_tready = '1' else (r_fifo_tdata_wr_en and not(s_tdata_fifo_full));
  s_fifo_tkeep_wr_en    <= s_axis_tvalid when s_tready = '1' else (r_fifo_tkeep_wr_en and not(s_tdata_fifo_full));
  s_fifo_tlast_wr_en    <= s_axis_tvalid when s_tready = '1' else (r_fifo_tlast_wr_en and not(s_tdata_fifo_full));
  s_fifo_tdest_wr_en    <= s_axis_tvalid when s_tready = '1' else (r_fifo_tdest_wr_en and not(s_tdata_fifo_full));
  s_fifo_tid_wr_en      <= s_axis_tvalid when s_tready = '1' else (r_fifo_tid_wr_en   and not(s_tdata_fifo_full));
  s_fifo_tuser_wr_en    <= s_axis_tvalid when s_tready = '1' else (r_fifo_tuser_wr_en and not(s_tdata_fifo_full));

  s_fifo_tdata_data     <= s_axis_tdata when s_tready = '1' else (others => '0');
  s_fifo_tkeep_data     <= s_axis_tkeep when s_tready = '1' else (others => '0');
  s_fifo_tdest_data     <= s_axis_tdest when s_tready = '1' else (others => '0');
  s_fifo_tuser_data     <= s_axis_tuser when s_tready = '1' else (others => '0');
  s_fifo_tid_data       <= s_axis_tid   when s_tready = '1' else (others => '0');
  s_fifo_tlast_data(0)  <= s_axis_tlast when s_tready = '1' else '1';

end generate;

end architecture;