from enum import IntEnum

'''
CPU details
'''
ADDR_BITS = 14
OUT_BITS  = 16
TCLK_MAX  = 6

class Ctrl(IntEnum):
	# Using a decoder for mutually exclusive ctrl lines to save space
	CO, AO, EO, RO, HT, T0, SPO = range(1, 8)
	FI, OI, II, RI, MAI, SU, BI, AI, J, CE, SPE, SPD = [1 << i for i in range(3, 15)]

Instr = IntEnum('Instr', 'NOP LDA LDAI STA ADD ADDI SUB SUBI OUT HLT PHA PHC PLA RET JMP JZ JNZ JC JNC JS JNS JMPI JZI JNZI JCI JNCI JSI JNSI', start=0)

class BitSlice:
	def __init__(self, start: int, len: int):
		self.start = start
		self.len = len

	def get(self, val: int) -> int:
		mask = (1 << self.len) - 1
		return (val >> self.start) & mask

INSTR_SLICE = BitSlice(0, 8)
TCLK_SLICE  = BitSlice(8, 3)
CFLAG_SLICE = BitSlice(11, 1)
ZFLAG_SLICE = BitSlice(12, 1)
SFLAG_SLICE = BitSlice(13, 1)
