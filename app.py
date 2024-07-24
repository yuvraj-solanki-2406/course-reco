from flask import Flask, render_template
from data import CourseRecommendation
from data import ContentbasedRecommendation

app = Flask(__name__)

course_reco = CourseRecommendation()
content_based_reco = ContentbasedRecommendation()

# 
@app.route("/", methods=['GET'])
def home_page():
    popular_course = course_reco.popular_course_fun(num_return=5)
    return render_template("index.html", popular_course=popular_course)


@app.route("/courses/<id>", methods=['GET'])
def get_course_details(id):
    course_detail = course_reco.find_course_detail(id)
    reco_course = content_based_reco.content_based_filtering(id, n_recommend=6)
    print( (reco_course))
    return render_template("course.html", c_detail=course_detail, reco_course=reco_course)


app.run(port=5500, debug=True)
