import bge
from bge import logic
import numpy as np
import copy
from math import sqrt

import numpy as np
import structs
import time

from random import randint

from Threads import Thread1, thread1OpenClose1, Thread2, thread2OpenClose2

scene = logic.getCurrentScene()
computer = scene.objects['Computer']

#поиск бляайшего значения
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


#объект для инициализация Computer
#Удаляется сразу после иницилизации
def initBlock(cont):
    own = cont.owner
    if 'init' in own:
        init(own.parent)
        own.endObject()

def init(own):
    scene = logic.getCurrentScene()
    own['Interfaces'] = ComputerInterfaces(own)
    own['Selected Player Unit'] = scene.objects['Unit Soldier'].groupMembers['Unit Controller']
    own['BeamHitPoint'] = scene.objects['BeamHitPoint']
    own['Player Turn'] = True
    own['Tracker exist'] = False
    print('---> Computer initiated!')
        
            
def hitProcessing(blow, updatePlayGround):
    #объекты которые получили урон
    checkObjectColorList = []
    checkColorList = []
    for mesh in blow.meshes:
        for material_index in range(len(mesh.materials)):
            for vertex_index in range(mesh.getVertexArrayLength(material_index)):
                vertex  = mesh.getVertex(material_index, vertex_index)
                endPosition = blow.worldPosition + vertex.getXYZ()
                startPosition = blow.worldPosition
                delX = endPosition.x - startPosition.x
                delY = endPosition.y - startPosition.y
                delZ = endPosition.z - startPosition.z
                beamDistance = sqrt(delX*delX + delY*delY + delZ*delZ)
                hitObject, hitPosition, hitNormal, polygone = blow.rayCast(endPosition, startPosition, beamDistance, '', 0, 0, 1)
                #TODO последние 2 условия это костыль от меха, который нужно исправить
                if hitObject:
                    if ('Barrier' in hitObject) and\
                            ('Sensor' not in hitObject.name) \
                            and ('Ragdoll' not in hitObject.name)\
                        or ('Floor Floor' in hitObject.name):
                        for meshHitObject in hitObject.meshes:
                            vertex  = meshHitObject.getVertex(polygone.material_id, polygone.v1)
                            color = vertex.color
                            if color not in checkColorList:
                                checkColorList.append(color)
                                #убираем элемент
                                #hitObject['Inerfaces'].removeBrickByColor(color)
                                checkObjectColorList.append((hitObject, color))

    for elem in checkObjectColorList:
        pass
        #elem[0]['Interfaces'].removeBrickByColor(elem[1])
    #return #DEBUG
    #проход всех поврежденных элементов
    updateGridCoordsList = []
    gridCoorFinder = updatePlayGround['Interfaces'].getGridCoorFinde()
    for elem in checkObjectColorList:
        for mesh in elem[0].meshes:
            for material_index in range(len(mesh.materials)):
                # TODO подумать, много жрет ресурсов
                for vertex_index in range(mesh.getVertexArrayLength(material_index)):
                    vertex  = mesh.getVertex(material_index, vertex_index)
                    red = vertex.color[0]
                    green = vertex.color[1]
                    blue = vertex.color[2]
                    sigma = 0.00001
                    deltaRed = abs(vertex.color[0] - elem[1][0])
                    deltaGreen = abs(vertex.color[1] - elem[1][1]) 
                    deltaBlue = abs(vertex.color[2] - elem[1][2])
                    if (deltaRed < sigma) and (deltaGreen < sigma) and (deltaBlue < sigma):
                        gridCoorFinder.worldPosition = vertex.getXYZ() + elem[0].worldPosition
                        gridCoor = updatePlayGround['Interfaces'].objGridPosition(gridCoorFinder.worldPosition)
                        if len(updateGridCoordsList) == 0:
                            updateGridCoordsList.append(gridCoor)
                        else:
                            #флаг наличия точки в списке
                            existInList = False
                            for gridUpdt in updateGridCoordsList:
                                if gridCoor == gridUpdt:
                                    existInList = True
                                    break
                            if not(existInList):
                                updateGridCoordsList.append(gridCoor)
                        vertex.XYZ = [0.0, 0.0, 0.0]
        prevTime = time.clock()
        #TODO подумать, много жрет ресурсов
        elem[0].reinstancePhysicsMesh()
        curTime = time.clock()
        delta = curTime - prevTime
        print(elem[0], 'Finish reinstance physics mesh, time spent = ', delta)
    #TODO подумать над обновлением play ground при деформации мехом
    for gridCoor in updateGridCoordsList:
        prevTime = time.clock()
        updatePlayGround['Interfaces'].updateAvlbGridCoor(gridCoor)
        curTime = time.clock()
        delta = curTime - prevTime
        print(updatePlayGround, gridCoor, 'Finish update grid, time spent = ', delta)

