import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import socket
import struct
from PyQt5.QtWidgets import *
import atexit
from design import *
import sys
from pqueue import Queue
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.Ctl_timer = QTimer()
        self.Ctl_timer.setSingleShot(True)
        self.Ctl_timer.setInterval(50)
        self.Ctl_timer.timeout.connect(self.Ctl_loop)
        self.Ctl_timer.start()
        
        self.N=1024*8
        self.fmt_r='I'*self.N*2

        self.ip="192.168.1.2"
        self.port_s=8889
        self.port_r=8888
        self.Int=500 #unit us
        self.Scan=5000000 #unit ms, setting trigger
        self.Sim=50 #unit ns, setting simulation
        self.counter=0
        #UNIT and DATA initiation
        self._socket_s = None
        self._socket_t = None
        self._unit_connected_to = None
        self._unit_connected= False
        self.para_changed() 

        self.line,=self.ui.widget.canvas.ax.plot([1],[1],'r.',markersize=0.1)
        self.ui.widget.canvas.ax.set_ylim(-1,1)
        self.ui.widget.canvas.ax.set_xlim(0,100)

        self.ui.widget.canvas.draw()
        self.ui.statusbar.showMessage(f"Software started")
    def para_changed(self):
        self.ip=self.ui.IP_line.text()
        self.port_s=int(self.ui.Port_s_line.text())
        self.port_r=int(self.ui.Port_r_line.text())
        self.Int=int(self.ui.Int_line.text())*50
        self.Scan=int(self.ui.Scan_line.text())*50000
        self.Sim=int(int(self.ui.Sim_line.text())/20)
        if self._unit_connected:
            self.Pls_control()

    def Pls_control(self):
        i=0
        if i!=1:
            i=self.Pls_control_handler()

    def Pls_control_handler(self):
        fmt_tran='I'*3
        mark=0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._socket_s:
            tran_raw=struct.pack(fmt_tran,self.Int,self.Scan,self.Sim)
            try:
                self._socket_s.connect((self.ip, self.port_s))
                self._socket_s.sendall(tran_raw)
                self._socket_s.settimeout(1.0)
                mark=self._socket_s.recv(4)
                if mark==b'':
                    mark=self._socket_s.recv(4)
                return 0
            except Exception as e:
                self.ui.statusbar.showMessage(f"control data send failed")
                self._socket_s.close()
                return 0
            self.ui.statusbar.showMessage(f"control data sended")
        self._socket_s.close()
        return 1

    def server_connect(self):
        if self._unit_connected==False:
            try:
                self._socket_r= socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
                self._socket_r.connect((self.ip, self.port_r))  # connect to the server
                #self._socket_s= socket.socket()  # instantiate
                #self._socket_s.connect((self.ip, self.port_s))  # connect to the server
                self.ui.IP_line.setEnabled(False)
                self.ui.Port_s_line.setEnabled(False)
                self.ui.Port_r_line.setEnabled(False)
                self.ui.Connect_button.setText("Disconnect")
                self._unit_connected_to = True
                self._unit_connected = True 
                self.ui.statusbar.showMessage(f"server connected")
                self.Pls_control()
            except Exception as ex:
                self._unit_connected_to =False
                self._unit_connected =False 

                self.ui.statusbar.showMessage(ex.message)
                #self.ui.statusbar.showMessage(f"server connect error!")
                self.ui.IP_line.setEnabled(True)
                self.ui.Port_s_line.setEnabled(True)
                self.ui.Port_r_line.setEnabled(True)
                self.ui.Connect_button.setText("Connect")
        else:
            self.counter=0
            self._socket_r.close()  # instantiate
            #self._socket_s.close()  # instantiate
            self.ui.IP_line.setEnabled(True)
            self.ui.Port_s_line.setEnabled(True)
            self.ui.Port_r_line.setEnabled(True)
            self.ui.Connect_button.setText("Connect")
            self._unit_connected_to = False
            self._unit_connected = False 
            self.ui.statusbar.showMessage(f"server disconnectted")

    def Ctl_loop(self):
        while self._unit_connected:
            if self._unit_connected_to:
                self.ui.statusbar.showMessage(f"data receiving")
                data_raw = self._socket_r.recv(8*self.N,socket.MSG_WAITALL)  # receive response
            else:
                self._socket_r= socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
                self._socket_r.connect((self.ip, self.port_r))  # connect to the server
                self.ui.statusbar.showMessage(f"data receiving")
                data_raw = self._socket_r.recv(8*self.N,socket.MSG_WAITALL)  # receive response
            self.ui.statusbar.showMessage(f"data received")
            data=struct.unpack(self.fmt_r,data_raw)
            self.plot_data(data)
            self._socket_r.close()
            self._unit_connected_to=False
        self.Ctl_timer.start()
        
    def plot_data(self,data):
        si=2147483648;
        x=[]
        y=[]
        for i in range(self.N):
            x.append(data[i*2])
            y.append(data[i*2+1])
        y=np.array(y)
        I=y>si
        y[I]=y[I]-si
        x=np.array(x)*20e-6
        ##self.ui.statusbar.showMessage(f"data plotting, "+str(self.counter))
        ##self.counter=self.counter+1
        self.ui.widget.canvas.ax.set_ylim(0,np.max(y)*1.2)
        self.ui.widget.canvas.ax.set_xlim(0,self.Scan*20e-6)
        ##self.line.set_ydata(y)
        ##self.line.set_xdata(x)
        ##self.ui.widget.canvas.draw()
        ##self.ui.widget.canvas.flush_events()
        II=np.where(np.diff(x)<0)[0]
        III=[0]
        for i in II:
            III.append(i)
        III.append(len(y)-1)
        sl=len(II)+1;
        print(II)
        for i in range(sl): 
            xx=x[III[i]:III[i+1]]
            yy=y[III[i]:III[i+1]]
            self.line.set_ydata(y)
            self.line.set_xdata(x)
            self.ui.widget.canvas.draw()
            self.ui.widget.canvas.flush_events()
            self.ui.statusbar.showMessage(f"data plotting, "+str(self.counter))
            self.counter=self.counter+1
        
        
if __name__ == "__main__":
    #atexit.register(exit_cleanup)
    app = QApplication(sys.argv)
    form = MyApp()
    form.show()
    sys.exit(app.exec_())
