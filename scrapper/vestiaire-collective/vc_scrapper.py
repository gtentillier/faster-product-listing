# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 22:05:49 2021

@author: Talha
"""
from bs4 import BeautifulSoup
import requests
import re
import os 
import uuid
import csv
import glob

#Header for the summary.csv file
headers=['Product_ID', 'Label', 'Category', 'SubCategory','Brand','Color','Material', 'Urls']

def cleansing(text):
    text=text.strip()
    regex = re.compile('[(){}—*^:;£$",.”“!%&+-/Ã©§™]|<[^>]*>')
    text = regex.sub("", text)
    return text

def csv_file(path, data, mode):
    f = open(path, mode)
    writer = csv.writer(f, lineterminator='\r')
    writer.writerow(data)
    f.close()
    
def make_dir(dirName):
    try:
        os.makedirs(dirName)    
        print("Directory " , dirName ,  "Created ")
    except FileExistsError:
        print("Directory " , dirName ,  "Already exists") 

def make_csv(path, headers, mode):
    if len(glob.glob(path+'/*.csv'))==0:
        csv_file(path+'/summary.csv', headers, mode)   
        print("CSV File" , 'Summary.csv' ,  "Created ")
    else: 
        print("CSV File" , 'Summary.csv' ,  "Already exists") 
        
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
        self.parent_url='https://us.vestiairecollective.com'
        
    def start_scrapping(self, dirpath, url):
        make_dir(dirpath) # for making the subcategory directory
        csv_dict={}
        for i in range(self.fpage, self.lpage+1): #traversing product pages (1-17)
            #time.sleep(20)
            print(url+'/p-'+str(i)+'/')
            source_code = self.session.get(url+'/p-'+str(i)+'/')
            plain_text_brand = source_code.text
            soup = BeautifulSoup(plain_text_brand, "html.parser") 
            parts=dirpath.split('/')
            csv_dict['Category']=parts[3]
            csv_dict['SubCategory']=parts[4]   
            for link in soup.findAll('div', {'class':'productSnippet'}):
                a=link.find('a', {'itemprop':'url'})
                if a!=None:
                    a_url=a['href']
                    brand=link.find('span', {'itemprop':'brand'})
                    csv_dict['Brand']=brand.text
                    uni_id=uuid.uuid4()
                    make_dir(dirpath+str(uni_id))
                    csv_dict['Product_ID']=uni_id
                    #time.sleep(5)
                    resp_text = self.session.get(self.parent_url+a_url)
                    plain_text_details = resp_text.text
                    soup2 = BeautifulSoup(plain_text_details, "html.parser")
                    items=[]
                    for div in soup2.findAll('div', {'class':'productDetails__resume__characteristics'}):
                        items=div.findAll('p')[-1]
                        items=[x for x in cleansing(str(items)).strip().split(' ') if x != '']  
                    items.append(brand.text)
                    txt_file = open(dirpath+str(uni_id)+'/'+str(uni_id)+'.txt','w', encoding='utf-8')
                    txt_file.write(",".join(items))
                    txt_file.close()
                    if len(items)>1:
                        csv_dict['Color']=items[0]
                        csv_dict['Material']=items[1]
                    else:
                        csv_dict['Color']='None'
                        csv_dict['Material']='None'
                    loc_c=1
                    s_chk=True
                    p_size=0
                    label=''
                    sub_urls=[]
                    for img in soup2.findAll('img', {'class':'image'}): 
                        if s_chk:
                            p_size=int(img['width'])
                            label=img['alt']
                            s_chk=False
                        if int(img['width'])==p_size:
                            d_url=img['src']
                            sub_urls.append(d_url)
                            resp_img = self.session.get(d_url)
                            img_file = open(dirpath+str(uni_id)+'/'+str(uni_id)+'_'+str(loc_c)+'.jpg', "wb")
                            img_file.write(resp_img.content)
                            img_file.close()
                            loc_c+=1
                        else:
                            break
                        
                    csv_dict['Urls']=sub_urls
                    csv_dict['Label']=label
                    with open('scrapper/Dataset2/summary.csv', 'a', encoding='UTF8') as f:
                        writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\r')
                        writer.writerow(csv_dict)  
    
    
if __name__ == "__main__":
    header = {
                'user-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Accept': 'application/json',
                'Accept-Language': 'en-US;q=0.5,en;q=0.3', #fr,fr-FR;q=0.8,
                'Referer': 'https://us.vestiairecollective.com/',
                'Content-Type': 'application/json',
                'Origin': 'https://us.vestiairecollective.com',
                'Connection': 'keep-alive',
                'TE': 'Trailers'}
    params = (
        ('x-currency', 'EUR'),
        ('x-language', 'en'),
        ('x-siteid', '1'),
    )
    data = '{"email":"fkxav246@gmail.com","password":"123456789WwQ@!","digest":"v1fd4e3c2c18"}' #"digest":"v12853d8fa2a"
    url = 'https://apiv2.vestiairecollective.com/sessions/'
    
    s = loginSession(data, params, header, url)   
    sess = s.invoke()
    
    scrap = scrapper(1, 17, sess)
    
    #----------------Creating Necessary Directories----------------------------#
    make_dir('scrapper/Dataset2')
    make_dir('scrapper/Dataset2/Women')
    make_dir('scrapper/Dataset2/Women/clothing')
    make_dir('scrapper/Dataset2/Women/Bags')
    make_dir('scrapper/Dataset2/Women/Jewellery')
    make_dir('scrapper/Dataset2/Women/Shoes')
    make_dir('scrapper/Dataset2/Women/Accessories')
    
    
    make_dir('scrapper/Dataset2/Men') 
    make_dir('scrapper/Dataset2/Men/Clothing') 
    make_dir('scrapper/Dataset2/Men/Shoes') 
    make_dir('scrapper/Dataset2/Men/Bags & Accessories') 
    make_dir('scrapper/Dataset2/Men/Watches & Jewellery') 
    
    
    make_csv('scrapper/Dataset2', headers, 'w')
    ###---------------------------------------------Category - Women------------------------------------------###
    
    #-----------------------------------------------clothing----------------------------------------------------
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/coats/', 'https://us.vestiairecollective.com/women-clothing/coats/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/trenchcoats/', 'https://us.vestiairecollective.com/women-clothing/trench-coats/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/jackets/', 'https://us.vestiairecollective.com/women-clothing/jackets/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/bikerjackets/', 'https://us.vestiairecollective.com/women-clothing/biker-jackets/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/dresses/', 'https://us.vestiairecollective.com/women-clothing/dresses/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/knitwear/', 'https://us.vestiairecollective.com/women-clothing/knitwear/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/tops/', 'https://us.vestiairecollective.com/women-clothing/tops/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/skirts/', 'https://us.vestiairecollective.com/women-clothing/skirts/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/shorts/', 'https://us.vestiairecollective.com/women-clothing/shorts/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/trousers/', 'https://us.vestiairecollective.com/women-clothing/trousers/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/jeans/', 'https://us.vestiairecollective.com/women-clothing/jeans/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/jumpsuits/', 'https://us.vestiairecollective.com/women-clothing/jumpsuits/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/lingerie/', 'https://us.vestiairecollective.com/women-clothing/lingerie/')
    scrap.start_scrapping('scrapper/Dataset2/Women/clothing/swimwear/', 'https://us.vestiairecollective.com/women-clothing/swimwear/')
    
    # # #-----------------------------------------------Bags------------------------------------------------------
    scrap.start_scrapping('scrapper/Dataset2/Women/Bags/handbags/', 'https://us.vestiairecollective.com/women-bags/handbags/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Bags/totes/', 'https://us.vestiairecollective.com/women-bags/handbags/totes/_l/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Bags/crossbodybags/', 'https://us.vestiairecollective.com/women-bags/handbags/crossbody-bags/_l/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Bags/clutchbags/', 'https://us.vestiairecollective.com/women-bags/clutch-bags/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Bags/beltbags/', 'https://us.vestiairecollective.com/women-bags/belt-bags/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Bags/backpacks/', 'https://us.vestiairecollective.com/women-bags/backpacks/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Bags/travelbags/', 'https://us.vestiairecollective.com/women-bags/travel-bags/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Bags/satchels/', 'https://us.vestiairecollective.com/women-bags/handbags/satchels/_l/')
    
    # # #----------------------------------------------Jewellery--------------------------------------------------------
    scrap.start_scrapping('scrapper/Dataset2/Women/Jewellery/rings/', 'https://us.vestiairecollective.com/women-jewellery/rings/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Jewellery/bracelets/', 'https://us.vestiairecollective.com/women-jewellery/bracelets/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Jewellery/necklaces/', 'https://us.vestiairecollective.com/women-jewellery/necklaces/')
    scrap.start_scrapping('scrapper/Dataset2/Women//Jewellery/earrings/', 'https://us.vestiairecollective.com/women-jewellery/earrings/')
    
    
    # # # #---------------------------------------------Shoes---------------------------------------------------------------
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/heels/', 'https://us.vestiairecollective.com/women-shoes/heels/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/ankleboots/', 'https://us.vestiairecollective.com/women-shoes/ankle-boots/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/boots/', 'https://us.vestiairecollective.com/women-shoes/boots/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/sandals/', 'https://us.vestiairecollective.com/women-shoes/sandals/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/espadrilles/', 'https://us.vestiairecollective.com/women-shoes/espadrilles/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/mulesclogs/', 'https://us.vestiairecollective.com/women-shoes/mules-clogs/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/trainers/', 'https://us.vestiairecollective.com/women-shoes/trainers/') 
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/flats/', 'https://us.vestiairecollective.com/women-shoes/flats/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/balletflats/', 'https://us.vestiairecollective.com/women-shoes/ballet-flats/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Shoes/laceups/', 'https://us.vestiairecollective.com/women-shoes/lace-ups/')
    
    
    # # # #------------------------------------------------Accessories-------------------------------------------------
    scrap.start_scrapping('scrapper/Dataset2/Women/Accessories/scarves/', 'https://us.vestiairecollective.com/women-accessories/scarves/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Accessories/silkhandkerchief/', 'https://us.vestiairecollective.com/women-accessories/silk-handkerchief/') 
    scrap.start_scrapping('scrapper/Dataset2/Women/Accessories/gloves/', 'https://us.vestiairecollective.com/women-accessories/gloves/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Accessories/hats/', 'https://us.vestiairecollective.com/women-accessories/hats/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Accessories/wallet/', 'https://us.vestiairecollective.com/women-accessories/wallet/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Accessories/belts/', 'https://us.vestiairecollective.com/women-accessories/belts/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Accessories/sunglasses/', 'https://us.vestiairecollective.com/women-accessories/sunglasses/')
    scrap.start_scrapping('scrapper/Dataset2/Women/Accessories/purseswalletscases/', 'https://us.vestiairecollective.com/women-accessories/purses-wallets-cases/') 
    
    
    # # ###--------------------------------------------Category - Men---------------------------------------------------------------
    
    # # #----------------------------------------------Clothing----------------------------------------------------------
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/coats/', 'https://us.vestiairecollective.com/men-clothing/coats/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/jackets/', 'https://us.vestiairecollective.com/men-clothing/jackets/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/knitwearsweatshirts/', 'https://us.vestiairecollective.com/men-clothing/knitwear-sweatshirts/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/shirts/', 'https://us.vestiairecollective.com/men-clothing/shirts/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/poloshirts/', 'https://us.vestiairecollective.com/men-clothing/polo-shirts/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/tshirts/', 'https://us.vestiairecollective.com/men-clothing/t-shirts/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/jeans/', 'https://us.vestiairecollective.com/men-clothing/jeans/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/trousers/', 'https://us.vestiairecollective.com/men-clothing/trousers/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/shorts/', 'https://us.vestiairecollective.com/men-clothing/shorts/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/suits/', 'https://us.vestiairecollective.com/men-clothing/suits/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Clothing/swimwear/', 'https://us.vestiairecollective.com/men-clothing/swimwear/')
    
    # # # #----------------------------------------------Shoes-------------------------------------------------------------
    scrap.start_scrapping('scrapper/Dataset2/Men/Shoes/trainers/', 'https://us.vestiairecollective.com/men-shoes/trainers/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Shoes/boots/', 'https://us.vestiairecollective.com/men-shoes/boots/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Shoes/laceups/', 'https://us.vestiairecollective.com/men-shoes/lace-ups/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Shoes/flats/', 'https://us.vestiairecollective.com/men-shoes/flats/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Shoes/sandals/', 'https://us.vestiairecollective.com/men-shoes/sandals/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Shoes/espadrilles/', 'https://us.vestiairecollective.com/men-shoes/espadrilles/')
    
    # # # #----------------------------------------------Bags & Accessories------------------------------------------------
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/bags/', 'https://us.vestiairecollective.com/men-bags/bags/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/small-bags-wallets-cases/', 'https://us.vestiairecollective.com/men-bags/small-bags-wallets-cases/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/beltbags/', 'https://us.vestiairecollective.com/men-bags/belt-bags/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/belts/', 'https://us.vestiairecollective.com/men-accessories/belts/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/sunglasses/', 'https://us.vestiairecollective.com/men-accessories/sunglasses/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/scarves-pocket-squares/', 'https://us.vestiairecollective.com/men-accessories/scarves-pocket-squares/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/ties/', 'https://us.vestiairecollective.com/men-accessories/ties/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/hats-pull-on-hats/', 'https://us.vestiairecollective.com/men-accessories/hats-pull-on-hats/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/gloves/', 'https://us.vestiairecollective.com/men-accessories/gloves/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Bags & Accessories/cufflinks/', 'https://us.vestiairecollective.com/men-accessories/cufflinks/')
    
    # # # #----------------------------------------------Watches & Jewellery-----------------------------------------------
    scrap.start_scrapping('scrapper/Dataset2/Men/Watches & Jewellery/watches/', 'https://us.vestiairecollective.com/men-accessories/watches/')
    scrap.start_scrapping('scrapper/Dataset2/Men/Watches & Jewellery/jewellery/', 'https://us.vestiairecollective.com/men-accessories/jewellery/')  
