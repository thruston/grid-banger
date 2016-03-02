#import zipfile
#with zipfile.ZipFile('ostn.zip') as z:
with open('ostn02.txt') as o:
    ostn = list(o)
 
    x = 280
    y = 310
    dx,dy = [float(s)/1000 for s in ostn[701*y+x].strip().split()]

    print(x, y, x*1000+dx, y*1000+dy) 
