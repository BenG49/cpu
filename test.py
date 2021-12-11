# a > 0 and b > 0
def divide(a: int, b: int) -> int:
	out = 0
	neg = (a < 0) != (b < 0)

	a = abs(a)
	b = abs(b)

	while a >= b:
		out += 1

		a -= b

	return out * (-1 if neg else 1)

# multiply
def mul(a: int, b: int) -> int:
	if a == 0 or b == 0:
		return 0

	out = 0
	neg = (a < 0) != (b < 0)

	a = abs(a)
	b = abs(b)

	while a > 0:
		out += b
		a -= 1

	return out * (-1 if neg else 1)

def isqrt(n: int) -> int:
	x = 1

	while mul(x, x) <= n:
		x += 1

	return x - 1

print(isqrt(27))
