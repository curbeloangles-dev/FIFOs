# FIFOs Collection
This repository contains a collection of FIFO (First-In-First-Out) hardware IP cores implemented in VHDL, with testbenches written for cocotb/pytest. Each subdirectory implements a specific FIFO variant and contains documentation, source files, and testbenches.

## Contents
- `asymmetric_fifo/` — Asymmetric-width synchronous FIFO (separate data widths on write/read sides).
- `asynchronous_fifo/` — Asynchronous FIFO for crossing clock domains using dual-port memory and proper pointer synchronization.
- `fifo_bram/` — FIFO implemented using block RAM (BRAM) primitives for FPGA BRAM-based buffering.
- `one_bit_ring_fifo/` — One-bit ring FIFO: a minimal FIFO structure with ring buffer behavior for single-bit flows.

Each implementation follows a similar folder layout:
- `package.json` — Metadata for packaging/publishing the IP (name, version). Not all are published.
- `README.md` — Local module readme for extra details.
- `doc/` — Diagrams and additional documentation (SVGs, markdown design notes).
- `src/` — VHDL source files.
- `tb/` — Testbenches and unit tests (cocotb + pytest). Some folders include `test_*.py` files for automated testing.


## Per-FIFO descriptions
### asymmetric_fifo
Asymmetric FIFO where write and read data widths differ. Useful when interfacing modules with different data bus widths.

### asynchronous_fifo
Asynchronous FIFO for crossing clock domains with independent read and write clocks. Designed with pointer synchronization and safe dual-port memory access.

### fifo_bram
Implement large FIFOs using FPGA block RAM (BRAM) to provide compact, high-capacity buffering.

### one_bit_ring_fifo
A minimal, single-bit ring FIFO used for low-overhead bitwise buffering. Useful for control signals or single-bit streams.


## Running tests locally
These projects use cocotb and pytest for Python-based testbenches. To run tests locally:

1. Install simulator and Python deps (example for GHDL + cocotb):
```bash
sudo apt-get update
sudo apt-get install -y ghdl
python3 -m pip install --user cocotb pytest cocotb-test
```

2. Run a module's pytest test from the repo root, for example:
```bash
pytest -o log_cli=True ./asynchronous_fifo/tb/test_async_fifo.py
```

Each FIFO's `package.json` may also include a `test` script that runs the appropriate test command.

## Contributing
- Update or add tests when changing behavior.
- Keep `package.json/version` bumped when you want the CI to publish a new package version.
- Open PRs for changes and ensure CI passes before merge.