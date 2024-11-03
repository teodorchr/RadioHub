import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup
import pyttsx3

class NewsScraperThread(QThread):
    # Signal to emit when a news item is scraped
    news_scraped = pyqtSignal(str)

    def run(self):
        # This method is called when the thread starts
        # Example scraping from a news website
        url = "https://example-news-site.com"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h2', class_='headline')
        for headline in headlines:
            # Emit the scraped headline
            self.news_scraped.emit(headline.text)
            # Save the headline to the database
            self.save_to_db(headline.text)

    def save_to_db(self, headline):
        # Save a single headline to the SQLite database
        conn = sqlite3.connect('news.db')
        c = conn.cursor()
        c.execute("INSERT INTO headlines (text) VALUES (?)", (headline,))
        conn.commit()
        conn.close()

class TextToSpeechThread(QThread):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        # Initialize the text-to-speech engine and speak the text
        engine = pyttsx3.init()
        engine.say(self.text)
        engine.runAndWait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("News Narrator")
        self.setGeometry(100, 100, 400, 300)

        # Create the main layout
        layout = QVBoxLayout()
        
        # Text area to display scraped news
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        # Button to trigger news scraping
        scrape_button = QPushButton("Scrape News")
        scrape_button.clicked.connect(self.scrape_news)
        layout.addWidget(scrape_button)

        # Button to trigger text-to-speech
        speak_button = QPushButton("Speak News")
        speak_button.clicked.connect(self.speak_news)
        layout.addWidget(speak_button)

        # Set the main layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize the database
        self.init_db()

    def init_db(self):
        # Create the SQLite database and headlines table if they don't exist
        conn = sqlite3.connect('news.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS headlines
                     (id INTEGER PRIMARY KEY, text TEXT)''')
        conn.commit()
        conn.close()

    def scrape_news(self):
        # Start the news scraping thread
        self.scraper_thread = NewsScraperThread()
        # Connect the news_scraped signal to the update_news method
        self.scraper_thread.news_scraped.connect(self.update_news)
        self.scraper_thread.start()

    def update_news(self, news):
        # Append the scraped news to the text edit area
        self.text_edit.append(news)

    def speak_news(self):
        # Get the text from the text edit area
        text = self.text_edit.toPlainText()
        # Start the text-to-speech thread
        self.tts_thread = TextToSpeechThread(text)
        self.tts_thread.start()

if __name__ == "__main__":
    # Create and run the application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())