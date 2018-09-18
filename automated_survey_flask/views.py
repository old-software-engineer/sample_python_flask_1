from . import app
from . import question_view
from . import answer_view
from . import survey_view
from flask import render_template
from .models import Question, Answer
from twilio.rest import Client


@app.route('/')
def root():
    # account_sid = 'ACc0b0e2b6f5acb4ed72d4eb953403059c'
    # auth_token = '52df89c6c440b54b828b5b2210778f69'
    # client = Client(account_sid, auth_token)
    # questions_all = []
    # answer_response = {}
    # for question in Question.query.all():
    #     # for answer in question.answers.all():
    #     #     answer_response["content"] = answer.content
    #     #     answer_response["question"] = answer.question.content
    #     #     call_id = answer.session_id
    #     #     answer_response['recordings'] = client.recordings.list(call_sid=call_id)
    #     # questions_all.append(answer_response)
    #     questions_all.append(question.answers.all())
    #     answer_response = {}
    questions = Answer.query.order_by("id desc").all()
    return render_template('index.html', questions=questions)
    # return render_template('index.html', questions=questions_all)