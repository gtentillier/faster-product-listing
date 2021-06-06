# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 22:05:49 2021

@author: Talha
"""
from bs4 import BeautifulSoup
import requests
import re
import os 
import time


def cleansing(text):
    text=text.strip()
    regex = re.compile('[(){}—*^:;£$",.”“!%&+-/Ã©§™]|<[^>]*>')
    text = regex.sub("", text)
    return text

def make_dir(dirName):
    try:
        os.makedirs(dirName)    
        print("Directory " , dirName ,  "Created ")
    except FileExistsError:
        print("Directory " , dirName ,  "Already exists") 


class loginSession:
    def __init__(self, data, params, header, loginUrl):
        self.data = data
        self.params = params
        self.loginUrl = loginUrl
        self.session = requests.Session()
        self.session.headers.update(header)
    
    def invoke(self):   
        response = self.session.post(self.loginUrl, params=self.params, data=self.data)
        if response.status_code != 201:
            raise Exception("could not log into provided site {}".format(self.loginUrl))
        else:
            print('Logged-In Successfully: {}'.format(response.status_code))
        
        return self.session

class scrapper:
    def __init__(self, fpage, lpage, session):
        self.fpage=fpage
        self.lpage=lpage
        self.session=session
        self.parent_url='https://us.vestiairecollective.com/'
        
    def start_scrapping(self, dirpath, url):
        img_count=1
        txt_count1=1
        txt_count2=1
        make_dir(dirpath)
        for i in range(self.fpage, self.lpage+1):
            print(url+'p-'+str(i)+'/')
            source_code = self.session.get(url+'/p-'+str(i)+'/')
            plain_text_brand = source_code.text
            soup = BeautifulSoup(plain_text_brand, "html.parser")
            #Extracting Name and Brand against images
            for link in soup.findAll('img', {'class':'image'}):
                items=[]
                metadata = link.get('alt').replace(' ', '_').split('_') 
                item_brand = metadata[-1]
                item_name = cleansing('_'.join(metadata[:-1])) 
                items.append(item_brand)
                items.append(item_name)
                txt_file = open(dirpath+str(txt_count1)+'.txt','w')
                txt_file.write(",".join(items))
                txt_file.close()
                txt_count1+=1
            #Extracting images from the main product page
            for link in soup.findAll('meta', {'itemprop':'image'}):
                img_url = link.get('content')        
                resp_img = self.session.get(img_url)
                #item_name = img_url.split('/')[-1]
                img_file = open(dirpath+str(img_count)+'.jpg', "wb")
                img_file.write(resp_img.content)
                img_file.close()
                img_count+=1
            #Extracting Color and Material from the nested product pages
            for link in soup.findAll('div', {'class':'productSnippet'}):
                a = str(link.select('a', {'class':'ng-star-inserted'})).split(' ')
                if len(a)>1:
                    a = str(a[2]).replace('href="','')
                    a = a.replace('"','')
                    time.sleep(20)
                    resp_text = self.session.get(self.parent_url+a)
                    plain_text_details = resp_text.text
                    soup2 = BeautifulSoup(plain_text_details, "html.parser")
                    items=[]
                    for div in soup2.findAll('div', {'class':'productDetails__resume__characteristics'}):
                        items=div.findAll('p')[-1]
                        items=[x for x in cleansing(str(items)).strip().split(' ') if x != '']                
                    txt_file = open(dirpath+str(txt_count2)+'.txt','a')
                    txt_file.write(",")
                    txt_file.write(",".join(items))
                    txt_file.close()
                    txt_count2+=1
                else:
                    txt_count2+=1
        img_count=1
        txt_count1=1
        txt_count2=1
    
    
if __name__ == "__main__":
    header = {
                'user-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Accept': 'application/json',
                'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                'Referer': 'https://fr.vestiairecollective.com/',
                'Content-Type': 'application/json',
                'Origin': 'https://fr.vestiairecollective.com',
                'Connection': 'keep-alive',
                'TE': 'Trailers'}
    params = (
        ('x-currency', 'EUR'),
        ('x-language', 'fr'),
        ('x-siteid', '1'),
    )
    data = '{"email":"ktester101@gmail.com","password":"123456789WwQ@!","digest":"v12853d8fa2a"}'
    url = 'https://apiv2.vestiairecollective.com/sessions/'
    
    s = loginSession(data, params, header, url)   
    sess = s.invoke()
    
    scrap = scrapper(1, 17, sess)
    
    
    #----------------Creating Necessary Directories----------------------------#
    make_dir('Dataset')
    make_dir('Dataset/Women')
    make_dir('Dataset/Men')  
    ###---------------------------------------------Category - Women------------------------------------------###
    
    #-----------------------------------------------clothing----------------------------------------------------
    scrap.start_scrapping('Dataset/Women/coats/', 'https://us.vestiairecollective.com/women-clothing/coats/')
    scrap.start_scrapping('Dataset/Women/trenchcoats/', 'https://us.vestiairecollective.com/women-clothing/trench-coats/')
    scrap.start_scrapping('Dataset/Women/jackets/', 'https://us.vestiairecollective.com/women-clothing/jackets/')
    scrap.start_scrapping('Dataset/Women/bikerjackets/', 'https://us.vestiairecollective.com/women-clothing/biker-jackets/')
    scrap.start_scrapping('Dataset/Women/dresses/', 'https://us.vestiairecollective.com/women-clothing/dresses/')
    scrap.start_scrapping('Dataset/Women/knitwear/', 'https://us.vestiairecollective.com/women-clothing/knitwear/')
    scrap.start_scrapping('Dataset/Women/tops/', 'https://us.vestiairecollective.com/women-clothing/tops/')
    scrap.start_scrapping('Dataset/Women/skirts/', 'https://us.vestiairecollective.com/women-clothing/skirts/')
    scrap.start_scrapping('Dataset/Women/shorts/', 'https://us.vestiairecollective.com/women-clothing/shorts/')
    scrap.start_scrapping('Dataset/Women/trousers/', 'https://us.vestiairecollective.com/women-clothing/trousers/')
    scrap.start_scrapping('Dataset/Women/jeans/', 'https://us.vestiairecollective.com/women-clothing/jeans/')
    scrap.start_scrapping('Dataset/Women/jumpsuits/', 'https://us.vestiairecollective.com/women-clothing/jumpsuits/')
    scrap.start_scrapping('Dataset/Women/lingerie/', 'https://us.vestiairecollective.com/women-clothing/lingerie/')
    scrap.start_scrapping('Dataset/Women/swimwear/', 'https://us.vestiairecollective.com/women-clothing/swimwear/')
    
    # # #-----------------------------------------------Bags------------------------------------------------------
    scrap.start_scrapping('Dataset/Women/handbags/', 'https://us.vestiairecollective.com/women-bags/handbags/')
    scrap.start_scrapping('Dataset/Women/totes/', 'https://us.vestiairecollective.com/women-bags/handbags/totes/_l/')
    scrap.start_scrapping('Dataset/Women/crossbodybags/', 'https://us.vestiairecollective.com/women-bags/handbags/crossbody-bags/_l/')
    scrap.start_scrapping('Dataset/Women/clutchbags/', 'https://us.vestiairecollective.com/women-bags/clutch-bags/')
    scrap.start_scrapping('Dataset/Women/beltbags/', 'https://us.vestiairecollective.com/women-bags/belt-bags/')
    scrap.start_scrapping('Dataset/Women/backpacks/', 'https://us.vestiairecollective.com/women-bags/backpacks/')
    scrap.start_scrapping('Dataset/Women/travelbags/', 'https://us.vestiairecollective.com/women-bags/travel-bags/')
    scrap.start_scrapping('Dataset/Women/satchels/', 'https://us.vestiairecollective.com/women-bags/handbags/satchels/_l/')
    
    # # #----------------------------------------------Jewellery--------------------------------------------------------
    scrap.start_scrapping('Dataset/Women/rings/', 'https://us.vestiairecollective.com/women-jewellery/rings/')
    scrap.start_scrapping('Dataset/Women/bracelets/', 'https://us.vestiairecollective.com/women-jewellery/bracelets/')
    scrap.start_scrapping('Dataset/Women/necklaces/', 'https://us.vestiairecollective.com/women-jewellery/necklaces/')
    scrap.start_scrapping('Dataset/Women/earrings/', 'https://us.vestiairecollective.com/women-jewellery/earrings/')
    
    
    # # #---------------------------------------------Shoes---------------------------------------------------------------
    scrap.start_scrapping('Dataset/Women/heels/', 'https://us.vestiairecollective.com/women-shoes/heels/')
    scrap.start_scrapping('Dataset/Women/ankleboots/', 'https://us.vestiairecollective.com/women-shoes/ankle-boots/')
    scrap.start_scrapping('Dataset/Women/boots/', 'https://us.vestiairecollective.com/women-shoes/boots/')
    scrap.start_scrapping('Dataset/Women/sandals/', 'https://us.vestiairecollective.com/women-shoes/sandals/')
    scrap.start_scrapping('Dataset/Women/espadrilles/', 'https://us.vestiairecollective.com/women-shoes/espadrilles/')
    scrap.start_scrapping('Dataset/Women/mulesclogs/', 'https://us.vestiairecollective.com/women-shoes/mules-clogs/')
    scrap.start_scrapping('Dataset/Women/trainers/', 'https://us.vestiairecollective.com/women-shoes/trainers/') 
    scrap.start_scrapping('Dataset/Women/flats/', 'https://us.vestiairecollective.com/women-shoes/flats/')
    scrap.start_scrapping('Dataset/Women/balletflats/', 'https://us.vestiairecollective.com/women-shoes/ballet-flats/')
    scrap.start_scrapping('Dataset/Women/laceups/', 'https://us.vestiairecollective.com/women-shoes/lace-ups/')
    
    
    # # #------------------------------------------------Accessories-------------------------------------------------
    scrap.start_scrapping('Dataset/Women/scarves/', 'https://us.vestiairecollective.com/women-accessories/scarves/') #pending...
    scrap.start_scrapping('Dataset/Women/silkhandkerchief/', 'https://us.vestiairecollective.com/women-accessories/silk-handkerchief/') 
    scrap.start_scrapping('Dataset/Women/gloves/', 'https://us.vestiairecollective.com/women-accessories/gloves/')
    scrap.start_scrapping('Dataset/Women/hats/', 'https://us.vestiairecollective.com/women-accessories/hats/')
    scrap.start_scrapping('Dataset/Women/wallet/', 'https://us.vestiairecollective.com/women-accessories/wallet/') #pending...
    scrap.start_scrapping('Dataset/Women/belts/', 'https://us.vestiairecollective.com/women-accessories/belts/')
    scrap.start_scrapping('Dataset/Women/sunglasses/', 'https://us.vestiairecollective.com/women-accessories/sunglasses/')
    scrap.start_scrapping('Dataset/Women/purseswalletscases/', 'https://us.vestiairecollective.com/women-accessories/purses-wallets-cases/') 
    
    
    # ###--------------------------------------------Category - Men---------------------------------------------------------------
    
    # #----------------------------------------------Clothing----------------------------------------------------------
    scrap.start_scrapping('Dataset/Men/coats/', 'https://us.vestiairecollective.com/men-clothing/coats/')
    scrap.start_scrapping('Dataset/Men/jackets/', 'https://us.vestiairecollective.com/men-clothing/jackets/') #pending...
    scrap.start_scrapping('Dataset/Men/knitwearsweatshirts/', 'https://us.vestiairecollective.com/men-clothing/knitwear-sweatshirts/')
    scrap.start_scrapping('Dataset/Men/shirts/', 'https://us.vestiairecollective.com/men-clothing/shirts/')
    scrap.start_scrapping('Dataset/Men/poloshirts/', 'https://us.vestiairecollective.com/men-clothing/polo-shirts/')
    scrap.start_scrapping('Dataset/Men/tshirts/', 'https://us.vestiairecollective.com/men-clothing/t-shirts/') #pending...
    scrap.start_scrapping('Dataset/Men/jeans/', 'https://us.vestiairecollective.com/men-clothing/jeans/')
    scrap.start_scrapping('Dataset/Men/trousers/', 'https://us.vestiairecollective.com/men-clothing/trousers/')
    scrap.start_scrapping('Dataset/Men/shorts/', 'https://us.vestiairecollective.com/men-clothing/shorts/')
    scrap.start_scrapping('Dataset/Men/suits/', 'https://us.vestiairecollective.com/men-clothing/suits/')
    scrap.start_scrapping('Dataset/Men/swimwear/', 'https://us.vestiairecollective.com/men-clothing/swimwear/')
    
    # # #----------------------------------------------Shoes-------------------------------------------------------------
    scrap.start_scrappin('Dataset/Men/trainers/', 'https://us.vestiairecollective.com/men-shoes/trainers/') #pending...
    scrap.start_scrapping('Dataset/Men/boots/', 'https://us.vestiairecollective.com/men-shoes/boots/')
    scrap.start_scrapping('Dataset/Men/laceups/', 'https://us.vestiairecollective.com/men-shoes/lace-ups/')
    scrap.start_scrapping('Dataset/Men/flats/', 'https://us.vestiairecollective.com/men-shoes/flats/')
    scrap.start_scrapping('Dataset/Men/sandals/', 'https://us.vestiairecollective.com/men-shoes/sandals/')
    scrap.start_scrapping('Dataset/Men/espadrilles/', 'https://us.vestiairecollective.com/men-shoes/espadrilles/')
    
    # # #----------------------------------------------Bags & Accessories------------------------------------------------
    scrap.start_scrapping('Dataset/Men/bags/', 'https://us.vestiairecollective.com/men-bags/bags/') #pending...
    scrap.start_scrapping('Dataset/Men/small-bags-wallets-cases/', 'https://us.vestiairecollective.com/men-bags/small-bags-wallets-cases/')
    scrap.start_scrapping('Dataset/Men/beltbags/', 'https://us.vestiairecollective.com/men-bags/belt-bags/')
    scrap.start_scrapping('Dataset/Men/belts/', 'https://us.vestiairecollective.com/men-accessories/belts/')
    scrap.start_scrapping('Dataset/Men/sunglasses/', 'https://us.vestiairecollective.com/men-accessories/sunglasses/')
    scrap.start_scrapping('Dataset/Men/scarves-pocket-squares/', 'https://us.vestiairecollective.com/men-accessories/scarves-pocket-squares/')
    scrap.start_scrapping('Dataset/Men/ties/', 'https://us.vestiairecollective.com/men-accessories/ties/')
    scrap.start_scrapping('Dataset/Men/hats-pull-on-hats/', 'https://us.vestiairecollective.com/men-accessories/hats-pull-on-hats/')
    scrap.start_scrapping('Dataset/Men/gloves/', 'https://us.vestiairecollective.com/men-accessories/gloves/')
    scrap.start_scrapping('Dataset/Men/cufflinks/', 'https://us.vestiairecollective.com/men-accessories/cufflinks/')
    
    # # #----------------------------------------------Watches & Jewellery-----------------------------------------------
    scrap.start_scrapping('Dataset/Men/watches/', 'https://us.vestiairecollective.com/men-accessories/watches/')
    scrap.start_scrapping('Dataset/Men/jewellery/', 'https://us.vestiairecollective.com/men-accessories/jewellery/')
    
    
    


        
