#Copyright 2011 Kurtis Heimerl <kheimerl@cs.berkeley.edu>. All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are
#permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, this list of
#      conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this list
#      of conditions and the following disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY Kurtis Heimerl ''AS IS'' AND ANY EXPRESS OR IMPLIED
#WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Kurtis Heimerl OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#The views and conclusions contained in the software and documentation are those of the
#authors and should not be interpreted as representing official policies, either expressed
#or implied, of Kurtis Heimerl.

import messaging.sms.submit
import random

#converts an integer to hex form (with 2 digits)
def to_hex2(i):
    tmp = hex(i)[2:]
    if (len(tmp) == 1):
        return "0" + tmp
    else:
        return tmp

#Given a number, encodes a 3GPP string to represent it
def encode_num(num):
    #jumble the number. i.e. 123 --> "321f"
    snuml = list(str(num))
    if len(snuml)%2 == 1:
        snuml += 'f'
    for i in range(len(snuml)):
        if (i%2 == 0):
            snuml[i],snuml[i+1] = snuml[i+1],snuml[i]

    enc_num = (
      to_hex2(len(str(num)))  #length of number
    + "81"                 #use undefined numbering type
    + ''.join(snuml))

    return enc_num

#Generates the TPDU
def gen_tpdu(ref, to, text, empty):
    if empty:
        text = ""

    TPPID = "40" if empty else "00" #TP-PID = 40 ==> short message type 0
    TPDCS = "c3" if empty else "00" #TP-DCS = c3 ==> disable "other message indicator" and discard message
    tpdu_header = (
      "11"           #SMS-Submit: 
    + ref            #Message reference
    + encode_num(to) #Destination number
    + TPPID
    + TPDCS)
    + "ff")          #TP-validity-period = 63 weeks (maximum) to ensure delivery

    #use python-messaging to get the payload
    user_data = messaging.sms.submit.SmsSubmit("123",text).to_pdu()[0].pdu
    user_data = user_data[18:] #cut off the header generated by python-messaging

    tpdu = tpdu_header + user_data
    return tpdu

#Generates the RP-header. If 'empty' is true, generates for Empty SMS
def gen_rp_header(ref, empty):
    rp_header = (
      "01"              #Message Type = n->ms
    + ref               #Message Reference
    + "00"              #RP-originator Address IEI for outgoing messages
    + "03919999")       #RP-destination address for Service Center (I think it is ignored)
    return rp_header

#Generates the RPDU
def gen_msg(to, text, empty=False):
    #note we are constructing a RPDU which encapsulates a TPDU
    ref = str(to_hex2(random.randint(0,255))) #random reference?
    rp_header = gen_rp_header(ref, empty)
    tpdu = gen_tpdu(ref, to, text, empty)
    tp_len = len(tpdu)/2 #in octets
    body = rp_header + to_hex2(tp_len) + tpdu
    return body

if __name__ == '__main__':
    to = "101"
    msg = "Test Message"
    if (len(sys.argv) > 2):
        to = sys.argv[1]
        msg = sys.argv[2]
    
    print (gen_msg(to, msg))
