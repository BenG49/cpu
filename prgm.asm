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
	hlt => 0x09

	jmp {addr} => 0x0a @ addr`8

	jz  {addr} => 0x0b @ addr`8
	je  {addr} => 0x0b @ addr`8
	jnz {addr} => 0x0c @ addr`8
	jne {addr} => 0x0c @ addr`8

	jc  {addr} => 0x0d @ addr`8
	jnc {addr} => 0x0e @ addr`8

	js  {addr} => 0x0f @ addr`8
	jns {addr} => 0x10 @ addr`8
}

; no stack, uses address 0xff as return address, no nested calls
; return in 0xe0
; args start at 0xf0, end at 0xfe

; scratch memory:
; 0xe1-ef

; udiv:
; 	lda $0
; 	sta 0xe1

; 	.loop:
; 		lda 0xf0
; 		sub 0xf1

; 		js .end  ; a - b was negative, a < b

; 		sta 0xf0 ; a -= b

; 		lda 0xe1 ; out += 1
; 		add #1
; 		sta 0xe1

; 	.end:

; 	lda 0xe1
; 	sta 0xe0
; 	lda 0xff

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
