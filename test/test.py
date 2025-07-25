# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_trivium_lite(dut):
    dut._log.info("Starting test")

    clock = Clock(dut.clk, 10, units="ns")  # 100 MHz clock
    cocotb.start_soon(clock.start())

    seed = 0x3D
    plaintext = [0xDE, 0xAD, 0xBE, 0xEF]
    ciphertext = []
    decrypted = []

    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # === SEEDING PHASE ===
    dut._log.info("Setting seed")
    dut.uio_in.value = seed
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)

    # === ENCRYPTION ===
    dut._log.info("Encryption phase")
    for i, pt in enumerate(plaintext):
        dut.ui_in.value = pt
        await ClockCycles(dut.clk, 8)
        ct = int(dut.uo_out.value)
        ciphertext.append(ct)
        dut._log.info(f"Plain: 0x{pt:02X} => Cipher: 0x{ct:02X}")

    # === RESET ===
    dut._log.info("Resetting")
    dut.uio_in.value = 0xFF
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)

    # === SEED AGAIN FOR DECRYPTION ===
    dut._log.info("Seeding again for decryption")
    dut.uio_in.value = seed
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)

    # === DECRYPTION ===
    dut._log.info("Decryption phase")
    for i, ct in enumerate(ciphertext):
        dut.ui_in.value = ct
        await ClockCycles(dut.clk, 8)
        pt = int(dut.uo_out.value)
        decrypted.append(pt)
        dut._log.info(f"Cipher: 0x{ct:02X} => Decrypted: 0x{pt:02X}")

    # === CHECK ===
    for i in range(len(plaintext)):
        assert decrypted[i] == plaintext[i], f"Mismatch at [{i}]"
