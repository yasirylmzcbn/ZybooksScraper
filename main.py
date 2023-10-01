import streamlit as sl
import os
from dotenv import load_dotenv

load_dotenv('creds/credentials.env')
env_user = os.getenv('USER')
env_pass = os.getenv('PASS')

sl.title("Zybooks Scraper")
email = sl.text_input("Enter zybooks email", value=env_user)
pw = sl.text_input("Enter zybooks password", type="password", value=env_pass)
labNumber = sl.text_input("Enter lab number")
assignmentType = f'({sl.radio("Enter assignment type",("team","individual"))})'
prof = sl.text_input("Enter professor last name")
numPages = sl.number_input("Enter the number of pages of students in zybooks. (37 for Prof. Wickliff)",1,1000)
startBut = sl.button("Scrape 🤖")

if email != env_user or pw != env_pass:
    sl.write("Credentials updated")
    with open('creds/credentials.env', 'w') as f:
        f.write(f"USER={email}\n")
        f.write(f"PASS={pw}\n")
if startBut:
    print('submitted')
    with open('headers.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if f'LAB: Topic {labNumber} {assignmentType}' in line:
                canvasName = line.strip()
                print("new canvas name:", canvasName)
                break
            
    from scraper import Scraper
    scraper = Scraper(email, pw, labNumber, assignmentType, prof, numPages, canvasName)
    scraper.login_to_zybooks()
    scraper.get_zybooks_grades()
    scraper.update_csv()
    os.rename('GRADEBOOK.csv', 'oldGRADEBOOK.csv')
    os.rename('updatedGRADEBOOK.csv', 'GRADEBOOK.csv')
    if os.path.exists('oldGRADEBOOK.csv'):
        os.remove('oldGRADEBOOK.csv')
        
    sl.write("Done! 🎉")