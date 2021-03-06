from http import client as httpsconn
import config
import os
import threading
import time
import hashlib
import json
new_plist=[]
def write_new_local_plist():
    global new_plist,remote_version
    f=open(config.download_dir+'plist_local.txt',mode='w')
    f.write(remote_version)
    for line in new_plist:
        try:
            f.write(line[0]+' '+line[1]+' '+str(line[2])+'\n')
        except:
            pass
    f.close()

def read_local_plist():
    global local_version
    result={}
    try:
        f=open(config.download_dir+'plist_local.txt')
    except:
        local_version='0'
        return result
    local_version=f.readline()
    for line in f.readlines():
        info=line.split(' ')
        result[info[0]]=info[1]
    f.close()
    return result
def get_ready_to_write(fn):
    try:
        fn=fn[0:fn.rindex('/')]
    except:
        pass
    os.makedirs(fn,exist_ok=True)
def getmd5(fn):
    try:
        f=open(fn,mode="rb")
    except:
        return -1
    md5=hashlib.md5(f.read()).hexdigest()
    f.close()
    return md5
def getjsondata(s):
    if s['retcode']=='0':
        return s['data']
    else:
        return s['retcode']+':'+s['msg']
def get_from_plist(plist,name):
    try:
        return plist[name]
    except:
        return -1
def parse_plist(local=None):
    global local_version,remote_version
    f=open(config.download_dir+'plist.txt')
    remote_version=f.readline()
    print('remote plist version:\t',remote_version[:-1])
    print('local plist version:\t',local_version[:-1])
    data=f.readlines()
    for line in data:
        info=line.split(' ')
        if len(info)==3:
            local_md5=get_from_plist(local,info[0])
            if (remote_version==local_version) and (local_md5==info[1]):
                if config.verbose:
                    print('Skipped:',info[0],' Size:',int(info[2][:-1]),'local md5:',getmd5(config.download_dir+info[0]),'remote md5:',info[1])
                local_plist_append((info[0],info[1],int(info[2][:-1])))
            else:
                print('Download:',info[0],' Size:',int(info[2][:-1]))
                yield info[0],info[1],int(info[2][:-1])
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
def local_plist_append(target):
    global new_plist
    new_plist.append(target)
def downloader(fn,size=-1,plist_info=None):
    url=geturl(fn)
    target_fn=config.download_dir+fn
    get_ready_to_write(target_fn)
    with open(target_fn,'wb') as f:
        conn=httpsconn.HTTPSConnection(config.res_server_path,port=443)
        conn.connect()
        conn.request('GET',url)
        resp=conn.getresponse()
        data=resp.read()
        assert (size==-1) or (len(data)==size), 'Wrong size!!! fn='+fn
        f.write(data)
        f.close()
        local_plist_append(plist_info)
def start_download(fn,size,plist_info):
    while threading.active_count()>config.thread:
        time.sleep(0.5)
    worker=threading.Thread(target=downloader,args=(fn,size,plist_info))
    worker.start()
def geturl(dir):
    return parse_url(config.version,config.platform_name,parse_dir(dir))
def get_server_info():
    conn=httpsconn.HTTPSConnection(config.server_info_path)
    conn.connect()
    conn.request('GET','/resource/get?version='+config.version)
    resource=conn.getresponse().read()
    conn.request('GET','/notice/get?platid='+'5')
    notice=conn.getresponse().read()
    conn.request('GET','/server/list?platid='+'5')
    serverlist=conn.getresponse().read()
    resource=json.loads(resource)
    notice=json.loads(notice)
    serverlist=json.loads(serverlist)
    print('resource:',getjsondata(resource))
    print('serverlist:',getjsondata(serverlist))
    print('notice:',getjsondata(notice))
def main():
    local_plist=read_local_plist()
    downloader('plist.txt')
    for target in parse_plist(local=local_plist):
        url,md5,size=target
        start_download(url,size,target)
    while threading.active_count()>1:
        time.sleep(0.5)
        print(threading.active_count()-1,' files to go...')

get_server_info()
try:
    main()
finally:
    print('Updating local plist...')
    write_new_local_plist()