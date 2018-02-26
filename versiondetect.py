from http import client as httpsconn
import queue
import threading
import time
#import config
wf=open('./versions.txt',mode='w')
def write_version(s):
    global wf
    wf.write(s+'\n')
def trystr():
    while True:
        s=versions.get()
        conn=httpsconn.HTTPSConnection('zjzksvr.xiimoon.com',port=443)
        conn.connect()
        url='/resource/get?version='+s
        conn.request('GET',url)
        resp=conn.getresponse()
        data=resp.read()
        #print(data)
        if (r'"retcode":"0"') in str(data):
            print(s)
            write_version(s)
        else:
            continue
            print('fail:',s)
def gen_version():
    global versions
    for v1 in range(0,15):
        for v2 in range(0,15):
            print('try:',v1,' ',v2)
            for v3 in range(0,15):
                for suffix in ('','_elite','_admin','_manage','_internal','_gm'):
                    versions.put(str(v1)+'.'+str(v2)+'.'+str(v3)+suffix)
versions=queue.Queue(800)
threadlist=[]
threadlist.append(threading.Thread(target=gen_version))
for i in range(0,25):
    threadlist.append(threading.Thread(target=trystr))
for item in threadlist:
    item.start()
while threading.active_count()>0:
    time.sleep(1)