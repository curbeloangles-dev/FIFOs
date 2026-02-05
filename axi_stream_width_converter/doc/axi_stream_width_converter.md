
# Entity: axi_stream_width_converter 
- **File**: axi_stream_width_converter.vhd

## Diagram
![Diagram](axi_stream_width_converter.svg "Diagram")
## Description

- **Name:** axi_stream_width_converter

- **Human Name:** Axistream Width Converter

- **One-line Description:**   Convert data width from one AXI-Stream interface to another with different data width.

- **One-paragraph Description:**  Convert data width from one AXI-Stream interface to another with different data width. The module has a FIFO to store the data when the input data width is greater than the output data width. The FIFO is implemented using the asymmetric_sync_fifo module. The module has a generic to set the input and output data width and the FIFO depth.

- **Block diagram:**


### Features

**Generic accepted values**
- g_INPUT_WIDTH:  Multiple of 8 bits
- g_OUTPUT_WIDTH: Multiple of 8 bits
- g_DEPTH:        >= 2 * max(g_OUTPUT_WIDTH, g_INPUT_WIDTH)/min(g_OUTPUT_WIDTH, g_INPUT_WIDTH)
- g_AXIS_TUSER_WIDTH  : Any accepted value, but standard recommends to be no more than 8
- g_AXIS_TID_WIDTH    : Any accepted value, but standard recommends be an integer multiple of g_INPUT_WIDTH/8
- g_AXIS_TDEST_WIDTH  : Any accepted value, but standard recommends to be no more than 8

**Latency**
- Clock cycles: TBD

**Running mode**
- Pipelined: Yes

**Corner cases**
- The is just one data stored in the fifo. The data should came out in the next clock cycle.
- The amount of input data is not enough to fill an output data. The output data should be empty.

### Future improvements
- Add generic to put registers in the output and input interfaces to improve timing.
- Add generic to select the memory implementation.

## Generics

| Generic name       | Type    | Value | Description                                                                          |
| ------------------ | ------- | ----- | ------------------------------------------------------------------------------------ |
| g_INPUT_WIDTH      | integer | 8     | Input data width                                                                     |
| g_OUTPUT_WIDTH     | integer | 32    | Output data width                                                                    |
| g_DEPTH            | integer | 64    | FIFO depth in input words when input width < output width, in output words otherwise |
| g_AXIS_TUSER_WIDTH | integer | 8     | AXI-Stream tuser width                                                               |
| g_AXIS_TID_WIDTH   | integer | 8     | AXI-Stream tid width                                                                 |
| g_AXIS_TDEST_WIDTH | integer | 8     | AXI-Stream tdest width                                                               |

## Ports

| Port name     | Direction | Type                                                | Description                                      |
| ------------- | --------- | --------------------------------------------------- | ------------------------------------------------ |
| axis_aclk     | in        | std_logic                                           | AXI-Stream clock                                 |
| axis_aresetn  | in        | std_logic                                           | AXI-Stream resetn. This means FIFO will be empty |
| s_axis_tdata  | in        | std_logic_vector(g_INPUT_WIDTH - 1 downto 0)        | AXI-Stream Slave tdata signal                    |
| s_axis_tvalid | in        | std_logic                                           | AXI-Stream Slave tvalid signal                   |
| s_axis_tready | out       | std_logic                                           | AXI-Stream Slave tready signal                   |
| s_axis_tkeep  | in        | std_logic_vector((g_INPUT_WIDTH / 8) - 1 downto 0)  |                                                  |
| s_axis_tuser  | in        | std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0)   |                                                  |
| s_axis_tid    | in        | std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0)     |                                                  |
| s_axis_tdest  | in        | std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0)   |                                                  |
| s_axis_tlast  | in        | std_logic                                           |                                                  |
| m_axis_tdata  | out       | std_logic_vector(g_OUTPUT_WIDTH - 1 downto 0)       | AXI-Stream Master tdata signal                   |
| m_axis_tvalid | out       | std_logic                                           | AXI-Stream Master tvalid signal                  |
| m_axis_tready | in        | std_logic                                           | AXI-Stream Master tready signal                  |
| m_axis_tkeep  | out       | std_logic_vector((g_OUTPUT_WIDTH / 8) - 1 downto 0) |                                                  |
| m_axis_tuser  | out       | std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0)   |                                                  |
| m_axis_tid    | out       | std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0)     |                                                  |
| m_axis_tdest  | out       | std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0)   |                                                  |
| m_axis_tlast  | out       | std_logic                                           |                                                  |

## Signals

