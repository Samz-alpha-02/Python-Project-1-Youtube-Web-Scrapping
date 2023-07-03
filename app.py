from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import csv
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
from selenium import webdriver
from pymongo.mongo_client import MongoClient
import pymongo

app = Flask(__name__) # initializing a flask app

@app.route('/', methods=['GET']) # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/result', methods=['POST', 'GET']) # route to show the scrapped data in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            urls = request.form['content'].replace(" ", "")
            driver = webdriver.Chrome()
            driver.get(urls)
            content = driver.page_source
            soup = BeautifulSoup(content, 'html.parser')
            titles = soup.find_all("yt-formatted-string", id="video-title")
            views = soup.find_all("span", class_="inline-metadata-item style-scope ytd-video-meta-block")
            thumbnail = soup.find_all("img", class_="yt-img-shadow")
            video_urls = soup.find_all("a", id="video-title-link")
            filename = "scrapper.csv"
            data = []
            my_dict=[]
            for i in range(min(5, len(titles))):
                video_url = "https://www.youtube.com" + video_urls[i].get('href')
                thumbnail_url = thumbnail[i].get('src')
                title = titles[i].text
                views_count = views[2 * i].text
                publish_date = views[2 * i + 1].text

                my_dict = [{"Video URL":video_url,"Thumbnail URL":thumbnail_url,"Title of the Video":title,"Number of Views":views_count,"Date of Publish":publish_date}]

                data.append([video_url, thumbnail_url, title, views_count, publish_date])

                with open(filename, "w", newline='', encoding='utf-8') as fw:
                    writer = csv.writer(fw)
                    writer.writerow(["Video URL", "Thumbnail URL", "Title of the Video", "Number of Views", "Date of Publish"])
                    writer.writerows(data)

                uri = "mongodb+srv://Python_Project_1_Youtube_Web_Scraping:pwskills_pythonproject_123@cluster0.6xne1kl.mongodb.net/?retryWrites=true&w=majority"
                client = MongoClient(uri)
                db = client["info_scrap"]
                info_col = db["info_scrap_data"]
                info_col.insert_many(my_dict)



            return render_template('results.html', data=data)

        except Exception as e:
            print('The Exception message is: ', e)
            return 'Something went wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
