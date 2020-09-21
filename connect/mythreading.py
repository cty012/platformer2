from threading import Thread
import time


def func1():
    while True:
        print('func1')
        time.sleep(0.2)


def func2():
    while True:
        print('func2')
        time.sleep(0.3)


thread1 = Thread(target=func1)
thread2 = Thread(target=func2)
thread1.start()
thread2.start()
