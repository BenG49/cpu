#include "cpu.asm"

; no stack, uses address 0xff as return address, no nested calls
; return in 0xe0
; args start at 0xf0, end at 0xfe

; scratch memory:
; 0xe1-ef

	; store return address
	lda $(proc_end)
	sta 0xff

	; 5 / 2
	lda $5
	sta 0xf0
	lda $2
	sta 0xf1
	jmp udiv

proc_end:
	lda 0xe0
	out
	hlt

; unsigned divide
; 0xe0 = 0xf0 / 0xf1
udiv:
	lda $0
	sta 0xe1

	.loop:
		lda 0xf0
		sub 0xf1

		js .end  ; a - b was negative, a < b

		sta 0xf0 ; a -= b

		lda 0xe1 ; out += 1
		add $1
		sta 0xe1
		jmp .loop

	.end:

	lda 0xe1
	sta 0xe0  ; return out

	jmp #0xff ; ret