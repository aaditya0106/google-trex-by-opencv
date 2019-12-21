import numpy as np
import cv2
import glob
import time
import win32gui, win32ui, win32con, win32api
import pyautogui


def screenrecord(region=None):

    hwin = win32gui.GetDesktopWindow()

    if region:
            x1,y1,x2,y2 = region
            width = x2 - x1 + 1
            height = y2 - y1 + 1
    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        x1 = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        y1 = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (x1, y1), win32con.SRCCOPY)
    
    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height,width,4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)


dino = cv2.imread('trex.jpg',0)
w_dino, h_dino = dino.shape[::-1]

files = glob.glob ('cactus/*.jpg')   
cactus = []       
for img in files:
    cac=cv2.imread(img, 0)  
    cactus.append(cac)
    
gameover = cv2.imread('gameover.jpg', 0)

#def initialize():
second = time.time()
start = time.time()
obstacle_height = 0
bend = False
bending = False
jump_len = 253
dino_walk_height = 110
speed_time = 118
#self.notstart=True
#return second,start,obstacle_height,bend,bending,jump_len,dino_walk_height,speed_time

#second,start,obstacle_height,bend,bending,jump_len,dino_walk_height,speed_time = initialize()
while(True):
    leftest = 1000     
    if(time.time() - second >= 1 and time.time() - start < speed_time):
        jump_len += 1.7       
        #print(jump_len)
        second = time.time() 
    pts = []
    ss = screenrecord(region=(75, 250, 750, 450))
    ss_gray = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)    
    res_dino = cv2.matchTemplate(ss_gray, dino, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc_dino = np.where(res_dino >= threshold)
    dinoX = 1 
    for pt in zip(*loc_dino[::-1]):        
        cv2.rectangle(ss, pt, (pt[0] + w_dino, pt[1] + h_dino + 9), (50,205,50), 1)
        dinoX = pt[0] + w_dino
        dinoH = pt[1]
        bending = False
        
    """if notstart==True:
        pyautogui.press('space')
        notstart = False
        second,start,obstacle_height,bend,bending,jump_len,dino_walk_height,speed_time = initialize()"""
        
    for cac in cactus: 
        res = cv2.matchTemplate(ss_gray, cac, cv2.TM_CCOEFF_NORMED)
        w, h = cac.shape[::-1]
        loc = np.where(res >= 0.8)
        for pt in zip(*loc[::-1]):
            if(pt in pts):
                continue
            cv2.rectangle(ss, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 1)
            pts.append(pt)
            if(leftest > pt[0] + w and pt[0] > dinoX):
                leftest = pt[0] + w
                obstacle_height = h
                if(h < 20 and pt[1] + 5 < dinoH):
                    bend = True
                elif(bend == True):
                    bend = False
                    pyautogui.keyUp('down')
    
    if(leftest - dinoX < jump_len - obstacle_height and bend == False and dinoH > dino_walk_height):
        pyautogui.press('space')
    elif(bend == True):
        if(bending == False):
           pyautogui.keyDown('down')
           bending = True 
    cv2.putText(ss,"Press Q to close screen",(0,20),cv2.FONT_HERSHEY_DUPLEX, 0.4, (255,0,0))
    cv2.imshow('screen', ss) 
    
    """game_over = cv2.matchTemplate(ss_gray, gameover, cv2.TM_CCOEFF_NORMED)
    loc_gameover = np.where(game_over >= 0.8)
    if len(loc_gameover)>0:
        cv2.putText(ss,"Press space to play again",(0,20),cv2.FONT_HERSHEY_DUPLEX, 0.7, (0,0,255))
        second,start,obstacle_height,bend,bending,jump_len,dino_walk_height,speed_time=initialize()"""
    
    if cv2.waitKey(1) & 0xFF == ord('q'):# or len(loc_gameover) > 0:
        cv2.destroyAllWindows()
        break 