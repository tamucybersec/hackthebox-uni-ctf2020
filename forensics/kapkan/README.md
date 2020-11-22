# KapKan

We received an email from one of our clients regarding an invoice, with contains an attachment. However, after calling the client it seems they have no knowledge of this. We strongly believe that this document contains something malicious. Can you take a look?

## Solution
change .docx to .zip, unzip

![Image of Unzipped document contents](https://github.com/tamucybersec/hackthebox-uni-ctf2020/blob/main/forensics/kapkan/KapKan1.png)

in /word/document.xml, you find

![Image of contents of document.xml](https://github.com/tamucybersec/hackthebox-uni-ctf2020/blob/main/forensics/kapkan/KapKan2.png)

from decimal yields

`powershell -ep bypass -e SABUAEIAewBEADAAbgA3AF8ANAA1AEsAXwBNADMAXwBoADAAVwBfADEANwBfAHcAMABSAEsANQBfAE0ANAA3ADMAfQA=`

run the command, get the flag:

`HTB{D0n7_45K_M3_h0W_17_w0RK5_M473}`
