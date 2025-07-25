# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_trivium_lite(dut):
    """
    Basic encryption and decryption test for Trivium-lite cipher
    """

    dut._log.info("Starting test")

    # Set the clock period to 10 ns (100 MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # === Initialization ===
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
    dut.uio_in.value = 0x3D  # Custom seed
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === ENCRYPTION PHASE ===
    dut._log.info("Encryption phase")
    for i, pt in enumerate(plaintext):
        dut.ui_in.value = pt
        await ClockCycles(dut.clk, 8)
        ct = dut.uo_out.value.integer
        ciphertext.append(ct)
        dut._log.info(f"Plain: 0x{pt:02X} => Cipher: 0x{ct:02X}")

    # === RESET PHASE ===
    dut._log.info("Resetting")
    dut.uio_in.value = 0xFF  # Trigger reset
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === SEED AGAIN ===
    dut._log.info("Seeding again for decryption")
    dut.uio_in.value = 0x3D
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # === DECRYPTION PHASE ===
    dut._log.info("Decryption phase")
    for i, ct in enumerate(ciphertext):
        dut.ui_in.value = ct
        await ClockCycles(dut.clk, 8)
        pt = dut.uo_out.value.integer
        decrypted.append(pt)
        dut._log.info(f"Cipher: 0x{ct:02X} => Decrypted: 0x{pt:02X}")
        assert pt == plaintext[i], f"Mismatch at [{i}]"

    # === FINAL RESULT ===
    dut._log.info("=== Test Result ===")
    for i in range(len(plaintext)):
        dut._log.info(
            f"{'PASS' if decrypted[i] == plaintext[i] else 'FAIL'}: "
            f"[{i}] 0x{plaintext[i]:02X} -> 0x{ciphertext[i]:02X} -> 0x{decrypted[i]:02X}"
        )

