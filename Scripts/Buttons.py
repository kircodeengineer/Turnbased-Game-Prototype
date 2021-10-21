import bge
from mathutils import Matrix
import copy
from enum import Enum
import structs

scene = bge.logic.getCurrentScene()


for scene in bge.logic.getSceneList():
    if scene.name == 'GUI':
        guiScene = scene
        guiControl = scene.objects['GUI Control']
        buttonsScene = scene
        mouseScene = scene
        cursor = scene.objects['Cursor']
    elif scene.name == 'Scene':
        computer = scene.objects['Computer']  

        
def initMessage(cont):
    own = cont.owner
    if 'Interfaces' not in computer:
        return
    if 'init' not in own:
        init()
        own.endObject()
            

def init():
    guiControl['Interfaces'] = GuiControlInterfaces(guiControl)
    #получилась несогласованность с определением переменной. Нужно обернуть в класс и сделать красиво.
    for scene in bge.logic.getSceneList():
        if scene.name == 'GUI':
            cursor = scene.objects['Cursor']
            print(cursor, ' here 2')

    cursor['Interfaces'] = CursorInterfaces(cursor)
    #инициализация кнопок
    etalon = buttonsScene.objects['Etalon Unit Control Button']
    mesh = etalon.meshes[0]
    array = mesh.getVertexArrayLength(0)
    etalon['UV'] = []
    for v in range(0, array):
        vertex = mesh.getVertex(0, v)
        uv = vertex.getUV()
        vertex.setUV(uv)
        etalon['UV'].append(copy.copy(uv))
    #настройка текстур
    for object in buttonsScene.objects:
        if 'TurnFight' in object.name:
            object['Interfaces'] = TurnFightButton(object)
            object['Interfaces'].unlockButton()
        elif 'Select Unit' in object.name:
            object['Interfaces'] = SelectUnitButton(object)
            object['Interfaces'].unlockButton()
        elif 'Change Floor' in object.name:
            object['Interfaces'] = ChangeFloorButton(object) 
            object['Interfaces'].unlockButton()
        elif 'Floor Indicator' in object.name:
            object['Interfaces'] = FloorIndicatorButton(object) 
            object['Interfaces'].unlockButton()
        elif 'Button Box' in object.name:
            mesh = object.meshes[0]
            array = mesh.getVertexArrayLength(0)
            i = 0
            for v in range(0, array):
                vertex = mesh.getVertex(0, v)
                vertex.setUV(etalon['UV'][i])
                i += 1
            object['Interfaces'] = ButtonFromButtonBox(object)
            
            if '0' in object.name:
                object['Interfaces'].setImage(ButtonImage['Shoot'])
                object['Interfaces'].unlockButton()
            if '1' in object.name:
                object['Interfaces'].setImage(ButtonImage['None'])
                object['Interfaces'].lockButton()
            if '2' in object.name:
                object['Interfaces'].setImage(ButtonImage['None'])
                object['Interfaces'].lockButton()
            if '3' in object.name:
                object['Interfaces'].setImage(ButtonImage['None'])
                object['Interfaces'].lockButton()
            if '4' in object.name:
                object['Interfaces'].setImage(ButtonImage['None'])
                object['Interfaces'].lockButton()
            if '5' in object.name:
                object['Interfaces'].setImage(ButtonImage['Run'])
                object['Interfaces'].unlockButton()
            if '6' in object.name:
                object['Interfaces'].setImage(ButtonImage['None'])
                object['Interfaces'].lockButton()
            if '7' in object.name:
                object['Interfaces'].setImage(ButtonImage['None'])
                object['Interfaces'].lockButton()
                
        
UVimages = {'Buttons' : 0, 'Cursor' : 1, 'TurnFight' : 2, 'Change Floor' : 3, 'Floor Indicator' : 4}

