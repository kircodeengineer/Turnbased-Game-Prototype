class LevelInterfaces(object):
    def __init__(self, level):
        #объекты по этажам
        self.__objByFloorsList = []
        self.__objByFloorsList.append([])
        self.__level = level
        self.__currentVisibleFloor = 2
    
    def collectObjectsByFloors(self):
        for member in self.__level.groupMembers:
            if member.groupMembers != None:
                if 'Building' in member.name:
                    buildingFloorList = member['Interfaces'].getFloorsList()
                    for idf,floor in enumerate(buildingFloorList):
                        self.putObjInObjByFloorsList(idf, member)
        self.showObjOnFloor(0)
    
    #запись объекта в список объектов по этажам
    def putObjInObjByFloorsList(self, floorNum, object):
        while floorNum > (len(self.__objByFloorsList) - 1):
            self.__objByFloorsList.append([])
        self.__objByFloorsList[floorNum].append(object)
        
    
    def maxFloorNum(self):
        return (len(self.__objByFloorsList) - 1)
    
    #отображение объектов на этаже    
    def showObjOnFloor(self, floorNum):
        #проверка ограничений
        if (floorNum > self.maxFloorNum()) or (floorNum < 0):
            return self.__currentVisibleFloor
        if floorNum == self.__currentVisibleFloor:
            return self.__currentVisibleFloor
        #скрываем объекты для этажей выше указанного
        if floorNum < self.__currentVisibleFloor:
            i = self.__currentVisibleFloor
            while i > floorNum:
                hideList = self.__objByFloorsList[i]
                for obj in hideList:
                    obj['Interfaces'].hideFloor(i)
                i -= 1
        #отображаем этажи выше указаннного включительно
        elif floorNum > self.__currentVisibleFloor:
            i = self.__currentVisibleFloor + 1
            while i <= floorNum:
                showList = self.__objByFloorsList[i]
                for obj in showList:
                    obj['Interfaces'].showFloor(i)
                i += 1
        self.__currentVisibleFloor = floorNum
        return self.__currentVisibleFloor
