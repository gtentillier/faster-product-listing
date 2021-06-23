import urllib.request
import os

f = open('models-gtin-attributes.txt','r')
data = f.read()

print('reading is over')

def count_semicolons(str):
    r=0
    for c in str :
        r+=(c==';')
    return r

dist_size_url = 7
dist_color_size = 31
dist_url_color = 4
dist_color_category = 1

#number of semicolons per line : 42

def make_dir(dirName):
    try:
        os.makedirs(dirName)    
        #print("Directory " , dirName ,  "Created ")
    except FileExistsError:
        #print("Directory " , dirName ,  "Already exists")
        () 

def after_semicolons(c,dist):
    res=0
    b=True
    d=0
    while (d<dist) :
        if (data[c+res-1:c+res+2]=='";"') :
            d+=1
        res+=1
    return res

def is_size_of_shoe(size,c):
    if (len(size)<2):                #à racourcir
        return False
    if (size[1]=='½' or size[1]=='-'):
        return True
    if ((size[0]=='3' or size[0]=='4' or size[0]=='2') and len(size)==2):
        next_size=data[c+after_semicolons(c,42)+1:c+after_semicolons(c,43)-2]
        try :
            if (int(next_size) - int(size) !=2) :
                return True
        except ValueError :
            return True
    return False

def is_shoe(c):
    a=data[c+1:c+after_semicolons(c,2)-2]
    l=a.split('";"')
    return (is_size_of_shoe(l[0],c) or is_size_of_shoe(l[1],c+after_semicolons(c,1)))

def get_url(c):
    a=data[c+1:c+after_semicolons(c,4)-2]
    return (a.split('";"'))

def download(download_count,url,color,path,counter):
    plus=0
    for src in url :
        if (len(src)>0) :
            new_path="Shoe_data/"+path+color+"/"
            if len(new_path)<221:
                make_dir(new_path)
                if (download_count>counter):
                    urllib.request.urlretrieve('https:'+src, "Shoe_data/"+path+color+"/"+str(download_count+plus)+".png")
                    print(str(download_count+plus)+"th link downloaded")
            plus+=1
    return plus

def get_color(c):
    color=data[c+1:c+after_semicolons(c,1)-2]
    #print(color)
    return color

def path_from(l):
    str=''
    for dir in l:
        str=str+dir+'/'
    return str           

def make_dir_from_list(l):
    last_path=''
    path=''
    for i in range(1,len(l)+1):
        path=path_from(l[0:i])
        if len(path)<211:
            last_path=path
            make_dir('Shoe_data/'+path)
        else :
            #print ('path too long encountered and shortened')
            break
    return last_path

def get_path(c):
    if (data[c+1:c+after_semicolons(c,1)-2]==''):
        return('Uncategorized/')
    path=data[c+1:c+after_semicolons(c,1)-2]
    l=path.split(',')
    return (make_dir_from_list(l))
    
def scrap(counter): # counter is the number of downloads we want to skip (to do it in several sessions)
    c=677 # char counter
    download_count=0
    url=[] #current url list
    last_url=''
    path=''
    shoe=False
    while(True):
        shoe=is_shoe(c)
        c+=after_semicolons(c,dist_size_url)
        url=get_url(c)
        if (shoe and (url[0]!=last_url)):
            c+=after_semicolons(c,dist_url_color)
            color=get_color(c)
            c+=after_semicolons(c,dist_color_category)
            path=get_path(c)
            download_count+=download(download_count,url,color,path,counter)
            c+=after_semicolons(c,dist_color_size-dist_color_category)
        else :
            c+=after_semicolons(c,dist_url_color+dist_color_size)
        last_url=url[0]
    return(0)

make_dir("Shoe_data/")

scrap(0)

#70 images downloaded per minute at Home
#120 images downloaded per minute at Polytechnique

f.close()