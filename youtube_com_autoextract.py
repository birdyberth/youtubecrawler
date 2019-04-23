import time
import math
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
from random import randint

os.environ['DISPLAY'] = ':1'
time.sleep(120)

profile = webdriver.FirefoxProfile()
profile.set_preference("permissions.default.image", 2) #2 - Block all images
driver = webdriver.Firefox(firefox_profile=profile)
wait = WebDriverWait(driver, 10)
driver.get("https://www.youtube.com/playlist?list=LLiH1yoyPXZM7H-XhOf_HwJQ")
element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.yt-simple-endpoint.ytd-playlist-video-renderer')))
for i in range(1, 50):
    driver.execute_script("window.scrollTo(0, 1000000000);") #il y a un bug dans firefox qui empeche d'utiliser le scroll to bottom
    time.sleep(2)
elements = driver.find_elements_by_css_selector('a.yt-simple-endpoint.ytd-playlist-video-renderer')
longurls = []
for element in elements:
    longurls.append(element.get_attribute("href"))

f = open('/home/fred/Documents/python/ytcomments/checklist.txt', 'a+')
data = f.readlines()
j = 0
notok = 1
while notok:
    notok = 0
    u = longurls[j]
    current_url = u[0:43]
    for i in range(0, len(data)):
        d = data[i]
        if (current_url == d[0:-1]):
            j = j + 1
            notok = 1
            break

u = longurls[j]
current_url = u[0:43]
f.write(current_url+"\n")
f.close()
current_url = [current_url]

def PageScraper(urls):
    last_urls = urls[1:len(urls)]
    try:
        i = randint(0, len(urls)-1) #navigue de maniere aleatoire dans les choix de prochaine lecture
        current_url = urls[i]
        wait = WebDriverWait(driver, 10)
        driver.get(current_url)
        time.sleep(6) #attend que la page soit loadee avec la pub aussi
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'ytp-play-button')))
        element.click() #met la video en pause
        driver.execute_script("window.scrollTo(0, 200);") #descend pour activer le chargement des commentaires
    
        #trouve le nombre total de commentaires
        #no = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'yt-formatted-string.count-text.style-scope.ytd-comments-header-renderer'))).text #extrait la string decrivant le nombre de commentaires total
        time.sleep(10);
        no = driver.find_elements_by_css_selector('yt-formatted-string.count-text.style-scope.ytd-comments-header-renderer')
        if len(no) > 0: #si les commentaires sont actives
            no = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'yt-formatted-string.count-text.style-scope.ytd-comments-header-renderer'))).text #a changer mais pour l'instant cette commande fonctionne bien pour extraire le texte de la string des commentaires
            nbcom = no[0]
            i = 1
            number = 0
            while no[i] != ' ':
                if no[i] != ',':
                    nbcom = nbcom + no[i]
                i = i + 1
                
            number = int(math.ceil(float(nbcom)/20)) #convertit la string en nombre (il y a 20 commentaires visibles par loading)
        
            if number > 0: #s'il y a des commentaires
                #loade tous les commentaires
                lastscrollposition = 0
                lastlastscrollposition = 0
                for i in range(1, number):
                    driver.execute_script("window.scrollTo(0, 1000000000);") #il y a un bug dans firefox qui empeche d'utiliser le scroll to bottom
                    scrollposition = driver.execute_script("return window.pageYOffset;")
                    if scrollposition == lastlastscrollposition:
                        break
                    lastlastscrollposition = lastscrollposition
                    lastscrollposition = scrollposition
                    time.sleep(2) 

                userdata = driver.find_elements_by_id('author-text')
                commentsdata = driver.find_elements_by_id('content-text')
                size_of_users = len(userdata)
            
                filename = '/home/fred/Documents/python/ytcomments/' + datetime.now().strftime("%d-%m-%Y") + '.xml'
                f = open(filename,'a')
                data = "<video><url>"+current_url+"</url>\n"
                for i in range (0, size_of_users):
                    name = userdata[i].text
                    userurl = userdata[i].get_attribute("href")
                    comment = commentsdata[i].text
                    if name and userurl and comment:
                        data = data + "<name>"+name+"</name>"+"<userurl>"+userurl+"</userurl>"+"<comment>"+comment+"</comment>\n"
        
                data = data.encode('utf-8') + "</video>\n"
                f.write(data)
                f.close()
    
        elements = driver.find_elements_by_css_selector("a.yt-simple-endpoint.style-scope.ytd-compact-video-renderer")
        urls = []
        for element in elements:
            urls.append(element.get_attribute("href"))

    except:
        urls = last_urls
        
    return urls

#for i in range (0, 1):
try:
    while 1:
        next_url = PageScraper(current_url)
        current_url = next_url
        if not current_url:
            driver.close()
        #    driver = webdriver.Firefox()
        #    current_url = ['https://www.youtube.com/watch?v=3Dt9xJGPQBk']
            print "Le crawler est reparti!"
            os.system('sudo systemctl reboot')
    
except:
    os.system('sudo systemctl reboot')
