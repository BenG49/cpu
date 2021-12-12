#include "cpu.asm"

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