class UVTransform(object):
    def __init__(self, own, currentUVobject):
        if currentUVobject == UVimages['Buttons']:
            self.cells = [4, 10]
        elif currentUVobject == UVimages['Cursor']:
            self.cells = [2, 1]
        elif currentUVobject == UVimages['TurnFight']:
            self.cells = [1, 3]
        elif currentUVobject == UVimages['Change Floor']:
            self.cells = [1, 2]
        elif currentUVobject == UVimages['Floor Indicator']:
            self.cells = [1, 4]
            
        def get_mat_id(self):
            return 0
        def get_cell_coords(self):
            cell_size = [1 / self.cells[i] for i in range(2)]
            cell_coords = []
            for y in range(self.cells[1]):
                for x in range(self.cells[0]):
                    cell_coords.append([x * cell_size[0], y * cell_size[1]])    
            return cell_coords
        self.mesh = own.meshes[0]
        self.mat_id = get_mat_id(self)
        self.cell_coords = get_cell_coords(self)
        self.id = 0
        
    def main(self, id):
        offset = [self.cell_coords[id][i] - self.cell_coords[self.id][i] for i in range(2)]
        matrix = Matrix.Translation((offset[0], offset[1], 0))
        self.mesh.transformUV(self.mat_id, matrix, 0)
        self.id = id


                
def pressDispetcher(cont):
    own = cont.owner
    act = cont.actuators['Pressed']
    if 'Interfaces' not in own:
        return
    own['Interfaces'].pressDispetcher(act)
    

def pressed(cont):
    sensors = cont.sensors
    own = cont.owner
    if 'Interfaces' not in own:
        return
    own['Interfaces'].pressed(cont)
    

                
#dict состояний панели кнопок управления персонажем            
ButtonBoxWindow = {'Main Window' : 0, 'Move Type Window' : 1, 'Attack Window' : 2}
#dict состояний кнопки
ButtonState = {'Unlocked' : 0, 'Active' : 1, 'Avalable' : 2, 'Locked' : 3}
#dict состояний панели кнопок управления персонажем  
ButtonImage = {'Shoot Blocked' : 0, 'Shoot' : 4, 'None' : 5, 'Choose Move Point Locked' : 8, 'Choose Move Point' : 12, 'Look Around' : 14, 'Look Around Locked' : 10, 'Run Locked' : 16, 'Walk Locked' : 17, 'Crouch Locked' : 18, 'Run Locked' : 19, 'Run Active' : 20, 'Walk Active' : 21, 'Crouch Active' : 22, 'Prone Active' : 23, 'Run Avalable' : 24, 'Walk Avalable' : 25, 'Crouch Avalable' : 26, 'Prone Avalable' : 27, 'Run' : 28, 'Walk' : 29, 'Crouch' : 30, 'Prone' : 31, 'Cancel' : 36}
#dict состояния кнопки управления боем и ходом
TurnFightButtonFunctions = {'Start Fight' : 0, 'Locked' : 1, 'End Turn' : 2, }
#dict кнопки изменения этажа
ChangeFloorButtonImages = {'Up' : 0, 'Down' : 1}


        
TextIndicatorValues = {'Player Turn' : 'Player Turn', 'Enemy Turn' : 'Enemy Turn'}
ColorIndicatorValues = {'Player Turn' : [0.001545, 0.178862, 0.000558, 0], 'Enemy Turn' : [0.367238, 0.001208, 0.00433, 0]}

#массив иконок юнитов
class UnitsImages(Enum):
    SoldierMen = buttonsScene.objects['Soldier Men Image']
    SoldierGirl = buttonsScene.objects['Soldier Girl Image']
    SoldierMech = buttonsScene.objects['Soldier in Mech Image']
    NoImage = None

#массив иконок юнитов
class UnitsControlMenu(Enum):
    Unit0 = buttonsScene.objects['Unit 0 Active']
    Unit1 = buttonsScene.objects['Unit 1 Active']
    Unit2 = buttonsScene.objects['Unit 2 Active']
    Unit3 = buttonsScene.objects['Unit 3 Active']
    Unit4 = buttonsScene.objects['Unit 4 Active']
    Unit5 = buttonsScene.objects['Unit 5 Active']
    Unit6 = buttonsScene.objects['Unit 6 Active']


