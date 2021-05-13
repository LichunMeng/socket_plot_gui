import zmq
import numpy as np
import matplotlib.pyplot as plt 
import struct 
import datetime
from time import gmtime, strftime
def ZMQ_Data(IP_add, PLOT=1, IMSAVE=0,NAME='spec',Length=5):
    port = 5556
    port_str="tcp://"+IP_add+":%s" 
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.connect (port_str % port)
    fmt1='B'+251*"B"+"f"
    fmt2=256*"l"
    ss=socket.recv(0)
    t_data=struct.unpack(fmt1,ss)
    LEN=len(t_data)
    M=[]
    plt.ion()
    if LEN==253:
        for i in range(Length):
            ss=socket.recv(0)
            t_data=struct.unpack(fmt1,ss)
            Data=t_data[1:252]
            scal=t_data[252]
            Data=np.array(Data)/scal
            M.append(Data)
            print(str(t_data[0]))
            if PLOT:
                plt.plot(Data)
                plt.show()
                plt.pause(0.0001)
                plt.clf()
    else:
        for i in range(Length):
            ss=socket.recv(0)
            t_data=struct.unpack(fmt2,ss)
            Data=t_data[1:252]
            M.append(Data)
            if PLOT:
                plt.plot(Data)
                plt.show()
                #plt.pause(0.001)
                plt.clf()
    if IMSAVE:
        if len(M)>0:
            ss=strftime("%Y%m%d_%H%M%S", gmtime())
            np.savetxt(NAME+ss+'.csv',M)
    return M


def main():
    IP_add="172.16.3.33"
    #IP_add="192.168.0.5"
    name="No_filterLP900_1273_beam2"
    OFFSET=54.2
    name="10m_fiber"
   # Length=8000
    ZMQ_Data(IP_add,PLOT=0,NAME=name,IMSAVE=0,Length=1000)
    #ZMQ_Data(IP_add, NAME, IMSAVE,Length)
  
if __name__== "__main__":
  main()
