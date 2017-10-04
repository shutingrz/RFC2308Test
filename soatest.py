#!/usr/local/bin/python3.6

import socket

#pip install dnslib
from dnslib import A, SOA, RR, DNSHeader, DNSRecord, QTYPE, RCODE


class SOATestServer():

    def __init__(self, ipaddr):
        self.host = ipaddr
        self.port = 53
        self.ttl = 30
        self.minimum = 15
        self.soaQname = "shutingrz.com."
        self.nsQname = "ns." + self.soaQname
        self.adminQname = "admin." + self.soaQname

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))

        print("Server Started.")

        while True:
            msg, (cliHost, cliPort) = sock.recvfrom(8096)
            print("Received DNS Packet. Client:" + str(cliHost) + ":" + str(cliPort))
            responseData = self.returnSOA(msg)

            if responseData is not None:
                sock.sendto(responseData, (cliHost, cliPort))

    def returnSOA(self, msg):
        query = self.parse(msg)
        response = self.createSOA(query)

        if response.__class__.__name__ == "DNSRecord":
            print("===============================")
            print(response)
            print("===============================")
            return response.pack()
        else:
            return None

    def parse(self, raw):
        return DNSRecord.parse(raw)

    def getQname(self, query):
        return str(query.q.qname)

    def createSOA(self, query):
        responseData = query.reply()
        soarr = RR( self.soaQname,
                    QTYPE.SOA,
                    ttl=self.ttl,
                    rdata=SOA( self.nsQname,
                               self.adminQname,
                               (20170101, 3600, 3600, 3600, self.minimum)
                             )
                  )

        responseData.add_auth(soarr)
        responseData.header.rcode = RCODE.NXDOMAIN

        return responseData


if __name__ == '__main__':
    srv = SOATestServer("192.168.1.2") 
    srv.run()
