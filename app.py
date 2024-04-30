from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

RESPONSES = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRETKEY'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = True
toolbar = DebugToolbarExtension(app)

@app.route("/")
def start_page():
  return render_template("start.html", survey=survey)

@app.route("/start_survey", methods=["POST"])
def start_survey():
  session[RESPONSES] = []
  return redirect("/questions/0")

@app.route("/response", methods=["POST"])
def survey_response():
  choice = request.form['responses']

  responses = session[RESPONSES]
  responses.append(choice)
  session[RESPONSES] = responses

  if(len(responses) == len(survey.questions)):
    return redirect("/survey_completed")
  else:
    return redirect(f"/questions/{len(responses)}")
  
@app.route("/questions/<int:qid>")
def show_question(qid):
  responses = session.get(RESPONSES)

  if (responses is None):
    return redirect("/")
  
  if (len(responses) == len(survey.questions)):
    return redirect("/survey_completed")
  
  if (len(responses) != qid):
    flash(f"Wrong question id: {qid}.")
    return redirect(f"/questions/{len(responses)}")
  
  question = survey.questions[qid]
  return render_template("questions.html", question_num=qid, question = question)

@app.route("/survey_completed")
def completed():
  return render_template("completed.html")

