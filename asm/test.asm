#include "cpu.asm"

call func
out
hlt

func:
	lda $42
	ret
