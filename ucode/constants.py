from enum import IntEnum

# CPU details
ADDR_BITS = 14
OUT_BITS  = 16

'''
Clock:     (HT)
Counter:   (CO), CE, ~J
B Reg:     ~BI
A Reg:     ~AI, (AO)
ALU:       (EO), SU
MAR:       ~MAI
RAM:       RI, (RO)
Stack:     (SPO), ~SPE, ~SPD, ~SPI
Flags:     ~FI
Out Reg:   ~OI
Instr Reg: ~II
Control:   (T0)
'''

class BitSlice:
	def __init__(self, start: int, len: int):
		self.start = start
		self.len = len

	def mask(self) -> int:
		return ((1 << self.len) - 1) << self.start

	def get(self, val: int) -> int:
		mask = (1 << self.len) - 1
		return (val >> self.start) & mask

	def apply(self, val_in: int, data: int) -> int:
		val_in &= ~self.mask()
		val_in |= data << self.start
		return val_in

class CtrlLine:
	def apply(in_val: int, *args) -> int:
		for l in args:
			in_val = l.applyto(in_val)
		return in_val

	def bit(name: str, n: int, inv: bool=False):
		return CtrlLine(name, BitSlice(n, 1), 0 if inv else 1)

	def __init__(self, name: str, bits: BitSlice, val: int):
		self.name = name
		self.bits = bits
		self.val = val

	def applyto(self, in_val: int, enabled: bool=True):
		if enabled:
			return self.bits.apply(in_val, self.val)

		# disabled value is either inverted or just zeroed out if bits.len > 1
		if self.bits.len == 1:
			return self.bits.apply(in_val, ~self.val)

		return self.bits.apply(in_val, 0)

	def isactive(self, val: int) -> bool:
		return self.bits.get(val) == self.val

	def __str__(self) -> str:
		return self.name
	
	def __repr__(self) -> str:
		return self.__str__()

class Ctrl:
	# Using a decoder for mutually exclusive ctrl lines to save space
	CO = CtrlLine('CO', BitSlice(0, 3), 1)
	AO = CtrlLine('AO', BitSlice(0, 3), 2)
	EO = CtrlLine('EO', BitSlice(0, 3), 3)
	RO = CtrlLine('RO', BitSlice(0, 3), 4)
	HT = CtrlLine('HT', BitSlice(0, 3), 5)
	T0 = CtrlLine('T0', BitSlice(0, 3), 6)
	SPO = CtrlLine('SPO', BitSlice(0, 3), 7)

	FI = CtrlLine.bit('FI', 3, True)
	OI = CtrlLine.bit('OI', 4, True)
	II = CtrlLine.bit('II', 5, True)
	RI = CtrlLine.bit('RI', 6)
	MAI = CtrlLine.bit('MAI', 7, True)
	SU = CtrlLine.bit('SU', 8)
	BI = CtrlLine.bit('BI', 9, True)
	AI = CtrlLine.bit('AI', 10, True)
	J =  CtrlLine.bit('J', 11, True)
	CE = CtrlLine.bit('CE', 12)
	SPE = CtrlLine.bit('SPE', 13, True)
	SPD = CtrlLine.bit('SPD', 14, True)
	SPI = CtrlLine.bit('SPI', 15, True)

	ALL = (CO, AO, EO, RO, HT, T0, SPO, FI, OI, II, RI, MAI, SU, BI, AI, J, CE, SPE, SPD, SPI)
	NONE = 0
	for a in ALL:
		NONE = a.applyto(NONE, False)

Instr = IntEnum('Instr', 'NOP LDA LDAI STA ADD ADDI SUB SUBI OUT HLT PHA PHC PLA RET JMP JZ JNZ JC JNC JS JNS JMPI JZI JNZI JCI JNCI JSI JNSI', start=0)

INSTR_SLICE = BitSlice(0, 8)
TCLK_SLICE  = BitSlice(8, 3)
CFLAG_SLICE = BitSlice(11, 1)
ZFLAG_SLICE = BitSlice(12, 1)
SFLAG_SLICE = BitSlice(13, 1)
