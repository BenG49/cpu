#ruledef
{
    nop => 0x00

	lda {addr: u8} => 0x01 @ addr
	lda ${val: i8} => 0x02 @ val

	sta {addr: u8} => 0x03 @ addr

	add {addr: u8} => 0x04 @ addr
	add ${val: i8} => 0x05 @ val

	sub {addr: u8} => 0x06 @ addr
	sub ${val: i9} => 0x07 @ val

	out => 0x08
	hlt => 0x09

	jmp {addr: u8} => 0x0a @ addr

	jz  {addr: u8} => 0x0b @ addr
	je  {addr: u8} => 0x0b @ addr
	jnz {addr: u8} => 0x0c @ addr
	jne {addr: u8} => 0x0c @ addr

	jc  {addr: u8} => 0x0d @ addr
	jnc {addr: u8} => 0x0e @ addr

	js  {addr: u8} => 0x0f @ addr
	jns {addr: u8} => 0x10 @ addr

	jmp #{addr: u8} => 0x11 @ addr

	jz  #{addr: u8} => 0x12 @ addr
	je  #{addr: u8} => 0x12 @ addr
	jnz #{addr: u8} => 0x13 @ addr
	jne #{addr: u8} => 0x13 @ addr

	jc  #{addr: u8} => 0x14 @ addr
	jnc #{addr: u8} => 0x15 @ addr

	js  #{addr: u8} => 0x16 @ addr
	jns #{addr: u8} => 0x17 @ addr
}
