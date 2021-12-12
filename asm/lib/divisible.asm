; 0xf0 = a
; 0xf1 = b
; ret to 0xff
divisible:
	.loop:
		lda 0xf0
		sub 0xf1

		js .end  ; a - b was negative, a < b

		sta 0xf0 ; a -= b

		jmp .loop

	.end:
		lda 0xf0
		add $0
		jz .true

		lda $0
		jmp #0xff ; ret

	.true:
		lda $1
		jmp #0xff