class GuiControlInterfaces(object):
    def __init__(self, guiControl):
        """Constructor"""
        self.__guiControl = guiControl
        self.__buttonBoxWindow = ButtonBoxWindow['Main Window']
        #buttonBox
        self.__buttonBox = []
        self.__buttonBox.append(buttonsScene.objects['Button Box.Button 0'])
        self.__buttonBox.append(buttonsScene.objects['Button Box.Button 1'])
        self.__buttonBox.append(buttonsScene.objects['Button Box.Button 2'])
        self.__buttonBox.append(buttonsScene.objects['Button Box.Button 3'])
        self.__buttonBox.append(buttonsScene.objects['Button Box.Button 4'])
        self.__buttonBox.append(buttonsScene.objects['Button Box.Button 5'])
        self.__buttonBox.append(buttonsScene.objects['Button Box.Button 6'])
        self.__buttonBox.append(buttonsScene.objects['Button Box.Button 7'])
        
        self.__cursor = mouseScene.objects['Cursor']
        self.__turnFightButton = buttonsScene.objects['TurnFight Button']
        self.__turnBaseTextIndicator = buttonsScene.objects['Turn Base Text Indicator']
        self.__turnBaseTextIndicator.text = TextIndicatorValues['Player Turn']
        self.__turnBaseTextIndicator.resolution = 1
        textColor = [0.527719 , 0.482956, 0.108567, 1.0]
        self.__turnBaseTextIndicator.color = textColor
        self.__turnBaseTextIndicator.visible = False
        
        self.__apCount = buttonsScene.objects['AP Count']
        self.__apCount.color = textColor
        self.__apCount.resolution = 1
        self.__apCount.visible = False
        self.__apText = 'AP '
        self.__apCount.text = self.__apText + str(0)

        self.__turnBaseColorIndicator = guiScene.objects['Turn Base Color Indicator']
        for mesh in self.__turnBaseColorIndicator.meshes:
            for matIdx in range(len(mesh.materials)):
                for vertexIdx in range(mesh.getVertexArrayLength(matIdx)):
                    vertex = mesh.getVertex(matIdx, vertexIdx)
                    vertex.color = ColorIndicatorValues[self.__turnBaseTextIndicator.text] 
        
        

        
        
        self.__selectUnitBbuttons = []
        self.__selectUnitBbuttons.append(buttonsScene.objects['Select Unit 0 Button'])
        self.__selectUnitBbuttons.append(buttonsScene.objects['Select Unit 1 Button'])
        self.__selectUnitBbuttons.append(buttonsScene.objects['Select Unit 2 Button'])
        #getUnitsList
        #unlockSelectUnitButtons
        
        #массив менюшек юнитов
        self.__unitsMenus = []
        self.__unitsMenus.append(UnitsControlMenu.Unit0.value)
        self.__unitsMenus.append(UnitsControlMenu.Unit1.value)
        self.__unitsMenus.append(UnitsControlMenu.Unit2.value)
        self.__unitsMenus.append(UnitsControlMenu.Unit3.value)
        self.__unitsMenus.append(UnitsControlMenu.Unit4.value)
        self.__unitsMenus.append(UnitsControlMenu.Unit5.value)
        self.__unitsMenus.append(UnitsControlMenu.Unit6.value)
        # отключаем их видимость менюшек на сцене
        for menu in self.__unitsMenus:
            menu.visible = False

        #отключаем их видимость на сцене
        UnitsImages.SoldierMen.value.visible = False
        UnitsImages.SoldierGirl.value.visible = False
        UnitsImages.SoldierMech.value.visible = False
        #его нужно зополнить компьютеру, в момент инициализации списка юнитов
        self.__playerUnitsImages = []
        self.__playerUnitsImages.append(UnitsImages.NoImage.value)
        self.__playerUnitsImages.append(UnitsImages.NoImage.value)
        self.__playerUnitsImages.append(UnitsImages.NoImage.value)
        self.__playerUnitsImages.append(UnitsImages.NoImage.value)
        self.__playerUnitsImages.append(UnitsImages.NoImage.value)
        self.__playerUnitsImages.append(UnitsImages.NoImage.value)
        self.__playerUnitsImages.append(UnitsImages.NoImage.value)
        #подразумевается.что управляющий алгоритм проинициализирован
        self.setPlayerUnitImage()
        self.setUnitControl(0)
        
        #массив индикаторов этажей
        self.__floorsIndicators = []
        self.__floorsIndicators.append(buttonsScene.objects['Floor Indicator Button.000'])
        self.__floorsIndicators.append(buttonsScene.objects['Floor Indicator Button.001'])
        self.__floorsIndicators.append(buttonsScene.objects['Floor Indicator Button.002'])
        self.__floorsIndicators.append(buttonsScene.objects['Floor Indicator Button.003'])
        self.__floorsIndicators.append(buttonsScene.objects['Floor Indicator Button.004'])
        self.__floorsIndicators.append(buttonsScene.objects['Floor Indicator Button.005'])
        self.__floorsIndicators.append(buttonsScene.objects['Floor Indicator Button.006'])
        self.__floorsIndicators.append(buttonsScene.objects['Floor Indicator Button.007'])
        self.__activeFloorNum = 0

    #устанавливаем гифку для нужного юнита
    def setPlayerUnitImage(self):
        allPlayerUnits = computer['Interfaces'].getAllPlayerUnits()
        print(allPlayerUnits)
        for id, unit in enumerate(allPlayerUnits):
            unitInterfaces = unit['Interfaces']
            if unitInterfaces.getUnitType() == structs.UnitTypes.Soldier:
                if unitInterfaces.getSubUnitType() == structs.SoldierSubType.Men:
                    self.__playerUnitsImages[id] = UnitsImages.SoldierMen.value
                elif unitInterfaces.getSubUnitType() == structs.SoldierSubType.Girl:
                    self.__playerUnitsImages[id] = UnitsImages.SoldierGirl.value
            elif unitInterfaces.getUnitType() == structs.UnitTypes.Mech:
                print(12345)
                self.__playerUnitsImages[id] = UnitsImages.SoldierMech.value


    def showUpFloor(self):
        if self.__activeFloorNum == (len(self.__floorsIndicators) - 1):
            return
        nextFloor = self.__activeFloorNum + 1
        computer['Interfaces'].signalFromGuiShowFloor(nextFloor)
    
    def hideDownFloor(self):
        minFloorNum = 0
        if self.__activeFloorNum == minFloorNum:
            return
        nextFloor = self.__activeFloorNum - 1
        computer['Interfaces'].signalFromGuiShowFloor(nextFloor)
        
    def setFloorIndicators(self, floorNumber):
        for id, floor in enumerate(self.__floorsIndicators):
            if id <= floorNumber:
                floor['Interfaces'].show()
            else:
                floor['Interfaces'].hide()
        self.__activeFloorNum = floorNumber

    
    def hideFloors(self, floorNumber):
        for id, floor in enumerate(self.__floorsIndicators):
            if id > floorNumber:
                floor['Interfaces'].hide()
            elif id == floorNumber:
                self.__activeFloorNum = id
                break
    
    def updateAPCountIndicator(self, count):
        self.__apCount.text = self.__apText + str(count)
    
    def setTurnBaseOn(self):
        computer['Interfaces'].setFightOn()
        #из компа
        unit = computer['Interfaces'].getPlayerUnit()
        unitInterf = unit['Interfaces']
        pgInterf = unitInterf.getPGinterfaces()
        self.__apCount.text = self.__apText + str(pgInterf.getAPcount())
        
        self.__turnFightButton['Interfaces'].setCurrentFunction(TurnFightButtonFunctions['End Turn'])
        self.__turnBaseTextIndicator.visible = True
        self.__apCount.visible = True
        self.__turnBaseTextIndicator.text = TextIndicatorValues['Player Turn']
        for mesh in self.__turnBaseColorIndicator.meshes:
            for matIdx in range(len(mesh.materials)):
                for vertexIdx in range(mesh.getVertexArrayLength(matIdx)):
                    vertex = mesh.getVertex(matIdx, vertexIdx)
                    vertex.color = ColorIndicatorValues[self.__turnBaseTextIndicator.text]
    
    def setTurnBaseOff(self):
        #из компа
        self.__turnFightButton['Interfaces'].setCurrentFunction(TurnFightButtonFunctions['Start Fight'])
        self.__turnBaseTextIndicator.visible = False
        self.__apCount.visible = False
        self.__turnBaseTextIndicator.text = TextIndicatorValues['Player Turn']
        for mesh in self.__turnBaseColorIndicator.meshes:
            for matIdx in range(len(mesh.materials)):
                for vertexIdx in range(mesh.getVertexArrayLength(matIdx)):
                    vertex = mesh.getVertex(matIdx, vertexIdx)
                    vertex.color = ColorIndicatorValues[self.__turnBaseTextIndicator.text]    
    
    #интерфейс отображения панели управления юнитом
    def setUnitControl(self, number):
        #скрываем все менюшки и гифки всех юнитов
        for idx, unitImage in enumerate(self.__playerUnitsImages):
            if unitImage == UnitsImages.NoImage.value:
                continue
            unitImage.visible = False
            self.__unitsMenus[idx].visible = False
        #отображаем менюшки и гифки подконтрольного игроку юнита
        self.__playerUnitsImages[number].visible = True
        self.__unitsMenus[number].visible = True
        #устанавливаем подконтрольный юнит
        #TODO Надо подумать над тем чтобы изменить это. Графика только отображет. Никакой логики
        computer['Interfaces'].setPlayerUnit(number)
    
    
    def getbuttonBoxRDwindow(self):
        return self.__buttonBoxWindow
    def getPlayerControl(self):
        return self.__playerControl        
    
    def getbuttonBoxRDwindow(self):
        return self.__buttonBoxWindow
    def getPlayerControl(self):
        return self.__playerControl
    def getCursor(self):
        return self.__cursor

    def setMainWindow(self, selectedMoveType):
        self.__cursor['Interfaces'].setMainCursor()
        unit = computer['Interfaces'].getPlayerUnit()
        unitInterf = unit['Interfaces']
        pgInterf = unitInterf.getPGinterfaces()
        pgInterf.setIdleState()
        currentMoveType = unitInterf.getCurrentMoveType()
        if self.__buttonBoxWindow == ButtonBoxWindow['Move Type Window']:
            if selectedMoveType == structs.SoldierMoveTypes.Run:
                unitInterf.setRunMainMoveType()
            elif selectedMoveType == structs.SoldierMoveTypes.Walk:
                unitInterf.setWalkMainMoveType()
            elif selectedMoveType == structs.SoldierMoveTypes.Crouch:
                unitInterf.setCrouchMainMoveType()
            elif selectedMoveType == structs.SoldierMoveTypes.Prone:
                unitInterf.setProneMainMoveType()
            elif selectedMoveType == 'Cancel':
                pass
        self.__buttonBoxWindow = ButtonBoxWindow['Main Window']
        for idx, button in enumerate(self.__buttonBox):
            if idx == 0:
                button['Interfaces'].setImage(ButtonImage['Shoot'])
                button['Interfaces'].unlockButton()
            elif idx == 1:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()
            elif idx == 2:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()
            elif idx == 3:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()
            elif idx == 4:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()
            elif idx == 5:
                if selectedMoveType == structs.SoldierMoveTypes.Run:
                    button['Interfaces'].setImage(ButtonImage['Run'])
                elif selectedMoveType == structs.SoldierMoveTypes.Walk:
                    button['Interfaces'].setImage(ButtonImage['Walk'])
                elif selectedMoveType == structs.SoldierMoveTypes.Crouch:
                    button['Interfaces'].setImage(ButtonImage['Crouch'])
                elif selectedMoveType == structs.SoldierMoveTypes.Prone:
                    button['Interfaces'].setImage(ButtonImage['Prone'])
                elif selectedMoveType == 'Cancel':
                    if unitInterf.getMainMoveType() == structs.SoldierMoveTypes.Run:
                        button['Interfaces'].setImage(ButtonImage['Run'])
                    elif unitInterf.getMainMoveType() == structs.SoldierMoveTypes.Walk:
                        button['Interfaces'].setImage(ButtonImage['Walk'])
                    elif unitInterf.getMainMoveType() == structs.SoldierMoveTypes.Crouch:
                        button['Interfaces'].setImage(ButtonImage['Crouch'])
                    elif unitInterf.getMainMoveType() == structs.SoldierMoveTypes.Prone:
                        button['Interfaces'].setImage(ButtonImage['Prone'])
                button['Interfaces'].unlockButton()
            elif idx == 6:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()
            elif idx == 7:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()

    def setButton5Image(self):
        unit = computer['Interfaces'].getPlayerUnit()
        unitInterf = unit['Interfaces']
        currentMoveType = unitInterf.getCurrentMoveType()
        if currentMoveType == structs.SoldierMoveTypes.Run:
            self.__buttonBox[5]['Interfaces'].setImage(ButtonImage['Run'])
        elif currentMoveType == structs.SoldierMoveTypes.Walk:
            self.__buttonBox[5]['Interfaces'].setImage(ButtonImage['Walk'])
        elif currentMoveType == structs.SoldierMoveTypes.Crouch:
            self.__buttonBox[5]['Interfaces'].setImage(ButtonImage['Crouch'])
        elif currentMoveType == structs.SoldierMoveTypes.Prone:
            self.__buttonBox[5]['Interfaces'].setImage(ButtonImage['Prone'])
    
    def updateMoveTypeButton(self):
        if self.__buttonBoxWindow == ButtonBoxWindow['Main Window']:
            self.setButton5Image()
        elif self.__buttonBoxWindow == ButtonBoxWindow['Move Type Window']:
            self.setMoveTypeButtons()
            
    def setMoveTypeButtons(self):
        unit = computer['Interfaces'].getPlayerUnit()
        unitInterf = unit['Interfaces']
        currentMoveType = unitInterf.getCurrentMoveType()
        for idx, button in enumerate(self.__buttonBox):
            if currentMoveType == structs.SoldierMoveTypes.Run:
                if idx == 0:
                    button['Interfaces'].setImage(ButtonImage['Run Active'])
                    button['Interfaces'].unlockButton()
                elif idx == 1:
                    button['Interfaces'].setImage(ButtonImage['Walk Avalable'])
                    button['Interfaces'].unlockButton()
                elif idx == 2:
                    button['Interfaces'].setImage(ButtonImage['Crouch Avalable'])
                    button['Interfaces'].unlockButton()
                elif idx == 3:
                    button['Interfaces'].setImage(ButtonImage['Prone Avalable'])
                    button['Interfaces'].unlockButton()
            elif currentMoveType == structs.SoldierMoveTypes.Walk:
                if idx == 0:
                    button['Interfaces'].setImage(ButtonImage['Run Avalable'])
                    button['Interfaces'].unlockButton()
                elif idx == 1:
                    button['Interfaces'].setImage(ButtonImage['Walk Active'])
                    button['Interfaces'].unlockButton()
                elif idx == 2:
                    button['Interfaces'].setImage(ButtonImage['Crouch Avalable'])
                    button['Interfaces'].unlockButton()
                elif idx == 3:
                    button['Interfaces'].setImage(ButtonImage['Prone Avalable'])
                    button['Interfaces'].unlockButton()
            elif currentMoveType == structs.SoldierMoveTypes.Crouch:
                if idx == 0:
                    button['Interfaces'].setImage(ButtonImage['Run Avalable'])
                    button['Interfaces'].unlockButton()
                elif idx == 1:
                    button['Interfaces'].setImage(ButtonImage['Walk Avalable'])
                    button['Interfaces'].unlockButton()
                elif idx == 2:
                    button['Interfaces'].setImage(ButtonImage['Crouch Active'])
                    button['Interfaces'].unlockButton()
                elif idx == 3:
                    button['Interfaces'].setImage(ButtonImage['Prone Avalable'])
                    button['Interfaces'].unlockButton()
            elif currentMoveType == structs.SoldierMoveTypes.Prone:
                if idx == 0:
                    button['Interfaces'].setImage(ButtonImage['Run Avalable'])
                    button['Interfaces'].unlockButton()
                elif idx == 1:
                    button['Interfaces'].setImage(ButtonImage['Walk Avalable'])
                    button['Interfaces'].unlockButton()
                elif idx == 2:
                    button['Interfaces'].setImage(ButtonImage['Crouch Avalable'])
                    button['Interfaces'].unlockButton()
                elif idx == 3:
                    button['Interfaces'].setImage(ButtonImage['Prone Active'])
                    button['Interfaces'].unlockButton()
            if idx == 4:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()
            elif idx == 5:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()
            elif idx == 6:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()
            elif idx == 7:
                button['Interfaces'].setImage(ButtonImage['Cancel'])
                button['Interfaces'].unlockButton()
            #checkLock
            maxCurrentMoveType = unitInterf.getMaxCurrentMoveType()
            if maxCurrentMoveType == structs.SoldierMoveTypes.RunWalk:
                pass
            if (maxCurrentMoveType == structs.SoldierMoveTypes.Crouch) or\
                    (maxCurrentMoveType == structs.SoldierMoveTypes.Prone):
                if idx == 0:
                    button['Interfaces'].setImage(ButtonImage['Run Locked'])
                    button['Interfaces'].lockButton()
                elif idx == 1:
                    button['Interfaces'].setImage(ButtonImage['Walk Locked'])
                    button['Interfaces'].lockButton()
            if maxCurrentMoveType == structs.SoldierMoveTypes.Prone:
                if idx == 2:
                    button['Interfaces'].setImage(ButtonImage['Crouch Locked'])
                    button['Interfaces'].lockButton()
                
        
    
    def setMoveTypeWindow(self):
        self.__buttonBoxWindow = ButtonBoxWindow['Move Type Window']
        #for idx, button in enumerate(self.__buttonBox):
        self.setMoveTypeButtons()
        
    
    def setAttackWindow(self):
        unit = computer['Interfaces'].getPlayerUnit()
        pgInterf = unit['Interfaces'].getPGinterfaces()
        pgInterf.setAttackState()
        for idx, button in enumerate(self.__buttonBox):
            if idx != 7:
                button['Interfaces'].setImage(ButtonImage['None'])
                button['Interfaces'].lockButton()
            elif idx == 7:
                button['Interfaces'].setImage(ButtonImage['Cancel'])
                button['Interfaces'].unlockButton()
        self.__buttonBoxWindow = ButtonBoxWindow['Attack Window']
        self.__cursor['Interfaces'].setAttackCursor()
        
        


