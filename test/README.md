## Testing the Trivium Lite Stream Cipher:

## Setting up

Clone the repo in your local machine and follow the steps:

1. Check the requirements.txt file and make sure the listed tools are available.
2. Go to test folder to run tests

## How to run

To run the RTL simulation using the verilog testbench:

```sh
make verilog
```

To run the cocotb test bench written inthe file test.py

```sh
make -B
```

## How to view the VCD file

Using GTKWave
```sh
gtkwave tb.vcd tb.gtkw
```

Using Surfer
```sh
surfer tb.vcd
```
