import socket
import sys
    

my_cash =0
securites =[]

def run(*commands):
    HOST, PORT = "codebb.cloudapp.net", 17429
    data="Team4" + " " + "1234a" + "\n" + "\n".join(commands) + "\nCLOSE_CONNECTION\n"
    global sock
    #print "somthing"
    return_lines = []
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((HOST, PORT))
        sock.sendall(data)
        sfile = sock.makefile()
        rline = sfile.readline()
        while rline:
           # print(rline.strip())
            return_lines.append(rline.strip())
            rline = sfile.readline()
    finally:
        sock.close()

    return return_lines

def subscribe(user, password):
    HOST, PORT = "codebb.cloudapp.net", 17429
    
    data=user + " " + password + "\nSUBSCRIBE\n"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((HOST, PORT))
        sock.sendall(data)
        sfile = sock.makefile()
        rline = sfile.readline()
        while rline:
            print(rline.strip())
            rline = sfile.readline()
    finally:
        sock.close()


def get_cash():
  global my_cash
  my_cash = float(run("MY_CASH")[0].split()[1])


def autorun():
    get_cash()
    get_securities()
    print my_cash

def get_securities():
    temp=run("SECURITIES")[0].split()[1:]
    for i in range(len(temp)/4):
        securites[temp[4*i]] = (float(temp[4*i+1]), float(temp[4*i+2]), float(temp[4*i+3]))

autorun()
