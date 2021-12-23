#ruledef
{
    nop => 0x00

	lda {addr: u8} => 0x01 @ addr`8
	lda ${val: i8} => 0x02 @ val`8

	sta {addr: u8} => 0x03 @ addr`8

	add {addr: u8} => 0x04 @ addr`8
	add ${val: i8} => 0x05 @ val`8

	sub {addr: u8} => 0x06 @ addr`8
	sub ${val: i9} => 0x07 @ val`8

	out => 0x08
	hlt => 0x09

	pha => 0x0a
	pla => 0x0b

	jmp {addr: u8} => 0x0c @ addr `8

	jz  {addr: u8} => 0x0d @ addr `8
	je  {addr: u8} => 0x0d @ addr `8
	jnz {addr: u8} => 0x0e @ addr `8
	jne {addr: u8} => 0x0e @ addr `8

	jc  {addr: u8} => 0x0f @ addr `8
	jnc {addr: u8} => 0x10 @ addr `8

	js  {addr: u8} => 0x10 @ addr `8
	jns {addr: u8} => 0x12 @ addr `8

	jmp #{addr: u8} => 0x13 @ addr`8

	jz  #{addr: u8} => 0x14 @ addr`8
	je  #{addr: u8} => 0x14 @ addr`8
	jnz #{addr: u8} => 0x15 @ addr`8
	jne #{addr: u8} => 0x15 @ addr`8

	jc  #{addr: u8} => 0x16 @ addr
	jnc #{addr: u8} => 0x17 @ addr

	js  #{addr: u8} => 0x18 @ addr
	jns #{addr: u8} => 0x19 @ addr
}
