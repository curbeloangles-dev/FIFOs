
# Entity: axi_stream_fifo 
- **File**: axi_stream_fifo.vhd

## Diagram
![Diagram](axi_stream_fifo.svg "Diagram")
## Description

- **Name:** axi_stream_fifo

- **Human Name:** Asynchronous Axi stream FIFO

- **One-line Description:**   Asynchronous Axi stream FIFO

- **One-paragraph Description:**  Asynchronous FIFO is inside this wrapper. The wrapper convert the FIFO interfaces into AXI-Stream interfaces.

- **Block diagram:**


### Features

**Generic accepted values**
- g_DATA_WIDTH:  Multiple of 8 bits
- g_DEPTH: 32 - x
- g_AXIS_TUSER_WIDTH  : Any accepted value, but standard recommends to be no more than 8
- g_AXIS_TID_WIDTH    : Any accepted value, but standard recommends be an integer multiple of g_DATA_WIDTH/8
- g_AXIS_TDEST_WIDTH  : Any accepted value, but standard recommends to be no more than 8

**Latency**
- Clock cycles: TBD

**Running mode**
- Pipelined: Yes

**Corner cases**
- Just one data is written and read.
- Fifo is full tready is low.
- Fifo is empty tready is high.
- Fifo is full and write data: when the fifo is full and the tvalid is set, the fifo is not written. terady is low.
- Fifo is empty and read data: when the fifo is empty and the tready is set, the fifo is not read. tvalid is low.

### Future improvements
- Axis registers to improve timing and routing.

## Generics

| Generic name       | Type    | Value | Description            |
| ------------------ | ------- | ----- | ---------------------- |
| g_DATA_WIDTH       | integer | 32    | Data width             |
| g_DEPTH            | integer | 256   | FIFO depth             |
| g_AXIS_TUSER_WIDTH | integer | 8     | AXI-Stream tuser width |
| g_AXIS_TID_WIDTH   | integer | 8     | AXI-Stream tid width   |
| g_AXIS_TDEST_WIDTH | integer | 8     | AXI-Stream tdest width |

## Ports

| Port name      | Direction | Type                                              | Description                                                                                     |
| -------------- | --------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| s_axis_aclk    | in        | std_logic                                         | AXI-Stream clock                                                                                |
| s_axis_aresetn | in        | std_logic                                         | AXI-Stream resetn. Resets write side (S_AXIS). This means write pointer will be back at index 0 |
| m_axis_aclk    | in        | std_logic                                         | AXI-Stream clock                                                                                |
| m_axis_aresetn | in        | std_logic                                         | AXI-Stream resetn. Resets read side (M_AXIS). This means read pointer will be back at index 0   |
| s_axis_tdata   | in        | std_logic_vector(g_DATA_WIDTH - 1 downto 0)       | AXI-Stream Slave tdata signal                                                                   |
| s_axis_tvalid  | in        | std_logic                                         | AXI-Stream Slave tvalid signal                                                                  |
| s_axis_tready  | out       | std_logic                                         | AXI-Stream Slave tready signal                                                                  |
| s_axis_tkeep   | in        | std_logic_vector((g_DATA_WIDTH / 8) - 1 downto 0) |                                                                                                 |
| s_axis_tuser   | in        | std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0) |                                                                                                 |
| s_axis_tid     | in        | std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0)   |                                                                                                 |
| s_axis_tdest   | in        | std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0) |                                                                                                 |
| s_axis_tlast   | in        | std_logic                                         |                                                                                                 |
| m_axis_tdata   | out       | std_logic_vector(g_DATA_WIDTH - 1 downto 0)       | AXI-Stream Master tdata signal                                                                  |
| m_axis_tvalid  | out       | std_logic                                         | AXI-Stream Master tvalid signal                                                                 |
| m_axis_tready  | in        | std_logic                                         | AXI-Stream Master tready signal                                                                 |
| m_axis_tkeep   | out       | std_logic_vector((g_DATA_WIDTH / 8) - 1 downto 0) |                                                                                                 |
| m_axis_tuser   | out       | std_logic_vector(g_AXIS_TUSER_WIDTH - 1 downto 0) |                                                                                                 |
| m_axis_tid     | out       | std_logic_vector(g_AXIS_TID_WIDTH - 1 downto 0)   |                                                                                                 |
| m_axis_tdest   | out       | std_logic_vector(g_AXIS_TDEST_WIDTH - 1 downto 0) |                                                                                                 |
| m_axis_tlast   | out       | std_logic                                         |                                                                                                 |

## Signals

| Name            | Type                         | Description |
| --------------- | ---------------------------- | ----------- |
| s_s_axis_areset | std_logic                    |             |
| s_m_axis_areset | std_logic                    |             |
| s_async_full    | std_logic                    |             |
| s_s_axis_tlast  | std_logic_vector(0 downto 0) |             |
| s_m_axis_tlast  | std_logic_vector(0 downto 0) |             |

## Constants

| Name             | Type    | Value                              | Description |
| ---------------- | ------- | ---------------------------------- | ----------- |
| c_ADDR_WIDTH     | natural | integer(ceil(log2(real(g_DEPTH)))) |             |
| c_data_width_mod | integer | (g_DATA_WIDTH mod 8)               |             |

## Instantiations

- async_fifo_tdata: work.async_fifo
- async_fifo_tkeep: work.async_fifo
- async_fifo_tlast: work.async_fifo
- async_fifo_tdest: work.async_fifo
- async_fifo_tuser: work.async_fifo
- async_fifo_tid: work.async_fifo
