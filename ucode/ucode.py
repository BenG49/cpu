from constants import *

# readable output of which control lines are activated
def ctrl_line_str(data: int) -> str:
	out = ''

	for c in Ctrl:
		if (c < 8 and (data & 0b111) == c) or (c >= 8 and (data & c) == c):
			out += str(Ctrl(c))[5:]
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

			if tclk > TCLK_MAX or instr >= len(Instr): continue

			cflag = CFLAG_SLICE.get(addr)
			zflag = ZFLAG_SLICE.get(addr)
			sflag = SFLAG_SLICE.get(addr)

			data = int(l.strip(), 16)

			print(f'{addr:04x} {str(Instr(instr))[6:].rjust(4)}   {tclk}   {cflag}  {zflag}  {sflag}:   0x{data:04x}', ctrl_line_str(data))	

# get data byte after instruction
FETCH_VAL =  Ctrl.CO | Ctrl.MAI
# move data byte after instruction into MAR
FETCH_ADDR = Ctrl.RO | Ctrl.MAI | Ctrl.CE

# T0 = CO | MAI
# T1 = CE | RO | II
# T2 = CO | MAI (for non-implied instructions)
# ucode for T2-6
ucode = [
	[0,                   0,                                       0,                                     0,                                       0],                # NOP
	[FETCH_VAL,           FETCH_ADDR,                              Ctrl.RO | Ctrl.AI,                     Ctrl.T0,                                 0],                # LDA
	[FETCH_VAL,           Ctrl.RO | Ctrl.AI | Ctrl.CE,             Ctrl.T0,                               0,                                       0],                # LDA imm
	[FETCH_VAL,           FETCH_ADDR,                              Ctrl.AO | Ctrl.RI,                     Ctrl.T0,                                 0],                # STA
	[FETCH_VAL,           FETCH_ADDR,                              Ctrl.RO | Ctrl.BI,                     Ctrl.EO | Ctrl.AI | Ctrl.FI,             0],                # ADD
	[FETCH_VAL,           Ctrl.RO | Ctrl.BI | Ctrl.CE,             Ctrl.EO | Ctrl.AI | Ctrl.FI,           Ctrl.T0, 0,                              0],                # ADD imm
	[FETCH_VAL,           FETCH_ADDR,                              Ctrl.RO | Ctrl.BI,                     Ctrl.EO | Ctrl.AI | Ctrl.SU | Ctrl.FI,   0],                # SUB
	[FETCH_VAL,           Ctrl.RO | Ctrl.BI | Ctrl.CE,             Ctrl.EO | Ctrl.AI | Ctrl.SU | Ctrl.FI, Ctrl.T0, 0,                              0],                # SUB imm
	[Ctrl.AO | Ctrl.OI,   Ctrl.T0,                                 0,                                     0,                                       0],                # OUT
	[Ctrl.HT,             0,                                       0,                                     0,                                       0],                # HLT
	[Ctrl.SPO | Ctrl.MAI, Ctrl.AO | Ctrl.RI | Ctrl.SPE | Ctrl.SPD, Ctrl.T0,                               0,                                       0],                # PHA
	[Ctrl.SPE,            Ctrl.SPO | Ctrl.MAI,                     Ctrl.RO | Ctrl.AI,                     Ctrl.T0,                                 0],                # PLA
	[FETCH_VAL,           Ctrl.RO | Ctrl.AI | Ctrl.CE,             Ctrl.SPO | Ctrl.MAI,                   Ctrl.CO | Ctrl.RI | Ctrl.SPE | Ctrl.SPD, Ctrl.AO | Ctrl.J], # CALL
	[Ctrl.SPE,            Ctrl.SPO | Ctrl.MAI,                     Ctrl.RO | Ctrl.J,                      Ctrl.T0,                                 0],                # RET
	[FETCH_VAL,           Ctrl.RO | Ctrl.J,                        Ctrl.T0,                               0,                                       0],                # JMP
	[FETCH_VAL,           FETCH_ADDR,                              Ctrl.RO | Ctrl.J,                      Ctrl.T0,                                 0],                # JMP indirect
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

	if tclk > TCLK_MAX or instr >= len(Instr): return 0

	# inc, set address
	if tclk == 0: return Ctrl.CO | Ctrl.MAI
	# fetch instruction
	if tclk == 1: return Ctrl.RO | Ctrl.II | Ctrl.CE

	# jump instruction
	if instr > Instr.JMP:
		# jump condition is satisifed
		if valid_jmp(instr, zero, carry, sign):
			if instr >= Instr.JMP and instr < Instr.JMPI:
				# microcode for imm jumps are all the same
				return ucode[Instr.JMP][tclk - 2]
			else:
				# microcode for ind jumps are all the same
				return ucode[Instr.JMP + 1][tclk - 2]

		if tclk == 3:
			return Ctrl.CE | Ctrl.T0

		return 0

	return ucode[instr][tclk - 2]

with open('ucode.hex', 'w') as file:
	file.write('v2.0 raw\n')

	for n in range(1 << ADDR_BITS):
		file.write(f'{get(n):04x}')
		file.write('\n')

read_ucode('ucode.hex')
