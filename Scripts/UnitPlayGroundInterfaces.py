import structs
import bge
import copy
from math import radians, sqrt, asin, degrees
import collections

import time
import sys


scene = bge.logic.getCurrentScene()

#интерфейсы связанные с игровым полем.
class UnitPlayGroundIntefaces(object):
    def __init__(self, unit):
        self.__apCount = 58
        #количество AP на текущем шаге
        self.__turnAP = self.__apCount
        #состояние юнита
        self.__state = structs.UnitStates['Idle']
        self.__unit = unit
        #обводка
        self.__outline = []
        self.initOutline(self.__unit)
        scene = unit.scene
        #игрвоое поле
        beamDistance = 1
        rayStart = (unit.worldPosition.x, unit.worldPosition.y, unit.worldPosition.z + 0.1)
        rayEnd = (unit.worldPosition.x, unit.worldPosition.y, 0.0)
        hitObject, hitPosition, hitNormal = unit.rayCast(rayEnd, rayStart, beamDistance, 'Play Ground', 0, 1)
        self.__playGround = hitObject
        #откуда пришли
        self.__playGroundFrom = self.__playGround
        #вычислитель
        self.__computer = scene.objects['Computer']
        #ячейка пеорсонажа
        self.__gridLoc = self.__playGround['Interfaces'].objGridPosition(self.__unit.worldPosition)
        #тип юнита
        self.__unitType = None
        self.__unitType = structs.UnitType['Soldier']

        #оружее

        #управление GUI
        sceneList = bge.logic.getSceneList()
        for scene in sceneList:
            if scene.name == 'GUI':
                self.__GUIcontrol = scene.objects['GUI Control']
        #управление
        self.__controlType = structs.UnitControlType['None']
        #сторона
        self.__side = structs.UnitSide['Ally']
        #этаж
        self.__currentFloor = None

        #входная информация необходимая для расчета пути
        self.__cursorPos = None
        self.__goToPlayGround = None
        #нужен для передачи пути
        self.__tracker = None


    def getUnitType(self):
        return self.__unitType
        
    #Тип управления юнитом
    def setPlayerControlType(self):
        self.__controlType = structs.UnitControlType['Player']
    
    def setAIcontrolType(self):
        self.__controlType = structs.UnitControlType['AI']
        
    def getControlType(self):
        return self.__controlType
    
    #Гуйня   
    def getGUIcontrol(self):
        return self.__GUIcontrol
    
    #Unit Controller В конце пути
    #В компьютере, когда обновляется карта
    def setGridLoc(self, gridLoc):
        self.__gridLoc = gridLoc
        
    def getGridLoc(self):
        return self.__gridLoc
    
    def setAPcount(self, count):
        self.__apCount = count
        
    def updateAPcount(self):
        self.__apCount -= 1
        self.__GUIcontrol['Interfaces'].updateAPCountIndicator(self.__apCount)
        
    def getAPcount(self):
        return self.__apCount
    
    def newMoveType(self):
        return self.__unitType   

    '''инициализация обводки'''
    def initOutline(self, unit):
        self.__outline = []
        unitObjectsGroup = unit.groupObject
        for member in unitObjectsGroup.groupMembers:
            if 'Doll' in member.name:
                for member2 in member.groupMembers:
                    if 'Outline' in member2.name:
                        self.__outline.append(member2)
                        member2.visible = False
        self.setPlayerUnitOutline()
            
    #обводка для юнитов игрока
    def setPlayerUnitOutline(self):
        for elem in self.__outline:
            elem.color = [0.0, 1.0, 0.0, 1.0]
    #обводка союзника
    def setAllyUnitOutline(self):
        for elem in self.__outline:
            elem.color = [0.0, 1.0, 1.0, 1.0]
            elem.visible = True
     #обводка
    def setOutlineOn(self):
        for elem in self.__outline:
            elem.visible = True
    
    def setOutlineOff(self):
       for elem in self.__outline:
            elem.visible = False
    
    #состояния       
    def setIdleState(self):
        self.__state = structs.UnitStates['Idle']
        
    def setMoveState(self):
        self.__state = structs.UnitStates['Move']
        #разблокировка тайла для других юнитов
        self.__playGround['Interfaces'].unlockGridCoorByUnit(self.__gridLoc)
        self.__unit['Interfaces'].setPlayAnimation()
    
    def setAttackState(self):
        self.__state = structs.UnitStates['Attack']
    
    def getState(self):
        return self.__state 
    
    #игровое поле
    def setPlayGround(self, newPlayGround):
        self.__playGroundFrom = self.__playGround
        self.__playGround = newPlayGround         
    
    def getPlayGround(self):
        return self.__playGround


    def setDisplayPathPoints(self, pathPoints):
        self.__displayPathPoints = pathPoints
        
    def getDisplayPathPoints(self):
        return self.__displayPathPoints
    
    def clearDisplayPathPoints(self):
        self.__displayPathPoints.clear()    


    #поворот юнита в направлении атаки
    def setDirection(self, directionWorldPos, attackFlag):
        deltaX = directionWorldPos.x - self.__unit.worldPosition.x
        deltaY = directionWorldPos.y - self.__unit.worldPosition.y
        distance = sqrt(deltaX*deltaX + deltaY*deltaY)

        deg180inRad = radians(180.0)
        deg90inRad = radians(90.0)
        
        if deltaY > 0.0:
            fi = deg180inRad - asin(deltaX / distance)
        elif deltaY < 0.0:
            fi = asin(deltaX / distance)
        elif deltaY == 0.0:
            if deltaX > 0.0:
                fi = deg90inRad
            elif deltaX < 0.0:
                fi = -deg90inRad
            elif deltaX == 0.0:
                fi = deg180inRad
        
        tempOrient = self.__unit.worldOrientation.to_euler()
        tempOrient[2] = fi
        self.__unit.worldOrientation = tempOrient.to_matrix()
        #анимирование атаки конкретного юнита
        if attackFlag:
            self.__unit['Interfaces'].setAttackAnimation()
    
    #поворот юнита в направлении атаки
    def setMoveDirection(self, direction):
        if direction == 'my':
            fi = 180.0
        elif direction == 'mypx':
            fi = 135.0
        elif direction == 'px':
            fi = 90.0
        elif direction == 'pypx':
            fi = 45.0
        elif direction == 'py':
            fi = 0.0
        elif direction == 'pymx':
            fi = -45.0
        elif direction == 'mx':
            fi = -90.0
        elif direction == 'mymx':
            fi = -135.0
        tempOrient = self.__unit.worldOrientation.to_euler()
        tempOrient[2] = radians(fi)
        self.__unit.worldOrientation = tempOrient.to_matrix()

    def calcPath(self, point1, point2, currentPlayGround, targetPlayGround):
        #пункт назначения
        goalY = point2[0]
        goalX = point2[1]
        #положение персонажа
        startDirection = 'None'
        start = (currentPlayGround, point1, startDirection)
        queue = collections.deque([[start]])
        seen = set([start])
        pathFind = False
        if not(targetPlayGround['Interfaces'].isTileAvalableToStay(point2)):
            print('locked tile')
            return None
        #поиск пути
        while queue and not(pathFind):
            path = queue.popleft()
            currentPlayGround, coords, direction = path[-1]
            y = coords[0]
            x = coords[1]
            if y == goalY and x == goalX:
                if currentPlayGround.name == targetPlayGround.name:
                    pathFind = True
                    return path
            calcPathGrid = currentPlayGround['Interfaces'].getCalcPathGrid()
            #TODO можно сделать функцию в каждой ячейке, которая будет возвращать avlblDirectList по заданному MoveTYpe
            #TODO avlblDirectList будет содержать moveType
            avlblDirectList = calcPathGrid[y][x]
            for y2, x2, newPlayGround, direction in avlblDirectList:
                # TODO Здесь делаем проверку maxMoveType
                if (y2, x2, newPlayGround, direction) not in seen:
                    queue.append(path + [(newPlayGround, (y2,x2), direction)])
                    seen.add((y2,x2, newPlayGround, direction))
        return None
    
    #предварительный расчет пути
    def calcPathInThread(self):
        cursorPos = self.__cursorPos
        goToPlayGround = self.__goToPlayGround
        #координаты юнита на play ground
        unitTile = self.getGridLoc()
        path = self.calcPath(unitTile, cursorPos, self.__playGround, goToPlayGround)
        #ТОЛЬКО если боевой режим
        if path != None:
            #prevTime = time.clock()
            reqAP = self.__unit['Interfaces'].calcAP3(path, self.__tracker) #0.0024 sec 103 шага
            #curTime = time.clock()
            #delta = curTime - prevTime
            #print('reqAP time ', delta) 0.015 и меньше
            self.__tracker['Interfaces'].pathProcessing(path, reqAP)
        else:
            self.__tracker['Interfaces'].removeTracker()

    def nonPlayerUnitCalcPathInThread(self):
        cursorPos = self.__cursorPos
        goToPlayGround = self.__goToPlayGround
        #координаты юнита на play ground
        unitTile = self.getGridLoc()
        path = self.calcPath(unitTile, cursorPos, self.__playGround, goToPlayGround)
        #ТОЛЬКО если боевой режим
        if path != None:
            reqAP = self.__unit['Interfaces'].calcAP3(path, self.__tracker) #0.0024 sec 103 шага
            self.setMoveState()

    def setCursorPosAndFinalPlayGroundNoTracker(self, cursorPos, goToPlayGround):
        self.__cursorPos = cursorPos
        self.__goToPlayGround = goToPlayGround

    #назначить финальный tile и play ground где он располагается
    def setCursorPosAndFinalPlayGround(self, cursorPos, goToPlayGround, tracker):
        self.__cursorPos = cursorPos
        self.__goToPlayGround = goToPlayGround
        self.__tracker = tracker
        





