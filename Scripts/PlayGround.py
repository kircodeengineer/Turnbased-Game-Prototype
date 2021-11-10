import bge
import numpy as np
import copy
import structs
import Building
import Landscape
import time
scene = bge.logic.getCurrentScene()
initBlockEmpty = scene.objects['Init Block']
#computer = scene.objects['Computer'] #debug

#объект для инициализация Play Ground
#Удаляется сразу после иницилизации
def initBlock(cont):
    own = cont.owner
    if 'init' in own:
        barrierChecker = scene.objects['Barrier Checker'].groupMembers['All Rays Base']
        if 'Interfaces' not in barrierChecker:
            return
        #начальная инициализация
        print('     PLAY GROUNDS START INTERFACES INICIALIZATION')
        prevTime = time.clock()
        playGroundInterfacesInit(own)
        curTime = time.clock()
        delta1 = curTime - prevTime
        print('     PLAY GROUNDS FINISH INTERFACES INICIALIZATION, time spent = ', delta1)
        print('-------------------------------------------------------------------------------')
        #проверка инициализацияи для Posture и Bridg        
        if not(checkInit(own)):
            return
        #инициализация posture
        print('     PLAY GROUNDS START POSTURE INICIALIZATION')
        prevTime = time.clock()
        postureInit(own)
        curTime = time.clock()
        delta2 = curTime - prevTime
        print('     PLAY GROUNDS FINISH POSTURE INICIALIZATION, time spent = ', delta2)
        print('-------------------------------------------------------------------------------')
        #инициализация bridges
        print('     PLAY GROUNDS START BRIDGES INICIALIZATION')
        prevTime = time.clock()
        bridgesInit(own)
        curTime = time.clock()
        delta3 = curTime - prevTime
        print('     PLAY GROUNDS FINISH BRIDGES INICIALIZATION, time spent = ', delta3)
        print('-------------------------------------------------------------------------------')
        #инициализация допустимых направлений перемещения
        print('     PLAY GROUNDS START MOVE DIRECTIONS INICIALIZATION')
        prevTime = time.clock()
        moveDirectionsInit(own)
        curTime = time.clock()
        delta4 = curTime - prevTime
        print('     PLAY GROUNDS FINISH MOVE DIRECTIONS INICIALIZATION, time spent = ', delta4)
        print('-------------------------------------------------------------------------------')
        #уничтожение инициализитора
        print('     PLAY GROUNDS FINISH INICIALIZATION, time spent = ', delta1 + delta2 + delta3 + delta4)
        print('-------------------------------------------------------------------------------')
        own.endObject()

def playGroundInterfacesInit(own):
    for object in own.groupObject.groupMembers:
        if 'Interfaces' in object:
            break
        if 'Ladder' in object.name:
            init_ladder(object)
        elif 'Play Ground' in object.name:
            init(object)
        if 'Building' in object.name:
            if 'Play Ground' not in object.name:
                Building.init(object)
        if 'Landscape' in object.name:
            if 'Play Ground' not in object.name:
                Landscape.init(object)
        
def checkInit(own):
    isInit = False
    for object in own.groupObject.groupMembers:
        if 'Play Ground' in object.name:
            if 'Interfaces' not in object:
                return isInit
        elif 'Building' in object.name:
            if 'Interfaces' not in object:
                return isInit
            pgList = object['Interfaces'].getPlayGroundsList()
            for elem in pgList:
                if 'Interfaces' not in elem:
                    return isInit
        elif 'Landscape' in object.name:
            if 'Interfaces' not in object:
                return isInit
            pgList = object['Interfaces'].getPlayGroundsList()
            for elem in pgList:
                if 'Interfaces' not in elem:
                    return isInit
    isInit = True
    return isInit
    

def bridgesInit(own):
    for object in own.groupObject.groupMembers:
        if 'Play Ground' in object.name:
            print(object.name , '--> Start Loking Bridges.')
            object['Interfaces'].findBridges()
            print(object.name , '--> Bridges Found.')
        elif 'Building' in object.name:
            pgList = object['Interfaces'].getPlayGroundsList()
            for elem in pgList:
                print(elem.name , '--> Start Loking Bridges.')
                elem['Interfaces'].findBridges()
                print(elem.name , '--> Bridges Found.')
        elif 'Landscape' in object.name:
            pgList = object['Interfaces'].getPlayGroundsList()
            for elem in pgList:
                print(elem.name , '--> Start Loking Bridges.')
                elem['Interfaces'].findBridges()
                print(elem.name , '--> Bridges Found.')
                
    
def postureInit(own):
    for object in own.groupObject.groupMembers:
        if 'Play Ground' in object.name:
            print(object.name , '--> Poster Start Init.')
            object['Interfaces'].setAvlbGridCoorForCalcPath()
            print(object.name , '--> Poster Grid Initiated.')
        elif 'Building' in object.name:
            pgList = object['Interfaces'].getPlayGroundsList()
            for elem in pgList:
                print(elem.name , '--> Poster Start Init.')
                elem['Interfaces'].setAvlbGridCoorForCalcPath()
                print(elem.name , '--> Poster Grid Initiated.')
        elif 'Landscape' in object.name:
            pgList = object['Interfaces'].getPlayGroundsList()
            for elem in pgList:
                print(elem.name , '--> Poster Start Init.')
                elem['Interfaces'].setAvlbGridCoorForCalcPath()
                print(elem.name , '--> Poster Grid Initiated.')

def moveDirectionsInit(own):
    for object in own.groupObject.groupMembers:
        if 'Play Ground' in object.name:
            print(object.name , '--> Move Directions Start Init.')
            object['Interfaces'].initCalcPathGrid()
            print(object.name , '--> Move Directions Start Initiated.')
        elif 'Building' in object.name:
            pgList = object['Interfaces'].getPlayGroundsList()
            for elem in pgList:
                print(elem.name , '--> Move Directions Start Init.')
                elem['Interfaces'].initCalcPathGrid()
                print(elem.name , '--> Move Directions Start Initiated.')
        elif 'Landscape' in object.name:
            pgList = object['Interfaces'].getPlayGroundsList()
            for elem in pgList:
                print(elem.name , '--> Move Directions Start Init.')
                elem['Interfaces'].initCalcPathGrid()
                print(elem.name , '--> Move Directions Start Initiated.')

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

