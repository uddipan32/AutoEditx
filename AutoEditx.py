import os
import cv2
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from Xml_Generate import Xml_Generate

files = []

def getfile():
      global dir
      global files
      global total_duration
      total_duration = 0.0
      dir = str(QtWidgets.QFileDialog.getExistingDirectory())
      ext = [".MOV",".mov", ".mp4",".MP4", ".MTS", ".mts" ,".m4v", ".M4V",".AVI",".avi"]
      files = [f for f in os.listdir(dir) if f.endswith(tuple(ext))]
      dlg.listWidget.addItems(files)
      total_file = len(files)
      i=0
      for file in files: 
            i += 1
            path = dir+'/'+ file
            v=cv2.VideoCapture(path)
            fps = v.get(cv2.CAP_PROP_FPS)
            frame_count = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
            if(fps!=0):
                  duration = frame_count/fps
                  total_duration += duration
            else:
                  dlg.lineEdit_Totalduration.setText('can not count')
            dlg.progressBar.setValue((i/total_file)*100)
      dlg.lineEdit_fps.setText(str(int(fps)))
      min = str(int(total_duration/60))
      sec = str(int(total_duration%60))   
      msec = total_duration%1   
      msec = int(round(msec,2))
      dlg.lineEdit_Totalduration.setText(min+' : '+sec+' : '+ str(msec))
def close():
      quit()


xmlgenerate = Xml_Generate()
app = QtWidgets.QApplication([])
dlg = uic.loadUi("AutoEditx.ui")
dlg.progressBar.setValue(0)
dlg.B_import.clicked.connect(getfile)
dlg.B_generate.clicked.connect(lambda:xmlgenerate.xml_prj(dir , files, dlg))
dlg.B_Cancel.clicked.connect(close)



dlg.show()
app.exec()
   
