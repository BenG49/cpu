; 0xf0 = a
; 0xf1 = b
; ret to 0xff
udiv:
	lda $0
	sta 0xe0

	.loop:
		lda 0xf0
		sub 0xf1

		js .end  ; a - b was negative, a < b

		sta 0xf0 ; a -= b

		lda 0xe0 ; out += 1
		add $1
		sta 0xe0
		jmp .loop

	.end:
		lda 0xe0
		jmp #0xff ; ret
