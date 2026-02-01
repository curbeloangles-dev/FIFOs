
# Entity: one_bit_ring_fifo 
- **File**: one_bit_ring_fifo.vhd

## Diagram
![Diagram](one_bit_ring_fifo.svg "Diagram")
## Description

- **Name:** one_bit_ring_fifo

- **Human Name:** One Bit Ring FIFO

- **One-line Description:** One Bit Ring FIFO

- **One-paragraph Description:** One Bit Ring FIFO. This module implements a one-bit wide ring FIFO buffer. It allows for the storage and retrieval of data in a circular manner, with a configurable depth and data width.

- **Block diagram:** N/A

### Features

**Generic accepted values**
- g_data_in_width: Width of the input data bus (default: 10)
- g_data_out_width: Width of the output data bus (default: 32)
- g_fifo_depth: Depth of the FIFO buffer (default: 64, power of 2 and higher than g_data_in_width and g_data_out_width)

**Latency**
N/A

**Running mode**
- Sequential

**Corner cases**
- Continuous writing data
- Input or output data with same width than FIFO depth

### Future improvements
- None

## Generics

| Generic name     | Type    | Value | Description |
| ---------------- | ------- | ----- | ----------- |
| g_data_in_width  | integer | 10    |             |
| g_data_out_width | integer | 32    |             |
| g_fifo_depth     | integer | 64    |             |

## Ports

| Port name      | Direction | Type                                          | Description |
| -------------- | --------- | --------------------------------------------- | ----------- |
| clk            | in        | std_logic                                     |             |
| rstn           | in        | std_logic                                     |             |
| data_in        | in        | std_logic_vector(g_data_in_width-1 downto 0)  |             |
| data_valid_in  | in        | std_logic                                     |             |
| data_out       | out       | std_logic_vector(g_data_out_width-1 downto 0) |             |
| data_out_valid | out       | std_logic                                     |             |
| data_out_ready | in        | std_logic                                     |             |
| full_out       | out       | std_logic                                     |             |
| empty_out      | out       | std_logic                                     |             |

## Signals

| Name               | Type                                          | Description |
| ------------------ | --------------------------------------------- | ----------- |
| mem                | mem_type                                      |             |
| r0_unread_bits_ctr | integer range 0 to g_fifo_depth               |             |
| r0_data_out        | std_logic_vector(g_data_out_width-1 downto 0) |             |
| r0_data_out_valid  | std_logic                                     |             |
| r0_overflow_fifo   | std_logic                                     |             |

## Constants

| Name         | Type    | Value                                   | Description |
| ------------ | ------- | --------------------------------------- | ----------- |
| c_addr_width | integer | integer(ceil(log2(real(g_fifo_depth)))) |             |

## Types

| Name     | Type | Description |
| -------- | ---- | ----------- |
| mem_type |      |             |

## Processes
- write_p: ( clk )
- read_p: ( clk )
- bits_ctr_p: ( clk )
