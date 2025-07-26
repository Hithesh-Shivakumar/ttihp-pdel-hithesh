`default_nettype none
`timescale 1ns / 1ps

module tt_um_trivium_lite (
    // Dedicated inputs/outputs
    input  wire [7:0] ui_in,     // Data input for encryption/decryption
    output reg  [7:0] uo_out,    // Encrypted/decrypted data output
    
    // Bidirectional IOs
    input  wire [7:0] uio_in,    // Control input: seed value or reset command
    output wire [7:0] uio_out,   // Not used - tied to 0
    output wire [7:0] uio_oe,    // Not used - tied to 0
    
    // System signals
    input  wire       ena,       // Enable (always high)
    input  wire       clk,       // Clock
    input  wire       rst_n      // Active-low reset
);

    // ====================================
    // Constants and Parameters
    // ====================================
    localparam IDLE  = 2'd0;
    localparam RUN   = 2'd1;
    localparam RESET = 2'd2;
    
    // Default initialization values for Trivium registers
    localparam INIT_S1 = 64'h23A2B;
    localparam INIT_S2 = 64'h2A892;
    localparam INIT_S3 = 64'hF4511;
    
    // Control commands
    localparam CMD_NORMAL = 8'h00;  // Normal operation
    localparam CMD_RESET  = 8'hFF;  // Reset command
    
    // ====================================
    // Internal Registers
    // ====================================
    reg [63:0] s1, s2, s3;           // Trivium state registers
    reg [7:0] temp_keystream;       // Accumulates keystream bits
    reg [2:0] step;                 // Step counter (0-7 for 8 bits)
    reg [1:0] state;                // FSM state
    
    // ====================================
    // Output Assignments
    // ====================================
    assign uio_out = 8'b0;  // Bidirectional outputs not used
    assign uio_oe  = 8'b0;  // Bidirectional inputs used so enable set to 0
    
    // ====================================
    // Main State Machine
    // ====================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset all registers to initial state
            s1             <= INIT_S1;
            s2             <= INIT_S2;
            s3             <= INIT_S3;
            temp_keystream <= 8'b0;
            uo_out         <= 8'b0;
            step           <= 3'd0;
            state          <= IDLE;
            
        end else begin
            case (state)
                
                // ====================================
                // IDLE State: Wait for seed input
                // ====================================
                IDLE: begin
                    step           <= 3'd0;
                    temp_keystream <= 8'b0;
                    
                    // Check for valid seed input (not normal or reset command)
                    if (uio_in != CMD_NORMAL && uio_in != CMD_RESET) begin
                        // Initialize Trivium state with seed
    			s1    <= {48'd0, uio_in,                   uio_in                  };
    			s2    <= {48'd0, uio_in, ~uio_in[3:0], uio_in[7:4]             };
    			s3    <= {48'd0, uio_in, (uio_in ^ 8'hA5)                    };                        state <= RUN;
                    end
                end
                
                // ====================================
                // RUN State: Generate keystream and encrypt/decrypt
                // ====================================
                RUN: begin
                    // Check for reset command
                    if (uio_in == CMD_RESET) begin
                        state <= RESET;
                        
                    end else begin
                        // Initialize temp_keystream at start of new byte
                        if (step == 3'd0) begin
                            temp_keystream <= 8'b0;
                        end
                        
                        // Trivium state update (shift registers with feedback)
			s1 <= {s1[62:0], s2[0] ^ s3[1] ^ s1[5] ^ s2[7] ^ s3[13] ^ s1[31] ^ s2[47] ^ s3[60]};
			s2 <= {s2[62:0], s3[3] ^ s1[1] ^ s2[2] ^ s3[19] ^ s1[23]};
			s3 <= {s3[62:0], s1[5] ^ s2[2] ^ s3[4] ^ s1[17] ^ s2[29] ^ s3[63] ^ s1[10] ^ s2[40]};
                        
                        // Generate keystream bit and accumulate
                        temp_keystream <= {temp_keystream[6:0], s1[0] ^ s2[0] ^ s3[0]};
                        
                        // Increment step counter
                        step <= step + 1;
                        
                        // After 8 steps, output encrypted/decrypted byte
                        if (step == 3'd7) begin
                            uo_out <= ui_in ^ temp_keystream;  // XOR input with generated keystream
                            step   <= 3'd0;                   // Reset step counter
                        end
                    end
                end
                
                // ====================================
                // RESET State: Return to initial conditions
                // ====================================
                RESET: begin
                    s1             <= INIT_S1;
                    s2             <= INIT_S2;
                    s3             <= INIT_S3;
                    temp_keystream <= 8'b0;
                    uo_out         <= 8'b0;
                    step           <= 3'd0;
                    state          <= IDLE;
                end
                
                // ====================================
                // Default: Safety fallback
                // ====================================
                default: begin
                    state <= IDLE;
                end
                
            endcase
        end
    end

endmodule
