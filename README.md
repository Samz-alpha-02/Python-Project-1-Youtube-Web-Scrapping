
##YOUTUBE WEB SCRAPPER

This is a Python Flask application that scrapes YouTube video information based on a provided URL. It uses Selenium and BeautifulSoup to parse the HTML content of the webpage, retrieves relevant data, and stores it in a CSV file and a MongoDB database. The application is also deployed on Render Cloud Platform for easy accessibility.

## For Running the Application on Your Local System:

* A.Prerequisites:

Before running the application, make sure you have the following installed on your system (if run on local system):

1.Python 3.x

2.Flask

3.Flask-CORS

4.Selenium

5.BeautifulSoup

6.PyMongo

7.Pytube

You will also need to have Google Chrome installed on your system as the code uses the Chrome web driver.

* B.Installation:

1.Clone the repository:

Copy code: git clone https://github.com/your_username/your_repository.git

2.Change into the project directory:

Copy code: cd your_repository

3.Install the required dependencies using pip:

Copy code: pip install -r requirements.txt

* C.Usage:

To run the application, follow these steps:

1.Run the Flask application:

Copy code: python application.py

2.Open your web browser and visit http://localhost:5000 to access the home page.

3.Enter the YouTube URL in the provided input field and click the "Submit" button.

4.The application will scrape the video information from the YouTube page and store it in a CSV file named scrapper.csv.

5.The scraped data will also be inserted into a MongoDB database named info_scrap in the collection info_scrap_data.

## For Running the Application on Render Cloud Platform:

**USAGE**

1.Enter the channel name and the number of videos to scrape in the search form.

2.Click the "Search" button.

3.The application will scrape the specified number of videos from the YouTube channel and store the data in the MongoDB database.

4.A CSV file named scrapper.csv will be generated with the scraped data.

## Contributing:

Contributions are welcome! Please feel free to submit any issues or pull requests.
