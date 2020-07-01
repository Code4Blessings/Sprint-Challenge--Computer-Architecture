"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc =  0
        self.FL = 0b00000000

    def load(self):
        """Load a program into memory."""
        
        address = 0
        #print(sys.argv)
        with open(sys.argv[1]) as f:
            for line in f:
                string_val = line.split("#")[0].strip()
                if string_val == '':
                    continue
                v = int(string_val, 2) 
                #print(string_val, v)
                self.ram[address] = v
                address += 1

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        
        elif op == "CMP":
            #Compare the values in two registers.
            #FL = 00000LGE
            # * If they are equal
            if self.reg[reg_a] == self.reg[reg_b]:
                #set the Equal `E` flag to 1
                self.FL = 0b00000001
                # * If registerA is less than registerB
            elif self.reg[reg_a] < self.reg[reg_b]:
            # set the Less-than `L` flag to 1,
                self.FL = 0b00000100
            # * If registerA is greater than registerB, 
            elif self.reg[reg_a] > self.reg[reg_b]:
                #set the Greater-than `G` flag to 1
                self.FL = 0b00000010
            #otherwise set it to 0.
            else: 
                self.FL = 0b00000000
        
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        LDI = 0b10000010
        HLT = 0b00000001
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        SP = 7
        #CALL = 0b01010000
        #RET = 0b00010001
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101

        running = True
        self.reg[SP] = 0xF4

        while running:
            IR = self.ram[self.pc]
            #print(IR, self.pc)
            if IR == HLT:
                running = False
            
            elif IR == LDI:
                operand_a = self.ram[self.pc + 1]  # Address
                operand_b = self.ram[self.pc + 2]  # Value or integer
                self.reg[operand_a] = operand_b
                self.pc += 3 #Update the pc

            elif IR == PRN:
                reg_a = self.ram[self.pc + 1]
                print(self.reg[reg_a])
                self.pc += 2

            elif IR == MUL:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu("MUL", reg_a, reg_b)
                self.pc += 3

            elif IR == PUSH: #e.g. PUSH R3
                #1. Decrement the `SP`.
                self.reg[SP] -= 1
                #2. Get the register #
                reg_a = self.ram[self.pc + 1]
                #3. Get the value out of the register
                value = self.reg[reg_a]
                #4. # Store value in memory at SP
                top_of_stack_addr = self.reg[SP]
                self.ram[top_of_stack_addr] = value
                self.pc += 2

            elif IR == POP:
                top_of_stack_addr = self.reg[SP]
                value = self.ram[top_of_stack_addr]
                reg_a = self.ram[self.pc + 1]
                self.reg[SP] += 1
                self.pc += 2
            
            elif IR == CMP:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu("CMP", reg_a, reg_b)
                self.pc += 3
            
            elif IR == JMP:
                # Jump to the address stored in the given register.
                register = self.ram_read(self.pc + 1)
                # Set the `PC` to the address stored in the given register.
                self.pc = self.reg[register]
            
            elif IR == JEQ:
                pass
            # elif IR == CALL:
            #     return_addr = self.pc + 2
            #     # Push it on the stack
            #     self.reg[SP] -= 1
            #     top_of_stack_addr = self.reg[SP]
            #     self.ram[top_of_stack_addr] = return_addr
            #     # Set the PC to the subroutine addr
            #     reg_a = self.ram[self.pc + 1]
            #     subroutine_addr = self.reg[reg_a]
            #     self.pc = subroutine_addr

            # elif IR == RET:
            #     # Pop the return addr off stack
            #     top_of_stack_addr = self.reg[SP]
            #     return_addr = self.ram[top_of_stack_addr]
            #     self.reg[SP] += 1
            #     # Store it in the PC
            #     self.pc = return_addr

    def ram_read(self, mar): #Memory Address Register--Address
        return self.ram[mar]

    def ram_write(self, mdr, mar): #Memory Data Register--Value
        self.ram[mar] = mdr

