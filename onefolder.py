src_dir='./assets/'
fin_dir='./assets-ext/'
import os
def get_ready_to_write(fn):
    try:
        fn=fn[0:fn.rindex('/')]
    except:
        pass
    os.makedirs(fn,exist_ok=True)
for fn in os.walk(src_dir):
    if fn[2]!=[]:
        for filename in fn[2]:
            path=fn[0]+'/'+filename
            path=path.replace("\\","/")
            #print(path)
            fread=open(path,mode='rb')
            wdir=fin_dir+path[path.rindex('/')+1:]
            print(wdir)
            get_ready_to_write(wdir)
            fwrite=open(wdir,mode="wb")
            fwrite.write(fread.read())
            fread.close()
            fwrite.close()