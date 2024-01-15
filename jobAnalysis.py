from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from getLink import get_searchLink
import re


class Browser:
    browser,service = None ,None
    def __init__(self,driver:str):
        opt = Options()
        opt.add_experimental_option("debuggerAddress","localhost:9222")
        self.service = Service(driver)
        self.browser = webdriver.Chrome(service= self.service,chrome_options=opt)
    
    def open_page(self,url:str):
        self.browser.get(url)
    def maximW(self):
        self.browser.maximize_window()
    def getSource(self):
        return  self.browser.page_source
    def switchPartime(self,partTime):
         try:
            filter_btn = self.browser.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[3]/div[1]/div[1]/button')
            filter_btn.click()
            jobType_btn = self.browser.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[3]/div[1]/div[1]/div/div/div[6]/div/button[1]')
            self.browser.execute_script("arguments[0].scrollIntoView();", jobType_btn)
            jobType_btn.click()
            if partTime:  
                partTime_btn = self.browser.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[3]/div[1]/div[1]/div/div/div[6]/div[2]/ul/li[3]/button')
                self.browser.execute_script("arguments[0].scrollIntoView();", partTime_btn)
                partTime_btn.click()
                time.sleep(2)
            else:
                fullTime_btn = self.browser.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[3]/div[1]/div[1]/div/div/div[6]/div[2]/ul/li[2]/button')
                self.browser.execute_script("arguments[0].scrollIntoView();",fullTime_btn)
                fullTime_btn.click()
                time.sleep(2)
         except:
                print('unable to find element close')

    def show_more(self):
        count = 4
        while count>0 :
            try:
                show_more_btn = self.browser.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button')
                self.browser.execute_script("arguments[0].scrollIntoView();", show_more_btn)
                show_more_btn.click()
                try:
                    element = WebDriverWait(self.browser, 10).until(
                        EC.visibility_of_element_located((By.XPATH, "/html/body/div[8]/div/div[2]/span"))
                    )
                    element.click()
                except:
                    print('unable to find element close')
                time.sleep(2)
            except:
                print('unable to find showMore')
            count-=1

    
    def get_jobDiscription(self,index):
        show_more_btn = self.browser.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li['+str(index)+']')
        self.browser.execute_script("arguments[0].scrollIntoView();", show_more_btn)
        show_more_btn.click()
        element = WebDriverWait( self.browser, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "JobDetails_jobDescription__6VeBn"))
            )
        time.sleep(2)
        return element.text
        
        

    

browser  = Browser('driver/chromedriver.exe')  

def load_cities(cities='cities.txt'):
    with open(cities, 'r') as f:
        cities = f.readlines()
    cities = [x.lower().strip().replace(' ', '%20') for x in cities]
    return cities

def job_titles(titles = 'jobtitles.txt'):
    with open(titles, 'r') as f:
        titles = f.readlines()
    titles = [x.lower().strip().replace(' ', '%20') for x in titles]
    return titles
def job_title_check(titles = 'jobtitles.txt'):
    with open(titles, 'r') as f:
        titles = f.readlines()
    return titles
def skills(skills = 'skillset.txt'):
    with open(skills, 'r') as f:
        skills = f.readlines()
    skills = [x.lower().strip().replace('\n', '') for x in skills]
    return skills

def words_present(job_title,word_list):
    for phrase in word_list:
        words_to_check = re.sub(r'[^a-zA-Z\s]', '', phrase).split()
        for word in words_to_check:
            if word.lower() not in re.sub(r'[^a-zA-Z\s]', '', job_title).lower():
                break  
        else:
            return True 

    return False

def getSkills(disc_str):
    keywords=skills()
    pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b', flags=re.IGNORECASE)
    matches = re.findall(pattern,disc_str)
    return matches

def runBeutifulSoup(resp,job_type):
    job_data = list()
    o={}
    job_titles_list  = job_title_check() 
    soup=BeautifulSoup(resp,'html.parser')

    allJobsContainer = soup.find("ul",{"class":"JobsList_jobsList__Ey2Vo"})

    allJobs = allJobsContainer.find_all("li")
    index = 1
    for job in allJobs:
        try:
             job_title = job.find("a",{"class":"JobCard_seoLink__WdqHZ"}).text
             if words_present(job_title,job_titles_list) == False:
                 index+=1
                 continue
        except:
                 continue    
        try:
            company_name_div = job.find("span", {"class": "EmployerProfile_employerName__Xemli"}).text
            o["name-of-company"] = company_name_div
            
        except:
            o["name-of-company"]=None

        try:
            o["name-of-job"]=job.find("a",{"class":"JobCard_seoLink__WdqHZ"}).text
        except:
            o["name-of-job"]=None


        try:
            o["location"]=job.find("div",{"class":"JobCard_location__N_iYE"}).text
        except:
            o["location"]=None


        try:
            o["salary"]=job.find("div",{"class":"JobCard_salaryEstimate___m9kY"}).text
        except:
            o["salary"]=None
        try:
            o["job type"]=job_type
        except:
            o["job type"]=None
       
        try:
            job_description_text=browser.get_jobDiscription(index)
            o["skills"] = getSkills(job_description_text)
            
        except:
            o["job type"]=None

        index+=1

        
      
                
        job_data.append(o)
        o={}
    
    df = pd.DataFrame(job_data)
    df.to_csv('jobs.csv', mode='a', header=False, index=False, encoding='utf-8')

def addPageResponse(targetUrl):
    target_url = targetUrl+"clickSource=searchBox"
    browser.open_page(target_url)
    browser.maximW()
    time.sleep(2)
    browser.switchPartime(False)
    browser.show_more()
    resp = browser.getSource()
    runBeutifulSoup(resp,'Full Time')
    time.sleep(2)
    browser.switchPartime(True)
    browser.show_more()
    resp = browser.getSource()
    runBeutifulSoup(resp,'Part Time')

  

def runTitles(location):
    jobTitles = job_titles()
    for title in jobTitles:
        print(title,location)
        targetUrl = get_searchLink(title,location)
        addPageResponse(targetUrl)


def runLocs():
    cities = load_cities()
    for city in cities:
        runTitles(city)

runLocs()
