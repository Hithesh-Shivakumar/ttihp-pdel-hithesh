/*
 * Copyright (c) 2024 hitheshs
 * SPDX-License-Identifier: Apache-2.0
 */

`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/25/2025 05:35:13 PM
// Design Name: 
// Module Name: tt_um_trivium_lite
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

`default_nettype none

module tt_um_trivium_lite (
    input  wire [7:0] ui_in,     // Data input
    output reg  [7:0] uo_out,    // Encrypted/decrypted output
    input  wire [7:0] uio_in,    // Used for seed/load/reset
    output wire [7:0] uio_out,   // Not used
    output wire [7:0] uio_oe,    // Not used
    input  wire       ena,       // Always 1
    input  wire       clk,       // Clock
    input  wire       rst_n      // Active-low reset
);

  reg [7:0] s1, s2, s3;
  reg [7:0] keystream;
  reg [7:0] temp_keystream;
  reg [2:0] step;
  reg [1:0] state;

  localparam IDLE  = 2'd0;
  localparam LOAD  = 2'd1;
  localparam RUN   = 2'd2;
  localparam RESET = 2'd3;

  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      s1 <= 8'h1;
      s2 <= 8'h2;
      s3 <= 8'h3;
      keystream <= 8'b0;
      temp_keystream <= 8'b0;
      uo_out <= 8'b0;
      step <= 0;
      state <= IDLE;
    end else begin
      case (state)

        IDLE: begin
          step <= 0;
          temp_keystream <= 8'b0;
          if (uio_in != 8'h00 && uio_in != 8'hFF) begin
            s1 <= uio_in;
            s2 <= {~uio_in[3:0], uio_in[7:4]};
            s3 <= uio_in ^ 8'hA5;
            state <= RUN;
          end
        end

        RUN: begin
          if (uio_in == 8'hFF) begin
            state <= RESET;
          end else begin
            // Run Trivium-lite keystream generation
            s1 <= {s1[6:0], s2[0] ^ s3[1]};
            s2 <= {s2[6:0], s3[3] ^ s1[1]};
            s3 <= {s3[6:0], s1[5] ^ s2[2]};

            temp_keystream <= {temp_keystream[6:0], s1[0] ^ s2[0] ^ s3[0]};
            step <= step + 1;

            if (step == 3'd7) begin
              keystream <= {temp_keystream[6:0], s1[0] ^ s2[0] ^ s3[0]};
              uo_out <= ui_in ^ {temp_keystream[6:0], s1[0] ^ s2[0] ^ s3[0]};
              step <= 0;
              temp_keystream <= 8'h9;
            end
          end
        end

        RESET: begin
          s1 <= 8'h1;
          s2 <= 8'h2;
          s3 <= 8'h3;
          keystream <= 8'b0;
          temp_keystream <= 8'b0;
          uo_out <= 8'b0;
          step <= 0;
          state <= IDLE;
        end

      endcase
    end
  end

endmodule
