from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from fuzzywuzzy import process, fuzz
import json
import csv

# labNumber = 2 # lab number
# assignmentType = "(team)" # "(individual)" or "(team)"
# prof = "Wickliff" # professor name
# canvasName = "LAB: Topic 2 (team) part 2 (1811112)" # the name of the column in the gradebook.csv file that you want to update
# numPages = 37 # the number of pages of students in zybooks
class Scraper:
    def __init__(self, email, password, labNumber, assignmentType, prof, numPages, canvasName):    
        self.names = []
        self.gradesDict = {}
        self.email = email
        self.password = password
        self.labNumber = labNumber
        self.assignmentType = assignmentType
        self.prof = prof
        self.numPages = numPages
        self.canvasName = canvasName
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def login_to_zybooks(self):
        # login to zybooks
        self.driver.get("https://learn.zybooks.com/zybook/TAMUENGR102Fall2023/")
        emailInput = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='email']")))
        emailInput.send_keys(self.email)
        passwInput = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password']")))
        passwInput.send_keys(self.password, Keys.ENTER)
        

    def get_zybooks_grades(self):
        # get the grades
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//i[@aria-label='assignment']"))).click()
        assignment = f"Lab Topic {self.labNumber} {self.assignmentType}".strip()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//h3[contains(text(), '{assignment}')]"))).click()
        labs = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='section-list pr-2']")))
        labs = labs.find_elements(By.TAG_NAME, "li")
        index = 0
        for lab in labs:
            try:
                lab.click()
            except:
                labs = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='section-list pr-2']")))
                labs = labs.find_elements(By.TAG_NAME, "li")
                lab = labs[index]
                lab.click()
            
            showButtons = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='content-resource programming-submission-payload ember-view']")))
            showButtons = showButtons.find_elements(By.XPATH, "//span[contains(text(), 'Show')]")
            showButtons[2].click()
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Section Alvarado (540/541)')]"))).click()
            
            profSelect = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{self.prof}')]")))
            profSelect.click()
            
            for page in range(self.numPages):
                student_names = WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//div[@class='list flex flex-col']")))
                student_names = student_names.find_elements(By.XPATH, "//span[@class='student-header']")
                student_rows = WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='flex pr-11']")))
                i = 1
                row = 3;
                for student in student_rows:
                    grade = int(student.find_elements(By.XPATH, "//div[@class='flex mx-2']")[row].text)
                    # check if student is in dictionary
                    if not self.gradesDict.get(student_names[i].text.lower()):
                        self.gradesDict[student_names[i].text.lower()] = [{"lab": f"{self.labNumber} {self.assignmentType}", "grade": grade}]
                    else:
                        self.gradesDict[student_names[i].text.lower()] = [{"lab": f"{self.labNumber} {self.assignmentType}", "grade": grade+self.gradesDict[student_names[i].text.lower()][0]["grade"]}]
                        
                    row += 2
                    i+=1
                
                # next page
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//i[@aria-label='keyboard_arrow_right']"))).click()
            # break
            self.driver.back()
            index += 1
        self.driver.close()
        # enter the data to json
        with open(f'{self.prof}_lab{self.labNumber}_{self.assignmentType}_grades.json', 'w+') as jsonFile:
            json.dump(self.gradesDict, jsonFile)

    # login_to_zybooks()
    # get_zybooks_grades()



    def get_first_last(self, s):
        if len(s) == 2:
            return (s[1] + " " + s[0]).strip()
        return (s[2] + " " + s[0]).strip()

    def find_best_match(self, name, threshold=80):
        best_match = None
        best_score = 0

        for student_name in self.gradesDict.keys():
            score = fuzz.token_sort_ratio(name, student_name)
            if score > best_score and score >= threshold:
                best_match = student_name
                best_score = score

        return best_match, best_score


    def update_csv(self):    
        gradebook = csv.DictReader(open('GRADEBOOK.csv', 'r', encoding="utf-8"))
        updatedGradebook = csv.DictWriter(open('updatedGRADEBOOK.csv', 'w', newline='', encoding="utf-8"), fieldnames=gradebook.fieldnames)
        updatedGradebook.writeheader()
        # gradesDict = json.loads(open(f'{prof}_lab{labNumber}_{assignmentType}_grades.json', 'r').read())

        firstTime = True
        index = 0
        for line in gradebook:
            if firstTime:
                updatedGradebook.writerow(line)
                firstTime = False
                continue
            
            student = line["Student"].lower() # name from csv
            student = self.find_best_match(student)[0]
            if not student:
                continue
            grade = self.gradesDict[student][0]["grade"]
            line[self.canvasName] = grade
            updatedGradebook.writerow(line)
        
