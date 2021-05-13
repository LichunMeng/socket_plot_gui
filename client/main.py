import socket
import struct
from PyQt5.QtWidgets import *
import atexit
from design import *
import sys

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.plot_data()
        
        self.ip="127.0.0.1"
        self.port_s=5000
        self.port_t=5001
        self.Int=100 #unit us
        self.Scan=100 #unit ms, setting trigger
        self.Sim=100 #unit ns, setting simulation
        
        #UNIT and DATA initiation
        self._socket_s = None
        self._socket_t = None
        self._unit_connected_to = None
        self._unit_connected= False
        self.ui.statusbar.showMessage(f"Software started")
    
    def server_connect(self):
        if self._unit_connect==False:
            try:
                self._socket_r= socket.socket()  # instantiate
                self._socket_r.connect((self.ip, self.port_r))  # connect to the server
                self._socket_s= socket.socket()  # instantiate
                self._socket_s.connect((self.ip, self.port_s))  # connect to the server
                self.ui.IP_line.setEnabled(False)
                self.ui.Port_s_line.setEnabled(False)
                self.ui.Port_r_line.setEnabled(False)
                self.ui.Connect_button.setText("Disconnect")
                self._unit_connected_to = True
                self._unit_connect = True 
                self.ui.statusbar.showMessage(f"server connectted")
            except:

                self.ui.statusbar.showMessage(f"server connect error!")
                self.ui.IP_line.setEnabled(True)
                self.ui.Port_s_line.setEnabled(True)
                self.ui.Port_r_line.setEnabled(True)
                self.ui.Connect_button.setText("Connect")
        else:
            self._socket_r.close()  # instantiate
            self._socket_s.close()  # instantiate
            self.ui.IP_line.setEnabled(True)
            self.ui.Port_s_line.setEnabled(True)
            self.ui.Port_r_line.setEnabled(True)
            self.ui.Connect_button.setText("Connect")
            self._unit_connected_to = False
            self._unit_connect = False 
            self.ui.statusbar.showMessage(f"server disconnectted")


        
    def plot_data(self):
        x=range(0, 10)
        y=range(0, 20, 2)
        self.ui.widget.canvas.ax.plot(x, y)
        self.ui.widget.canvas.draw()
        
        
if __name__ == "__main__":
    #atexit.register(exit_cleanup)
    app = QApplication(sys.argv)
    form = MyApp()
    form.show()
    sys.exit(app.exec_())
