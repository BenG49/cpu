# cpu
Digital logic simulation of [Ben Eater's 8-bit CPU](https://eater.net/8bit).

Using https://github.com/hneemann/Digital logic simulator and https://github.com/hlorenzi/customasm assembler.

# Modifications
- 4 bit -> 8 bit addresses
- 8 bit opcodes (instructions with arguments spread over 2 bytes)
- Add a stack
  - Add a stack pointer up/down counter (starts at 0xFF)
  - Add PHA/PLA instructions
  - Add CALL instruction (clobbers A register)
  - Add RET instruction (jumps to address at stack pointer in memory)
- Extend instruction set
  - Add imm for LDA, ADD, SUB

![picture of circuit](https://github.com/BenG49/cpu/blob/main/cpu.png?raw=true)
