# datview/api/filters.py
# File contains all filters. Filter objects calculate a boolean array of keepable values and do not directly interact with the model.
# Author Natasha Stander

import numpy as np
try:
    from PyQt5.QtCore import QObject,pyqtSignal
except ImportError:
    from PyQt4.QtCore import QObject,pyqtSignal
import lxml.etree as ElementTree

class DataFilter(QObject):
    filterchange=pyqtSignal() # When filtering needs to update, final "keep" changed. 
    activechange=pyqtSignal()
    modelchange=pyqtSignal(object) # When the model needs to update (active or values changed)

    def __init__(self,keep):
        QObject.__init__(self)
        self.keep = keep
        self.active=True
        self.row=0
        self.par=None
        self.invert=False

    def setkeep(self,keep):
        if not np.array_equal(keep,self.keep):
            self.keep = keep
            self.filterchange.emit()

    def getKeep(self):
        if self.invert:
            return np.logical_not(self.keep)
        return self.keep

    def isActive(self):
        return self.active

    def setActive(self,active):
        if active != self.active:
            self.active=active
            self.activechange.emit()
            self.modelchange.emit(self)

    def childcnt(self):
        return 0

    def parent(self):
        return self.par

    def kind(self):
        return ""

    def prettyvals(self):
        return ""

    def hasMin(self):
        return False

    def hasMax(self):
        return False

    def toXML(self,parent):
        pass

    def state(self,row):
        return self.keep[row]

    def setState(self,row,value):
        if self.state(row) != value:
            self.keep[row]=value
            self.filterchange.emit()

    def setInvert(self,invert):
        if invert != self.invert:
            self.invert=invert
            self.filterchange.emit()
        



class GroupFilter(DataFilter):
    beforeAddChild=pyqtSignal(object,object)
    afterAddChild=pyqtSignal()

    def __init__(self,shape):
        DataFilter.__init__(self,np.ones(shape,dtype=bool))
        self.shape=shape
        self.children=[]

    def addChild(self,child):
        self.beforeAddChild.emit(self,child)
        self.children.append(child)
        child.row=len(self.children)-1
        child.par=self
        child.filterchange.connect(self.onchange)
        child.activechange.connect(self.onchange)
        self.onchange()
        self.afterAddChild.emit()

    def isActive(self):
        if self.active:
            childActive=False
            for child in self.children:
                childActive |= child.isActive()
            return childActive
        return False

    def onchange(self):
        pass

    def childcnt(self):
        return len(self.children)

class AndFilter(GroupFilter):
    def __init__(self,shape):
        GroupFilter.__init__(self,shape)

    def onchange(self):
        keep=np.ones(self.shape,dtype=bool)
        for child in self.children:
            if child.isActive():
                keep &= child.getKeep()
        self.setkeep(keep)

    def kind(self):
        return "AND"

    def toXML(self,parent):
        e=ElementTree.SubElement(parent,"and")
        e.set("active",str(self.active))
        for child in self.children:
            child.toXML(e)
        

class OrFilter(GroupFilter):
    def __init__(self,shape):
        GroupFilter.__init__(self,shape)

    def onchange(self):
        keep=np.zeros(self.shape,dtype=bool)
        for child in self.children:
            if child.isActive():
                keep |= child.getKeep()
        self.setkeep(keep)

    def kind(self):
        return "OR"

    def toXML(self,parent):
        e=ElementTree.SubElement(parent,"or")
        e.set("active",str(self.active))
        for child in self.children:
            child.toXML(e)

class FieldFilter(DataFilter):
    def __init__(self,keep,field,values):
        DataFilter.__init__(self,keep)
        self.field=field
        self.values=values

    def setfield(self,field,values):
        self.field=field
        self.values=values
        self.update()

    def update(self):
        pass



class BetweenFilter(FieldFilter):
    def __init__(self,minimum,maximum,values,field):
        FieldFilter.__init__(self, (values >= minimum) & (values < maximum),field,values)
        self.minimum=minimum
        self.maximum=maximum

    def setMin(self,minimum):
        self.minimum=minimum
        self.update()
        self.modelchange.emit(self)

    def setMax(self,maximum):
        self.maximum=maximum
        self.update()
        self.modelchange.emit(self)

    def setRange(self,minimum,maximum):
        self.minimum=minimum
        self.maximum=maximum
        self.update()
        self.modelchange.emit(self)
        

    def update(self):
        self.setkeep((self.values >= self.minimum) & (self.values < self.maximum))

    def kind(self):
        return "Between"

    def hasMin(self):
        return True

    def hasMax(self):
        return True

    def toXML(self,parent):
        e=ElementTree.SubElement(parent,"between")
        e.set("active",str(self.active))
        e.set("min",str(self.minimum))
        e.set("max",str(self.maximum))
        e.set("field",self.field)

class GreaterEqualFilter(FieldFilter):
    def __init__(self,minimum,values,field):
        FieldFilter.__init__(self, values >= minimum,field,values)
        self.minimum=minimum

    def setMin(self,minimum):
        self.minimum=minimum
        self.update()
        self.modelchange.emit(self)

    def update(self):
        self.setkeep(self.values >= self.minimum)

    def kind(self):
        return ">="

    def hasMin(self):
        return True

    def toXML(self,parent):
        e=ElementTree.SubElement(parent,"greaterequal")
        e.set("active",str(self.active))
        e.set("min",str(self.minimum))
        e.set("field",self.field)

class LessThanFilter(FieldFilter):
    def __init__(self,maximum,values,field):
        FieldFilter.__init__(self,values < maximum,field,values)
        self.maximum=maximum
        self.values=values

    def setMax(self,maximum):
        self.maximum=maximum
        self.update()
        self.modelchange.emit(self)

    def update(self):
        self.setkeep(self.values < self.maximum)

    def kind(self):
        return "<"

    def hasMax(self):
        return True

    def toXML(self,parent):
        e=ElementTree.SubElement(parent,"lessthan")
        e.set("active",str(self.active))
        e.set("max",str(self.maximum))
        e.set("field",self.field)

class InSetFilter(FieldFilter):
    def __init__(self,allowed,values,field,decoder):
        FieldFilter.__init__(self, np.in1d(values,list(allowed)),field,values)
        self.allowed=allowed
        self.values=values
        self.decoder=decoder # From number to string

    def addAllowed(self,value):
        self.allowed.add(value)
        self.update()
        self.modelchange.emit(self)

    def removeAllowed(self,value):
        if value in allowed:
            allowed.remove(value)
            self.update()
            self.modelchange.emit(self)

    def update(self):
        self.setkeep(np.in1d(self.values,list(self.allowed)))

    def setAllowed(self,allowed):
        self.allowed=allowed
        self.update()
        self.modelchange.emit(self)

    def kind(self):
        return "In"

    def valuesString(self):
        vals=[]
        for v in self.allowed:
            vals.append(self.decoder(self.field,v))
        return ",".join(vals)

    def toXML(self,parent):
        e=ElementTree.SubElement(parent,"inset")
        e.set("active",str(self.active))
        e.set("field",self.field)
        e.set("set", self.valuesString())


    





