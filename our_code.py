from PIL import ImageGrab
import pyautogui
import torch
import time
import os
import keyboard
import random


def get_screen(title:str, target:tuple = None, mini: bool = False) -> list[object, tuple]:
    ao: object = pyautogui.getWindowsWithTitle(title) #'Albion Online Client'
    if(ao):
        while (pyautogui.getActiveWindow() != ao[0]):
            print('Window is closed')
            try:
                ao[0].activate()
            except:
                print("Couldn't open app")
            time.sleep(0.1)
        active_region: tuple = (ao[0].left, ao[0].top, ao[0].right, ao[0].bottom)
        if(mini):
            target_region: tuple = minibox(active_region)
        else:
            if(target is None):
                target_region: tuple = active_region
            else:
                target_region:tuple = find_quarter(active_region, target)
        screenshot: object = ImageGrab.grab(bbox=target_region, all_screens=True)
        return screenshot, target_region
    else:
        return None, None

def minibox(active_region: tuple) -> tuple:
    mid_x: int = int((active_region[0]+active_region[2]) / 2)
    mid_yy: int = int((active_region[1]+active_region[3]) / 2)
    mid_y: int = int(mid_yy-(mid_yy*0.038)) # Adjusting mid_Y by 3.8%
    # Width and height of active window
    width: int = int(active_region[2] - active_region[0])
    height: int = int(active_region[3] - active_region[1])
    # 0.2 = 20% and 0.3 = 30% for height and width detection box in minigame, might need to adjust for dif resolution of game screen
    return mid_x - int(width * 0.2),mid_y - int(height * 0.3), mid_x + int(width * 0.2), mid_y + int(height * 0.3)

def find_quarter(active_region: tuple, target: tuple) -> tuple:
    mid_x: int = int((active_region[0]+active_region[2]) / 2)
    mid_yy: int = int((active_region[1]+active_region[3]) / 2)
    mid_y: int = int(mid_yy-(mid_yy*0.038)) # Adjusting mid_Y by 3.8%
    if(target[0]>mid_x and target[1]<mid_y):
        # print('TOP_RIGHT')
        return mid_x, active_region[1],active_region[2],mid_y
    if(target[0]>mid_x and target[1]>mid_y):
        # print('BOTTOM_RIGHT')
        return mid_x, mid_y, active_region[2], active_region[3]
    if(target[0]<mid_x and target[1]>mid_y):
        # print('BOTTOM_LEFT')
        return active_region[0], mid_y, mid_x, active_region[3]
    if(target[0]<mid_x and target[1]<mid_y):
        # print('TOP_LEFT')
        return active_region[0], active_region[1], mid_x, mid_y
    return None
        

def create_model(model_file_path) -> object:
    model: object = torch.hub.load('model', 'custom', model_file_path, force_reload=True, trust_repo=True, source='local')
    model.cuda()
    model.multi_label = False
    return model


def detection(title: str, target: tuple = None, mini: bool = False) -> list[object, tuple]:
    screenshot, region = get_screen(title, target, mini)
    # print(screenshot)
    if (screenshot == None):
        return [], None
    result_model = model(screenshot)
    detections: object = result_model.pandas().xyxy[0]
    if (detections.empty):
        print('No detections')
        return [], None
    return detections, region


def exiting() -> None:
    confirm: str = pyautogui.confirm(text="Confirm to Exit")
    if (confirm == 'OK'):
        time.sleep(0.1)
        print('Bye-Bye')
        os._exit(0)

# 


def throw(x, y) -> None:
    pyautogui.mouseDown(x=x, y=y)
    time.sleep(random.randint(2, 10)/10)
    pyautogui.mouseUp()

def cork_loc(x, reg):
    detect_box_width = reg[2]-reg[0]
    # 55 % of detection box, since we adjusted detection box for mini game we getting back Avg(x) relevant that detection box
    if (int(x)>(detect_box_width*0.55)): 
        pyautogui.mouseUp() 
    else:
        pyautogui.mouseDown()
  
    


def minigame(title: str) -> None:
    detections, reg = detection(title, None, True)
    vals = iterate_df(detections) 
    could_not: int = 0
    while(could_not < 5):
        if('minigame' not in vals):
            if('cork' not in vals):
                could_not+=1
                print(f'No minigame or cork, couldnot find = {could_not}')                
        else:
            if(keyboard.is_pressed('k')):
                print('Exited cycle')
                return
            if('cork' in vals):
                # print(detections)
                for index, row in detections.iterrows():
                    if (row['name'] == 'cork'):
                        x = (row["xmin"]+row["xmax"])/2
                        pyautogui.mouseDown # Mouse down when minigame starts
                        cork_loc(x, reg)
            detections, reg = detection(title, None, True)
            if isinstance(detections, list):
                pyautogui.mouseUp()
                time.sleep(1)
                return                
            vals = iterate_df(detections)      
        detections, reg = detection(title, None, True)
        vals = iterate_df(detections)

def iterate_df(df) -> list:
    results: list = []
    if(type(df) is not list):
        for index, row in df.iterrows():
            results.append(row['name'])
    return results


def runner(x,y,title) -> None:
    target: tuple = (x,y)
    throw(x, y)
    time.sleep(2)
    detections , region = detection(title, target)
    vals: list = iterate_df(detections)
    
    while('stat' in vals):
        if(keyboard.is_pressed('k')):
            print('Exited cycle')
            return
        if('catch' in vals):
            break
        detections, region  = detection(title, target)
        vals = iterate_df(detections)      
    if('catch' in vals):
        for index, row in detections.iterrows():
                if (row['name'] == 'catch'):
                    if (row['confidence'] > 0.7):
                        print(f"Confidence = {row['confidence']}")
                        pyautogui.click(x, y) 
                        minigame(title)
                        pyautogui.mouseUp()
                        time.sleep(0.5)              


def start() -> None:
    x, y = pyautogui.position()
    title: str = 'Albion Online Client'
    while(True):
        if(keyboard.is_pressed('k')):
            print('Exited cycle')
            return
        runner(x,y,title)

def mini() -> None:
    title: str = 'Albion Online Client'
    pyautogui.mouseDown()
    time.sleep(0.1)
    minigame(title)
    x, y = pyautogui.position()
    time.sleep(1)
    # throw(x, y)

def buttons_listener():
    print('Main Listener')
    keyboard.add_hotkey('ctrl+l', mini)
    keyboard.add_hotkey('ctrl+q', exiting)
    keyboard.add_hotkey('ctrl+space', start)
    keyboard.wait()



def main() -> None:
    buttons_listener()


if __name__ == "__main__":
    path: str = fr'trained\latest_4_20.pt'
    model: object = create_model(path)
    main()