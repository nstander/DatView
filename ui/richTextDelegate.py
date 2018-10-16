# datview/ui/richtextdelegate.py
# Rich text delegate (interprets html)
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QStyledItemDelegate, QTextDocument
    from PyQt5.QtGui import QAbstractTextDocumentLayout
    from PyQt5.QtCore import QSizeF
except ImportError:
    from PyQt4.QtGui import QStyledItemDelegate, QTextDocument, QAbstractTextDocumentLayout
    from PyQt4.QtCore import QSizeF


class RichTextDelegate(QStyledItemDelegate):
    def __init__(self):
        QStyledItemDelegate.__init__(self)

    def paint(self,painter,option,index):
        text=index.data()
        if isinstance(text,str):
            painter.save()
            doc=QTextDocument()
            doc.setHtml(text)
            doc.setPageSize(QSizeF(option.rect.size()))
            painter.setClipRect(option.rect)
            painter.translate(option.rect.x(),option.rect.y())
            doc.documentLayout().draw(painter,QAbstractTextDocumentLayout.PaintContext())
            painter.restore()
        else:
            QStyledItemDelegate.paint(self,painter,option,index)

