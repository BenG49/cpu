#include "cpu.asm"

; no stack, uses address 0xff as return address, no nested calls
; return in a
; args: 0xf0-fe

; scratch memory:
; 0xe0-ef

; print 2
lda $2
out

lda $3
sta 0xee ; i = 3

loop:
	lda 0xee
	sub $100
	jns end

	lda $3
	sta 0xef

	.l:
		lda 0xef
		sub 0xee
		jz .prime

		lda $(.ret)
		sta 0xff

		lda 0xee
		sta 0xf0

		lda 0xef
		sta 0xf1

		jmp divisible

		.ret:

		add $0
		jnz .l_end ; if divisible != 0

		lda 0xef
		add $1
		sta 0xef

		jmp .l

	.prime:
		lda 0xee
		out

	.l_end:

	lda 0xee
	add $2
	sta 0xee ; i += 2

	jmp loop

end:

hlt

#include "lib/divisible.asm"
