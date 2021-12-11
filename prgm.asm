#ruledef
{
    nop => 0x00
	lda {addr} => 0x01 @ addr`8
	lda ${val} => 0x02 @ val`8
	sta {addr} => 0x03 @ addr`8
	add {addr} => 0x04 @ addr`8
	add ${val} => 0x05 @ val`8
	sub {addr} => 0x06 @ addr`8
	sub ${val} => 0x07 @ val`8
	out => 0x08
	jmp {addr} => 0x09 @ addr`8
	jz  {addr} => 0x0a @ addr`8
	jc  {addr} => 0x0b @ addr`8
	hlt => 0x0c
}

; biggest = 0xfd
; second  = 0xfe
; temp    = 0xff
reset:
	lda $1
	sta 0xfd
	lda $0
	sta 0xfe
	sta 0xff

loop:
	lda 0xfd
	sta 0xff ; temp = biggest

	out

	add 0xfe

	; if overflow
	jc reset

	sta 0xfd ; biggest = biggest + second

	lda 0xff
	sta 0xfe ; other = temp

	jmp loop
