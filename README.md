# ZybooksScraper
### Selenium WebScraper to transfer students' grades from Zybooks to Canvas
## First Time Set-up:
First, clone the repository:<br>
```git clone https://github.com/yasirylmzcbn/ZybooksScraper.git```<br><br>
Then, cd into the directory:<br>
```cd ZybooksScraper```<br><br>
Download required libraries (you can create a venv first if you'd like):<br>
```pip install -r requirements.txt```<br><br>
## Instructions:
Download the newest version of the gradebook from Canvas as a csv:<br>
Go to Canvas > Open the Gradebook > Click Export > Export Entire Gradebook > Rename downloaded file to GRADEBOOK.csv > Put the file in the ZybooksScraper folder<br><br>
Run this command and fill out the information to get the updated gradebook:<br>
```streamlit run main.py```<br><br>
Import the updated gradebook to Canvas:<br>
Go to Canvas > Open the Gradebook > Click Import > Choose File (the GRADEBOOK.csv file in the ZybooksScraper directory) > Upload Data<br><br>
It may take a few minutes for the grades to be fully imported, check back in a few minutes to ensure everything is imported properly.<br>

## Technologies Used:
Python, Selenium, Streamlit, Dotenv, FuzzyWuzzy
