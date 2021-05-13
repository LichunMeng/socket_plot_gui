import socket
import struct
import matplotlib.pyplot as plt
N=100
fmt='f'*N

def client_program():
    host = socket.gethostname()  # as both code is running on same pc
    port = 5000  # socket server port number
    
    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    data_raw = client_socket.recv(1024,socket.MSG_WAITALL)  # receive response
    data=struct.unpack(fmt,data_raw)
    print(data)
    plt.plot(data)
    plt.show()
    client_socket.close()  # close the connection

if __name__ == '__main__':
    client_program()
