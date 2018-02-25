from http import client as httpsconn
import config
import os
import threading
import time
def get_ready_to_write(fn):
    try:
        fn=fn[0:fn.rindex('/')]
    except:
        pass
    os.makedirs(fn,exist_ok=True)
def parse_plist():
    f=open(config.download_dir+'plist.txt')
    data=f.readlines()
    for line in data:
        info=line.split(' ')
        if len(info)==3:
            print('Download:',info[0],' Size:',int(info[2][:-1]))
            yield info[0],int(info[2][:-1])
def parse_dir(dir):
    elements=dir.split('/')
    result=[]
    for element in elements:
        result.append(element)
    return result

def parse_url(*args):
    url=''
    for element in args:
        if type(element)==type([]):
            for e2 in element:
                url+='/'+e2
        else:
            url+='/'+element
    return url
def downloader(fn,size=-1):
    url=geturl(fn)
    target_fn=config.download_dir+fn
    get_ready_to_write(target_fn)
    with open(target_fn,'wb') as f:
        conn=httpsconn.HTTPSConnection(config.server_path,port=443)
        conn.connect()
        conn.request('GET',url)
        resp=conn.getresponse()
        data=resp.read()
        assert (size==-1) or (len(data)==size), 'Wrong size!!! fn='+fn
        f.write(data)
        f.close()
def start_download(fn,size):
    while threading.active_count()>=config.thread:
        time.sleep(0.5)
    worker=threading.Thread(target=downloader,args=(fn,size))
    worker.start()
def geturl(dir):
    return parse_url(config.version,config.platform_name,parse_dir(dir))

def main():
    downloader('plist.txt')
    for target in parse_plist():
        url,size=target
        start_download(url,size)
    while threading.active_count()>0:
        time.sleep(0.5)
main()