| Name                      | Type                                                                  | Description |
| ------------------------- | --------------------------------------------------------------------- | ----------- |
| s_axis_areset             | std_logic                                                             |             |
| s_tkeep_fifo_full         | std_logic                                                             |             |
| s_tdata_fifo_full         | std_logic                                                             |             |
| s_tkeep_fifo_rd_valid     | std_logic                                                             |             |
| s_tlast_fifo_rd_valid     | std_logic                                                             |             |
| s_tlast_expanded          | std_logic_vector(c_subwords_down-1 downto 0)                          |             |
| s_tlast_fifo_down_rd_data | std_logic_vector(0 downto 0)                                          |             |
| s_tdest_expanded          | std_logic_vector((c_subwords_down * g_AXIS_TDEST_WIDTH) - 1 downto 0) |             |
| s_tid_expanded            | std_logic_vector((c_subwords_down * g_AXIS_TID_WIDTH) - 1 downto 0)   |             |
| s_tuser_expanded          | std_logic_vector((c_subwords_down * g_AXIS_TUSER_WIDTH) - 1 downto 0) |             |
| s_subword_count           | integer range 0 to c_subwords_up                                      |             |
| s_store_state             | t_store_state                                                         |             |
| r_fifo_tdata_wr_en        | std_logic                                                             |             |
| s_fifo_tdata_data         | std_logic_vector(g_INPUT_WIDTH - 1 downto 0)                          |             |
| r_fifo_tkeep_wr_en        | std_logic                                                             |             |
| r_fifo_tdest_wr_en        | std_logic                                                             |             |
| s_fifo_tdest_data         | std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0)                     |             |
| r_fifo_tid_wr_en          | std_logic                                                             |             |
| s_fifo_tid_data           | std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0)                       |             |
| r_fifo_tuser_wr_en        | std_logic                                                             |             |
| s_fifo_tuser_data         | std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0)                     |             |
| s_fifo_tkeep_data         | std_logic_vector((g_INPUT_WIDTH/8)-1 downto 0)                        |             |
| r_fifo_tlast_wr_en        | std_logic                                                             |             |
| s_fifo_tlast_data         | std_logic_vector(0 downto 0)                                          |             |
| s_tdata_fifo_rd_valid     | std_logic                                                             |             |
| s_tlast_fifo_up_data      | std_logic_vector(c_subwords_up - 1 downto 0)                          |             |
| s_tready                  | std_logic                                                             |             |
| s_fifo_tdata_wr_en        | std_logic                                                             |             |
| s_fifo_tkeep_wr_en        | std_logic                                                             |             |
| s_fifo_tlast_wr_en        | std_logic                                                             |             |
| s_fifo_tdest_wr_en        | std_logic                                                             |             |
| s_fifo_tid_wr_en          | std_logic                                                             |             |
| s_fifo_tuser_wr_en        | std_logic                                                             |             |
| s_tdest_fifo_rd_valid     | std_logic                                                             |             |
| s_tid_fifo_rd_valid       | std_logic                                                             |             |
| s_tuser_fifo_rd_valid     | std_logic                                                             |             |
| s_tdest_fifo_up_data      | std_logic_vector((c_subwords_up * g_AXIS_TDEST_WIDTH) - 1 downto 0)   |             |
| s_tid_fifo_up_data        | std_logic_vector((c_subwords_up * g_AXIS_TID_WIDTH) - 1 downto 0)     |             |
| s_tuser_fifo_up_data      | std_logic_vector((c_subwords_up * g_AXIS_TUSER_WIDTH) - 1 downto 0)   |             |

## Constants

| Name               | Type    | Value                                                                         | Description |
| ------------------ | ------- | ----------------------------------------------------------------------------- | ----------- |
| c_subwords_down    | integer | g_INPUT_WIDTH / g_OUTPUT_WIDTH                                                |             |
| c_subwords_up      | integer | g_OUTPUT_WIDTH / g_INPUT_WIDTH                                                |             |
| c_tkeep_width      | integer | g_INPUT_WIDTH / 8                                                             |             |
| c_up_or_down       | boolean | up_or_down(g_input_width,<br><span style="padding-left:20px"> g_output_width) |             |
| c_input_width_mod  | integer | (g_INPUT_WIDTH mod 8)                                                         |             |
| c_output_width_mod | integer | (g_OUTPUT_WIDTH mod 8)                                                        |             |

## Enums


### *t_store_state*
| Name         | Description |
| ------------ | ----------- |
| RECEIVE_WORD |             |
| STORE_WORD   |             |


## Functions
- up_or_down <font id="function_arguments">( input_width  : natural;<br><span style="padding-left:20px"> output_width : natural)</font> <font id="function_return">return boolean</font>
