## Trivium-lite Stream Cipher

### How it works

This design implements *Trivium-lite*, a minimalistic variant of the Trivium stream cipher using three 64-bit shift registers (`s1`, `s2`, `s3`) as internal state. The cipher produces a keystream by iteratively updating these registers with a custom linear feedback shift register (LFSR) logic and XORing the output with the plaintext.

### Internal State

- `s1`, `s2`, `s3`: 64-bit registers acting as LFSRs.
- `temp_keystream`: 8-bit buffer to collect keystream bits.
- `step`: 3-bit counter to track cycles (0–7 per byte).
- FSM states: `IDLE`, `RUN`, `RESET`.

### Inputs

- `ui_in[7:0]`: Data input (plaintext or ciphertext).
- `uio_in[7:0]`: 
  - Any value ≠ 0x00, 0xFF → Used as seed to initialize `s1`, `s2`, `s3`.
  - `0x00` → Normal operation (encrypt/decrypt).
  - `0xFF` → Trigger reset to default state.
- `clk`, `rst_n`, `ena`: Standard control signals.

### Process Overview

1. **Seeding Phase (IDLE)**  
   When `uio_in` is a valid 8-bit seed (≠ 0x00, ≠ 0xFF), the FSM transitions to `RUN`. The seed is expanded into initial values for the 64-bit registers via concatenation and bitwise transformations:
   - `s1 = {48'd0, seed, seed}`
   - `s2 = {48'd0, seed, ~seed[3:0], seed[7:4]}`
   - `s3 = {48'd0, seed, seed ^ 8'hA5}`

2. **Encryption/Decryption (RUN)**  
   On every clock edge, for 8 cycles:
   - Registers are updated using fixed LFSR-like feedback:
     - `s1 <= {s1[62:0], s2[0] ^ s3[1] ^ s1[5] ^ s2[7] ^ s3[13] ^ s1[31] ^ s2[47] ^ s3[60]}`
     - `s2 <= {s2[62:0], s3[3] ^ s1[1] ^ s2[2] ^ s3[19] ^ s1[23]}`
     - `s3 <= {s3[62:0], s1[5] ^ s2[2] ^ s3[4] ^ s1[17] ^ s2[29] ^ s3[63] ^ s1[10] ^ s2[40]}`
   - A single keystream bit is generated per cycle as `s1[0] ^ s2[0] ^ s3[0]`.
   - After 8 bits, the `temp_keystream` is XORed with `ui_in` to yield `uo_out`.

3. **Reset Phase (RESET)**  
   If `uio_in == 0xFF`, internal state is reset to default constants and FSM returns to `IDLE`.

### Symmetry and Reuse

Due to the symmetric nature of the cipher, applying the same seed followed by the same ciphertext reproduces the original plaintext. The design supports both encryption and decryption by reusing the seed.

### How to test

You can test this design either using a Verilog testbench or via a Cocotb Python-based test. See: [How to test](test/README.MD)

All inputs/outputs are internal to the digital logic and tested in simulation. The design is fully self-contained and does not require external PMODs, displays, or peripherals. 

### How to use: 

Modify the test.py to test the cipher by passing textfiles or images. Decode the files using same seed as used for ecncryption.
