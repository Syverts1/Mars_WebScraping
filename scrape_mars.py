# Dependencies
import time
from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
import string

#create a function to call all parts of the scraping code
def scrape():
    
    mars_dict = mars_news()
    
    mars_dict.update(featured_image())
    mars_dict.update(mars_weather())
    mars_dict.update({'facts': mars_facts()})
    mars_dict.update({'hemisphere_image_urls': mars_hemi()})
    
    return mars_dict
#NASA Mars News
def mars_news():
    url = "https://mars.nasa.gov/news/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'html.parser')

    #find news titles within parsed html
    title = soup.find_all('div',class_="content_title")
    
    news_title=[]

    for item in title:
        contents = item.a.text
        news_title.append(contents.strip('\n'))

    #find news descriptions
    desc = soup.find_all('div', class_="rollover_description_inner")
                      
    news_p=[]
    
    for item in desc:
        contents = item.text
        news_p.append(contents.strip('\n'))
    
    return {"news_title": news_title, "news_p": news_p}

#Initialize browser function; used within functions that need splinter
def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path)

#JPL Mars Space Images - Featured Image
#returns path to featured image
def featured_image():
    browser = init_browser()

    base_url = "https://www.jpl.nasa.gov"
    search_url = base_url + "/spaceimages/?search=&category=Mars"
    browser.visit(search_url)
    time.sleep(1)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    main_img = soup.find('article', class_="carousel_item").get('style')

    rel_url = ""
    d= False
    base_url = "https://www.jpl.nasa.gov"


    for i in main_img:
        if(i=="'" and d== False):
            d = True
        elif(i=="'" and d==True):
            d = False
        elif(i!="'" and d==True):
            rel_url = rel_url + i

    image_url = {'image_url':base_url + rel_url}
    browser.quit()
    return image_url

#Mars Weather
#function to pull information on mars weather from twitter page
def mars_weather():
    url_weather = "https://twitter.com/marswxreport?lang=en"
    
    response_weather = requests.get(url_weather)
    
    soup_weather = BeautifulSoup(response_weather.text,'html.parser')
    
    #find paragraph text within parsed html
    tweets = soup_weather.find_all('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")

    weather_p=[]

    for item in tweets:
        i = item.text
        if i.startswith("Sol") == True:
            contents = item.text
            weather_p.append(contents.strip('\n'))
    
    weather = {'mars_weather': weather_p[0]}
    return weather

#Mars Facts
#Pull information from space facts page
def mars_facts():
    url_facts = "http://space-facts.com/mars/"
    
    response_facts = requests.get(url_facts)
    
    soup_facts = BeautifulSoup(response_facts.text,'html.parser')
    
    #find paragraph text within parsed html
    div_contents = soup_facts.find('div',class_='post-content')
    
    #pull mars description out of post-content div
    para = div_contents.find_all('p')
    #print(para)
    
    desc={0:['Description:'],1:[ para[1].text]}
    
    facts_df = pd.DataFrame(data=desc)
    
    profile_contents = pd.read_html("https://space-facts.com/mars/")[0]
    
    #append profile to description to get the full list of facts about mars, in one df
    facts = facts_df.append(profile_contents,ignore_index=True)
    
    facts = facts.set_index(0)
    
    facts = facts.rename(index=str,columns={1: 'value'})
    
    facts.index.name = None
    
    mars_facts_html = facts.to_html()
    
    return mars_facts_html

#Mars Hemispheres
def mars_hemi():
    #pull html contents of the website containing mars hemisphere information
    url_hemi = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    
    response_hemi = requests.get(url_hemi)
    
    soup_hemi = BeautifulSoup(response_hemi.text,'html.parser')  
    
    #find title of each mars hemisphere

    #print(soup_hemi.prettify())
    h3 = soup_hemi.find_all('h3')
    h3_parsed = []
    
    for item in h3:
        h3_parsed.append(item.text)
        
    #find path to the image page, that will be used by splinter to find the exact path to a sample image
    img_tag = soup_hemi.find_all('a', class_="itemLink product-item")
    
    #print(img_tag)
    
    img_path=[]
    
    for item in img_tag:
        i = item.get('href')
        img_path.append('https://astrogeology.usgs.gov' + i)

    #use splinter to navigate to each image download page, and retrieve its image url     
    browser = init_browser()

    downloads = []

    for url in img_path:
        browser.visit(url)
        time.sleep(1)

        html = browser.html
        downloads.append(BeautifulSoup(html, "html.parser").find('div',class_='downloads'))
    browser.quit()
    
    image_url=[]
    
    for item in downloads:
        contents = item.a.get('href')
        image_url.append(contents)
    
    hemisphere_image_urls = []

    for index,item in enumerate(h3_parsed):
    
        hemisphere_image_urls.append({"title": item , "img_url": image_url[index]})

    return hemisphere_image_urls

