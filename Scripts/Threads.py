import bge #bge
import threading #threads
import socket #server
import time
import copy
import math
import sys

#поток
class thread1OpenClose1():
    def __init__(self,thread):
        print("--> creating thread_ptr")
        self.thread = thread
        
        
    def __del__(self):
        print("--> deleting thread_ptr")
        self.thread.join()
        #self.thread.terminate() # not in Threads

class Thread1(threading.Thread):
    def __init__(self, threadNum):
        print("Creating thread")
        self.curTime = None
        self.prevTime = time.clock()
        self._stopevent = threading.Event()
        self._sleepperiod = 0.01 #0.01 # частота пробуждения потока
        threading.Thread.__init__(self, name="Thread1")
        self.threadNum = threadNum
        self.__unitPGinterfaces = None
        self.__processingFlag = False
        self.__callFunction = None
        self.__callFuncList = []
        self.__callerList = []

    
    def setProcessingFlagOn(self, callFunction):
        #self.__unitPGinterfaces = unitPGinterfaces
        self.__callFunction = callFunction
        self.__processingFlag = True

    def addFuncToCall(self, callFunction, caller):
        if caller not in self.__callerList:
            self.__callFuncList.append(callFunction)
            self.__callerList.append(caller)

    def run(self):
        print("starts Thread1", self.getName())
        count = 0
        while not self._stopevent.isSet():

            if len(self.__callFuncList) > 0:
                for elem in self.__callFuncList:
                    elem()
                self.__callerList.clear()
                self.__callFuncList.clear()

            if self.__processingFlag:
                self.curTime = time.clock()
                self.__callFunction()
                #self.__unitPGinterfaces.calcPath3()
                print(self.threadNum, 'lovely path calc time', time.clock() - self.curTime)
                self.__processingFlag = False
            '''
            i = 0
            while i < 1:
                playGround = self.unitPGinterfaces.publicPlayGround
                
                print(self.unitPGinterfaces.calcPath2((0,0), (25,25), playGround))
                sys.stdout.write('\r Progress: {}'.format(str(i)))
                i += 1
            i = 0
            '''
            #читаем данные от сервера
            self.curTime = time.clock()
            delta = self.curTime - self.prevTime
            self.prevTime = self.curTime
            #sys.stdout.write('\r Thread num: {} deltaTime {} Calc {}'.format(self.threadNum, delta, self.__processingFlag))
            #print(self.threadNum, delta, self.curTime, self.__processingFlag)
            #print ("loop " ,count)
            self._stopevent.wait(self._sleepperiod)
        print ("--> ends ",self.getName())

    def join(self,timeout=None):
        print("--> Terminating thread")
        self._stopevent.set()
        threading.Thread.join(self, timeout)


class thread2OpenClose2():
    def __init__(self, thread):
        print("--> creating thread_ptr")
        self.thread = thread

    def __del__(self):
        print("--> deleting thread_ptr")
        self.thread.join()
        # self.thread.terminate() # not in Threads


class Thread2(threading.Thread):
    def __init__(self, threadNum):
        print("Creating thread")
        self.curTime = None
        self.prevTime = time.clock()
        self._stopevent = threading.Event()
        self._sleepperiod = 0.01  # 0.01 # частота пробуждения потока
        threading.Thread.__init__(self, name="Thread2")
        self.threadNum = threadNum
        self.__unitPGinterfaces = None
        self.__processingFlag = False
        self.__callFunction = None

    def setProcessingFlagOn(self, callFunction):
        # self.__unitPGinterfaces = unitPGinterfaces
        self.__callFunction = callFunction
        self.__processingFlag = True

    def run(self):
        print("starts Thread2", self.getName())
        count = 0
        while not self._stopevent.isSet():
            if self.__processingFlag:
                self.curTime = time.clock()
                self.__callFunction()
                # self.__unitPGinterfaces.calcPath3()
                print(self.threadNum, 'lovely path calc time', time.clock() - self.curTime)
                self.__processingFlag = False
            # читаем данные от сервера
            #self.curTime = time.clock()
            #delta = self.curTime - self.prevTime
            #self.prevTime = self.curTime
            # sys.stdout.write('\r Thread num: {} deltaTime {} Calc {}'.format(self.threadNum, delta, self.__processingFlag))
            # print(self.threadNum, delta, self.curTime, self.__processingFlag)
            # print ("loop " ,count)
            self._stopevent.wait(self._sleepperiod)
        print("--> ends ", self.getName())

    def join(self, timeout=None):
        print("--> Terminating thread")
        self._stopevent.set()
        threading.Thread.join(self, timeout)