class CursorInterfaces(object):
    def __init__(self, cursor):
        self.__cursor = cursor
        self.__uvTransform = UVTransform(self.__cursor, UVimages['Cursor'])
        self.__uvTransform.main(0)
    
    def setAttackCursor(self):
        self.__uvTransform.main(1)
        
    def setMainCursor(self):
        self.__uvTransform.main(0)

class ButtonInterfaces(object):
    def __init__(self, button):
        self._button = button
        self.__buttonClicked = False
        self.__image = ButtonImage['Choose Move Point Locked']
        self.__state = ButtonState['Locked']
        if 'Button Box' in self._button.name:
            self.__uvTransform = UVTransform(self._button, UVimages['Buttons'])
        elif 'TurnFight' in self._button.name:
            self.__uvTransform = UVTransform(self._button, UVimages['TurnFight'])
        elif 'Floor Indicator' in self._button.name:
            self.__uvTransform = UVTransform(self._button, UVimages['Floor Indicator'])
            
        self.__pressed = False
        self._activated = False
        
        self._guiControl = guiControl

    #Turn Fight Button functions    
    def getButtonState(self):
        return self.__state
    
    def lockButton(self):
        self.__state = ButtonState['Locked']
        
    def unlockButton(self):
        self.__state = ButtonState['Unlocked']
    
    def setImage(self, image):
        self.__uvTransform.main(image)
        
    def setButtonPressed(self):
        self.__pressed = True
    
    def setButtonReleased(self):
        self.__pressed = False
        
    def getPressFlag(self):
        return self.__pressed
    
    def setButtonActivated(self):
        self._activated = True
        
    def setButtonUnactivated(self):
        self._activated = False
    
    def getButtonActivationFlag(self):
        return self._activated
    
    def pressed(self, cont):
        if self.__state == ButtonState['Unlocked']:
            if self.__pressed:
                self._activated = True
                self.__pressed = False
                act = cont.actuators["Pressed"]
                cont.activate(act)
        
