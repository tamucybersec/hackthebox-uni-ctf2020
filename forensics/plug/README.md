**Plug**

Opened file in Wireshark. Noticed that all of the protocols were either USB or USBMS, no out of the ordinary protocols.

Did search for the word "HACK" (case sensitive) and found some interesting packets.

Saw that the word "FLAG" often had "PNG" after it in those packets:

![r]

Searched for "PNG" and found a packet with what I believed to be a PNG and copied the data as a hexdump:

![b]

Downloaded that as .png file

Opened in hex editor (Hex Editor Pro (free version)) it showed that there should be a PNG and when I opened in Preview Mode, there was a QR code

![c]


I scanned the QR code with my phone and got: 
HTB{IN73R3S7iNG_Us8_s7UFf}

[r]: https://github.com/AlyssaScience/HTB_UNI2020/blob/main/hacktb_pic.PNG?raw=true
[b]: https://github.com/AlyssaScience/HTB_UNI2020/blob/main/hacktb_pic2.PNG?raw=true
[c]: https://github.com/AlyssaScience/HTB_UNI2020/blob/main/RESOURSE_27.png?raw=true
