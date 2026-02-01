onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate /one_bit_ring_fifo/rstn
add wave -noupdate /one_bit_ring_fifo/clk
add wave -noupdate /one_bit_ring_fifo/data_in
add wave -noupdate /one_bit_ring_fifo/data_valid_in
add wave -noupdate /one_bit_ring_fifo/mem
add wave -noupdate -radix unsigned /one_bit_ring_fifo/r0_count
add wave -noupdate -radix unsigned /one_bit_ring_fifo/r0_rd_ptr
add wave -noupdate -radix unsigned /one_bit_ring_fifo/r0_wr_ptr
add wave -noupdate /one_bit_ring_fifo/data_out
add wave -noupdate /one_bit_ring_fifo/data_out_valid
add wave -noupdate /one_bit_ring_fifo/empty_out
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {69605 ps} 0}
quietly wave cursor active 1
configure wave -namecolwidth 178
configure wave -valuecolwidth 156
configure wave -justifyvalue left
configure wave -signalnamewidth 0
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits us
update
WaveRestoreZoom {25200 ps} {193200 ps}
