; 0xf0 = a
; 0xf1 = b
; ret to 0xff

; uses 0xe0
umul:
	; b == 0 return 0 (optimization)
	lda 0xf1
	add $0
	jz .zero

	lda $0
	sta 0xe0

	.loop:
		lda 0xf0
		sub $1
		js .end  ; if a - 1 < 0: break

		lda 0xe0
		add 0xf1
		sta 0xe0 ; out += b

		lda 0xf0
		sub $1
		sta 0xf0

		jmp .loop

	.end:
		lda 0xe0
		jmp #0xff ; ret

	; return zero
	.zero:
		lda $0
		jmp #0xff