def init_ladder(own):
    #цвета
    color1 = None
    color1List = []
    color2 = None
    color2List = []
    #цоординаты
    for mesh in own.meshes:
        for material_index in range(len(mesh.materials)):
            for vertex_index in range(mesh.getVertexArrayLength(material_index)):
                vertex  = mesh.getVertex(material_index, vertex_index)
                #инициализация
                if color1 == None:
                    color1 = vertex.color
                if (color2 == None) and (color1 != vertex.color):
                    color2 = vertex.color
                #блок красок
                if color1 == vertex.color:
                    color1List.append(color1)
                elif color2 == vertex.color:
                    color2List.append(color2)
    if len(color2List) > len(color1List):
        stepColor = color1List[0]
    else:
        stepColor = color2List[0]
        
    vertexCo = []
    for mesh in own.meshes:
        for material_index in range(len(mesh.materials)):
            for vertex_index in range(mesh.getVertexArrayLength(material_index)):
                vertex  = mesh.getVertex(material_index, vertex_index)
                if vertex.color == stepColor:
                    vertexCo.append(vertex.getXYZ() + own.worldPosition)
                    
    
    #сортировка по Y всех координат
    if 'NonRev' in own.name:
        sortedVertexCoZ = sorted(vertexCo, key = lambda x:x[2], reverse = False)
    else:
        sortedVertexCoZ = sorted(vertexCo, key = lambda x:x[2], reverse = True)
    #startZ = sortedVertexCoZ[0]
    line = []
    grid = []
    #значения по X
    own['arrayX'] = np.array([])
    own['arrayY'] = np.array([])
    if 'RevY' in own.name:
        for elem in sortedVertexCoZ:
            line.append(elem)
            grid.append(copy.copy(line))
            line.clear()
        for line in grid:
            for elem in line:
                own['arrayY'] = np.append(own['arrayY'], elem.y)
        own['arrayX'] = np.append(own['arrayX'], grid[0][0].x)
    elif 'RevX' in own.name:
        grid.append(copy.copy(sortedVertexCoZ))
        for line in grid:
            for elem in line:
                own['arrayX'] = np.append(own['arrayX'], elem.x)
        own['arrayY'] = np.append(own['arrayY'], grid[0][0].y)
    

        

    own['Grid'] = grid 
    #Карта по которой будут расчитываться пути перемещения юнитов
    own['Calc Path Grid'] = []
    line = []
    for elem in own['Grid']:
        for elem2 in elem:
            line.append('Clear')
        own['Calc Path Grid'].append(copy.deepcopy(line))
        line.clear()

    own['Interfaces'] = PlayGroundInterfaces(own)
    own['Cursor Over Play Ground'] = False
    print(own.name , '---> initiated!')
    

    
    
def init(own):
    #цоординаты
    stepColor = (0.0, 1.0, 0.0) # red green blue
    vertexCo = []
    allVertexCo = []
    sigma = 0.00001
    for mesh in own.meshes:
        for material_index in range(len(mesh.materials)):
            for vertex_index in range(mesh.getVertexArrayLength(material_index)):
                vertex  = mesh.getVertex(material_index, vertex_index)
                allVertexCo.append(vertex.getXYZ())
                vertexColor = vertex.color
                deltaRed = abs(vertexColor[0] - stepColor[0])
                deltaGreen = abs(vertexColor[1] - stepColor[1])
                deltaBlue = abs(vertexColor[2] - stepColor[2])
                if (deltaRed < sigma) and (deltaGreen < sigma) and (deltaBlue < sigma):
                    vertexCo.append(vertex.getXYZ() + own.worldPosition)
    #сортировка по Y всех координат
    sortedVertexCoY = sorted(vertexCo, key = lambda x:x[1], reverse = True)
    startY = sortedVertexCoY[0]
    #значения по Y    
    own['arrayY'] = np.array([])
    own['arrayY'] = np.append(own['arrayY'], startY.y)
    startId = 0
    finalId = None
    sortedId = [[startId, finalId]]
    for id, elem in enumerate(sortedVertexCoY):
        modDelta = abs(elem.y - startY.y)
        if modDelta > sigma:
            startY = elem
            own['arrayY'] = np.append(own['arrayY'], startY.y)
            lastId = len(sortedId) - 1
            sortedId[lastId][1] = id
            startId = id
            sortedId.append([startId, finalId])
    lastId = len(sortedId) - 1
    sortedId[lastId][1] = len(sortedVertexCoY) - 1
    #сортировка по X всех координат
    sortedVertexCoX = sorted(vertexCo, key = lambda x:x[0], reverse = False)
    startX = sortedVertexCoX[0]
    #значения по X
    own['arrayX'] = np.array([])
    own['arrayX'] = np.append(own['arrayX'], startX.x)
    for elem in sortedVertexCoX:
        modDelta = abs(elem.x - startX.x)
        if modDelta > sigma:
            startX = elem
            own['arrayX'] = np.append(own['arrayX'], startX.x)
            
    line = []
    grid = []
    for elem in own['arrayY']:
        for elem2 in own['arrayX']:
            initBlockEmpty.worldPosition.x = elem2
            initBlockEmpty.worldPosition.y = elem
            position = copy.copy(initBlockEmpty.worldPosition)
            line.append(copy.copy(position))
        grid.append(copy.copy(line))
        line.clear()
    
    line = []
    gridClearEmpty = []
    isClear = False
    clearTile = 'Clear'
    emptyTile = 'Empty'
    gridCoor = []
    lineGridCoor = []
    for id, line2 in enumerate(grid):
        for elem in line2:
            finalId = sortedId[id][1]
            currentId = sortedId[id][0]
            while currentId <= finalId:
                elem2 = sortedVertexCoY[currentId]
                currentId += 1
                modDeltaX = abs(elem.x - elem2.x)
                modDeltaY = abs(elem.y - elem2.y)
                if (modDeltaY < sigma) and (modDeltaX < sigma):
                    line.append(clearTile)
                    lineGridCoor.append(elem2)
                    isClear = True
                    break
            if not(isClear):
                line.append(emptyTile)
                lineGridCoor.append(emptyTile)
                elem = emptyTile 
            isClear = False
        gridClearEmpty.append(copy.copy(line))
        line.clear()
        gridCoor.append(copy.copy(lineGridCoor))
        lineGridCoor.clear()
    #Карта по которой будут расчитываться пути перемещения юнитов
    own['Calc Path Grid'] = gridClearEmpty
    #сетка с координатами по номеру ячейки
    own['Grid'] = gridCoor
    own['Interfaces'] = PlayGroundInterfaces(own)
    own['Cursor Over Play Ground'] = False
    print(own.name , '---> initiated!')
    
    
    


def testFunc22(cont):
    own = cont.owner
    print('hello', own)                
                
def testFunc23(cont):
    own = cont.owner
    print('lololosh', own['Grid']) 
    
def updateUnitGridLoc(cont, unit):
    own = cont.owner
    unitWordPosX = unit.worldPosition.x
    unitWordPosY = unit.worldPosition.y
    nearX, idX = find_nearest(own['arrayX'], unitWordPosX)
    nearY, idY = find_nearest(own['arrayY'], unitWordPosY)
    computer['Selected Player Unit']['Current Grid Loc'] = (idY, idX)

