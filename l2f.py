import pyautogui as pag
import time as t

t.sleep(5)
def click(x,y, dur=0.5):
    pag.mouseDown(x,y)
    t.sleep(dur)
    pag.mouseUp(x,y)


def run():
    click(879,78)







for i in range(10000):
    run()