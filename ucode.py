'''
CPU details
'''
ADDR_BITS = 13
OUT_BITS  = 16

SIGNAL_COUNT = 16
INSTR_COUNT = 13

FI, T0, HT, OI, II, RO, RI, MAI, SU, EO, BI, AO, AI, J, CE, CO = [1 << n for n in range(SIGNAL_COUNT)]
ctrl_lines = ['FI', 'T0', 'HT', 'OI', 'II', 'RO', 'RI', 'MAI', 'SU', 'EO', 'BI', 'AO', 'AI', 'J', 'CE', 'CO']
NOP, LDA, LDAI, STA, ADD, ADDI, SUB, SUBI, OUT, JMP, JZ, JC, HLT = [n for n in range(INSTR_COUNT)]

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

# readable output of which control lines are activated
def ctrl_line_str(data: int) -> str:
	out = ''

	for i in range(OUT_BITS):
		if ((data >> i) & 1) == 1:
			out += ctrl_lines[i]
			out += ' '

	return out

# assumes valid checksum
def read_ucode(f):
	print(f'addr instr tclk cflag zflag')
	with open(f, 'r') as file:
		for i, l in enumerate(file):
			if i == 0: continue
			addr = i - 1

			instr = INSTR_SLICE.get(addr)

			if instr != JC:
				continue

			tclk = TCLK_SLICE.get(addr)

			if tclk > 5 or instr >= INSTR_COUNT: continue

			cflag = CFLAG_SLICE.get(addr)
			zflag = ZFLAG_SLICE.get(addr)

			data = int(l.strip(), 16)

			print(f'{format(addr, "#06x")} {format(instr, "02")}    {tclk}    {cflag}     {zflag}: \t0x{format(data, "04X")}', ctrl_line_str(data))

FETCH_ADDR = RO | MAI | CE

# T0 = CO | MAI
# T1 = CE | RO | II
# T2 = CO | MAI (for non-implied instructions)
# ucode for T3, T4, T5
ucode = [
	[0,            0,                  0],                  # NOP
	[FETCH_ADDR,   RO | AI,            T0],                 # LDA
	[RO | AI | CE, T0,                 0],                  # LDA imm
	[FETCH_ADDR,   AO | RI,            T0],                 # STA
	[FETCH_ADDR,   RO | BI,            EO | AI | FI],       # ADD
	[RO | BI | CE, EO | AI | FI,       T0],                 # ADD imm
	[FETCH_ADDR,   RO | BI,            EO | AI | SUB | FI], # SUB
	[RO | BI | CE, EO | AI | SUB | FI, T0],                 # SUB imm
	[T0,           0,                  0],                  # OUT
	[RO | J,       T0,                 0],                  # JMP
	[RO | J,       T0,                 0],                  # JZ
	[RO | J,       T0,                 0],                  # JC
	[0,            0,                  0],                  # HLT
]

def get(addr: int) -> int:
	instr = INSTR_SLICE.get(addr)
	tclk  = TCLK_SLICE.get(addr)
	zero  = ZFLAG_SLICE.get(addr)
	carry = CFLAG_SLICE.get(addr)

	if tclk > 5 or instr >= INSTR_COUNT: return 0

	# inc, set address
	if tclk == 0: return CO | MAI
	# fetch instruction
	if tclk == 1: return RO | II | CE
	if tclk == 2:
		# implied instructions
		if instr == NOP: return 0
		if instr == OUT: return AO | OI
		if instr == HLT: return HT

		# get data in byte after instruction
		return CO | MAI

	if instr == JZ and zero != 1:  return CE | T0
	if instr == JC and carry != 1: return CE | T0

	return ucode[instr][tclk - 3]

with open('ucode.hex', 'w') as file:
	file.write('v2.0 raw\n')

	for n in range(1 << ADDR_BITS):
		file.write(f'{get(n):04X}')
		file.write('\n')

read_ucode('ucode.hex')