def testFunc1(cont):
    own = cont.owner
    if 'Ladder' in own.name:
        return
    init(cont.owner)
    #playGround['Interfaces'].setAvlbGridCoorForCalcPath()
    #playGround['Interfaces'].lockGridCoorByUnit([0,0])

MoveDirection = {'py' : 0, 'my' : 1, 'px' : 2, 'mx' : 3, 'pypx' : 4, 'pymx' : 5, 'mypx' : 6, 'mymx' : 7}
#MoveDirection = {'my' : 0, 'mypx' : 1, 'px' : 2, 'pypx' : 3, 'py' : 4, 'pymx' : 5, 'mx' : 6, 'mymx' : 7}


       
class PlayGroundInterfaces(object):
    def __init__(self, playGround):
        """Constructor"""
        self.__playGround = playGround
        self.__gridCoor = self.__playGround['Grid']
        self.__barrierChecker = scene.objects['Barrier Checker'].groupMembers['All Rays Base']
        #сетка первой итерации поиска пути
        self.__gridFirstIteration = self.__playGround['Calc Path Grid']
        #нужен для поиска ячейки рядом с которой был вертекс от удаленного элемента стены
        self.__gridCoorFinder = scene.objects['Grid Coor Finder']
        #список Play GRound, к которым есть доступ с данного Play Ground
        self.__connectedPlayGrounds = []
        #Цепочки присоединенных Play Ground
        self.__bridgedPlayGroundsChains = []
        #список bridge tile
        self.__bridgeTilesList = []
        #сектка по которой будет расчитываться путь
        self.__calcPathGrid = []
        #сетка блокированная юнитами
        self.__unitLockGrid = []
        self.initUnitLockGrid()
        
    def initUnitLockGrid(self):
        ySize = len(self.__gridCoor)
        xSize = len(self.__gridCoor[0])
        line = []
        for idY in range(ySize):
            for idX in range(xSize):
                line.append(False)
            self.__unitLockGrid.append(copy.copy(line))
            line.clear()
                
    def getCalcPathGrid(self):
        return self.__calcPathGrid  
    def updateBridgeTilesList(self):
        #список Bridge tile
        self.__bridgeTilesList = []
        for idY, line in enumerate(self.__avlblGridCoords):
            for idX, tile in enumerate(line):
                emptyTile = 'Empty'
                if tile != emptyTile:
                    if tile.getBridgeFlag():
                        self.__bridgeTilesList.append((idY, idX))
        
    
    '''    
    def collectAllConnectedPlayGrounds(self, checkPlayGround):
        for elem in checkPlayGround['Interfaces'].getConnectedPlayGroundsList():
            exist = False
            for elem2 in self.__connectedPlayGrounds:
                if elem.name == elem2.name:
                    exist = True
                    pass
                elif elem.name == self.__playGround.name:
                    exist = True
                    pass
            if not(exist):
                print('end', elem)
                self.__connectedPlayGrounds.append(elem)

    #обновление списка присоединенных Play Ground
    def updateConnectedPlayGroundsList(self):
        print('start', self.__playGround.name, self.__connectedPlayGrounds)
        for elem in self.__connectedPlayGrounds:
            self.collectAllConnectedPlayGrounds(elem)
    '''
    #поиск веток play ground по начальным bridge
    def findBridges(self):
        if len(self.__bridgedPlayGroundsChains) > 0:
            return
        for elem in self.getConnectedPlayGroundsList():
            connections = []
            connections.append(self.__playGround)
            connections.append(elem)#зарождение списка
            self.__bridgedPlayGroundsChains.append(copy.copy(connections))
            self.findBridgesThreads(elem, connections, connections, True)
    
    #поиск всех веток от Play Ground к другим Play Ground
    def findBridgesThreads(self, startPlayGround, connections, mainConnection, mainConnectionFlag):
        for elem in startPlayGround['Interfaces'].getConnectedPlayGroundsList():
            #если основная ветка то нужно взять список сначала
            if mainConnectionFlag:
                currentConnections = copy.copy(mainConnection)
            else:
                currentConnections = copy.copy(connections)
            if elem.name == self.__playGround.name:
                continue
            inConnections = False
            for elem2 in currentConnections:
                if elem.name == elem2.name:
                    inConnections = True
                    break
            if not(inConnections):
                currentConnections.append(elem)
                self.__bridgedPlayGroundsChains.append(copy.copy(currentConnections))
                self.findBridgesThreads(elem, currentConnections, mainConnection, False)
    #поиск цепочки Play Ground
    def findChainToPlayGround(self, moveToPlayGround):
        chains = []
        for chain in self.__bridgedPlayGroundsChains:
            if chain[len(chain) - 1].name == moveToPlayGround.name:
                chains.append(chain)
        return chains
        
    #работа с присоединенными Play Ground
    def addConnectedPlayGround(self, newPlayGround):
        for elem in self.__connectedPlayGrounds:
            if elem.name == newPlayGround.name:
                return
        self.__connectedPlayGrounds.append(newPlayGround)
    
    #интерфейс для получения всех присоединенных play ground по цепочке
    def getBridgedPlayGrounds(self):
        return self.__bridgedPlayGroundsChains
        
        
        
        
        
    #список присоединенных Play Ground
    def getConnectedPlayGroundsList(self):
        return self.__connectedPlayGrounds
    
    def getGridMaxY(self):
        return len(self.__gridCoor) - 1
    def getGridMaxX(self):
        return len(self.__gridCoor[0]) - 1
    #Юнит для првоерки пути
    def getBarrierChecker(self):
        return self.__barrierChecker
    #vertex сам установит координаты и найдет нужные ячейки
    def getGridCoorFinde(self):
        return self.__gridCoorFinder
    
    #обновление текущей ячейки 
    def updateAvlbGridCoor(self, gridCoor):
        worldPos = self.__gridCoor[gridCoor[0]][gridCoor[1]]
        barrierCheckResult = self.__barrierChecker['Interfaces'].checkTile(worldPos)
        self.__avlblGridCoords[gridCoor[0]][gridCoor[1]] = GridCoorAvlblDirections((gridCoor[0],gridCoor[1]), barrierCheckResult, self.__playGround)
        self.updtAvlblDirectionsNearTile(gridCoor, True)

        for key, value in barrierCheckResult[1].straightData.items():
            if(value[0]):
                bridgePlayGround = value[1]
                bridgeGridCoor = value[2]
                bridgePlayGround['Interfaces'].updateAvlbGridCoorTest(bridgeGridCoor)

        for key, value in barrierCheckResult[1].diagonalData.items():
            if(value[0]):
                bridgePlayGround = value[1]
                bridgeGridCoor = value[2]
                bridgePlayGround['Interfaces'].updateAvlbGridCoorTest(bridgeGridCoor)



        
    def updateAvlbGridCoorTest(self, gridCoor):
        self.__calcPathGrid[gridCoor[0]][gridCoor[1]] = self.setAvlblDirectionsForCalcPathTile(gridCoor)


    
    #блокировка текущей ячейки под юнитом
    def lockGridCoorByUnit(self, gridCoor):
        self.__unitLockGrid[gridCoor[0]][gridCoor[1]] = True
        self.updtAvlblDirectionsNearTile(gridCoor, False)
        
    #разблоблокировка текущей ячейки под юнитом
    def unlockGridCoorByUnit(self, gridCoor):
        self.__unitLockGrid[gridCoor[0]][gridCoor[1]] = False
        self.updtAvlblDirectionsNearTile(gridCoor, False)
            
    def getGridCoor(self):
        return self.__gridCoor
    
    #определение положение объекта на сетке по его координатам
    def objGridPosition(self, objLoc):
        nearY, idY = find_nearest(self.__playGround['arrayY'], objLoc.y)
        nearX, idX = find_nearest(self.__playGround['arrayX'], objLoc.x)
        return idY, idX
     #положение курсора
    def cursorGridPosition(self):
        cursorLoc = self.__playGround['Mouse Over Sensor'].hitPosition
        nearY, idY = find_nearest(self.__playGround['arrayY'], cursorLoc.y)
        nearX, idX = find_nearest(self.__playGround['arrayX'], cursorLoc.x)
        return idY, idX
    
    def getCoorByGridPos(self, y, x):
        return self.__gridCoor[y][x]
    
    #сетка для расчета пути
    def setAvlbGridCoorForCalcPath(self):
        #массив  с доступными полоениями
        self.__avlblGridCoords = []
        resultLine = []
        #строка
        for idl, line in enumerate(self.__gridCoor):
            #столбец
            for ide, elem in enumerate(line):
                emptyTile = 'Empty'
                if elem != emptyTile:
                    currentGridCoord = GridCoorAvlblDirections((idl,ide), self.__barrierChecker['Interfaces'].checkTile(elem), self.__playGround)
                else:
                    currentGridCoord = emptyTile
                resultLine.append(currentGridCoord)
            self.__avlblGridCoords.append(copy.copy(resultLine))
            resultLine.clear()
        #нужен список Bridge для оптимизации поиска
        self.updateBridgeTilesList()
        
        
    #result.append((bridgedTile[0], bridgedTile[1], bridgedPlayGround, direction))
    #result.append((nextCoor[0], nextCoor[1], self.__playGround, direction))
    def setAvlblDirectionsForCalcPathTile(self, gridCoor):
        maxY = len(self.__gridCoor) - 1
        maxX = len(self.__gridCoor[0]) -1
        path = []
        result = []
        idl = gridCoor[0]
        ide = gridCoor[1]
        directions = ('py', 'my', 'px', 'mx', 'pypx', 'pymx', 'mypx', 'mymx')
        for direction in directions:
            #вообще хорошобы, чтобы эта функци возвращала либо координату либо None
            isBridge = self.__avlblGridCoords[gridCoor[0]][gridCoor[1]].getBridgeFlag()
            isBridgeDirection = False
            bridgeData = None
            if isBridge:
                if len(direction) == 2:
                    bridgeData = self.__avlblGridCoords[gridCoor[0]][gridCoor[1]].getTileBridges().straightData
                elif len(direction) == 4:
                    bridgeData = self.__avlblGridCoords[gridCoor[0]][gridCoor[1]].getTileBridges().diagonalData
                if bridgeData[direction][0]:
                    isBridgeDirection = True
            if isBridgeDirection:
                bridgedPlayGround = bridgeData[direction][1]
                bridgedTile = bridgeData[direction][2]
                #[3] = bridgeDirection
                checkDiagonalTiles = bridgeData[direction][4]
                #TODO isAvlblDirection к result нужно добавить ещё макимальный moveType
                isAvlblDirection = self.checkGridCoorByDirectionToBridgeTile(gridCoor, bridgedTile, direction, checkDiagonalTiles, bridgedPlayGround)
                if isAvlblDirection:
                    result.append((bridgedTile[0], bridgedTile[1], bridgedPlayGround, direction))
            else:
                if idl == 0:
                    if (direction == 'my') or (direction == 'mypx') or (direction == 'mymx'):
                        continue
                    if ide == 0:
                        if (direction == 'pymx') or (direction == 'mx'):
                            continue
                    if ide == maxX:
                        if (direction == 'pypx') or (direction == 'px'):
                            continue
                if idl == maxY:
                    if (direction == 'pypx') or (direction == 'py') or (direction == 'pymx'):
                        continue
                    if ide == 0:
                        if (direction == 'mymx') or (direction == 'mx'):
                            continue
                    if ide == maxX:
                        if (direction == 'pypx') or (direction == 'px'):
                            continue     
                if ide == maxX:
                    if (direction == 'mypx') or (direction == 'px') or (direction == 'pypx'):
                        continue
                if ide == 0:
                    if (direction == 'mymx') or (direction == 'mx') or (direction == 'pymx'):
                        continue
                isAvlblDirection = self.checkGridCoorByDirection(gridCoor, direction, path)
                if isAvlblDirection:
                    if direction == 'my':
                        nextCoor = (gridCoor[0] - 1, gridCoor[1])
                    elif direction == 'mypx':
                        nextCoor = (gridCoor[0] - 1, gridCoor[1] + 1)
                    elif direction == 'px':
                        nextCoor = (gridCoor[0], gridCoor[1] + 1)
                    elif direction == 'pypx':
                        nextCoor = (gridCoor[0] + 1, gridCoor[1] + 1)
                    elif direction == 'py':
                        nextCoor = (gridCoor[0] + 1, gridCoor[1])
                    elif direction == 'pymx':
                        nextCoor = (gridCoor[0] + 1, gridCoor[1] - 1)
                    elif direction == 'mx':
                        nextCoor = (gridCoor[0], gridCoor[1] - 1)
                    elif direction == 'mymx':
                        nextCoor = (gridCoor[0] - 1, gridCoor[1] - 1)
                    result.append((nextCoor[0], nextCoor[1], self.__playGround, direction))
        return result       
    
    #инициализации сетки по которой будет расчитываться путь
    #TODO как сделать так чтобы можно было рассчитать путь для заданного movetype? Сейчас ограничение Prone
    def initCalcPathGrid(self):
        avlblDirections = []
        line2 = []
        #строка
        for idl, line in enumerate(self.__gridCoor):
            #столбец
            for ide, elem in enumerate(line):
                emptyTile = 'Empty'
                if elem != emptyTile:
                    gridCoord = (idl, ide)
                    avlblDirections = self.setAvlblDirectionsForCalcPathTile(gridCoord)
                line2.append(copy.copy(avlblDirections))
            self.__calcPathGrid.append(copy.copy(line2))
            line2.clear()
        #заполнение calcPathGrid
    
    def updtAvlblDirectionsNearTile(self,gridCoor, updtCurrentTile):
        y = gridCoor[0]
        x = gridCoor[1]
        ySize = len(self.__gridCoor) - 1
        xSize = len(self.__gridCoor[0]) -1
        my = (y - 1, x)
        mypx = (y - 1, x + 1)
        px = (y, x + 1)
        pypx = (y + 1, x + 1)
        py = (y + 1, x)
        pymx = (y + 1, x - 1)
        mx = (y, x - 1)
        mymx = (y - 1, x - 1)
        tilesNearLockedTile = (my, mypx, px, pypx, py, pymx, mx, mymx)
        for tile in tilesNearLockedTile:
            if tile[0] < 0 or tile[1] < 0 or tile[0] > ySize or tile[1] > xSize:
                continue
            else:
                self.__calcPathGrid[tile[0]][tile[1]] = self.setAvlblDirectionsForCalcPathTile(tile)
        if updtCurrentTile:
            self.__calcPathGrid[gridCoor[0]][gridCoor[1]] = self.setAvlblDirectionsForCalcPathTile(gridCoor)
        
    
    #получить исследованное поле
    def getAvlblGridCoords(self):
        return self.__avlblGridCoords
    
    #получить координаты bridge ячеек к Play Ground
    def getBridgeTiles(self, goToPlayGround):
        bridgedTiles = []
        for elem in self.__bridgeTilesList:
            for item in self.__avlblGridCoords[elem[0]][elem[1]].getTileBridges().straightData.items():
                if item[1][0]:
                    if item[1][1].name == goToPlayGround.name:
                        bridgedTiles.append([elem, item[1][2], item[1][3], item[1][4]])
            for item in self.__avlblGridCoords[elem[0]][elem[1]].getTileBridges().diagonalData.items():
                if item[1][0]:
                    if item[1][1].name == goToPlayGround.name:
                        bridgedTiles.append([elem, item[1][2], item[1][3], item[1][4]])
        return bridgedTiles           
    
    #список всех bridge ячеек
    def getAllBridgedTiles(self):
        bridgedTiles = []
        for elem in self.__bridgeTilesList:
            #прямые мосты
            for item in self.__avlblGridCoords[elem[0]][elem[1]].getTileBridges().straightData.items():
                if item[1][0]:
                    if item[1][1] != None:
                        bridgedTiles.append([elem, item[1][2], item[1][3], item[1][4]])
            #диагональные мосты
            for item in self.__avlblGridCoords[elem[0]][elem[1]].getTileBridges().diagonalData.items():
                if item[1][0]:
                    if item[1][1] != None:
                        bridgedTiles.append([elem, item[1][2], item[1][3], item[1][4]])
        return bridgedTiles
    
    def getTileBridgesFromPGtoPG(self, fromPlayGround, toPlayGround):
        fromTiles = []
        toTiles = []
        for idY, line in enumerate(self.__avlblGridCoords):
            for idX, tile in enumerate(line):
                #прямые мосты
                for item in tile.getTileBridges().straightData.items():
                    if item[1][1] != None:
                        if fromPlayGround.name == item[1][1].name:
                            fromTiles.append([(idY, idX), item[1][1]])
                        elif toPlayGround.name == item[1][1].name:
                            toTiles.append([(idY, idX), item[1][1]])
                #диагональные мосты
                for item in tile.getTileBridges().diagonalData.items():
                    if item[1][1] != None:
                        #зачем нам повторные ячейки?
                        exist = False
                        for elem in fromTiles:
                            if  item[1][1].name == elem[1].name:
                                exist = True
                        for elem in toTiles:
                            if  item[1][1].name == elem[1].name:
                                exist = True
                        if exist:
                            continue
                        if fromPlayGround.name == item[1][1].name:
                            fromTiles.append([(idY, idX), item[1][1]])
                        elif toPlayGround.name == item[1][1].name:
                            toTiles.append([(idY, idX), item[1][1]])
                                
        return fromTiles, toTiles
    
    #направление движения пр переходе в bridge tile соседнего playGround
    def getBridgeDirection(self, curGridCoor, nextPlayGround, nextGridCoor):
        for elem in self.__bridgeTilesList:
            if curGridCoor == elem:
                for direction,item in self.__avlblGridCoords[elem[0]][elem[1]].getTileBridges().straightData.items():
                    if item[0]:
                        if item[1].name == nextPlayGround.name:
                            if item[2] == nextGridCoor:
                                return direction
                for direction, item in self.__avlblGridCoords[elem[0]][elem[1]].getTileBridges().diagonalData.items():
                    if item[0]:
                        if item[1].name == nextPlayGround.name:
                            if item[2] == nextGridCoor:
                                return direction
    
    #ячейки которые нужно проекрить при диагональном перемещение
    def getBridgeDiagonalMoveTiles(self, curGridCoor, prevGridCoor):
        for elem in self.__bridgeTilesList:
            if curGridCoor == elem:
                for item in self.__avlblGridCoords[elem[0]][elem[1]].getTileBridges().straightData.items():
                    if item[1][0]:
                        if item[1][1].name == prevGridCoor[0].name:
                            if item[1][2] == prevGridCoor[1]:
                                return item[1][4]
                for item in self.__avlblGridCoords[elem[0]][elem[1]].getTileBridges().diagonalData.items():
                    if item[1][0]:
                        if item[1][1].name == prevGridCoor[0].name:
                            if item[1][2] == prevGridCoor[1]:
                                return item[1][4]
            
        
    #расчет доступного положения тела для перехода в ячейку
    def getMoveTypeByGridCoor(self, curGridCoor, prevGridCoor):
        if self.__playGround.name != prevGridCoor[0].name:
            return self.getMoveTypeByGridCoorBridge(curGridCoor, prevGridCoor)
        else:
            return self.getMoveTypeByGridCoorNoBridge(curGridCoor, prevGridCoor[1])
    
    #расчет доступного положения тела для перехода в ячейку соседнего playground
    def getMoveTypeByGridCoorBridge(self, curGridCoor, prevGridCoor):
        #нужно получить direction
        diagonalData = self.getBridgeDiagonalMoveTiles(curGridCoor, prevGridCoor)
        #если перемещение по диагонали
        if diagonalData != None:
            #первый соседний тайл
            firstDiagPlayGround = diagonalData[0][0]
            firstAvlblGridCoords = firstDiagPlayGround['Interfaces'].getAvlblGridCoords()
            check1Tile = firstAvlblGridCoords[diagonalData[0][1][0]][diagonalData[0][1][1]]
            #второй соседний тайл
            secondDiagPlayGround = diagonalData[1][0]
            secondAvlblGridCoords = secondDiagPlayGround['Interfaces'].getAvlblGridCoords()
            check2Tile = secondAvlblGridCoords[diagonalData[1][1][0]][diagonalData[1][1][1]]
            #проверка первого соседнего тайла
            check1 = check1Tile.getAvlblPosture2(diagonalData[1][1], secondDiagPlayGround)
            #проверка второго соседнего тайла
            check2 = check2Tile.getAvlblPosture2(diagonalData[0][1], firstDiagPlayGround)
            #тип перемещения на итоговом тайле
            stayMoveType = self.__avlblGridCoords[curGridCoor[0]][curGridCoor[1]].getAvlblPostureToStay()
            checkTuple = (check1.value, check2.value)
            checkList = (check1, check2)
            index = np.argmax(checkTuple)
            #возвращается тип перемещения при перехода в тайл и итоговый тип перемещения
            return (checkList[index], stayMoveType)
        #если прямолинейное перемещение
        else:
            #playGround с которого уходим
            prevPlayGround = prevGridCoor[0]
            #сетка с данными по типу перемещения
            prevAvlblGridCoords = prevPlayGround['Interfaces'].getAvlblGridCoords()
            #тип перемерещения для перехода на тайл
            moveType = prevAvlblGridCoords[prevGridCoor[1][0]][prevGridCoor[1][1]].getAvlblPostureToStay()
            #тип перемещения по итогу перехода на тайл
            stayMoveType = self.__avlblGridCoords[curGridCoor[0]][curGridCoor[1]].getAvlblPostureToStay()
            if stayMoveType.value > moveType.value:
                moveType = stayMoveType
            return (moveType, stayMoveType)
          
    
    #расчет доступного положения тела для перехода в ячейку
    def getMoveTypeByGridCoorNoBridge(self, curGridCoor, prevGridCoor):    
        deltaY = curGridCoor[0] - prevGridCoor[0]
        deltaX = curGridCoor[1] - prevGridCoor[1]
        #диагональное двиение
        if (deltaY > 0) and (deltaX > 0):
            direction = 'pypx'
        elif (deltaY < 0) and (deltaX > 0):
            direction = 'mypx'
        elif (deltaY < 0) and (deltaX < 0):
            direction = 'mymx'
        elif (deltaY > 0) and (deltaX < 0):
            direction = 'pymx'
        elif (deltaY > 0) and (deltaX == 0):
            direction = 'py'
        elif (deltaY < 0) and (deltaX == 0):
            direction = 'my'
        elif (deltaY == 0) and (deltaX < 0):
            direction = 'mx'
        elif (deltaY == 0) and (deltaX > 0):
            direction = 'px'
        if len(direction) == 2:
            return self.getMoveTypeStraight(curGridCoor, prevGridCoor)
        elif len(direction) == 4:
            return self.getMoveTypeDiagonal(curGridCoor, prevGridCoor, direction)
        
    #получение положения тела при диагональном пермещении        
    def getMoveTypeDiagonal(self, curGridCoor, prevGridCoor, direction):
        if direction == 'pypx':
            check1 = self.__avlblGridCoords[prevGridCoor[0] + 1][prevGridCoor[1]].getAvlblPosture(prevGridCoor, direction)
            check2 = self.__avlblGridCoords[prevGridCoor[0]][prevGridCoor[1] + 1].getAvlblPosture(prevGridCoor, direction)               
        elif direction == 'mypx':
            check1 = self.__avlblGridCoords[prevGridCoor[0] - 1][prevGridCoor[1]].getAvlblPosture(prevGridCoor, direction)
            check2 = self.__avlblGridCoords[prevGridCoor[0]][prevGridCoor[1] + 1].getAvlblPosture(prevGridCoor, direction) 
        elif direction == 'mymx':
            check1 = self.__avlblGridCoords[prevGridCoor[0] - 1][prevGridCoor[1]].getAvlblPosture(prevGridCoor, direction)
            check2 = self.__avlblGridCoords[prevGridCoor[0]][prevGridCoor[1] - 1].getAvlblPosture(prevGridCoor, direction) 
        elif direction == 'pymx':
            check1 = self.__avlblGridCoords[prevGridCoor[0] + 1][prevGridCoor[1]].getAvlblPosture(prevGridCoor, direction)
            check2 = self.__avlblGridCoords[prevGridCoor[0]][prevGridCoor[1] - 1].getAvlblPosture(prevGridCoor, direction) 
        check4 = self.__avlblGridCoords[prevGridCoor[0]][prevGridCoor[1]].getAvlblPostureToStay()
        check3 = self.__avlblGridCoords[curGridCoor[0]][curGridCoor[1]].getAvlblPostureToStay()
        checkTuple= (check1.value, check2.value, check3.value, check4.value)
        checkList = (check1, check2, check3, check4)
        index = np.argmax(checkTuple)
        return (checkList[index], check3)
    #получение положения тела при прямом пермещении   
    def getMoveTypeStraight(self, curGridCoor, prevGridCoor):
        moveType = self.__avlblGridCoords[prevGridCoor[0]][prevGridCoor[1]].getAvlblPostureToStay()
        stayMoveType = self.__avlblGridCoords[curGridCoor[0]][curGridCoor[1]].getAvlblPostureToStay()
        if stayMoveType.value > moveType.value:
            moveType = stayMoveType
        return (moveType, stayMoveType)
    
    #проверка перемещения между play ground
    #path - нам нуен для расчет прыжка
    def checkGridCoorByDirectionToBridgeTile(self, gridCoor, bridgedTile, direction, checkDiagonalTiles, bridgedPlayGround):
        if len(direction) == 2:
            return self.checkGridCoorStraightBridge(gridCoor, bridgedTile, direction, bridgedPlayGround)
        elif len(direction) == 4:
            return self.checkGridCoorDiagonalBridge(gridCoor, bridgedTile, direction, bridgedPlayGround, checkDiagonalTiles)
    #!!! В теории можно оббъединить с простым чекером
    #проверка диагонального перемещения на соседний play ground 
    #check1 - отсутствие диагональной преграды слева по движению
    #check2 - отсутствие диагональной преграды справа по движению
    #check3 - отсутствие преграды в точке назначения
    def checkGridCoorDiagonalBridge(self, gridCoor, bridgedTile, direction, bridgedPlayGround, checkDiagonalTiles):
        firstDiagPlayGround = checkDiagonalTiles[0][0]
        firstAvlblGridCoords = firstDiagPlayGround['Interfaces'].getAvlblGridCoords()
        check1Tile = firstAvlblGridCoords[checkDiagonalTiles[0][1][0]][checkDiagonalTiles[0][1][1]]
        
        secondDiagPlayGround = checkDiagonalTiles[1][0]
        secondAvlblGridCoords = secondDiagPlayGround['Interfaces'].getAvlblGridCoords()
        check2Tile = secondAvlblGridCoords[checkDiagonalTiles[1][1][0]][checkDiagonalTiles[1][1][1]]
        
        check1 = check1Tile.getAvlblDirection2(checkDiagonalTiles[1][1], secondDiagPlayGround)
        check2 = check2Tile.getAvlblDirection2(checkDiagonalTiles[0][1], firstDiagPlayGround)
        
        bridgedAvlblGridCoords = bridgedPlayGround['Interfaces'].getAvlblGridCoords()
        check3Tile = bridgedAvlblGridCoords[bridgedTile[0]][bridgedTile[1]]
        check3 = check3Tile.getAvlblToStay()
        
        #проверка блокировки ячейки юнитом
        lockedByUnit =  firstDiagPlayGround['Interfaces'].checkUnitLockTile(checkDiagonalTiles[0][1])
        if lockedByUnit:
            check1 = False
        lockedByUnit =  secondDiagPlayGround['Interfaces'].checkUnitLockTile(checkDiagonalTiles[1][1])
        if lockedByUnit:
            check2 = False    
        lockedByUnit = bridgedPlayGround['Interfaces'].checkUnitLockTile(bridgedTile)
        if lockedByUnit:
            check3 = False        
        if (check1 == True) and (check2 == True) and (check3 == True):
            return True
        return False
        
    def checkUnitLockTile(self, nextGridCoor):
        return self.__unitLockGrid[nextGridCoor[0]][nextGridCoor[1]]
        
    #проверка продольного перемещения 
    #нужно будет чекануть после расчета пути, т.к. нужен путь для расчета barrel jump
    #но как минимум нужно подумать над примитивным чекером 
    def checkGridCoorStraightBridge(self, gridCoor, bridgedTile, direction, bridgedPlayGround):
        
        nextGridCoor = bridgedTile
        bridgedAvlblGridCoords = bridgedPlayGround['Interfaces'].getAvlblGridCoords()
        #проверка блокировки ячейки юнитом
        #lockedByUnit = bridgedAvlblGridCoords[nextGridCoor[0]][nextGridCoor[1]].getTileLockedByUnitFlag()
        lockedByUnit = bridgedPlayGround['Interfaces'].checkUnitLockTile(nextGridCoor)
        if lockedByUnit:
            return False        
        #чекаем ячейки для перехода
        bridgeCheckStayResult = bridgedAvlblGridCoords[nextGridCoor[0]][nextGridCoor[1]].getAvlblToStay()
        checkStayResult = self.__avlblGridCoords[gridCoor[0]][gridCoor[1]].getAvlblToStay()
        #можем пройти 
        if checkStayResult and bridgeCheckStayResult:
            return True
        else:
            return False

        
    #проверка перемещения
    #path - нам нуен для расчет прыжка
    def checkGridCoorByDirection(self, gridCoor, direction, path):
        if len(direction) == 2:
            return self.checkGridCoorStraight(gridCoor, direction, path)
        elif len(direction) == 4:
            return self.checkGridCoorDiagonal(gridCoor, direction)

    #проверка диагонального перемещения
    #check1 - отсутствие диагональной преграды слева по движению
    #check2 - отсутствие диагональной преграды справа по движению
    #check3 - отсутствие преграды в точке назначения
    def checkGridCoorDiagonal(self, gridCoor, direction):
        #проверка блокировки ячейки юнитом    
        if direction == 'pypx':
            nextGridCoor1 = (gridCoor[0] + 1, gridCoor[1])
            nextGridCoor2 = (gridCoor[0], gridCoor[1] + 1)
            nextGridCoor3 = (gridCoor[0] + 1, gridCoor[1] + 1)
        elif direction == 'pymx':
            nextGridCoor1 = (gridCoor[0] + 1, gridCoor[1])
            nextGridCoor2 = (gridCoor[0], gridCoor[1] - 1)
            nextGridCoor3 = (gridCoor[0] + 1, gridCoor[1] - 1)
        elif direction == 'mypx':
            nextGridCoor1 = (gridCoor[0] - 1, gridCoor[1])
            nextGridCoor2 = (gridCoor[0], gridCoor[1] + 1)
            nextGridCoor3 = (gridCoor[0] - 1, gridCoor[1] + 1)
        elif direction == 'mymx':
            nextGridCoor1 = (gridCoor[0] - 1, gridCoor[1])
            nextGridCoor2 = (gridCoor[0], gridCoor[1] - 1)
            nextGridCoor3 = (gridCoor[0] - 1, gridCoor[1] - 1)
        check1Tile = self.__avlblGridCoords[nextGridCoor1[0]][nextGridCoor1[1]]
        check2Tile = self.__avlblGridCoords[nextGridCoor2[0]][nextGridCoor2[1]]
        check3Tile = self.__avlblGridCoords[nextGridCoor3[0]][nextGridCoor3[1]]
        if check1Tile == 'Empty':
            check1 = False
        else:
            check1 = check1Tile.getAvlblDirection(gridCoor, direction)
            lockedByUnit = self.__unitLockGrid[nextGridCoor1[0]][nextGridCoor1[1]]
            if lockedByUnit:
                check1 = False  
        if check2Tile == 'Empty':
            check2 = False
        else:
            check2 = check2Tile.getAvlblDirection(gridCoor, direction)
            lockedByUnit = self.__unitLockGrid[nextGridCoor2[0]][nextGridCoor2[1]]
            if lockedByUnit:
                check2 = False
        if check3Tile == 'Empty':
            check3 = False
        else:
            check3 = check3Tile.getAvlblToStay()
            lockedByUnit = self.__unitLockGrid[nextGridCoor3[0]][nextGridCoor3[1]]
            if lockedByUnit:
                check3 = False
        #проверка блокировки ячейки юнитом  
        if (check1 == True) and (check2 == True) and (check3 == True):
            return True
        return False

    def isTileAvalableToStay(self, gridCoor):
        checkTile = self.__avlblGridCoords[gridCoor[0]][gridCoor[1]]
        return checkTile.getAvlblToStay()


    #проверка продольного перемещения
    def checkGridCoorStraight(self, gridCoor, direction, path):
        if direction == 'py':
            nextGridCoor = (gridCoor[0] + 1, gridCoor[1])
        elif direction == 'px':
            nextGridCoor = (gridCoor[0], gridCoor[1] + 1)
        elif direction == 'my':
            nextGridCoor = (gridCoor[0] - 1, gridCoor[1])
        elif direction == 'mx':
            nextGridCoor = (gridCoor[0], gridCoor[1] - 1)
        if self.__gridCoor[nextGridCoor[0]][nextGridCoor[1]] == 'Empty':
            return False
        #проверка блокировки ячейки юнитом
        #lockedByUnit = self.__avlblGridCoords[nextGridCoor[0]][nextGridCoor[1]].getTileLockedByUnitFlag()
        lockedByUnit = self.__unitLockGrid[nextGridCoor[0]][nextGridCoor[1]]
        if lockedByUnit:
            return False        
        #чекаем ячейки для перехода
        checkStayResult = self.__avlblGridCoords[nextGridCoor[0]][nextGridCoor[1]].getAvlblToStay()
        return checkStayResult

     
        
        
