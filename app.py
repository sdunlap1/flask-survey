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
    session.modified = True
    return redirect("/questions/0")

@app.route("/response", methods=["POST"])
def survey_response():
  responses = session.get(RESPONSES, [])
  current_question = len(responses)

  # Check if user has answered all questions
  if current_question >= len(survey.questions):
    flash("You have answered all questions")
    return redirect("/survey_completed")
  
  choice = request.form.get('response')

  # Check if no choice was made
  if choice is None:
    flash("Please select an answer to continue")
    return redirect(f"/questions/{current_question}")

  responses.append(choice)
  session[RESPONSES] = responses

  next_question = current_question + 1
  if next_question == len(survey.questions):
    return redirect("/survey_completed")
  else:
    return redirect(f"/questions/{next_question}")

@app.route("/questions/<int:qid>")
def show_question(qid):
    responses = session.get(RESPONSES)
    # Check to see if the survey has been started
    if responses is None:
       flash("Please start the survey.")
       return redirect("/")
    
    # Check for accessing questions out of order 
    if len(responses) == 0 and qid > 0:
       flash("Please start from the first question.")
       return redirect("/questions/0")

    if len(responses) == len(survey.questions):
        flash("YOU HAVE COMPLETED THE SURVEY. THANK YOU")
        return redirect("/survey_completed")
    
    # Prevent user from manipulating or view questions out of order 
    if qid >= len(survey.questions) or qid < 0:
        flash("Invalid question number.")
        return redirect(f"/questions/{len(responses)}")
    
    # Check to make sure user answers questions in order
    if qid != len(responses):
        flash(f"Wrong question id: {qid}. Redirecting")
        return redirect(f"/questions/{len(responses)}")
    
    # Retrieve question from survey using index (qid)
    question = survey.questions[qid]
    # Render the question on the page with it's index (qid)
    return render_template("questions.html", question_num=qid, question=question)


@app.route("/survey_completed")
def completed():
  flash("THANKS FOR TAKING THE SURVEY!!")
  return render_template("completed.html")

