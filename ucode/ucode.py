from constants import *

# readable output of which control lines are activated
def ctrl_line_str(data: int) -> str:
	out = ''

	for c in Ctrl.ALL:
		if c.isactive(data):
			out += str(c) + ' '

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

			if instr >= len(Instr): continue

			cflag = CFLAG_SLICE.get(addr)
			zflag = ZFLAG_SLICE.get(addr)
			sflag = SFLAG_SLICE.get(addr)

			data = int(l.strip(), 16)

			print(f'{addr:04X} {str(Instr(instr))[6:].rjust(4)}   {tclk}   {cflag}  {zflag}  {sflag}:   0x{data:04X}', ctrl_line_str(data))	

# get data byte after instruction
FETCH_VAL =  Ctrl.CO, Ctrl.MAI
# move data byte after instruction into MAR
FETCH_ADDR = Ctrl.RO, Ctrl.MAI, Ctrl.CE

# T0 = CO, MAI
# T1 = CE, RO, II
# T2 = CO, MAI (for non-implied instructions)
ucode = [
	# NOP
	[Ctrl.NONE] * 8,
	# LDA
	[FETCH_VAL,            FETCH_ADDR,                             (Ctrl.RO, Ctrl.AI)],
	# LDA imm
	[FETCH_VAL,            (Ctrl.RO, Ctrl.AI, Ctrl.CE)],
	# STA
	[FETCH_VAL,            FETCH_ADDR,                             (Ctrl.AO, Ctrl.RI)],
	# ADD
	[FETCH_VAL,            FETCH_ADDR,                             (Ctrl.RO, Ctrl.BI),                   (Ctrl.EO, Ctrl.AI, Ctrl.FI)],
	# ADD imm
	[FETCH_VAL,            (Ctrl.RO, Ctrl.BI, Ctrl.CE),            (Ctrl.EO, Ctrl.AI, Ctrl.FI)],
	# SUB
	[FETCH_VAL,            FETCH_ADDR,                             (Ctrl.RO, Ctrl.BI),                   (Ctrl.EO, Ctrl.AI, Ctrl.SU, Ctrl.FI)],
	# SUB imm
	[FETCH_VAL,            (Ctrl.RO, Ctrl.BI, Ctrl.CE),            (Ctrl.EO, Ctrl.AI, Ctrl.SU, Ctrl.FI)],
	# OUT
	[(Ctrl.AO, Ctrl.OI)],
	# HLT
	[[Ctrl.HT]],
	# PHA
	[(Ctrl.SPO, Ctrl.MAI), (Ctrl.AO, Ctrl.RI, Ctrl.SPE, Ctrl.SPD)],
	# PLA
	[[Ctrl.SPE],           (Ctrl.SPO, Ctrl.MAI),                   (Ctrl.RO, Ctrl.AI)],
	# CALL
	# TODO: use extra cycles to fix this
	[FETCH_VAL,            (Ctrl.RO, Ctrl.AI, Ctrl.CE),            (Ctrl.SPO, Ctrl.MAI),                 (Ctrl.CO, Ctrl.RI, Ctrl.SPE, Ctrl.SPD, Ctrl.AO, Ctrl.J)],
	# RET
	[[Ctrl.SPE],           (Ctrl.SPO, Ctrl.MAI),                   (Ctrl.RO, Ctrl.J)],
	# JMP
	[FETCH_VAL,            (Ctrl.RO, Ctrl.J)],
	# JMP indirect
	[FETCH_VAL,            FETCH_ADDR,                             (Ctrl.RO, Ctrl.J)],
]

def valid_jmp(instr: int, zero: bool, carry: bool, sign: bool) -> bool:
	# offset indirect jumps back to normal jumps, have same conditions
	if instr >= Instr.JMPI:
		instr -= Instr.JMPI - Instr.JMP

	return (instr == Instr.JMP
		or (instr == Instr.JZ  and zero)
		or (instr == Instr.JNZ and not zero)
		or (instr == Instr.JC  and carry)
		or (instr == Instr.JNC and not carry)
		or (instr == Instr.JNS and not sign)
        or (instr == Instr.JS  and sign))

def get(addr: int) -> int:
	def read_ucode_arr(instr, tclk):
		if tclk - 2 >= len(ucode[instr]):
			if tclk - 2 == len(ucode[instr]) and instr != Instr.HLT:
				return CtrlLine.apply(Ctrl.NONE, Ctrl.T0)
			
			return Ctrl.NONE
		
		if instr == Instr.NOP:
			return Ctrl.NONE

		return CtrlLine.apply(Ctrl.NONE, *ucode[instr][tclk - 2])

	instr = INSTR_SLICE.get(addr)
	tclk  = TCLK_SLICE.get(addr)
	zero  = ZFLAG_SLICE.get(addr)
	carry = CFLAG_SLICE.get(addr)
	sign  = SFLAG_SLICE.get(addr)

	if instr > len(Instr): return Ctrl.NONE

	# inc, set address
	if tclk == 0: return CtrlLine.apply(Ctrl.NONE, Ctrl.CO, Ctrl.MAI)
	# fetch instruction
	if tclk == 1: return CtrlLine.apply(Ctrl.NONE, Ctrl.RO, Ctrl.II, Ctrl.CE)

	# jump instruction
	if instr > Instr.JMP:
		# jump condition is satisifed
		if valid_jmp(instr, zero, carry, sign):
			# immediate jump
			if instr > Instr.JMP and instr < Instr.JMPI:
				return read_ucode_arr(Instr.JMP, tclk)
			# indirect jump
			else:
				return read_ucode_arr(Instr.JMP + 1, tclk)

		if tclk == 3:
			return CtrlLine.apply(Ctrl.NONE, Ctrl.CE, Ctrl.T0)

		return Ctrl.NONE

	return read_ucode_arr(instr, tclk)

if __name__ == '__main__':
	full = open('real/ucode-real.hex', 'w')
	top = open('real/top-real.hex', 'w')
	bot = open('real/bottom-real.hex', 'w')
	files = (full, top, bot)

	for f in files:
		f.write('v2.0 raw\n')

	for n in range(1 << ADDR_BITS):
		i = get(n)

		full.write(f'{i:04x}\n')
		top.write(f'{i >> 8:02x}\n')
		bot.write(f'{i & 0xFF:02x}\n')
	
	for f in files:
		f.close()

	read_ucode('real/ucode-real.hex')
