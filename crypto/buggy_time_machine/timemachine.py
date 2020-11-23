from functools import reduce
from math import gcd

def egcd(a, b):
    lastremainder, remainder = abs(a), abs(b)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient*x, x
        y, lasty = lasty - quotient*y, y
    return lastremainder, lastx * (-1 if a < 0 else 1), lasty * (-1 if b < 0 else 1)


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise ValueError('modinv for {} does not exist'.format(a))
    return x % m

def crack_unknown_increment(states, modulus, multiplier):
    increment = (states[1] - states[0]*multiplier) % modulus
    return modulus, multiplier, increment

def crack_unknown_multiplier(states, modulus):
    multiplier = (states[2] - states[1]) * modinv(states[1] - states[0], modulus) % modulus
    return crack_unknown_increment(states, modulus, multiplier)


def crack_unknown_modulus(states):
    diffs = [s1 - s0 for s0, s1 in zip(states, states[1:])]
    zeroes = [t2*t0 - t1*t1 for t0, t1, t2 in zip(diffs, diffs[1:], diffs[2:])]
    modulus = abs(reduce(gcd, zeroes))
    return crack_unknown_multiplier(states, modulus)


values = [
    585065537,
    141094830,
    1117894293,
    2053819234,
    1325680659,
    1213377283,
]

n, m, c = crack_unknown_modulus(values)
print("n = %s, m = %s, c = %s" % (n, m, c))

def get_next(num):
	return (num * m) % n

def get_prev(num):
	return modinv(m,n) * num % n

values.append(get_next(values[-1]))
print("predicted year = %s" % values[-1])

hops = 876578

print("seed = %s" % reduce(lambda acc, x: get_prev(acc), [x for x in range(hops)], 2020))
