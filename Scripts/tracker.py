from bge import logic
from math import sqrt, radians
import copy
import collections
import blf #редактирование текста #для prt можно ещё использовать textwrap
import structs

scene = logic.getCurrentScene()
computer = scene.objects['Computer']

#инициализация
# !!!! подумать над тем чтобы убрать в конструктор
# в cmputer -> tracker['Interfaces'] = trackerInterfaces(tracker)
def init(cont):
    own = cont.owner
    own['Grid Loc'] = None
    own['Interfaces'] = trackerInterfaces(own)
    own.visible = False
    print('---> Tracker initiated!')
    unit = computer['Interfaces'].getPlayerUnit()
    pgInterf = unit['Interfaces'].getPGinterfaces()
    #Play Ground для перемещения
    moveToPlayGround = own['Clicked Play Ground']
    if pgInterf.getUnitType() == structs.UnitType['Soldier']:
        cursorPos = moveToPlayGround['Interfaces'].objGridPosition(own['Cursor World Position'])
        own.worldPosition = moveToPlayGround['Interfaces'].getCoorByGridPos(cursorPos[0], cursorPos[1])
        pgInterf.setCursorPosAndFinalPlayGround(cursorPos, moveToPlayGround, own)
        calcPathThread = computer['Interfaces'].getThread()
        calcPathThread.setProcessingFlagOn(pgInterf.calcPathInThread)
        #
        #path = pgInterf.calcPath(cursorPos, moveToPlayGround)
        #pathProcessing(cont, path)
    elif pgInterf.getUnitType() == structs.UnitType['Mech']:
        pass
        #calcPath(cont)
  
MoveDirection = {'Straight' : 0, 'Diagonal' : 1}
        
class trackerInterfaces(object):
    def __init__(self, tracker):
        """Constructor"""
        self.__tracker = tracker
        self.__pathFound = False
        #работа по тексту
        self.__APcount = self.__tracker.groupObject.groupMembers['AP Count']
        self.__APcount.resolution = 5
        #
        self.__pathPoints = None
        #
        self.__reqAP = 0
        

    def updateUnitPath(self):
        unit = computer['Interfaces'].getPlayerUnit()
        pgInterf = unit['Interfaces'].getPGinterfaces()
        pgInterf.setMoveState()

    
    def pathProcessing(self, path, reqAP):
        if path == None:
            self.removeTracker()
            return
        #отображаемвые точки
        self.__pathPoints = []
        maxStepId = len(path) - 1
        for idx, playGroundTileGridCoor in enumerate(path):
            if  (idx == 0) or (idx == maxStepId):
                continue
            pointName = 'Move Point'
            point = scene.addObject(pointName)
            playGround = playGroundTileGridCoor[0]
            tileGridCoor = playGroundTileGridCoor[1]
            point.worldPosition = playGround['Interfaces'].getCoorByGridPos(tileGridCoor[0], tileGridCoor[1])
            self.__pathPoints.append(point)
            self.__tracker['Interfaces'].setReqAP(reqAP)
        self.__tracker.visible = True
        #unit = computer['Interfaces'].getPlayerUnit()
        #pgInterf = unit['Interfaces'].getPGinterfaces()
        #pgInterf.setDisplayPathPoints(pathPoints)#!!!
        #self.removeTracker()
        
    def removePathPoint(self):
        pointsCount = len(self.__pathPoints)
        if pointsCount > 0:
            currentPoint = self.__pathPoints.pop(0)
            currentPoint.endObject()
            return self.__tracker
        else:
            self.removeTracker()
            return None
    
    def setReqAP(self, reqAP):
        self.__reqAP = reqAP
        self.__APcount.text = str(self.__reqAP)
        fontSize = 22
        textSize = len(str(self.__reqAP)) * fontSize
        self.__APcount.localPosition.x = - (textSize / 2.0) * .005
        self.__APcount.visible = True
        self.__tracker.worldOrientation = scene.objects['Camera Control Rotation Main'].worldOrientation
            
    def updateAP(self, ap):
        self.__reqAP -= ap
        self.__APcount.text = str(self.__reqAP)
        fontSize = 22
        textSize = len(str(self.__reqAP)) * fontSize
        self.__APcount.localPosition.x = - (textSize / 2.0) * .005
    
    def removeTracker(self):
        self.__APcount.endObject()
        self.__tracker.endObject()
        computer['Tracker exist'] = False
        print('--> Tracker removed!')
    
    def setPathFoundOn(self):
        self.__pathFound = True
        
    def setPathFoundOff(self):
        self.__pathFound = False
        
    def getPathFoundFlag(self):
        return self.__pathFound
    