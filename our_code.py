from PIL import ImageGrab
import pyautogui
import torch
import time
import os
import keyboard
import random

# Helping functions copied from prev code
def get_screen(title:str) -> list[object, tuple]:
    ao: object = pyautogui.getWindowsWithTitle(title) #'Albion Online Client'
    # print(f'active {pyautogui.getActiveWindow()}')
    if(ao):
        while (pyautogui.getActiveWindow() != ao[0]):
            print('Window is closed')
            try:
                ao[0].activate()
            except:
                print("Couldn't open app")
            time.sleep(0.1)
        active_window_region: tuple = (ao[0].left+7, ao[0].top, ao[0].right-7, ao[0].bottom-7)
        # print(active_window_region)
        screenshot: object = ImageGrab.grab(bbox=active_window_region, all_screens=True)
        return screenshot, active_window_region
    else:
        return None, None
    
def create_model(model_file_path) -> object:
    model: object = torch.hub.load('model', 'custom', model_file_path, force_reload=True, trust_repo=True, source='local')
    model.cuda()
    model.multi_label = False
    return model


def detection(title: str) -> list[object, tuple]:
    screenshot, region = get_screen(title)
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
    # pyautogui.moveTo(x)
    pyautogui.mouseDown(x=x, y=y)
    time.sleep(random.randint(2, 10)/10)
    pyautogui.mouseUp()

def cork_loc(x, reg):
    x_len = reg[2]-reg[0]
    # print(f'xlen = {x_len}')
    # print(f'x_сork = {x}')

    if(x<(x_len/2 + x_len*0.03)): # Half screen + 3 %
        pyautogui.mouseDown()
    else: 
        pyautogui.mouseUp()
    


def minigame(title: str) -> None:
    detections, reg = detection(title)
    vals = iterate_df(detections) 
    # print(f'Vals before while{vals}')
    while('minigame' in vals or 'cork' in vals):
        if(keyboard.is_pressed('k')):
            print('Exited cycle')
            return
        if('cork' in vals):
            # print(detections)
            for index, row in detections.iterrows():
                if (row['name'] == 'cork'):
                    x = (row["xmin"]+row["xmax"])/2
                    cork_loc(x, reg)
        detections, reg = detection(title)
        if isinstance(detections, list):
            pyautogui.mouseUp()
            time.sleep(1)
            return                
        # print(f'Detections: /n {detections}')
        vals = iterate_df(detections)
        # print(f'Detections: /n {vals}')
                

def iterate_df(df) -> list:
    results: list = []
    if(type(df) is not list):
        for index, row in df.iterrows():
            results.append(row['name'])
    return results


def runner(x,y,title) -> None:
    throw(x, y)
    time.sleep(2)
    detections , region = detection(title)
    vals: list = iterate_df(detections)
    
    while('stat' in vals):
        if(keyboard.is_pressed('k')):
            print('Exited cycle')
            return
        # print('detected stat')
        # time.sleep(0.2)
        # print(detections)
        if('catch' in vals):
            break
        detections, region  = detection(title)
        vals = iterate_df(detections)      
    if('catch' in vals):
        for index, row in detections.iterrows():
                if (row['name'] == 'catch'):
                    if (row['confidence'] > 0.7):
                        print(f"Confidence = {row['confidence']}")
                        pyautogui.click(x, y)
                        time.sleep(0.2)    
                        minigame(title)
                        pyautogui.mouseUp()
                        time.sleep(1)              
    # time.sleep(0.2)


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