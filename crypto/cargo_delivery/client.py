import socket

BLOCK_SIZE=16

#HOST, PORT = "localhost", 23333
HOST, PORT = "docker.hackthebox.eu", 32355

received = []

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.recv(1024)
    sock.sendall(bytes("1" + "\n","utf-8"))
    cipher = sock.recv(1024)
    cipher = cipher.strip()
    cipher = bytes.fromhex(cipher.decode()) #Extract cipher

    #Start Oracle padding attack
    keys = [] 
    i = 0
    cipherfake=[0] * 16
    plaintext = [0] * 16
    current = 0
    msg = cipher
    message = ''

    number_of_blocks = int(len(msg)/BLOCK_SIZE)
    blocks = [[]] * number_of_blocks
    for i in (range(number_of_blocks)):
        blocks[i] = msg[i * BLOCK_SIZE: (i + 1) * BLOCK_SIZE]

    for z in range(len(blocks)-1):  #for each message, I calculate the number of block
        for itera in range (1,17): #the length of each block is 16. I start by one because than I use its in a counter
            for v in range(256):
                cipherfake[-itera]=v

                sock.sendall(bytes("2" + "\n","utf-8"))
                sock.recv(1024)
                sock.sendall(bytes((bytes(cipherfake)+blocks[z+1]).hex()+"\n","utf-8"))
                response = sock.recv(1024)
                response = response + sock.recv(1024)
                if b'This is a valid ciphertext!'  in response: #the idea is that I put in 'is_padding_ok' the cipherfake(array of all 0) plus the last block
                                                                 #if the function return true I found the value
                    current=itera
                    plaintext[-itera]= v^itera^blocks[z][-itera]
                    break

            for w in range(1,current+1):
                cipherfake[-w] = plaintext[-w]^itera+1^blocks[z][-w] #for decode the second byte I must set the previous bytes with 'itera+1'


        for i in range(16):
            if plaintext[i] >= 32:
                char = chr(int(plaintext[i]))
                message += char
    
    #print Encoded Message
    print(str.encode(message).decode("utf-8"))
finally:
    sock.close()

