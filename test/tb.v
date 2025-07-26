`default_nettype none
`timescale 1ns / 1ps

module tb ();

  // Dump the signals to a VCD file for waveform inspection
  initial begin
    $dumpfile("tb.vcd");
    $dumpvars(0, tb);
    #1;
  end

  // Wires and registers
  reg clk = 0;
  reg rst_n = 0;
  reg ena = 1;

  reg  [7:0] ui_in;
  reg  [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;

  // Clock generation: 50 MHz = 20 ns period
  always #10 clk = ~clk;

  // DUT instantiation
  tt_um_trivium_lite user_project (
      .ui_in  (ui_in),     // Dedicated inputs
      .uo_out (uo_out),    // Dedicated outputs
      .uio_in (uio_in),    // IOs: Input path
      .uio_out(uio_out),   // IOs: Output path
      .uio_oe (uio_oe),    // IOs: Enable path
      .ena    (ena),       // Always enabled
      .clk    (clk),       // Clock
      .rst_n  (rst_n)      // Active-low reset
  );

  // Test vectors
  reg [7:0] plaintext  [0:3];
  reg [7:0] ciphertext [0:3];
  reg [7:0] decrypted  [0:3];

  integer i;

  initial begin
    // Input Initialization
    plaintext[0] = 8'hDE;
    plaintext[1] = 8'hAD;
    plaintext[2] = 8'hBE;
    plaintext[3] = 8'hEF;

    ui_in  = 8'h00;
    uio_in = 8'h00;

    // Reset
    rst_n = 0;
    #50;
    rst_n = 1;

    // === SEED ===
    uio_in = 8'h76;  // Custom seed
    #20;
    uio_in = 8'h00;  // Clear
    #20;

    // === ENCRYPTION ===
    $display("=== Encryption Phase ===");
    for (i = 0; i < 4; i = i + 1) begin
      ui_in = plaintext[i];
      repeat (8) @(posedge clk);
      ciphertext[i] = uo_out;
      $display("Plaintext[%0d] = 0x%02x => Ciphertext = 0x%02x", i, plaintext[i], ciphertext[i]);
    end

    // === RESET ===
    uio_in = 8'hFF;
    #20;
    uio_in = 8'h00;
    #40;

    // === SAME SEED AGAIN ===
    uio_in = 8'h76;
    #20;
    uio_in = 8'h00;
    #20;

    // === DECRYPTION ===
    $display("=== Decryption Phase ===");
    for (i = 0; i < 4; i = i + 1) begin
      ui_in = ciphertext[i];
      repeat (8) @(posedge clk);
      decrypted[i] = uo_out;
      $display("Ciphertext[%0d] = 0x%02x => Decrypted = 0x%02x", i, ciphertext[i], decrypted[i]);
    end

    // === CHECK ===
    $display("=== Test Result ===");
    for (i = 0; i < 4; i = i + 1) begin
      if (plaintext[i] == decrypted[i])
        $display("PASS: [%0d] 0x%02x -> 0x%02x -> 0x%02x", i, plaintext[i], ciphertext[i], decrypted[i]);
      else
        $display("FAIL: [%0d] 0x%02x -> 0x%02x -> 0x%02x", i, plaintext[i], ciphertext[i], decrypted[i]);
    end

    #1000;
    $finish;
  end

endmodule
