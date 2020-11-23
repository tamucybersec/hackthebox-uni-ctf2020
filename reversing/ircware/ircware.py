from string import printable

def mutate(c):
	if c < 0x41:
		return c
	if c > 0x5a:
		return c
	c += 0x11
	if c <= 0x5a:
		return c
	c -= 0x5a
	c += 0x40
	return c

comp = "RJJ3DSCP"

for i in range(8):
	for j in printable:
		if chr(mutate(ord(j))) == comp[i]:
			print(j,end='')

# print(''.join([chr(mutate(ord(x))) for x in ]))