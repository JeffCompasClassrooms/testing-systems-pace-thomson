from subprocess import Popen
import time

p = Popen(["python3", "squirrel_server.py"]) # something long running

time.sleep(2)
print('after')
time.sleep(2)

p.terminate()