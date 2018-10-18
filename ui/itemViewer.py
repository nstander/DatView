# datview/ui/itemViewer.py
# ItemViewer code for ItemViewer.ui
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QWidget, QStyle, QHeaderView, QAbstractItemView
    from PyQt5.QtGui import QKeySequence
    from PyQt5.QtCore import QTimer
    from ui.Ui_ItemViewer5 import Ui_ItemViewer
    qt5=True
except ImportError:
    from PyQt4.QtGui import QWidget, QStyle, QHeaderView, QAbstractItemView, QKeySequence
    from PyQt4.QtCore import QTimer
    from ui.Ui_ItemViewer import Ui_ItemViewer
    qt5=False
from api.datamodel import DataModel
from api.itemmodel import ItemModel
from . import richTextDelegate, crystfelImage

class MyItemViewer(QWidget):
    def __init__(self,dmodel,geom,parent=None):
        QWidget.__init__(self,parent)
        self.ui=Ui_ItemViewer()
        self.ui.setupUi(self)
        self.dmodel=dmodel
        self.model=ItemModel(dmodel, self.orderMode())
        self.model.dataChanged.connect(self.updateFlag)
        
        self.ui.playButton.setIcon(self.ui.playButton.style().standardIcon(QStyle.SP_MediaPlay))
        self.ui.playButton.clicked.connect(self.onPlayPause)
        self.ui.backButton.setIcon(self.ui.backButton.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.ui.backButton.clicked.connect(self.model.previous)
        self.ui.backButton.setShortcut(QKeySequence("Ctrl+P"))
        self.ui.forwardButton.setIcon(self.ui.forwardButton.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.ui.forwardButton.clicked.connect(self.model.next)
        self.ui.forwardButton.setShortcut(QKeySequence("Ctrl+N"))
        self.ui.flagCheckBox.clicked.connect(self.onFlag)
        self.ui.flagCheckBox.setShortcut(QKeySequence("Ctrl+M"))

        self.ui.sortedRadioButton.clicked.connect(self.onOrderModeChange)
        self.ui.randomRadioButton.clicked.connect(self.onOrderModeChange)
        self.ui.originalRadioButton.clicked.connect(self.onOrderModeChange)

        self.ui.tableView.setModel(self.model)
        self.ui.tableView.setItemDelegate(richTextDelegate.RichTextDelegate())
        self.ui.tableView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.ui.rowSpinBox.setIModel(self.model)

        if qt5:
            self.ui.tableView.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        else:
            self.ui.tableView.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)

        imageManager=crystfelImage.CrystfelImage(self.model,self.ui.imageView,geom,self)
        self.timer=QTimer()
        self.timer.setInterval(dmodel.cfg.playtime)
        self.timer.timeout.connect(self.model.next)

    def orderMode(self):
        if self.ui.sortedRadioButton.isChecked():
            return 1
        elif self.ui.randomRadioButton.isChecked():
            return 2
        else:
            return 0

    def onOrderModeChange(self):
        self.model.setOrderMode(self.orderMode())

    def onPlayPause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.ui.playButton.setIcon(self.ui.playButton.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.timer.start()
            self.ui.playButton.setIcon(self.ui.playButton.style().standardIcon(QStyle.SP_MediaPause))

    def onFlag(self):
        self.dmodel.flagFilter.setState(self.model.currow,self.ui.flagCheckBox.isChecked())

    def updateFlag(self):
        self.ui.flagCheckBox.setChecked(self.dmodel.flagFilter.state(self.model.currow))
            
        
        


        
