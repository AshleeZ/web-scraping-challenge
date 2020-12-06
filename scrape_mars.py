# Import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import requests
import pandas as pd

# Define function to start browser session for scraping
def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

# Define function to scrape data
def scrape_info():
    # Start browser
    browser = init_browser()

    # Navigate to website 
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)

    # Wait 1 second
    time.sleep(1)

    # Prepare soup for scraping
    html = browser.html
    soup = bs(html, 'html.parser')

    # Scrape first news title and its article text
    news_title = soup.select('div.content_title > a')[0].text
    news_p = soup.select('div.article_teaser_body')[0].text

    # Navigate to next website
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    
    # Wait 1 second
    time.sleep(1)
    
    # Prepare soup for scraping
    html = browser.html
    soup = bs(html, 'html.parser')

    # Use splinter to navigate through web pages
    browser.click_link_by_id('full_image')
    browser.links.find_by_text('more info     ').click()
    featured_image = browser.links.find_by_partial_href('hires').click()

    # Set current url of browser to variable
    featured_image_url = browser.url

    # Navigate to next website
    url = 'https://space-facts.com/mars/'

    # Read html into pandas
    table = pd.read_html(url)[0]

    # Rename columns
    table.columns = ['Description', 'Mars']

    # Store table data in dictionary
    table = table.to_dict('records')
    
    # Navigate to next website
    base_url = 'https://astrogeology.usgs.gov'
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Wait 1 second
    time.sleep(1)

    # Prepare soup for scraping
    html = browser.html
    soup = bs(html, 'html.parser')

    # Use splinter to find all links with <a> tag
    links = soup.select('div.item > a')

    # Use for loop to find all <a> tags with href links
    for link in links:
        href = link['href']

    # Create variable to insert beginning part of url
    base_url = 'https://astrogeology.usgs.gov'

    # Add beginning part of url to all href links found
    links_list = [base_url + link['href'] for link in links]
    
    # Create 2 empty lists to store titles and links 
    img_title_list = []
    img_url_list = []

    # Create for loop to navigate through each store website link and obtain hemisphere image urls and names
    for link in links_list:
        browser.visit(link)
        html = browser.html
        soup = bs(html, 'html.parser')
        img_title = soup.find('h2', class_='title').text.split(' Enhanced')[0]
        img_title_list.append(img_title)
        browser.links.find_by_text('Sample').click()
        img_url = browser.windows[1].url
        img_url_list.append(img_url)
        browser.windows[1].close()
        browser.back()

    # Store url and title list into dictionary
    hemisphere_image_urls = [{'title': title, 'img_url': url} for title, url in zip(img_title_list, img_url_list)]

    # Quite browser
    browser.quit()

    # Store all scraped data into 1 dictionary
    mars_info = {'news_title': news_title, 'news_p': news_p, 'featured_image_url': featured_image_url, 'table': table, 'hemisphere_image_urls': hemisphere_image_urls}

    # Return dictionary of scraped data when function is called
    return mars_info