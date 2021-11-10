##################################################################
#                                                                #
# BGE Custom Cursor v1                                           #
#                                                                #
# By Jay (Battery)                                               #
#                                                                #
# https://whatjaysaid.wordpress.com/                              #
#                                                                #
# Feel free to use this as you wish, but please keep this header #
#                                                                #
##################################################################
import time
from bge import render, logic, types, events
 
class Cursor(types.KX_GameObject):
    def __init__(self, own):
        self._searchScene = logic.getCurrentScene()
        self.camera = logic.getCurrentScene().active_camera
        self.sens = 0.005
        self.screenX = render.getWindowWidth()
        self.screenY = render.getWindowHeight()
        self.centreX = int(self.screenX/2)
        self.centreY = int(self.screenY/2)
        self.searchScene = logic.getCurrentScene()
        render.setMousePosition(self.centreX, self.centreY)
        self.cursorPos = [0.5,0.5]
        self._limits = [0,0,1,1]
        #new
        self._own = self._searchScene.objects['Cursor']
        self._computer = None
        self._gameCamera = None
        return
 
    #new
    #установка обьекта управляющего класса 
    def setComputer(self, computer):
        self._computer = computer
    #установка оснвной игровой камеры
    def setGameCamera(self, gameCamera):
        self._gameCamera = gameCamera
        
    @property
    def searchScene(self):
        return self._searchScene
 
    @searchScene.setter
    def searchScene(self, scene):
        for s in logic.getSceneList():
            if s.name == scene:
                self._searchScene = s
 
    @property
    def limits(self):
        return self._limits
 
    @limits.setter
    def limits(self, limitList):
        assert isinstance(limitList, (list, tuple)), "Limits must be a list"
        assert len(limitList) == 4, "limits takes a list of 4 integers [x1,y1,x2,y2]"
        self._limits = [limitList[0]*0.01, limitList[1]*0.01, 1-(limitList[2]*0.01), 1-(limitList[3]*0.01)]
 
    def centreRealCursor(self):
        render.setMousePosition(self.centreX, self.centreY)
        return
 
    def getMovement(self):
        mPos = logic.mouse.position
        x = self.centreX - (mPos[0]*self.screenX)
        y = self.centreY - (mPos[1]*self.screenY)
        self.centreRealCursor()
        return [x, y]
 
    def moveCursor(self):
        movement = self.getMovement()
        movement[0] *= self.sens
        movement[1] *= self.sens
        self.position.x -= movement[0]
        self.position.y += movement[1]
        self.cursorPos = self.camera.getScreenPosition(self)
        if self.cursorPos[0] > self._limits[2] or self.cursorPos[0] < self._limits[0]:
            self.position.x += movement[0]
        if self.cursorPos[1] > self._limits[3] or self.cursorPos[1] < self._limits[1]:
            self.position.y -= movement[1]
        return
 
    def getCursorOver(self, prop=""):
        cam = self.searchScene.active_camera
        obj = cam.getScreenRay(self.cursorPos[0], self.cursorPos[1], 1000, prop)
        return obj
 
    def mouseEvents(self):
        if logic.mouse.events[events.MOUSEX] == logic.KX_INPUT_ACTIVE:
            self.onCursorMovement()
        if logic.mouse.events[events.MOUSEY] == logic.KX_INPUT_ACTIVE:
            self.onCursorMovement()
        if logic.mouse.events[events.LEFTMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
            self.onLeftClicked()
        if logic.mouse.events[events.RIGHTMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
            self.onRightClicked()
        if logic.mouse.events[events.MIDDLEMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
            self.onMiddleClick()
        if logic.mouse.events[events.WHEELUPMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
            self.onWheelUp()
        if logic.mouse.events[events.WHEELDOWNMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
            self.onWheelDown()
        return
    def onCursorMovement(self):
        self.moveCursor()
    
    #исправил имя функции, при onLeftClick не вызывалась
    def onLeftClicked(self):
        #обработка клика  по элементам GUI
        clickedObjOnGui = self.getCursorOver()
        if clickedObjOnGui != None:
            if 'Button' in clickedObjOnGui.name:
                clickedObjOnGui['Interfaces'].setButtonPressed()
            return
        vec = self._gameCamera.getScreenVect(self.cursorPos[0], self.cursorPos[1])
        camPos = self._gameCamera.worldPosition
        projectedPos = [0,0,0]
        z = 10     # user-set depth
        projectedPos[0] = camPos[0] - vec[0] * z
        projectedPos[1] = camPos[1] - vec[1] * z
        projectedPos[2] = camPos[2] - vec[2] * z
        
        #обработка клика по элементам на уровне
        beamDistance = 1000
        hitObject, hitPosition, hitNormal = self._gameCamera.rayCast(projectedPos, camPos, beamDistance, '')
        #self._computer['Interfaces'].leftClickProcessing(hitObject, hitPosition)
        self._computer['Interfaces'].leftClickProcessing(projectedPos, camPos)
        self.centreRealCursor()
        pass
    def onRightClicked(self):
        print('right click')
        pass
    def onMiddleClick(self):
        pass
    def onWheelUp(self):
        pass
    def onWheelDown(self):
        pass


def mouse2world():
    z = 16.6833 - 0.1 # distance for cursor

    cam = logic.getCurrentScene().active_camera
    vec = cam.getScreenVect(*logic.mouse.position)
    camPos = cam.worldPosition
    projectedPos = [0,0,0]
    
    projectedPos[0] = camPos[0] - vec[0] * z
    projectedPos[1] = camPos[1] - vec[1] * z
    projectedPos[2] = camPos[2] - vec[2] * z

    return projectedPos

def main(cont):

    cursorObj = cont.owner
    cam = logic.getCurrentScene().active_camera
    pos = mouse2world()

    cursorObj.worldPosition = pos
    cursorObj.worldOrientation = cam.worldOrientation
    print(logic.mouse.position)
    #return
    if logic.mouse.position[0] > 0.95:
        print(logic.mouse.position)
        mouseX = int(render.getWindowWidth() - 5)
        mouseY = int((render.getWindowHeight() * (logic.mouse.position[1])))
        render.setMousePosition(mouseX, mouseY)
        
        
    
def init(cont):
    own = cont.owner
    own['prev Time'] = time.clock()
    own['current Time'] = time.clock()
    print('init good')
    
def moveCursor(cont):
    own = cont.owner
    delta = own['current Time'] - own['prev Time']
    own['prev Time'] = own['current Time']
    own['current Time'] = time.clock()
    print(delta)