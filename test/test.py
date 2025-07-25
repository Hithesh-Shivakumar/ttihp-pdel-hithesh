# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_trivium_lite(dut):
    """Basic encryption and decryption test for Trivium-lite cipher"""
    dut._log.info("Starting test")

    clock = Clock(dut.clk, 20, units="ns")  # 50 MHz clock
    cocotb.start_soon(clock.start())

    # Apply reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    plaintext = [0xDE, 0xAD, 0xBE, 0xEF]
    ciphertext = []
    decrypted = []

    # === SEED PHASE ===
    dut._log.info("Setting seed")
    dut.uio_in.value = 0x3D
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === ENCRYPTION PHASE ===
    dut._log.info("Encryption phase")
    for i in range(4):
        dut.ui_in.value = plaintext[i]
        await ClockCycles(dut.clk, 8)
        c = int(dut.uo_out.value)
        ciphertext.append(c)
        dut._log.info(f"Plain: 0x{plaintext[i]:02X} => Cipher: 0x{c:02X}")

    # === RESET PHASE ===
    dut._log.info("Resetting")
    dut.uio_in.value = 0xFF
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === SEED AGAIN FOR DECRYPTION ===
    dut._log.info("Seeding again for decryption")
    dut.uio_in.value = 0x3D
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === DECRYPTION PHASE ===
    dut._log.info("Decryption phase")
    for i in range(4):
        dut.ui_in.value = ciphertext[i]
        await ClockCycles(dut.clk, 8)
        pt = int(dut.uo_out.value)
        decrypted.append(pt)
        dut._log.info(f"Cipher: 0x{ciphertext[i]:02X} => Decrypted: 0x{pt:02X}")

    # === RESULT CHECK ===
    dut._log.info("Test Result:")
    for i in range(4):
        pt = decrypted[i]
        if pt == plaintext[i]:
            dut._log.info(f"PASS: [{i}] 0x{plaintext[i]:02X} -> 0x{ciphertext[i]:02X} -> 0x{pt:02X}")
        else:
            dut._log.error(f"FAIL: [{i}] 0x{plaintext[i]:02X} -> 0x{ciphertext[i]:02X} -> 0x{pt:02X}")
            assert pt == plaintext[i], f"Mismatch at [{i}]"
