# SPDX-License-Identifier: Apache-2.0
# cocotb testbench for tt_um_trivium_lite
# Matches Verilog tb.v behavior exactly

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles


@cocotb.test()
async def test_trivium_lite(dut):
    """Basic encryption and decryption test for Trivium-lite cipher.
    Matches behavior from working Verilog testbench.
    """
    dut._log.info("Starting test")

    # Clock generation: 50 MHz => 20ns period
    cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())

    # === INPUTS ===
    plaintext  = [0xDE, 0xAD, 0xBE, 0xEF]
    ciphertext = [0] * 4
    decrypted  = [0] * 4

    # === RESET ===
    dut.rst_n.value = 0
    dut.ena.value   = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await Timer(50, units="ns")
    dut.rst_n.value = 1

    # === SEED ===
    dut.uio_in.value = 0x3D
    await Timer(20, units="ns")
    dut.uio_in.value = 0x00
    await Timer(20, units="ns")

    # === ENCRYPTION ===
    dut._log.info("=== Encryption Phase ===")
    for i in range(4):
        dut.ui_in.value = plaintext[i]
        await ClockCycles(dut.clk, 8)
        ciphertext[i] = int(dut.uo_out.value)
        dut._log.info(f"Plaintext[{i}] = 0x{plaintext[i]:02X} => Ciphertext = 0x{ciphertext[i]:02X}")

    # === RESET ===
    dut.uio_in.value = 0xFF
    await Timer(20, units="ns")
    dut.uio_in.value = 0x00
    await Timer(40, units="ns")

    # === SAME SEED AGAIN ===
    dut.uio_in.value = 0x3D
    await Timer(20, units="ns")
    dut.uio_in.value = 0x00
    await Timer(20, units="ns")

    # === DECRYPTION ===
    dut._log.info("=== Decryption Phase ===")
    for i in range(4):
        dut.ui_in.value = ciphertext[i]
        await ClockCycles(dut.clk, 8)
        decrypted[i] = int(dut.uo_out.value)
        dut._log.info(f"Ciphertext[{i}] = 0x{ciphertext[i]:02X} => Decrypted = 0x{decrypted[i]:02X}")

    # === RESULT CHECK ===
    dut._log.info("=== Test Result ===")
    for i in range(4):
        pt = plaintext[i]
        ct = ciphertext[i]
        dt = decrypted[i]
        if pt == dt:
            dut._log.info(f"PASS: [{i}] 0x{pt:02X} -> 0x{ct:02X} -> 0x{dt:02X}")
        else:
            dut._log.error(f"FAIL: [{i}] 0x{pt:02X} -> 0x{ct:02X} -> 0x{dt:02X}")
            assert pt == dt, f"Mismatch at [{i}]"

    dut._log.info("Test complete")
