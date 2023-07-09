from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import pandas as pd
from pymongo.mongo_client import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pytube import YouTube

app = Flask(__name__)  # initializing a Flask app

@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/result', methods=['POST', 'GET'])  # route to show the scraped data in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            url = request.form['content'].replace(" ", "")
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run Chrome in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.binary_location = '/usr/bin/google-chrome-stable'  # Chrome/Chromium path
            driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=chrome_options)  # Chromedriver path

            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-rich-grid-media.style-scope.ytd-rich-item-renderer")))
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            driver.quit()
            titles = soup.find_all("yt-formatted-string", id="video-title")
            views = soup.find_all("span", class_="inline-metadata-item style-scope ytd-video-meta-block")

            video_urls = soup.find_all("a", id="video-title-link")
            data = []
            my_dict = []
            for i in range(min(5, len(titles))):
                video_url = "https://www.youtube.com" + video_urls[i].get('href')

                # Retrieve the thumbnail URL using pytube
                yt = YouTube(video_url)
                thumbnail_url = yt.thumbnail_url

                title = titles[i].text
                views_count = views[2 * i].text
                publish_date = views[2 * i + 1].text

                my_dict = {
                    "Video URL": video_url,
                    "Thumbnail URL": thumbnail_url,
                    "Title of the Video": title,
                    "Number of Views": views_count,
                    "Date of Publish": publish_date
                }

                data.append([video_url, thumbnail_url, title, views_count, publish_date])

                uri = "mongodb+srv://Python_Project_1_Youtube_Web_Scraping:pwskills_pythonproject_123@cluster0.6xne1kl.mongodb.net/?retryWrites=true&w=majority"
                client = MongoClient(uri)
                db = client["info_scrap"]
                info_col = db["info_scrap_data"]
                info_col.insert_one(my_dict)

            df = pd.DataFrame(data, columns=['Video URL', 'Video Title', 'Views', 'Posted', 'Thumbnail Url'])
            df.to_csv('scrapper.csv', index=False)

            return render_template('results.html', data=data)

        except Exception as e:
            print('The Exception message is: ', e)
            return 'Something went wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