class SelectUnitButton(ButtonInterfaces):
    def pressDispetcher(self, actuator):
        if self._activated:
            if actuator.frame > 0.0:
                unitNum = 0
                if '0' in self._button.name:
                    unitNum = 0
                elif '1' in self._button.name:
                    unitNum = 1
                elif '2' in self._button.name:
                    unitNum = 2
                elif '3' in self._button.name:
                    unitNum = 3
                elif '4' in self._button.name:
                    unitNum = 4
                elif '5' in self._button.name:
                    unitNum = 5
                elif '6' in self._button.name:
                    unitNum = 6
                self._guiControl['Interfaces'].setUnitControl(unitNum)
                actuator.frame = 0.0 
                self._activated = False
             
class ButtonFromButtonBox(ButtonInterfaces):
    def pressDispetcher(self, actuator):
        if self._activated:
            if actuator.frame > 2.95:
                if self._guiControl['Interfaces'].getbuttonBoxRDwindow() == ButtonBoxWindow['Main Window']:
                    if 'Button 5' in self._button.name:
                        self._guiControl['Interfaces'].setMoveTypeWindow()
                    if 'Button 0' in self._button.name:
                        self._guiControl['Interfaces'].setAttackWindow()
                elif self._guiControl['Interfaces'].getbuttonBoxRDwindow() == ButtonBoxWindow['Move Type Window']:
                    if '0' in self._button.name:
                        self._guiControl['Interfaces'].setMainWindow(structs.SoldierMoveTypes.Run)
                    elif '1' in self._button.name:
                        self._guiControl['Interfaces'].setMainWindow(structs.SoldierMoveTypes.Walk)
                    elif '2' in self._button.name:
                        self._guiControl['Interfaces'].setMainWindow(structs.SoldierMoveTypes.Crouch)
                    elif '3' in self._button.name:
                        self._guiControl['Interfaces'].setMainWindow(structs.SoldierMoveTypes.Prone)
                    elif '7' in self._button.name:
                        self._guiControl['Interfaces'].setMainWindow('Cancel')
                elif self._guiControl['Interfaces'].getbuttonBoxRDwindow() == ButtonBoxWindow['Attack Window']:
                    if '7' in self._button.name:
                        self._guiControl['Interfaces'].setMainWindow('Cancel')
                actuator.frame = 0.0 
                self._activated = False

