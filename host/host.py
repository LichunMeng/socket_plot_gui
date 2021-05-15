
import socket
import numpy as np
import struct
N=100
x=np.linspace(0,10*np.pi,N)
def server_program():
    # get the hostname
    host = "127.0.0.1"
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    while True:
        conn, address = server_socket.accept()  # accept new connection
        while True:
            try:
                y=np.sin(x+np.random.random()*2*np.pi)
                pck=struct.pack('f'*N,*y)
                conn.send(pck)  # send data to the client
            except:
                break;
        conn.close()  # close the connection


if __name__ == '__main__':
    server_program()
