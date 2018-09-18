from time import sleep

from . import app, db
from .models import Question, Answer
from flask import url_for, request, session, redirect
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

account_sid = 'ACc0b0e2b6f5acb4ed72d4eb953403059c'
auth_token = '52df89c6c440b54b828b5b2210778f69'
client = Client(account_sid, auth_token)


@app.route('/answer/<question_id>', methods=['POST'])
def answer(question_id):
    question = Question.query.get(question_id)
    record = extract_content(question)
    if not record.get('next_question'):
        db.save(Answer(content=record['transcript'],
                       question=question,
                       session_id=session_id(),
                       recording_url=record['recording_url'],
                       recording_sid=record['recording_sid'],
                       transcription_sid=record['transcription_sid']))
        if question_id == '3' and record.get('transcript') == '1':
            next_question = Question.query.get(5)
        elif question_id == '3' and record.get('transcript') == '2':
            next_question = Question.query.get(4)
        else:
            next_question = question.next()
    else:
        next_question = record.get('next_question')
    if next_question:
        return redirect_twiml(next_question,record['recording_url'])
    else:
        return goodbye_twiml()


@app.route('/inter_answer/<question_id>', methods=['POST'])
def inter_answer(question_id):
    question = Question.query.get(question_id)
    record = extract_content(question)
    db.save(Answer(content=record['transcript'],
                   question=question,
                   session_id=session_id(),
                   recording_url=record['recording_url'],
                   recording_sid=record['recording_sid'],
                   transcription_sid=record['transcription_sid']))
    transcription = client.recordings.get(request.form['RecordingSid']).transcriptions.list()[0].transcription_text
    # if not transcription:
    #     redirect(url=url_for('hold_on', recording=client.recordings.get(request.form['RecordingSid'])), method='GET')
    #     transcription = client.recordings.get(request.form['RecordingSid']).transcriptions.list()[0].transcription_text
    redirect_to = ''
    if transcription == 'Yes.':
        redirect_to = "love_chocolate"
    elif transcription == "No.":
        redirect_to = "dont_love_chocolate"
    if redirect_to:
        return redirect(url_for(redirect_to, method='GET'))
    else:
        return goodbye_twiml()


def extract_content(question):
    recording = {}
    if is_sms_request():
        return request.values['Body']
    elif question.kind == Question.TEXT or question.kind == Question.RECORDING:
        recording['recording_url'] = request.values['RecordingUrl']
        recording['recording_sid'] = request.values['RecordingSid']
        recording['transcript'] = 'Transcription in progress.'
        recording['transcription_sid'] = ''
        return recording
    else:
        if 1 <= int(request.values['Digits']) <= 2:
            parsed_content = request.values['Digits']
        else:
            response = VoiceResponse()
            response.say("please choose a valid option", voice='alice', language='en-AU')
            recording["next_question"] = question
        recording['recording_url'] = ''
        recording['recording_sid'] = ''
        recording['transcription_sid'] = ''
        recording['transcript'] = parsed_content[0]
        return recording


def redirect_twiml(question,recording):
    response = MessagingResponse()
    response.redirect(url=url_for('question', question_id=question.id, recording=recording), method='GET')
    return str(response)


def goodbye_twiml():
    if is_sms_request():
        response = MessagingResponse()
        response.message("Thank you for answering. Good bye!", voice='woman', language='en-AU')
    else:
        response = VoiceResponse()
        response.say("Thank you for answering. Good bye!", voice='woman', language='en-AU')
        response.hangup()
    if 'question_id' in session:
        del session['question_id']
    return str(response)


def is_sms_request():
    return 'MessageSid' in request.values.keys()


@app.route('/answer/transcription/<question_id>', methods=['POST'])
def answer_transcription(question_id):
    session_id = request.values['CallSid']
    content = request.values['TranscriptionText']
    recording_url = request.values['RecordingSid']
    recording_sid = request.values['RecordingSid']
    transcription_sid = request.form['TranscriptionSid']
    Answer.update_content(session_id, question_id, content, recording_url, recording_sid, transcription_sid)
    return ''


def session_id():
    return request.values.get('CallSid') or request.values['MessageSid']

