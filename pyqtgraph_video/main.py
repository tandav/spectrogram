from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys
import time
import signal
import io
import subprocess


import pyqtgraph as pg
import pyqtgraph.exporters

# generate something to export
# plt = pg.plot([1,5,2,4,3])

# create an exporter instance, as an argument give it
# the item you wish to export
# exporter = pg.exporters.ImageExporter(plt.plotItem)

# set export parameters if needed
# exporter.parameters()['width'] = 100   # (note this also affects height parameter)

# save to file
# exporter.export('fileName.png')


f = io.BytesIO()

canvas_width, canvas_height = 1920, 1080

outf = 'tmp.mp4'
cmdstring = ('ffmpeg',
    '-y', '-r', '60', # overwrite, 60fps
    '-s', '%dx%d' % (canvas_width, canvas_height), # size of image string
    '-pix_fmt', 'argb', # format
    '-f', 'rawvideo',  '-i', '-', # tell ffmpeg to expect raw video from the pipe
    '-vcodec', 'mpeg4', outf) # output encoding
p = subprocess.Popen(cmdstring, stdin=subprocess.PIPE)



class Visualizer(QtGui.QWidget):
    def __init__(self):
        super().__init__()

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.setWindowTitle('Signal from stethoscope')
        self.layout = QtGui.QVBoxLayout()

        self.app = QtGui.QApplication(sys.argv)


        self.glayout = pg.GraphicsLayoutWidget()
        # self.view = self.glayout.addViewBox(lockAspect=False)
        self.view = self.glayout.addViewBox(lockAspect=True)
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)
        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], [0, 0, 255, 255], [255, 0, 0, 255]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        # set colormap
        self.img.setLookupTable(lut)
        # self.img.setLevels([-140, -50])
        self.img.setLevels([-50, 20])
        self.layout.addWidget(self.glayout)

        self.setLayout(self.layout)
        self.setGeometry(10, 10, 500, 500)
        self.show() 


        self.frame = 0


        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        # timer.start(0)
        timer.start(1000)
        self.start()



    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()



    def update(self):
        self.img.setImage(np.random.random((100, 100)), autoLevels=True)
        exporter = pg.exporters.ImageExporter(self.view)

        exporter.params.param('width').setValue(1920, blockSignal=exporter.widthChanged)
        exporter.params.param('height').setValue(1080, blockSignal=exporter.heightChanged)

        # exporter.params.param('width').setValue(1920, blockSignal=exporter.widthChanged)
        # exporter.params.param('height').setValue(1080, blockSignal=exporter.heightChanged)

        # exporter.export(f'frames/{self.frame}.png')
        b = exporter.export(toBytes=True).data.tobytes()
        # f.write(b)
        p.stdin.write(b)

        self.frame += 1

        if self.frame == 5:
            p.communicate()
            i = input()
        # exporter = pg.exporters.ImageExporter(self.img)
        # exporter.parameters()['width'] = 100   # (note this also affects height parameter)
        # exporter.parameters()['width'] = 100   # (note this also affects height parameter)
        # exporter.export('fileName.png')
        # sys.exit(1)



# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = Visualizer()
    gui.show()
    app.exec()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