#dict индикаторы этажа
FloorIndicatorButtonImages = {'Up Floor Invisible' : 0, 'Up Floor Visible' : 1 ,'Down Floor Invisible' : 2, 'Down Floor Visible' : 3}
class FloorIndicatorButton(ButtonInterfaces):
    def __init__(self, button):
        ButtonInterfaces.__init__(self, button)
        self.__floorNum = int(button.name[-1])
        self.__isVisible = False
        #down floor / up floor
    
    def pressDispetcher(self, actuator):
        if self._activated:
            if actuator.frame > 0.0:
                self._guiControl['Interfaces'].showFloors(self.__floorNum)
                actuator.frame = 0.0
                self._activated = False
    
    def show(self):
        if not(self.__isVisible): #это условие нужно, т.к. если мы сделаем setImage ,а image будет тот же реакция непредсказуем
            self.setImage(FloorIndicatorButtonImages['Up Floor Visible'])
            self.__isVisible = True
    
    def hide(self):
        if self.__isVisible:
            self.setImage(FloorIndicatorButtonImages['Up Floor Invisible'])
            self.__isVisible = False
        

ButtonDirections = {'Up' : 0, 'Down' : 1}
class ChangeFloorButton(ButtonInterfaces):
    def __init__(self, button):
        ButtonInterfaces.__init__(self, button)
        if 'Up' in button.name:
            self._direction = ButtonDirections['Up']
        elif 'Down' in button.name:
            self._direction = ButtonDirections['Down']   
            
    def pressDispetcher(self, actuator):
        if self._activated:
            if actuator.frame > 2.95:
                if self._direction == ButtonDirections['Up']:
                    self._guiControl['Interfaces'].showUpFloor()
                elif self._direction == ButtonDirections['Down']:
                    self._guiControl['Interfaces'].hideDownFloor()
                actuator.frame = 0.0
                self._activated = False
        
class TurnFightButton(ButtonInterfaces):
    def __init__(self, button):
        ButtonInterfaces.__init__(self, button)
        self._currentFunction = TurnFightButtonFunctions['Start Fight']
        
    def setCurrentFunction(self, function):
        self._currentFunction = function
        self.setImage(function)
        
    def pressDispetcher(self, actuator):
        if self._activated:
            if actuator.frame > 2.95:
                if self._currentFunction == TurnFightButtonFunctions['Start Fight']:
                    self._guiControl['Interfaces'].setTurnBaseOn()
                elif self._currentFunction == TurnFightButtonFunctions['End Turn']:
                    self._guiControl['Interfaces'].setTurnBaseOff()
                actuator.frame = 0.0
                self._activated = False
                
