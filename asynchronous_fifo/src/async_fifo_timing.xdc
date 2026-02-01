set_false_path -from [get_cells -hierarchical -filter NAME=~*/async_fifo*/o_WR_PTR*] -to [get_cells -hierarchical -filter NAME=~*/async_fifo*/r_synch_reg*]
set_false_path -from [get_cells -hierarchical -filter NAME=~*/async_fifo*/o_RD_PTR*] -to [get_cells -hierarchical -filter NAME=~*/async_fifo*/r_synch_reg*]
set_false_path -from [get_cells -hierarchical -filter NAME=~*/async_fifo*/r_synch_reg*] -to [get_cells -hierarchical -filter NAME=~*/async_fifo*/o_PTR_OUT*]
