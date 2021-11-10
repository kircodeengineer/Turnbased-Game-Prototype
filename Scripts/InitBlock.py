import bge
import Level



def init(cont):
    compInit = False
    unitInit = False
    guiInit = False
    mapInit = False
    sceneList = bge.logic.getSceneList()
    sceneCount = 2
    if len(sceneList) == sceneCount:
        for scene in sceneList:
            if scene.name == 'Scene':
                #pgGroup = scene.objects['Play Ground and Barrier Checker']
                level = scene.objects['Test Level']
                if 'Init Block' in level.groupMembers:
                    level.groupMembers['Init Block']['init'] = True
                    return
                
                #инициализация уровня
                if 'Interfaces' not in level:
                    level['Interfaces'] = Level.LevelInterfaces(level)
                    level['Interfaces'].collectObjectsByFloors()
                    return
                
                #инициализация этажей
                
                
                #инициализация Computer. Unit внутри
                computer = scene.objects['Computer']
                if 'Interfaces' not in computer:
                    computer.children['Init Block']['init'] = True
                    return
                
                
                
                compInit = True
                #проверка инициализации юнитов
                allUnits = computer
                allplayerUnits = computer['Interfaces'].getAllPlayerUnits()
                unitsCount = len(allplayerUnits)
                unitsInitiated = 0
                for unit in allplayerUnits:
                    if 'Interfaces' in unit:
                        unitsInitiated += 1
                if unitsInitiated < unitsCount:
                    return
                unitInit = True
                pgInterf = unit['Interfaces'].getPGinterfaces()
                
                #переделать
                bge.logic.sendMessage('Map Init', 'init', computer.name, '')

                mapInit = True
                
                #гуйня
                for scene2 in sceneList:
                    if scene2.name == 'GUI':
                        guiControl = scene2.objects['GUI Control']
                        cursor = scene2.objects['Cursor']
                        cursor.setComputer(computer)
                        gameCamera = scene.objects['Camera']
                        cursor.setGameCamera(gameCamera)
                        if 'GUI Init Block' in scene2:
                            guiInitBlock = scene2.objects['GUI Init Block']
                            guiInitBlock['init'] = True
                        #по нормальному нужно сделать. в классе
                        if 'Interfaces' in guiControl:
                            guiInit = True
    if compInit and unitInit and guiInit and mapInit:
        #даем доступ к объекту класса, который отвечает объекты на уровне
        computer['Interfaces'].setLevel(level)
        computer['Interfaces'].setGuiControl(guiControl)
        
        guiControl['Interfaces'].setFloorIndicators(0)
        own = cont.owner
        own.endObject()
    scene = bge.logic.getCurrentScene()
    if 'Unit Mech' not in scene.objects:
        if compInit and unitInit and guiInit and mapInit:
            own = cont.owner
            own.endObject()
        return

            