def updateMap(cont):
    sensor = cont.sensors[0]
    if len(sensor.bodies):
        allplayerUnits = computer['Interfaces'].getAllPlayerUnits()
        for unit in allplayerUnits:
            pgInterf = unit['Interfaces'].getPGinterfaces()
            unitPlayGround = pgInterf.getPlayGround()
            unitGridLoc = unitPlayGround['Interfaces'].objGridPosition(unit.worldPosition)
            pgInterf.setGridLoc(unitGridLoc)
            pgInterf.setPlayerControlType()
            unitPlayGround['Interfaces'].lockGridCoorByUnit(unitGridLoc)
            #запись себя на карту
        #работа с союзными юнитами
        allAllyUnits = computer['Interfaces'].getAllAllyUnits()
        for unit in allAllyUnits:
            pgInterf = unit['Interfaces'].getPGinterfaces()
            unitPlayGround = pgInterf.getPlayGround()
            unitGridLoc = unitPlayGround['Interfaces'].objGridPosition(unit.worldPosition)
            pgInterf.setGridLoc(unitGridLoc)
            unitPlayGround['Interfaces'].lockGridCoorByUnit(unitGridLoc)
            pgInterf.setAllyUnitOutline()
            pgInterf.setOutlineOff()
            pgInterf.setAIcontrolType()
        print('---> Unit position updated!')
        
# алгоритм управления AI
def dispetcherAI(cont):
    print('Ai calc')


    if 'Interfaces' not in computer:
        return
    allAllyUnits = computer['Interfaces'].getAllAllyUnits()
    if len(allAllyUnits) == 0:
        return
    unitIndex = randint(0, len(allAllyUnits) - 1)
    for idx, unit in enumerate(allAllyUnits):
        if 'Interfaces' not in unit:
            continue
        if idx != unitIndex:
            continue

        pgInterf = unit['Interfaces'].getPGinterfaces()
        allyUnitPlayGround = pgInterf.getPlayGround()
        grid = allyUnitPlayGround['Calc Path Grid']
        width, height = len(grid[0]), len(grid)

        unitPos = pgInterf.getGridLoc()
        minNewPosY = unitPos[0] - 10
        maxNewPosY = unitPos[0] + 10
        if maxNewPosY > height:
            maxNewPosY = height
        if minNewPosY < 0:
            minNewPosY = 0

        minNewPosX = unitPos[1] - 10
        maxNewPosX = unitPos[1] + 10
        if maxNewPosX > width:
            maxNewPosX = width
        if minNewPosX < 0:
            minNewPosX = 0
        if pgInterf.getState() != structs.UnitStates['Move']:

            cursorPos = [randint(minNewPosY, maxNewPosY), randint(minNewPosX, maxNewPosX)]
            #TODO условие при котором путь не будет больше заданого
            #path = pgInterf.calcPath(unitPos, cursorPos, allyUnitPlayGround, allyUnitPlayGround)
            #calcPathThread = computer['Interfaces'].getThread()
            thread = computer['Interfaces'].getThread2()
            pgInterf.setCursorPosAndFinalPlayGroundNoTracker(cursorPos, allyUnitPlayGround)
            thread.setProcessingFlagOn(pgInterf.nonPlayerUnitCalcPathInThread)





    
