## Trivium-lite Stream Cipher

### How it works

This design implements a simplified version of the Trivium stream cipher, called *Trivium-lite*. It operates on 8-bit internal state registers (`s1`, `s2`, `s3`) and generates an 8-bit keystream for symmetric encryption and decryption.

- The cipher is seeded using an 8-bit key loaded via the `uio_in` port.
- Internal states are derived from transformations of the seed.
- For each input byte (`ui_in`), the design runs 8 clock cycles of keystream generation using a lightweight shift/XOR network.
- The input is XOR-ed with the keystream to produce encrypted/decrypted output on `uo_out`.
- Resetting the design and applying the same seed regenerates the same keystream, enabling decryption.

The cipher logic runs continuously until an explicit stop signal (`uio_in = 0xFF`) is received.

### How to test

You can test this design either using a Verilog testbench or via a Cocotb Python-based test.

#### Using Verilog Testbench:
1. Reset the design by setting `rst_n = 0` → `rst_n = 1`.
2. Load seed using `uio_in = <seed>` (e.g., `0x3D`), then set `uio_in = 0x00`.
3. Send plaintext input on `ui_in` one byte at a time. Each byte will be encrypted after 8 clock cycles.
4. Capture encrypted output from `uo_out`.
5. To decrypt, reset the design again, load the same seed, and feed encrypted bytes into `ui_in`. Output will be the original plaintext.

#### Using Cocotb:
Run `make` to execute the Python-based simulation (`test/test.py`). This will:
- Encrypt a 4-byte plaintext.
- Reset and reseed the design.
- Decrypt the resulting ciphertext.
- Check for roundtrip consistency: `plaintext -> ciphertext -> plaintext`.

To use the Verilog-only testbench:
```bash
make verilog
To run the Cocotb test:

bash
Copy
Edit
make
External hardware
None.

All inputs/outputs are internal to the digital logic and tested in simulation. The design is fully self-contained and does not require external PMODs, displays, or peripherals.
