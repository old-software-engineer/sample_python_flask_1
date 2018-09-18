from . import app
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
from .models import Question, Answer
from flask import url_for, request, session


@app.route('/question/<question_id>')
def question(question_id):
    question = Question.query.get(question_id)
    session['question_id'] = question.id
    if not is_sms_request():
        return voice_twiml(question)
    else:
        return sms_twiml(question)


@app.route('/love_chocolate')
def love_chocolate():
    response = VoiceResponse()
    response.say('I like chocolate too!', voice='woman', language='en-AU')
    response.say('Thank you for answering. Good bye!', voice='woman', language='en-AU')
    response.hangup()
    if 'question_id' in session:
        del session['question_id']
    return str(response)

@app.route('/dont_love_chocolate')
def dont_love_chocolate():
    response = VoiceResponse()
    response.say('I also do not like chocolate!', voice='woman', language='en-AU')
    response.say('Thank you for answering. Good bye!', voice='woman', language='en-AU')
    response.hangup()
    if 'question_id' in session:
        del session['question_id']
    return str(response)

def is_sms_request():
    return 'MessageSid' in request.values.keys()


def voice_twiml(question):
    response = VoiceResponse()
    if not question.id == 1:
        if not question.id == 3:
            print(question.id)
            answer = Answer.query.order_by('-id').first()
            if answer.recording_url:
                response.say('your last answer was', voice='woman', language='en-AU')
                response.play(answer.recording_url, loop='1')
                response.say('your next question is', voice='woman', language='en-AU')
    if question.kind == Question.RECORDING or question.kind == Question.NUMERIC:
        print('/static/q_%s.mp3' % question.id)
        response.play('/static/q_%s.mp3' % question.id, loop='2')
        response.say(VOICE_INSTRUCTIONS[question.kind], voice='woman', language='en-AU')
    else:
        if question.id == 6:
            response.say(question.content, voice='woman', language='en-AU')
            response.say(VOICE_INSTRUCTIONS[question.kind], voice='woman', language='en-AU')
    if question.id == 6:
        action_url = url_for('inter_answer', question_id=question.id)
    else:
        action_url = url_for('answer', question_id=question.id)
    # action_url = url_for('answer', question_id=question.id)
    transcription_url = ''
    # transcription_url = url_for('answer_transcription', question_id=question.id)
    if question.kind == Question.TEXT or question.kind == Question.RECORDING:
        response.record(action=action_url,
                        transcribe_callback=transcription_url, RecordingChannels='dual', transcribe="true")
    else:
        response.gather(action=action_url)
    return str(response)

VOICE_INSTRUCTIONS = {
        Question.TEXT: 'Please record your answer after the beep and press the hash sign',
        Question.RECORDING: 'Please record your answer after the beep and press the hash sign',
        Question.BOOLEAN: 'Please Type your answer and press Hash sign.',
        Question.NUMERIC: 'Please press a number between 1 and 2 and press the hash sign'
}


def sms_twiml(question):
    response = MessagingResponse()
    response.message(question.content)
    response.message(SMS_INSTRUCTIONS[question.kind])
    return str(response)

SMS_INSTRUCTIONS = {
        Question.TEXT: 'Please type your answer',
        Question.BOOLEAN: 'Please type 1 for yes and 0 for no',
        Question.NUMERIC: 'Please type a number between 1 and 10'
}