def leftClickProcessing(cont):
    av = logic.mouse.active_events
    if bge.events.LEFTMOUSE in av:
        if av[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            own = cont.owner
            unit = own['Interfaces'].getPlayerUnit()
            pgInterf = unit['Interfaces'].getPGinterfaces()
            if pgInterf.getUnitType() == structs.UnitType['Soldier']:
                if (pgInterf.getState() != structs.UnitStates['Attack']) and (not(unit['Interfaces'].getChangePosFlag())):
                    mainScreen = own['Interfaces'].getMainScreen()
                    if not(mainScreen['Interfaces'].getMouseOver()):
                        if not(own['Tracker exist']):
                            #смотрим у кого playground сейчас трекер
                            for elem in own['Interfaces'].getPlayGroundList():
                                if elem['Interfaces'].getMouseOverFlag():
                                    own['Interfaces'].setСlickedGround(elem)
                                    #tracker = scene.addObject('Tracker')
                                    trackerAPcount = scene.addObject('Tracker and AP Count')
                                    tracker = trackerAPcount.groupMembers['Tracker']
                                    tracker['Play Ground'] = elem #костыль
                                    own['Tracker exist'] = True
                                    return
                else:
                    scene.addObject('Mouse Over Add Sensor Attack')
            elif pgInterf.getUnitType() == structs.UnitType['Mech']:
                if pgInterf.getState() != structs.UnitStates['Attack']:
                    mainScreen = own['Interfaces'].getMainScreen()
                    if not(mainScreen['Interfaces'].getMouseOver()):
                        if not(own['Tracker exist']):
                            if playGround['Interfaces'].getMouseOverFlag():
                                tracker = scene.addObject('Tracker')
                                tracker['Current Unit'] = own['Selected Player Unit']
                                own['Tracker exist'] = True
                





def BinarySearch(lys, val):
    first = 0
    last = len(lys) - 1
    index = -1
    while (first <= last) and (index == -1):
        mid = (first + last) // 2
        if lys[mid] == val:
            index = mid
        else:
            if val < lys[mid]:
                last = mid - 1
            else:
                first = mid + 1
    return index

def MechObjectDestructionDispetcher(cont):
    own = cont.owner
    own['Interfaces'].checkDestructionList()

class ComputerInterfaces(object):
    def __init__(self, computer):
        """Constructor"""
        self.__fight = False
        self.__computer = computer
        #по другому
        self.__allPlayerUnits = []
        #союзники
        self.__allAllyUnits = []
        
        self.__playerUnit = scene.objects['Unit Soldier'].groupMembers['Unit Controller']
        self.__controlType = structs.UnitControlType['Player']
    
        #поток для параллельных вычислений, чтобы графика не висла
        self.__thread0 = Thread1(0)
        bge.logic.bge_thread0 = thread1OpenClose1(self.__thread0)
        self.__thread0.start()

        self.__thread1 = Thread1(1)
        bge.logic.bge_thread1 = thread1OpenClose1(self.__thread1)
        self.__thread1.start()
        '''
        self.__thread3 = Thread2(3)
        bge.logic.bge_thread3 = thread2OpenClose2(self.__thread3)
        self.__thread3.start()
        '''
        
        self.__tracker = None
        
        #список областей для перемещения
        self.__playGroundList = []
        #область перемещения по которой кликнул игрок
        self.__clickedPlayGround = None
        #инициализируем юнитов
        unitIndex = 0
        for object in scene.objects:
            #TODO должно быть конечно через интерфейс в юните добававление в список
            if 'Unit' in object.name:
                if 'Side' not in object:
                    continue
                if object['Side'] == structs.UnitSide.Player.name:
                    print(object, structs.UnitSide.Player, 1)
                    initBlock = object.groupMembers['Init Block']
                    initBlock['init'] = True
                    self.__allPlayerUnits.append(object.groupMembers['Unit Controller'])
                elif object['Side'] == structs.UnitSide.Ally.name:
                    print(object, structs.UnitSide.Ally, 2)
                    initBlock = object.groupMembers['Init Block']
                    initBlock['init'] = True
                    self.__allAllyUnits.append(
                        object.groupMembers['Unit Controller'])


        #объекты на уровне по этажам
        self.__level = None
        self.__guiControl = None
        #поток в котором будет обновление физики
        self.threadNum = 0



    def setLevel(self, level):
        self.__level = level
        
    def setGuiControl(self, guiControl):
        self.__guiControl = guiControl
    
    #получить доступ к потоку расчитывающему путь
    def getThread(self):
        return self.__thread0
    def getThread2(self):
        return self.__thread2
        
    #работа с областью перемешения  
    def setСlickedGround(self, clickedPlayGround):
        self.__clickedPlayGround = clickedPlayGround
    
    def getClickedPlayGround(self):
        return self.__clickedPlayGround
                 
    #юниты игрока
    def getAllPlayerUnits(self):
        return self.__allPlayerUnits
    
    #союзные юниты
    def getAllAllyUnits(self):
        return self.__allAllyUnits
    
    def setFightOn(self):
        self.__fight = True
        
    def setFightOff(self):
        self.__fight = False
        
    def getFightFlag(self):
        return copy.copy(self.__fight)
            
    def getPlayerUnit(self):
        return self.__playerUnit
    
    def getMainScreen(self):
        for elem in bge.logic.getSceneList():
            if elem.name == 'GUI':
                #mouseScene = scene
                return elem.objects['Main Screen']
    
    def getControlType(self):
        return self.__controlType
    
    def setPlayerUnit(self, number):
        for idx, elem in enumerate(self.__allPlayerUnits):
            pgInterf = elem['Interfaces'].getPGinterfaces()
            if idx == number:
                self.__playerUnit = elem
                pgInterf.setOutlineOn()
            else:
                pgInterf.setOutlineOff()
                
    #добавление на сцену трекера, который отмечает пункт назначения для юнита
    def addTracker(self, clickedObject, hitPosition):
        if 'Play Ground' in clickedObject.name:
            self.setСlickedGround(clickedObject)
            #tracker = scene.addObject('Tracker')
            trackerAPcount = scene.addObject('Tracker and AP Count')
            self.__tracker = trackerAPcount.groupMembers['Tracker']
            self.__tracker['Clicked Play Ground'] = clickedObject #костыль
            self.__tracker['Play Ground'] = True #нужно для того, чтобы ray cast увидел
            self.__tracker['Cursor World Position'] = hitPosition
        if 'Tracker' in clickedObject.name:
            self.__tracker['Interfaces'].updateUnitPath()
        
    #отработка атаки в точку
    def attackPoint(self, clickedObject, hitPosition):
        if 'Barrier' not in clickedObject:
            return
        unit = self.__playerUnit
        unit['Ray End'].worldPosition = hitPosition #работаем
        beamHitPoint = self.__computer['BeamHitPoint']
        beamHitPoint.worldPosition = hitPosition
        unit['Bullet Aim'].worldPosition = beamHitPoint.worldPosition
        pgInterf = unit['Interfaces'].getPGinterfaces()
        pgInterf.setDirection(unit['Ray End'].worldPosition, True)
        findPGposition = (beamHitPoint.worldPosition.x, beamHitPoint.worldPosition.y, beamHitPoint.worldPosition.z)
        findPGposition = (findPGposition[0], findPGposition[1], clickedObject.worldPosition.z)
        #findPGbeamDist = beamHitPoint.worldPosition.z - findPGposition[2]
        findPGbeamDist = 100
        hitObject, hitPosition, hitNormal = beamHitPoint.rayCast(findPGposition, beamHitPoint, findPGbeamDist, 'Play Ground', 0, 1, 0)
        prevTime = time.clock()
        hitProcessing(beamHitPoint, hitObject)
        curTime = time.clock()
        delta = curTime - prevTime
        print('Finish Hit Pocessing, time spent = ', delta)

    def mechDamageObject(self, clickedObject, hitPosition, normal):
        beamHitPoint = self.__computer['BeamHitPoint']
        beamDistance = 0.2
        rayStart = hitPosition - (beamDistance/2) * normal
        rayEnd = hitPosition + (beamDistance/2) * normal
        beamHitPoint.worldPosition = rayStart
        hitObject, hitPosition2, hitNormal, polygone = beamHitPoint.rayCast(rayEnd, rayStart, beamDistance, 'Destructable', 0, 0, 1)
        if hitObject:
            vertex = hitObject.meshes[0].getVertex(polygone.material_id, polygone.v1)
            color = vertex.color
            #print(hitObject, color, color.length)
            if self.threadNum == 0:
                #hitObject['Interfaces'].removeBrickByColor2(self.__thread0, self.__thread1,color.length)
                hitObject['Interfaces'].removeBrickByColor(self.__thread0, color.length)
                #self.threadNum += 1
            #elif self.threadNum == 1:
                #hitObject['Interfaces'].removeBrickByColor(self.__thread2, color.length)
                #self.threadNum += 1
            #elif self.threadNum == 2:
                #hitObject['Interfaces'].removeBrickByColor(self.__thread3, color.length)
                #self.threadNum = 0
            return
            hitObject['Interfaces'].moveVerticiesByColor(color.length)
            # ищем имя деформированного объекта
            index = BinarySearch(self.destructionList, hitObject.name)
            if index < 0:
                self.destructionList.append(hitObject.name)
                self.destructionList.sort()
            self.updatePhysicsTime = time.clock()

    def checkDestructionList(self):
        if len(self.destructionList) > 0:
            deltaTime = time.clock() - self.updatePhysicsTime
            if deltaTime > 0.0:
                print(len(self.destructionList))
                self.updatePhysicsTime = time.clock()
                threadNum = 0
                for idx, objectName in enumerate(self.destructionList):
                    if threadNum == 0:
                        self.__thread0.setProcessingFlagOn(scene.objects[objectName].reinstancePhysicsMesh)
                        threadNum += 2
                    else:
                        self.__thread2.setProcessingFlagOn(scene.objects[objectName].reinstancePhysicsMesh)
                        threadNum = 0
                    del self.destructionList[idx]




        
        
    def leftClickProcessing(self, projectedPos, camPos):
        beamDistance = 1000
        pgInterf = self.__playerUnit['Interfaces'].getPGinterfaces()
        if pgInterf.getUnitType() == structs.UnitType['Soldier']:
            if (pgInterf.getState() != structs.UnitStates['Attack']) and (not(self.__playerUnit['Interfaces'].getChangePosFlag())):
                '''Над этим моментом надо подумать, т.к. получается, что мы может через объекты кликать по Play Ground, т.к. xray = 1
                hitProperty = ''
                hitObject, hitPosition, hitNormal = self.__computer.rayCast(projectedPos, camPos, beamDistance, hitProperty)
                if hitObject != None:
                    if 'Floor' not in hitObject.name:
                        return
                '''
                hitProperty = 'Play Ground'
                hitObject, hitPosition, hitNormal = self.__computer.rayCast(projectedPos, camPos, beamDistance, hitProperty, 0 ,1)
                if hitObject != None:
                    self.addTracker(hitObject, hitPosition)
            else:
                hitProperty = ''
                hitObject, hitPosition, hitNormal = self.__computer.rayCast(projectedPos, camPos, beamDistance, hitProperty)
                if hitObject != None:
                    self.attackPoint(hitObject, hitPosition)
                    
    def signalFromGuiShowFloor(self, floorNum):
        newFloor = self.__level['Interfaces'].showObjOnFloor(floorNum)
        self.__guiControl['Interfaces'].setFloorIndicators(newFloor)
    
        
                
        
        
        
            
                    
        
        