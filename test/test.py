# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

@cocotb.test()
async def test_trivium_cipher(dut):
    """Test Trivium cipher encryption and decryption"""
    
    dut._log.info("Starting Trivium cipher test")
    
    # Set the clock period to 20 ns (50 MHz) to match Verilog testbench
    clock = Clock(dut.clk, 20, units="ns")
    cocotb.start_soon(clock.start())
    
    # Test vectors - same as Verilog testbench
    plaintext = [0xDE, 0xAD, 0xBE, 0xEF]
    ciphertext = [0] * 4
    decrypted = [0] * 4
    
    # Input Initialization
    dut.ena.value = 1
    dut.ui_in.value = 0x00
    dut.uio_in.value = 0x00
    
    # Reset sequence
    dut._log.info("Reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 3)  # 50ns / 20ns = ~3 cycles
    dut.rst_n.value = 1
    
    # === SEED ===
    dut._log.info("Setting seed")
    dut.uio_in.value = 0x76  # Custom seed
    await ClockCycles(dut.clk, 1)  # 20ns
    dut.uio_in.value = 0x00  # Clear
    await ClockCycles(dut.clk, 1)  # 20ns
    
    # === ENCRYPTION ===
    dut._log.info("=== Encryption Phase ===")
    for i in range(4):
        dut.ui_in.value = plaintext[i]
        await ClockCycles(dut.clk, 8)  # Wait 8 clock cycles
        ciphertext[i] = int(dut.uo_out.value)
        dut._log.info(f"Plaintext[{i}] = 0x{plaintext[i]:02x} => Ciphertext = 0x{ciphertext[i]:02x}")
    
    # === RESET ===
    dut._log.info("Reset for decryption")
    dut.uio_in.value = 0xFF
    await ClockCycles(dut.clk, 1)  # 20ns
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)  # 40ns
    
    # === SAME SEED AGAIN ===
    dut._log.info("Setting same seed for decryption")
    dut.uio_in.value = 0x76
    await ClockCycles(dut.clk, 1)  # 20ns
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 1)  # 20ns
    
    # === DECRYPTION ===
    dut._log.info("=== Decryption Phase ===")
    for i in range(4):
        dut.ui_in.value = ciphertext[i]
        await ClockCycles(dut.clk, 8)  # Wait 8 clock cycles
        decrypted[i] = int(dut.uo_out.value)
        dut._log.info(f"Ciphertext[{i}] = 0x{ciphertext[i]:02x} => Decrypted = 0x{decrypted[i]:02x}")
    
    # === CHECK ===
    dut._log.info("=== Test Result ===")
    all_passed = True
    for i in range(4):
        if plaintext[i] == decrypted[i]:
            dut._log.info(f"PASS: [{i}] 0x{plaintext[i]:02x} -> 0x{ciphertext[i]:02x} -> 0x{decrypted[i]:02x}")
        else:
            dut._log.error(f"FAIL: [{i}] 0x{plaintext[i]:02x} -> 0x{ciphertext[i]:02x} -> 0x{decrypted[i]:02x}")
            all_passed = False
    
    # Final assertion
    assert all_passed, "Encryption/Decryption test failed - decrypted data doesn't match original plaintext"
    
    dut._log.info("Trivium cipher test completed successfully")
