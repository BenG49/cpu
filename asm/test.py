def div(a: int, b: int) -> int:
	out = 0
	neg = (a < 0) != (b < 0)

	a = abs(a)
	b = abs(b)

	while a >= b:
		out += 1

		a -= b

	return out * (-1 if neg else 1)

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

def udiv(a: int, b: int) -> int:
	out = 0

	while a >= b:
		out += 1

		a -= b

	return out

def divisible(a: int, b: int) -> bool:
	while a >= b:
		a -= b

	return not a

def umul(a: int, b: int) -> int:
	if b == 0:
		return 0

	out = 0

	while a - 1 >= 0:
		out += b
		a -= 1

	return out

def isqrt(n: int) -> int:
	x = 1

	while mul(x, x) <= n:
		x += 1

	return x - 1

def primes():
	print(2)
	i = 3

	while True:
		if i > 100:
			break

		j = 3
		while True:
			if j == i:
				print(i)
				break

			if divisible(i, j):
				break

			j += 1

		i += 2

primes()
