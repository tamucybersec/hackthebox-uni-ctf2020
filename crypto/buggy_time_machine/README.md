# buggy time machine

```text
I am the Doctor and I am in huge trouble. Rumors have it, you are the best time machine engineer in the galaxy. I recently bought a new randomiser for Tardis on Yquantine, but it must be counterfeit. Now every time I want to time travel, I will end up in a random year. Could you help me fix this? I need to find Amy and Rory! Daleks are after us. Did I say I am the Doctor?
```

## initial review

```python
import os
from datetime import datetime
from flask import Flask, render_template
from flask import request
import random
from math import gcd
import json
from secret import flag, hops, msg

class TimeMachineCore:
	
	n = ...
	m = ...
	c = ...
		

	def __init__(self, seed):
		self.year = seed 

	def next(self):
		self.year = (self.year * self.m + self.c) % self.n
		return self.year

app = Flask(__name__)
a = datetime.now()
seed = int(a.strftime('%Y%m%d')) <<1337 % random.getrandbits(128)
gen = TimeMachineCore(seed)


@app.route('/next_year')
def next_year():
	return json.dumps({'year':str(gen.next())})

@app.route('/predict_year', methods = ['POST'])
def predict_year():
	
	prediction = request.json['year']
	try:

		if prediction ==gen.next():
			return json.dumps({'msg': msg})
		else:
			return json.dumps({'fail': 'wrong year'})

	except:

		return json.dumps({'error': 'year not found in keys.'})

@app.route('/travelTo2020', methods = ['POST'])
def travelTo2020():
	seed = request.json['seed']
	gen = TimeMachineCore(seed)
	for i in range(hops): state = gen.next()
	if state == 2020:
		return json.dumps({'flag': flag})

@app.route('/')
def home():
	return render_template('index.html')
if __name__ == '__main__':
	app.run(debug=True)
```

The first thing I noticed is that TimeMachineCore is a [linear congruential generator](https://en.wikipedia.org/wiki/Linear_congruential_generator).  LCGs are not cryptographically secure so it is highly likely that we will be attacking the randomness.  

We have three routes that we can interact with the time machine with:

* `/next_year` which generates a random number using a TimeMachineCore that was seeded with random bits at the beginning of the program
*  `/predict_year` which will give us the secret variable `msg` if we can predict the number it generates
* `travelTo2020` which will give us the flag if we can provided it a seed which generates `2020` after `hops` random numbers

## cracking LCG parameters

So the first thing to do here is cracking the LCG parameters.  We have the ability to generate and receive an arbitrary number LCG states so it is pretty trivial to reverse engineer what the parameters which generated it are.  I'm not going to go into the math behind how it works, but [Cracking RNGs: Linear Congruential Generators](https://tailcall.net/blog/cracking-randomness-lcgs/) is the article I used if you would like to read about it.  


```python
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
	584293201,
	1514369420,
	1930412587,
	1483060100,
	279230708,
	1138137296,
	2098757662,
	1590055177,
	340421540,
	2090774143,
	617182341
]

print(crack_unknown_modulus(values))
```

```text
❯ python crack_lcg_parameters.py
(2147483647, 48271, 0)
```

## predicting the next year

We know the parameters and the last state so we can just solve for the next year trivially like so: `(617182341 * 48271) mod 2147483647`


```text
❯ curl -X POST http://docker.hackthebox.eu:30263/predict_year --header "Content-Type: application/json"  --data '{"year": 465839415}'
{"msg": "*Tardis trembles*\nDoctor this is Amy! I am with Rory in year 2020. You need to rescue us within exactly 876578 hops. Tardis bug has damaged time and space.\nRemeber, 876578 hops or the universes will collapse!"}
```

## determining what seed gets us to 2020

Fun fact: an LCG is reversible!  I'm not gonna bother with the math but it's a fairly simple function to get the previous state and you can see it in my solution script below.  See [this stackoverflow post](https://stackoverflow.com/questions/2911432/reversible-pseudo-random-sequence-generator) if you're interested in the math.  

```text
❯ curl -X POST http://docker.hackthebox.eu:30263/travelTo2020 --header "Content-Type: application/json"  --data '{"seed": 2113508741}'
{"flag": "HTB{l1n34r_c0n9ru3nc35_4nd_prn91Zz}"}
```

```python
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
```