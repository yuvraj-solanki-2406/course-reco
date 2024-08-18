import pandas as pd 
import numpy as np 
from bs4 import BeautifulSoup
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk


# popular based recommendation
class CourseRecommendation():
    def __init__(self) -> None:
        courses = pd.read_csv("./static/udemy_courses.csv")
        self.popular_course = courses[(courses['num_subscribers']>12000) & (courses['num_reviews']>5000)]
        self.all_courses = courses
        nltk.download('wordnet')
    
    def popular_course_fun(self, num_return):
        self.popular_course = self.popular_course.sort_values(by='num_subscribers', ascending=False, ignore_index=True).head(5)
        if num_return > self.popular_course.shape[0]:
            num_return = self.popular_course.shape[0]
        
        self.popular_course['image'] = self.popular_course['url'].apply(self.scrap_image)
        
        return self.popular_course.head(num_return)
    
    
    def all_courses(self):
        return self.all_courses 
    
    
    # find the details of the course
    def find_course_detail(self, c_id):
        c_id = int(c_id)
        c_detail = self.all_courses[self.all_courses['course_id']==c_id]
        url = c_detail['url'].values[0]
        c_detail['image'] = self.scrap_image(url)
        return c_detail
        
    
    # find the image
    def scrap_image(self, c_url):
        response = requests.get(c_url)
        if response.status_code == 200:
            bs = BeautifulSoup(response.content, 'html.parser')
            spans = bs.find("span", class_="intro-asset--img-aspect--3gluH")
            if spans:
                first_image = spans.find("img")
                output = first_image.get("src")
                return output
        return "No Image Found"


# Content based recommendation
class ContentbasedRecommendation():
    def __init__(self) -> None:
        self.courses = pd.read_csv("./static/udemy_courses.csv")
        # initializing PorterStemmer and stopwords
        self.stem = PorterStemmer()
        nltk.download('stopwords')
        nltk.download('wordnet')
        self.stopword = stopwords.words('english')
        
        # merging two columns
        self.courses['tags'] = self.courses['course_title'] + " " + self.courses['subject']
        # applying preproessing to merged column
        self.courses['tags'] = self.courses['tags'].apply(self.preprocess)
        # vectorization
        self.tokemizer = TfidfVectorizer().fit_transform(self.courses['tags'])
        # finding the cosine similarity
        self.similarity = cosine_similarity(self.tokemizer)

    
    # preprocess text
    def preprocess(self, text):
        stemmed_word = [self.stem.stem(word.lower()) for word in text.split(" ") if word.lower() not in self.stopword]
        return " ".join(stemmed_word)
    
    # content based filtering
    def content_based_filtering(self, c_id, n_recommend):
        n_recommend = int(n_recommend)
        c_id = int(c_id)
        course_index = self.courses[self.courses['course_id'] == c_id].index[0]
        distances = self.similarity[course_index]
        course_lists = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:n_recommend]
        
        output = []
        for i in course_lists:
            course_info = {
                'title': self.courses.iloc[i[0]]['course_title'],
                'num_subscribers': self.courses.iloc[i[0]]['num_subscribers'],
                'num_reviews': self.courses.iloc[i[0]]['num_reviews'],
                'image': self.scrap_image(self.courses.iloc[i[0]]['url']),
            }
            output.append(course_info)

        return output
    
    
    # find the image
    def scrap_image(self, c_url):
        response = requests.get(c_url)
        if response.status_code == 200:
            bs = BeautifulSoup(response.content, 'html.parser')
            spans = bs.find("span", class_="intro-asset--img-aspect--3gluH")
            if spans:
                first_image = spans.find("img")
                output = first_image.get("src")
                return output
        return "No Image Found"

