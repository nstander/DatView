# datview/api/groupmgr.py
# Read-only management of a group file. 
# Author Natasha Stander

class GroupMgr:
    prefix="g_"
    def __init__(self,groupfile,loadmatches=False):
        self.gmaps={}
        self.load(groupfile,loadmatches)

    def load(self,groupfile,loadmatches=False):
        with open(groupfile) as fin:
            line = fin.readline() # skip header line
            while True:
                line = fin.readline()
                if not line:
                    break
                fields = list(filter(None,line.strip().split('\t')))
                assert len(fields) == 5 # proper group file formats have 5 non-empty fields
                # Columns should be: group	id	value	matchcol	matchvals
                if fields[0] not in self.gmaps:
                    self.gmaps[fields[0]]={}
                    self.gmaps[fields[0]]["value"]={}
                    self.gmaps[fields[0]]["gid"]={}
                    self.gmaps[fields[0]]["matches"]={}
                self.gmaps[fields[0]]["value"][fields[2]]=int(fields[1])
                self.gmaps[fields[0]]["gid"][int(fields[1])]=fields[2]
                self.gmaps[fields[0]]["matchcol"]=fields[3]

                if loadmatches:
                    mtchs = set()
                    if fields[4][0] == '@':
                        # This field is a file that should be read.
                        with open(fields[4][1:]) as f:
                            mtchs.update(f.read().splitlines()) # Use splitlines instead of readlines to avoid \n characters
                    else:
                        for mtch in filter(None,fields[4].split(',')):
                            try:
                                mtch=int(mtch)
                            except ValueError:
                                pass
                            mtchs.add(mtch)
                    self.gmaps[fields[0]]["matches"][int(fields[1])]=mtchs


    def gid(self,group,value):
        """Return the id for a given group and value. Example: for sample,Phyco return 1"""
        return self.gmaps[group]["value"][value]

    def value(self,group,gid):
        """Return the value associated with group and gid. Example: for sample,1 return Phyco"""
        return self.gmaps[group]["gid"].get(gid,"Unknown")

    def values(self,group):
        """Return the list of values associated with group, index is gid. So, for sample, could by ["PSII","Phyco"]"""
        return sorted(self.gmaps[group]["value"],key=self.gmaps[group]["value"].__getitem__)

    def groups(self):
        """Return list of all groups managed by this manager"""
        return self.gmaps.keys()

    def matchcol(self,group):
        """Return the matchcol to use for a particular group, like "run" for "sample" """
        return self.gmaps[group]["matchcol"]

    def match(self,group,matchcolval):
        """Return the gid for a given matchcol. """
        try:
            matchcolval=int(matchcolval)
        except ValueError:
            pass

        for k,v in self.gmaps[group]["matches"].items():
            if matchcolval in v:
                return k
        return -1






