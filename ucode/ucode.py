from enum import IntEnum, IntFlag

'''
CPU details
'''
ADDR_BITS = 14
OUT_BITS  = 16

Ctrl = IntFlag('Ctrl', 'FI T0 HT OI II RO RI MAI SU EO BI AO AI J CE CO')
Instr = IntEnum('Instr', 'NOP LDA LDAI STA ADD ADDI SUB SUBI OUT HLT JMP JZ JNZ JC JNC JS JNS JMPI JZI JNZI JCI JNCI JSI JNSI', start=0)

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

# readable output of which control lines are activated
def ctrl_line_str(data: int) -> str:
	out = ''

	for i in range(OUT_BITS):
		if ((data >> i) & 1) == 1:
			out += str(Ctrl(1 << i))[5:]
			out += ' '

	return out

# ucode prettyprinting
def read_ucode(f):
	print('addr instr tclk cf zf sf')
	with open(f, 'r') as file:
		for i, l in enumerate(file):
			if i == 0: continue
			addr = i - 1

			instr = INSTR_SLICE.get(addr)

			tclk = TCLK_SLICE.get(addr)

			if tclk > 5 or instr >= len(Instr): continue

			cflag = CFLAG_SLICE.get(addr)
			zflag = ZFLAG_SLICE.get(addr)
			sflag = SFLAG_SLICE.get(addr)

			data = int(l.strip(), 16)

			print(f'{addr:04x} {str(Instr(instr))[6:].rjust(4)}   {tclk}   {cflag}  {zflag}  {sflag}:   0x{data:04x}', ctrl_line_str(data))	

FETCH_ADDR = Ctrl.RO | Ctrl.MAI | Ctrl.CE

# T0 = CO | MAI
# T1 = CE | RO | II
# T2 = CO | MAI (for non-implied instructions)
# ucode for T3, T4, T5
ucode = [
	[0,                           0,                                     0],                                     # NOP
	[FETCH_ADDR,                  Ctrl.RO | Ctrl.AI,                     Ctrl.T0],                               # LDA
	[Ctrl.RO | Ctrl.AI | Ctrl.CE, Ctrl.T0,                               0],                                     # LDA imm
	[FETCH_ADDR,                  Ctrl.AO | Ctrl.RI,                     Ctrl.T0],                               # STA
	[FETCH_ADDR,                  Ctrl.RO | Ctrl.BI,                     Ctrl.EO | Ctrl.AI | Ctrl.FI],           # ADD
	[Ctrl.RO | Ctrl.BI | Ctrl.CE, Ctrl.EO | Ctrl.AI | Ctrl.FI,           Ctrl.T0],                               # ADD imm
	[FETCH_ADDR,                  Ctrl.RO | Ctrl.BI,                     Ctrl.EO | Ctrl.AI | Ctrl.SU | Ctrl.FI], # SUB
	[Ctrl.RO | Ctrl.BI | Ctrl.CE, Ctrl.EO | Ctrl.AI | Ctrl.SU | Ctrl.FI, Ctrl.T0],                               # SUB imm
	[Ctrl.T0,                     0,                                     0],                                     # OUT
	[0,                           0,                                     0],                                     # HLT
	[Ctrl.RO | Ctrl.J,            Ctrl.T0,                               0],                                     # JMP
	[FETCH_ADDR,                  Ctrl.RO | Ctrl.J,                      Ctrl.T0],                               # JMP indirect
]

def valid_jmp(instr: int, zero: bool, carry: bool, sign: bool) -> bool:
	# offset indirect jumps back to normal jumps, have same conditions
	if instr >= Instr.JMPI:
		instr = instr - Instr.JMPI + Instr.JMP

	return (instr == Instr.JMP
		or (instr == Instr.JZ  and zero)
		or (instr == Instr.JNZ and not zero)
		or (instr == Instr.JC  and carry)
		or (instr == Instr.JNC and not carry)
		or (instr == Instr.JS  and sign)
		or (instr == Instr.JNS and not sign))

def get(addr: int) -> int:
	instr = INSTR_SLICE.get(addr)
	tclk  = TCLK_SLICE.get(addr)
	zero  = ZFLAG_SLICE.get(addr)
	carry = CFLAG_SLICE.get(addr)
	sign  = SFLAG_SLICE.get(addr)

	if tclk > 5 or instr >= len(Instr): return 0

	# inc, set address
	if tclk == 0: return Ctrl.CO | Ctrl.MAI
	# fetch instruction
	if tclk == 1: return Ctrl.RO | Ctrl.II | Ctrl.CE
	if tclk == 2:
		# implied instructions
		if instr == Instr.NOP: return 0
		if instr == Instr.OUT: return Ctrl.AO | Ctrl.OI
		if instr == Instr.HLT: return Ctrl.HT

		# get data in byte after instruction
		return Ctrl.CO | Ctrl.MAI

	# jump instruction
	if instr > Instr.JMP:
		# jump condition is satisifed
		if valid_jmp(instr, zero, carry, sign):
			if instr >= Instr.JMP and instr < Instr.JMPI:
				# microcode for imm jumps are all the same
				return ucode[Instr.JMP][tclk - 3]
			else:
				# microcode for ind jumps are all the same
				return ucode[Instr.JMP + 1][tclk - 3]

		if tclk == 3:
			return Ctrl.CE | Ctrl.T0

		return 0

	return ucode[instr][tclk - 3]

with open('ucode.hex', 'w') as file:
	file.write('v2.0 raw\n')

	for n in range(1 << ADDR_BITS):
		file.write(f'{get(n):04x}')
		file.write('\n')

read_ucode('ucode.hex')
