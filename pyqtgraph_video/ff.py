from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.ptime import time
import subprocess
import io



canvas_width, canvas_height = 1920, 1080

shape = canvas_width, canvas_height

outf = 'tmp.mp4'

cmd = ('ffmpeg',
    # '-hwaccel', 'videotoolbox', '-threads', '8',
    # '-hwaccel', 'videotoolbox', '-threads', '16',
    '-y', '-r', '60', # overwrite, 60fps
    '-s', f'{canvas_width}x{canvas_height}', # size of image string
    '-pix_fmt', 'argb', # format
    # '-pix_fmt', 'yuv420p', # format
    '-f', 'rawvideo',
    '-i', '-', # tell ffmpeg to expect raw video from the pipe
    '-c:v', 'hevc_videotoolbox', '-profile:v', 'main10', '-tag:v', 'hvc1', '-b:v', '1M', '-an', '-sn', outf)

    # '-vcodec', 'h264_videotoolbox', '-profile:v', 'high', outf) # output encoding

# ffmpeg -i [input_file] -c:v hevc_videotoolbox -profile:v main10 -tag:v hvc1 -b:v 10000k -an -sn output_filename.mp4

p = subprocess.Popen(cmd, stdin=subprocess.PIPE)





pg.setConfigOptions(antialias=True)

app = QtGui.QApplication([])

dims = 1280, 720
nsamp = 1102  # 25ms of 44100smp/s, subsampling=1
ndat = 50
data = np.random.normal(size=(ndat, nsamp))

p = pg.PlotWidget()
p.setWindowTitle('pyqtgraph example: PlotSpeedTest')
p.setRange(QtCore.QRectF(0, -10, nsamp-1, 20), padding=0)
# p.setLabel('bottom', 'Index', units='B')

p.resize(*dims)
p.centralWidget.resize(*dims)

p.plotItem.hideAxis('left')
p.plotItem.hideAxis('bottom')


curve = p.plot()

# curve.setFillBrush((0, 0, 100, 100))
# curve.setFillLevel(0)

# lr = pg.LinearRegionItem([100, 4900])
# p.addItem(lr)

ptr = 0
lastTime = time()
fps = None


def update():
    global curve, data, ptr, p, lastTime, fps
    curve.setData(data[ptr % ndat])
    ptr += 1
    now = time()
    dt = now - lastTime
    lastTime = now
    if fps is None:
        fps = 1.0 / dt
    else:
        s = np.clip(dt * 3., 0, 1)
        fps = fps * (1 - s) + (1.0 / dt) * s
    print('%0.2f fps' % fps)
    app.processEvents()  ## force complete redraw for every plot


# The QPixmap is stored on the video card doing the display. Not the QImage.
QImage = QtGui.QImage
Format = QtGui.QImage.Format


class LolExporter(pg.exporters.Exporter):
    """ based off pg ImageExporter.
    Design decisions:
    - Optimized for speed when repeatedly calling export() on the same plot.
    - Assumes widgets will never be drawn to screen.
        - Does not call self.setExportMode(False).
          Widgets will remain in export mode.
    - Do not change params.width/height,
      instead resize the GraphicsView and GraphicsWidget to the right size
      before constructing exporter.
    - TODO handle issues where screen DPI != 96.
    """

    def __init__(self, item, format: Format = QImage.Format_RGB32):
        """
        render(QPainter(image type?)):
        - Drawing on QPixmap is fastest, 300fps or more (but is stored on GPU).
        - Adding QPixmap.toImage() is same speed as QImage.
            - I avoid, since it allocates and discards many images, and QImage doesn't?
        - Drawing on makeQImage() is slow.
        - Drawing on QImage depends on format...
        format:
        - Format_RGB32 = 280fps or less
        - Format_ARGB32 = 150fps or less
        - Format_RGB888 = 110fps
        RGB32 is fastest.
        Clearing per frame:
        - upstream buf[:,:,0] = color.red() is slow.
        - broadcast buf[:] = [r,g,b,a] is slower.
        - QImage.fill(color) is near-instant.
        setExportMode is slow.
        - Called every frame: 180fps
        - Called once: 250fps
        - Not called: 200fps (it used to be higher)
        """
        super().__init__(item)
        self.format = format

        tr = self.getTargetRect()
        if isinstance(item, QtGui.QGraphicsItem):
            scene = item.scene()
        else:
            scene = item
        bgbrush = scene.views()[0].backgroundBrush()
        bg = bgbrush.color()
        if bgbrush.style() == QtCore.Qt.NoBrush:
            bg.setAlpha(0)

        self.params = pg.parametertree.Parameter(name='params', type='group', children=[
            {'name': 'width', 'type': 'int', 'value': int(tr.width()), 'limits': (0, None)},
            {'name': 'height', 'type': 'int', 'value': int(tr.height()), 'limits': (0, None)},
            {'name': 'antialias', 'type': 'bool', 'value': True},
            {'name': 'background', 'type': 'color', 'value': bg},
        ])

        # width and height control each other.
        # aspect ratio = self.getSourceRect().h,w.
        self.params.param('width').sigValueChanged.connect(self.widthChanged)
        self.params.param('height').sigValueChanged.connect(self.heightChanged)

    def widthChanged(self):
        sr = self.getSourceRect()
        ar = float(sr.height()) / sr.width()
        self.params.param('height').setValue(int(self.params['width'] * ar), blockSignal=self.heightChanged)

    def heightChanged(self):
        sr = self.getSourceRect()
        ar = float(sr.width()) / sr.height()
        self.params.param('width').setValue(int(self.params['height'] * ar), blockSignal=self.widthChanged)

    def parameters(self):
        return self.params

    qimage: QImage = None
    painter: QtGui.QPainter = None

    def export(self) -> QImage:
        targetRect = QtCore.QRect(0, 0, self.params['width'], self.params['height'])
        sourceRect = self.getSourceRect()

        if self.qimage is None:
            w, h = self.params['width'], self.params['height']
            if w == 0 or h == 0:
                raise Exception("Cannot export image with size=0 (requested export size is %dx%d)" % (w,h))
            self.qimage = QImage(w, h, self.format)

            origTargetRect = self.getTargetRect()
            resolutionScale = targetRect.width() / origTargetRect.width()
            assert resolutionScale == 1

            self.painter = QtGui.QPainter(self.qimage)
            self.setExportMode(True, {
                'antialias': self.params['antialias'],
                'background': self.params['background'],
                'painter': self.painter,
                'resolutionScale': resolutionScale,
            })
            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, self.params['antialias'])

        color = self.params['background']
        self.qimage.fill(color)

        # self.painter writes to self.qimage
        self.getScene().render(self.painter, QtCore.QRectF(targetRect), QtCore.QRectF(sourceRect))
        return self.qimage


e = LolExporter(p.scene())
for i in range(600):
    # QApplication.processEvents() is called twice.
    # removing 1 or both calls does not affect performance.
    update()
    img: QImage = e.export()
    # img.save('speed.png')

    # b = img.data.tobytes()

    print(hasattr(img, 'data'))
    # p.stdin.write(b)
p.communicate()


