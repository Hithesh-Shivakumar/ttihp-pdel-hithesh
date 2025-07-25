# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_trivium_lite(dut):
    """Basic encryption and decryption test for Trivium-lite cipher"""

    dut._log.info("Starting test")

    # 50 MHz clock = 20 ns period
    clock = Clock(dut.clk, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # === Seed phase ===
    SEED = 0x3D
    dut._log.info("Setting seed")
    dut.uio_in.value = SEED
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00  # clear seed
    await ClockCycles(dut.clk, 2)

    plaintext = [0xDE, 0xAD, 0xBE, 0xEF]
    ciphertext = []

    # === Encrypt ===
    dut._log.info("Encryption phase")
    for pt in plaintext:
        dut.ui_in.value = pt
        await ClockCycles(dut.clk, 8)
        ct = dut.uo_out.value.integer
        ciphertext.append(ct)
        dut._log.info(f"Plain: 0x{pt:02X} => Cipher: 0x{ct:02X}")

    # === Reset ===
    dut._log.info("Resetting")
    dut.uio_in.value = 0xFF
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === Seed again ===
    dut._log.info("Seeding again for decryption")
    dut.uio_in.value = SEED
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === Decrypt ===
    dut._log.info("Decryption phase")
    for i, ct in enumerate(ciphertext):
        dut.ui_in.value = ct
        await ClockCycles(dut.clk, 8)
        decrypted = dut.uo_out.value.integer
        dut._log.info(f"Cipher: 0x{ct:02X} => Decrypted: 0x{decrypted:02X}")
        assert decrypted == plaintext[i], f"Mismatch at [{i}]"

    dut._log.info("Test passed")
