import numpy as np
from PyQt4.QtCore import QObject,pyqtSignal

class DataFilter(QObject):
    filterchange=pyqtSignal()
    activechange=pyqtSignal()

    def __init__(self,keep):
        QObject.__init__(self)
        self.keep = keep
        self.active=True

    def setkeep(self,keep):
        if not np.array_equal(keep,self.keep):
            print ("Filter setkeep",keep)
            self.keep = keep
            self.filterchange.emit()

    def isActive(self):
        return self.active

    def setActive(self,active):
        if active != self.active:
            self.active=active
            self.activechange.emit()

class GroupFilter(DataFilter):
    def __init__(self,shape):
        DataFilter.__init__(self,np.ones(shape,dtype=bool))
        self.shape=shape
        self.children=[]

    def addChild(self,child):
        self.children.append(child)
        child.filterchange.connect(self.onchange)
        child.activechange.connect(self.onchange)
        self.onchange()

    def isActive(self):
        if self.active:
            childActive=False
            for child in self.children:
                childActive |= child.isActive()
            return childActive
        return False

    def onchange(self):
        pass

class AndFilter(GroupFilter):
    def __init__(self,shape):
        GroupFilter.__init__(self,shape)

    def onchange(self):
        print ("And onchange")
        keep=np.ones(self.shape,dtype=bool)
        for child in self.children:
            print ("Child")
            if child.isActive():
                print ("Was active")
                keep &= child.keep
        self.setkeep(keep)

class OrFilter(GroupFilter):
    def __init__(self,shape):
        GroupFilter.__init__(self,shape)

    def onchange(self):
        keep=np.ones(self.shape,dtype=bool)
        for child in self.children:
            if child.isActive():
                keep |= child.keep
        self.setkeep(keep)

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

    def isFieldChangable(self):
        return self.fieldChangeable

    def setFieldChangeable(self,fieldChangeable):
        self.fieldChangeable=fieldChangeable


class BetweenFilter(FieldFilter):
    def __init__(self,minimum,maximum,values,field):
        FieldFilter.__init__(self, (values >= minimum) & (values < maximum),field,values)
        self.minimum=minimum
        self.maximum=maximum

    def setMin(self,minimum):
        self.minimum=minimum
        self.update()

    def setMax(self,maximum):
        self.maximum=maximum
        self.update()

    def setRange(self,minimum,maximum):
        self.minimum=minimum
        self.maximum=maximum
        self.update()
        

    def update(self):
        print ("Between update")
        self.setkeep((self.values >= self.minimum) & (self.values < self.maximum))

class GreaterEqualFilter(FieldFilter):
    def __init__(self,minimum,values,field):
        FieldFilter.__init__(self, values >= minimum,field,values)
        self.minimum=minimum

    def setMin(self,minimum):
        self.minimum=minimum
        self.update()

    def update(self):
        self.setkeep(self.values >= self.minimum)

class LessThanFilter(FieldFilter):
    def __init__(self,maximum,values,field):
        FieldFilter.__init__(self,values < maximum,field,values)
        self.maximum=maximum
        self.values=values

    def setMax(self,maximum):
        self.maximum=maximum
        self.update()

    def update(self):
        self.setkeep(self.values < self.maximum)

class InSetFilter(FieldFilter):
    def __init__(self,allowed,values,field):
        FieldFilter.__init__(self, np.isin(values,allowed),field,values)
        self.allowed=allowed
        self.values=values

    def addAllowed(self,value):
        self.allowed.add(value)
        self.update()

    def removeAllowed(self,value):
        if value in allowed:
            allowed.remove(value)
            self.update()

    def update(self):
        self.setkeep(np.isin(values,allowed))