#этот класс кхранит данные по доступности ячейки для перемещения на и через неё
class GridCoorAvlblDirections(object):
    #checkTileResult
    #[0] checkPosturesResult доступные типы перемещения на тайле по блокам
    #[1] [self.__tileBridgesStraight, self.__tileBridgesDiagonal]
    #координаты в сетке и блоки с доступными перемещениями
    def __init__(self, gridCoor, checkTileResult, playGround):
        #slots TODO
        """Constructor"""
        self.__gridCoor = gridCoor
        #bridge инофрмация тайла
        self.__bridges = checkTileResult[1]
        #флаг того что это bridge tile
        self.__bridgeFlag = False
        for item in self.__bridges.diagonalData:
            if item[0]:
                self.__bridgeFlag = True
                break
        if not(self.__bridgeFlag):
            for item in self.__bridges.straightData:
                if item[0]:
                    self.__bridgeFlag = True
                    break
        self.__playGround = playGround
        #доступные типы перемещения на данном тайле по блокам
        self.__checkBlocks = checkTileResult[0]
        #флаг отвечающий за то что на ячейке впринцепе можно находится
        self.__checkBlock = [True, True, True, True]
        for id, elem in enumerate(self.__checkBlocks):
            if elem == structs.SoldierMoveTypes.NoMove:
                self.__checkBlock[id] = False
        self.__checkBlock = tuple(self.__checkBlock)
        
    def getBridgeFlag(self):
        return self.__bridgeFlag
    
    #получить текущие координаты
    def getGridCoords(self):
        return self.__gridCoor
    #получить Bridges тайла на другие playGround
    def getTileBridges(self):
        return self.__bridges
    
    def getAvlblPosture2(self, secondTileGridPos, secondPlayGround):
        checkResult = []
        firstTileWorldPos = self.__playGround['Interfaces'].getCoorByGridPos(self.__gridCoor[0], self.__gridCoor[1])
        secondTileWorldPos = secondPlayGround['Interfaces'].getCoorByGridPos(secondTileGridPos[0], secondTileGridPos[1])
        if firstTileWorldPos.y > secondTileWorldPos.y:
            if firstTileWorldPos.x < secondTileWorldPos.x:
                return self.__checkBlocks[2]
            elif firstTileWorldPos.x > secondTileWorldPos.x:
                return self.__checkBlocks[3]
        elif firstTileWorldPos.y < secondTileWorldPos.y:
            if firstTileWorldPos.x < secondTileWorldPos.x:
                return self.__checkBlocks[0]
            elif firstTileWorldPos.x > secondTileWorldPos.x:
                return self.__checkBlocks[1]
    
    #квадрат т
    def getAvlblPosture(self, gridCoor, direction):
        deltaY = gridCoor[0] - self.__gridCoor[0]
        deltaX = gridCoor[1] - self.__gridCoor[1]
        if (deltaY < 0) and (deltaX == 0):
            if direction == 'pypx':
                return self.__checkBlocks[1]
            elif direction == 'pymx':
                return self.__checkBlocks[0]
        elif (deltaY == 0) and (deltaX > 0):
            if direction == 'mymx':
                return self.__checkBlocks[1]
            elif direction == 'pymx':
                return self.__checkBlocks[2]
        elif (deltaY > 0) and (deltaX == 0):
            if direction == 'mypx':
                return self.__checkBlocks[2]
            elif direction == 'mymx':
                return self.__checkBlocks[3]
        elif (deltaY == 0) and (deltaX < 0):
            if direction == 'pypx':
                return self.__checkBlocks[3]
            elif direction == 'mypx':
                return self.__checkBlocks[0]
    
    def getAvlblDirection2(self, secondTileGridPos, secondPlayGround):
        firstTileWorldPos = self.__playGround['Interfaces'].getCoorByGridPos(self.__gridCoor[0], self.__gridCoor[1])
        secondTileWorldPos = secondPlayGround['Interfaces'].getCoorByGridPos(secondTileGridPos[0], secondTileGridPos[1])
        if firstTileWorldPos.y > secondTileWorldPos.y:
            if firstTileWorldPos.x < secondTileWorldPos.x:
                return self.__checkBlock[2]
            elif firstTileWorldPos.x > secondTileWorldPos.x:
                return self.__checkBlock[3]
        elif firstTileWorldPos.y < secondTileWorldPos.y:
            if firstTileWorldPos.x < secondTileWorldPos.x:
                return self.__checkBlock[0]
            elif firstTileWorldPos.x > secondTileWorldPos.x:
                return self.__checkBlock[1]

    def getAvlblDirection(self, gridCoor, direction):
        #здесь нужно предусмотреть, что возможен переход через bridge tile
        deltaY = gridCoor[0] - self.__gridCoor[0]
        deltaX = gridCoor[1] - self.__gridCoor[1]
        if (deltaY < 0) and (deltaX == 0):
            if direction == 'pypx':
                return self.__checkBlock[1]
            elif direction == 'pymx':
                return self.__checkBlock[0]
        elif (deltaY == 0) and (deltaX > 0):
            if direction == 'mymx':
                return self.__checkBlock[1]
            elif direction == 'pymx':
                return self.__checkBlock[2]
        elif (deltaY > 0) and (deltaX == 0):
            if direction == 'mypx':
                return self.__checkBlock[2]
            elif direction == 'mymx':
                return self.__checkBlock[3]
        elif (deltaY == 0) and (deltaX < 0):
            if direction == 'pypx':
                return self.__checkBlock[3]
            elif direction == 'mypx':
                return self.__checkBlock[0]

    #можно ли вообще переместиться в ячейку
    def getAvlblToStay(self):
        if False in self.__checkBlock:
            return False
        else:
            return True
    
    def getAvlblPostureToStay(self):
        checkTuple = (self.__checkBlocks[0].value,
                      self.__checkBlocks[1].value,
                      self.__checkBlocks[2].value,
                      self.__checkBlocks[3].value)
        index = np.argmax(checkTuple)
        return self.__checkBlocks[index]