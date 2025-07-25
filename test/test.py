# SPDX-FileCopyrightText: © 2024 Hithesh S
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


@cocotb.test()
async def test_trivium_lite(dut):
    """
    Basic encryption and decryption test for Trivium-lite cipher.
    Matches behavior from working Verilog testbench.
    """
    dut._log.info("Starting test")

    clk = Clock(dut.clk, 20, units="ns")  # 50 MHz clock
    cocotb.start_soon(clk.start())

    # Convenience assignments
    ui_in = dut.ui_in
    uio_in = dut.uio_in
    uo_out = dut.uo_out
    rst_n = dut.rst_n
    ena = dut.ena

    # Test vectors
    plaintext = [0xDE, 0xAD, 0xBE, 0xEF]
    ciphertext = [0] * 4
    decrypted = [0] * 4

    # === RESET ===
    ena.value = 1
    ui_in.value = 0
    uio_in.value = 0
    rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # === SEED PHASE ===
    dut._log.info("Setting seed")
    uio_in.value = 0x3D
    await ClockCycles(dut.clk, 2)
    uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === ENCRYPTION ===
    dut._log.info("Encryption phase")
    for i in range(4):
        ui_in.value = plaintext[i]
        await ClockCycles(dut.clk, 8)  # Wait for pipeline to flush
        ciphertext[i] = int(uo_out.value)
        dut._log.info(f"Plain: 0x{plaintext[i]:02X} => Cipher: 0x{ciphertext[i]:02X}")

    # === RESET ===
    uio_in.value = 0xFF
    await ClockCycles(dut.clk, 2)
    uio_in.value = 0x00
    await ClockCycles(dut.clk, 4)

    # === SAME SEED AGAIN ===
    dut._log.info("Seeding again for decryption")
    uio_in.value = 0x3D
    await ClockCycles(dut.clk, 2)
    uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === DECRYPTION ===
    dut._log.info("Decryption phase")
    for i in range(4):
        ui_in.value = ciphertext[i]
        await ClockCycles(dut.clk, 8)
        decrypted[i] = int(uo_out.value)
        dut._log.info(f"Cipher: 0x{ciphertext[i]:02X} => Decrypted: 0x{decrypted[i]:02X}")

    # === CHECK ===
    dut._log.info("Test Result:")
    for i in range(4):
        pt = plaintext[i]
        dt = decrypted[i]
        if pt == dt:
            dut._log.info(f"PASS: [{i}] 0x{pt:02X} -> 0x{ciphertext[i]:02X} -> 0x{dt:02X}")
        else:
            dut._log.error(f"FAIL: [{i}] 0x{pt:02X} -> 0x{ciphertext[i]:02X} -> 0x{dt:02X}")
        assert pt == dt, f"Mismatch at [{i}]"

