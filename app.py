from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import csv
from pymongo.mongo_client import MongoClient

app = Flask(__name__) # Initializing a Flask app
CORS(app) #CORS(app) enables Cross-Origin Resource Sharing (CORS) for the Flask application, allowing cross-origin requests from different domains.
@app.route('/', methods=['GET']) # Route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/result', methods=['POST', 'GET']) # Route to show the scraped data in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            url = request.form['content'] #Taking input of the url as input
            num_videos = int(request.form['num_videos']) #Taking the number of videos to scrape as input

            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")  # Add no-sandbox argument
            chrome_options.add_argument("--headless")  # Run Chrome in headless mode
            chrome_options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage

            service = Service(ChromeDriverManager().install()) #Sets up the ChromeDriver service by installing the appropriate driver executable using ChromeDriverManager. It ensures that the compatible version of ChromeDriver is downloaded and configured.
            driver = webdriver.Chrome(service=service, options=chrome_options) #Creates an instance of the Chrome WebDriver, passing the configured service and options. It creates a new Chrome browser window that can be controlled programmatically.

            driver.get(url) #This line navigates the Chrome WebDriver to the specified URL provided in the url variable.
            
            #This line waits for up to 10 seconds for the presence of a specific element identified by the CSS selector "ytd-rich-grid-media.style-scope.ytd-rich-item-renderer" on the page. It ensures that the required element is loaded before proceeding to the next steps.
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-rich-grid-media.style-scope.ytd-rich-item-renderer")))

            html = driver.page_source #Retrieves the HTML source code of the page using "driver.page_source" 
            soup = BeautifulSoup(html, 'html.parser') #Creates a BeautifulSoup object named "soup" for parsing the HTML content.
            driver.quit() #This line closes the Chrome WebDriver and terminates the browser session.

            #These lines use BeautifulSoup's find_all method to extract all the elements that match the specified HTML tags and attributes.
            titles = soup.find_all("yt-formatted-string", id="video-title") #It finds all the <yt-formatted-string> elements with id="video-title"
            views = soup.find_all("span", class_="inline-metadata-item style-scope ytd-video-meta-block") #It finds all the <span> elements with class="inline-metadata-item style-scope ytd-video-meta-block".
            video_urls = soup.find_all("a", id="video-title-link") #This line finds all the <a> elements with id="video-title-link". These elements typically contain the URLs of the videos.
            thumbnails = soup.find_all("img", class_="yt-core-image yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded") # Extract thumbnails from HTML

            data = []
            my_dict=[]
            
            print(f"Found {len(titles)} titles, {len(views)} view elements, {len(video_urls)} video URLs, {len(thumbnails)} thumbnails")
            
            for i in range(min(num_videos, len(titles))):
                try:
                    video_url = "https://www.youtube.com" + video_urls[i].get('href') #Retrieving the Video Url of each video.

                    # Extract thumbnail URL from HTML (avoid pytube issues)
                    thumbnail_url = "N/A"
                    if i < len(thumbnails):
                        thumbnail_url = thumbnails[i].get('src') or thumbnails[i].get('data-src') or "N/A"
                    
                    # If no direct thumbnail found, construct default YouTube thumbnail URL
                    if thumbnail_url == "N/A":
                        video_id = video_urls[i].get('href').split('watch?v=')[1].split('&')[0] if 'watch?v=' in video_urls[i].get('href') else "N/A"
                        if video_id != "N/A":
                            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

                    title = titles[i].text.strip() if titles[i].text else "N/A" #Retrieving the Titles of each video.
                    views_count = views[2 * i].text.strip() if 2 * i < len(views) else "N/A" #Retrieving the Views of each video.
                    publish_date = views[2 * i + 1].text.strip() if 2 * i + 1 < len(views) else "N/A" #Retrieving the publish date.

                    #Storing the contents in a dictionary(for MongoDB)
                    my_dict = {"Video URL":video_url,"Thumbnail URL":thumbnail_url,"Title of the Video":title,"Number of Views":views_count,"Date of Publish":publish_date}
                    
                    # Match the data order with the DataFrame columns and template expectations
                    data.append([video_url, thumbnail_url, title, views_count, publish_date])
                    
                    print(f"Processed video {i+1}: {title[:50]}...")
                    
                except Exception as video_error:
                    print(f"Error processing video {i+1}: {str(video_error)}")
                    continue

                # MongoDB setup
                # uri = "mongodb+srv://Python_Project_1_Youtube_Web_Scraping:pwskills_pythonproject_123@cluster0.6xne1kl.mongodb.net/?retryWrites=true&w=majority"
                # client = MongoClient(uri)
                # db = client["info_scrap"]
                # info_col = db["info_scrap_data"]
                # info_col.insert_one(my_dict)

            # Creating a pandas DataFrame and saving as CSV file
            df = pd.DataFrame(data, columns=['Video URL', 'Thumbnail URL', 'Title of the Video', 'Number of Views', 'Date of Publish'])
            
            print(f"Scraped {len(data)} videos successfully")
            
            print("Sample data:", data[:2] if data else "No data found")
            
            df.to_csv('scrapper.csv', index=False)

            return render_template('results.html', data=data)

        except Exception as e:
            error_message = str(e)
            return render_template('error.html', error=error_message)

    else:
        return render_template('index.html')

if __name__ == "__main__":
    # This condition checks if the current script is the main entry point
    # i.e., it is being directly run as a standalone script
    # The following line starts the Flask application
    # It binds the application to the 0.0.0.0 IP address and listens on port 8000
    # The debug mode is enabled to show detailed error messages
    app.run(host='0.0.0.0', port=8000, debug=True)
