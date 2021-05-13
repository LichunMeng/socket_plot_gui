import numpy as np
import struct
import sys
from time import sleep
from typing import *
import atexit
import pyqtgraph as pg
import pyqtgraph.exporters
import zmq
from sys import platform
from subprocess import call
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ui_mainwindow import Ui_MainWindow

url_worker = "tcp://127.0.0.1:19492"

port_track = 5555
port_track_4beam = 5556
port_unscaled = 5549



class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # COLLECTION
        self._Ymax=4000
        self._old_Ymax=4000
        self._Ymax_enable=False
        self.B1_line=None
        self.B2_line=None
        self.B3_line=None
        self.B4_line=None
        self.B1_std_line=None
        self.B2_std_line=None
        self.B3_std_line=None
        self.B4_std_line=None
        self.B1_std=[]
        self.B2_std=[]
        self.B3_std=[]
        self.B4_std=[]


        # UNIT and DATA
        self._context = zmq.Context()
        self._unit_socket = None
        self._unit_connected_to = None
        self.disconnect()
        self.old_MARK=5

        self.spectrum_timer = QTimer()
        self.spectrum_timer.setSingleShot(True)
        self.spectrum_timer.setInterval(50)
        self.spectrum_timer.timeout.connect(self.update_spectrum)

        self.B1_viewbox = self.ui.B1.getViewBox()
        self.B1_std_viewbox = self.ui.B1_std.getViewBox()
        self.B2_viewbox = self.ui.B2.getViewBox()
        self.B2_std_viewbox = self.ui.B2_std.getViewBox()
        self.B3_viewbox = self.ui.B3.getViewBox()
        self.B3_std_viewbox = self.ui.B3_std.getViewBox()
        self.B4_viewbox = self.ui.B4.getViewBox()
        self.B4_std_viewbox = self.ui.B4_std.getViewBox()
        self.spectrum_timer.start()

        self.show()


    def user_connect_unit(self, connect):
        self._unit_connect = connect

    def Ymax_enable(self,enable):
        self._Ymax=float(self.ui.lineEdit_Ymax.text())
        if self._Ymax!=self._old_Ymax:
            enable=True
            self._old_Ymax=self._Ymax
            self.ui.pushButton_Enable.setDown(True)
        

        if enable:
            self._Ymax_enable=True
            self.ui.pushButton_Enable.setText("Disable")
        else:
            self._Ymax=self._old_Ymax
            self._Ymax_enable=False
            self.ui.pushButton_Enable.setText("Enable")

    def STD_refresh(self):
        self.B1_std=[]
        self.B2_std=[]
        self.B3_std=[]
        self.B4_std=[]

    def disconnect(self):
        if self._unit_socket is not None:
            self._unit_socket.close()
        self._unit_socket_track = self._context.socket(zmq.REQ)
        self._unit_socket = self._context.socket(zmq.SUB)
        self._unit_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self._unit_socket.setsockopt(zmq.CONFLATE, 1)
        # self._unit_socket.setsockopt(zmq.RCVHWM, 1)

        self.ui.pushButton_connect.setEnabled(True)
        self.ui.Ip_input.setEnabled(True)
        self.ui.pushButton_connect.setText("Connect")
        self._unit_connected_to = None
        self._unit_connect = False


        #clean the data !!!!!!!!!!!
        self._Ymax_enable=False
        self._refreshing=False
        self._Ymax=4000
        self.B1_line=None
        self.B2_line=None
        self.B3_line=None
        self.B4_line=None
        self.B1_std_line=None
        self.B2_std_line=None
        self.B3_std_line=None
        self.B4_std_line=None
        self.ui.B1.clear()
        self.ui.B2.clear()
        self.ui.B3.clear()
        self.ui.B4.clear()
        self.ui.B1_std.clear()
        self.ui.B2_std.clear()
        self.ui.B3_std.clear()
        self.ui.B4_std.clear()
        self.B1_std=[]
        self.B2_std=[]
        self.B3_std=[]
        self.B4_std=[]

    def nag_unit(self):
        # This makes the unit start `fpga-data-capture -t`
        self._unit_socket_track.send(b"INFO")
        poller = zmq.Poller()
        poller.register(self._unit_socket_track, flags=zmq.POLLIN)
        if poller.poll(timeout=1000):
            resp = self._unit_socket_track.recv()
            #print(resp)
        else:
            raise zmq.error.ZMQError("Did not receive reply to INFO")


    def update_spectrum(self):

        # Ensure connected/disconnected based on what user has done
        ip = self.ui.Ip_input.text()
        str_unscaled = f"tcp://{ip}:{port_unscaled}"
        str_track = f"tcp://{ip}:{port_track}"
        str_track_4beam = f"tcp://{ip}:{port_track_4beam}"

        if self._unit_connect and self._unit_connected_to != ip: # should be connected, but is not
            self.ui.statusbar.showMessage(f"Connecting to unit")
            try:
                self._unit_socket_track.connect(str_track)
                print("nag1")
                self.nag_unit()
                self._unit_socket.connect(str_track_4beam)
            except Exception as e:
                self.ui.statusbar.showMessage(f"Failed to connect to unit: {e}")
                self.disconnect()
            else:
                self.ui.Ip_input.setEnabled(False)
                self.ui.pushButton_connect.setText("Disconnect")
                self._unit_connected_to = ip
                self.ui.statusbar.showMessage(f"Connected to unit")

        elif not self._unit_connect and self._unit_connected_to is not None: # should be disconnected, but is connected
            self.ui.statusbar.showMessage("Disconnecting from unit")
            self.disconnect()
            self.ui.statusbar.showMessage("Disconnected from unit")


        # Leave if no connection (to be) done
        if self._unit_connected_to is None:
            self.ui.B1.clear()
            self.ui.B2.clear()
            self.ui.B3.clear()
            self.ui.B4.clear()
            self.ui.B1_std.clear()
            self.ui.B2_std.clear()
            self.ui.B3_std.clear()
            self.ui.B4_std.clear()
            self.B1_line=None
            self.B2_line=None
            self.B3_line=None
            self.B4_line=None
            self.B1_std_line=None
            self.B2_std_line=None
            self.B3_std_line=None
            self.B4_std_line=None
            self.B1_std=[]
            self.B2_std=[]
            self.B3_std=[]
            self.B4_std=[]
            self.spectrum_timer.start()
            return

        # Load data
        try:
            data = self._unit_socket.recv(flags=zmq.NOBLOCK)
        except zmq.Again:
            self.ui.statusbar.showMessage("No data received")
            try:
                print("nag2", self._unit_connected_to)
                self.nag_unit()
            except zmq.error.ZMQError:
                self.ui.statusbar.showMessage("Unit stopped responding")
                self.disconnect()
        else:
            try:
                tmp= list(reversed(struct.unpack(252 * "B"+"f", data)))

                #tmp.reverse()

            except Exception as e:
                self.ui.statusbar.showMessage(f"Could not unpack spectrum data: {e}")
            else:
                self.ui.statusbar.showMessage("Data received")
                scal=1/tmp[0]
                MARK=(data[0]>>3)%4+1
                scal_tmp=scal/256
                spectrum=[i*scal_tmp for i in tmp[1:252]]
                if self._Ymax_enable:
                    Max_range=self._Ymax
                else:
                    Max_range=max(spectrum)
                str_m="{:.2f}".format(scal)+', '+str(MARK)

                if MARK==1 and self.old_MARK==1:
                    self.B1_std.append(scal)

                    Range_Max_std=np.max(self.B1_std)
                    Range_min_std=np.min(self.B1_std)
                    self.B1_std_viewbox.setRange(yRange=(Range_min_std*0.7, Range_Max_std*1.2))
                    MEAN=np.mean(self.B1_std)
                    STD=np.std(self.B1_std)
                    Ratio=STD/MEAN*100
                    str_mean="{:.2f}".format(MEAN)+', '
                    str_std="{:.2f}".format(STD)+', '
                    str_ratio="{:.2f}".format(Ratio)+'%. '
                    self.ui.B1_mean_value.setText(str_mean)
                    self.ui.B1_std_value.setText(str_std)
                    self.ui.B1_std_mean_value.setText(str_ratio)

                    self.B1_viewbox.setRange(yRange=(0, Max_range))
                    if self.B1_line is None:
                        self.B1_line = self.ui.B1.plot(range(len(spectrum)), spectrum)
                        self.B1_std_line = self.ui.B1_std.plot(range(len(self.B1_std)), self.B1_std)
                    else:
                        self.B1_line.setData(range(len(spectrum)), spectrum)
                        self.B1_std_line.setData(range(len(self.B1_std)), self.B1_std)
                if MARK==2 and self.old_MARK==2:
                    self.B2_std.append(scal)

                    Range_Max_std=np.max(self.B2_std)
                    Range_min_std=np.min(self.B2_std)
                    self.B2_std_viewbox.setRange(yRange=(Range_min_std*0.70, Range_Max_std*1.2))
                    MEAN=np.mean(self.B2_std)
                    STD=np.std(self.B2_std)
                    Ratio=STD/MEAN*100
                    str_mean="{:.2f}".format(MEAN)+', '
                    str_std="{:.2f}".format(STD)+', '
                    str_ratio="{:.2f}".format(Ratio)+'%. '
                    self.ui.B2_mean_value.setText(str_mean)
                    self.ui.B2_std_value.setText(str_std)
                    self.ui.B2_std_mean_value.setText(str_ratio)

                    self.B2_viewbox.setRange(yRange=(0, Max_range))
                    if self.B2_line is None:
                        self.B2_line = self.ui.B2.plot(range(len(spectrum)), spectrum)
                        self.B2_std_line = self.ui.B2_std.plot(range(len(self.B2_std)), self.B2_std)
                    else:
                        self.B2_line.setData(range(len(spectrum)), spectrum)
                        self.B2_std_line.setData(range(len(self.B2_std)), self.B2_std)
                if MARK==3 and self.old_MARK==3:
                    self.B3_std.append(scal)

                    Range_Max_std=np.max(self.B3_std)
                    Range_min_std=np.min(self.B3_std)
                    self.B3_std_viewbox.setRange(yRange=(Range_min_std*0.70, Range_Max_std*1.2))
                    MEAN=np.mean(self.B3_std)
                    STD=np.std(self.B3_std)
                    Ratio=STD/MEAN*100
                    str_mean="{:.2f}".format(MEAN)+', '
                    str_std="{:.2f}".format(STD)+', '
                    str_ratio="{:.2f}".format(Ratio)+'%. '
                    self.ui.B3_mean_value.setText(str_mean)
                    self.ui.B3_std_value.setText(str_std)
                    self.ui.B3_std_mean_value.setText(str_ratio)

                    self.B3_viewbox.setRange(yRange=(0, Max_range))
                    if self.B3_line is None:
                        self.B3_line = self.ui.B3.plot(range(len(spectrum)), spectrum)
                        self.B3_std_line = self.ui.B3_std.plot(range(len(self.B3_std)), self.B3_std)
                    else:
                        self.B3_line.setData(range(len(spectrum)), spectrum)
                        self.B3_std_line.setData(range(len(self.B3_std)), self.B3_std)
                if MARK==4 and self.old_MARK==4:
                    self.B4_std.append(scal)

                    Range_Max_std=np.max(self.B4_std)
                    Range_min_std=np.min(self.B4_std)
                    self.B4_std_viewbox.setRange(yRange=(Range_min_std*0.70, Range_Max_std*1.2))
                    MEAN=np.mean(self.B4_std)
                    STD=np.std(self.B4_std)
                    Ratio=STD/MEAN*100
                    str_mean="{:.2f}".format(MEAN)+', '
                    str_std="{:.2f}".format(STD)+', '
                    str_ratio="{:.2f}".format(Ratio)+'%. '
                    self.ui.B4_mean_value.setText(str_mean)
                    self.ui.B4_std_value.setText(str_std)
                    self.ui.B4_std_mean_value.setText(str_ratio)

                    self.B4_viewbox.setRange(yRange=(0, Max_range))
                    if self.B4_line is None:
                        self.B4_line = self.ui.B4.plot(range(len(spectrum)), spectrum)
                        self.B4_std_line = self.ui.B4_std.plot(range(len(self.B4_std)), self.B4_std)
                    else:
                        self.B4_line.setData(range(len(spectrum)), spectrum)
                        self.B4_std_line.setData(range(len(self.B4_std)), self.B4_std)
                self.old_MARK=MARK

        finally:
            self.spectrum_timer.start()



def exit_cleanup():
    if platform == 'win32':
        call('powershell.exe -Command {Set-ItemProperty "HKCU:\\Software\\Microsoft\\Windows\\Windows Error Reporting" -Name DontShowUI -Value 0}')

if __name__ == '__main__':
    atexit.register(exit_cleanup)
    if platform == 'win32':
        call('powershell.exe -Command {Set-ItemProperty "HKCU:\\Software\\Microsoft\\Windows\\Windows Error Reporting" -Name DontShowUI -Value 1}')

    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())
