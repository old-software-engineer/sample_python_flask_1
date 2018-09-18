from automated_survey_flask import db


class Survey(db.Model):
    __tablename__ = 'surveys'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    questions = db.relationship('Question', backref='survey', lazy='dynamic')

    def __init__(self, title):
        self.title = title

    @property
    def has_questions(self):
        return self.questions.count() > 0


class Question(db.Model):
    __tablename__ = 'questions'

    TEXT = 'text'
    NUMERIC = 'numeric'
    BOOLEAN = 'boolean'
    RECORDING = 'recording'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    kind = db.Column(db.Enum(TEXT, NUMERIC, BOOLEAN,RECORDING,
                             name='question_kind'))
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))
    answers = db.relationship('Answer', backref='question', lazy='dynamic')

    def __init__(self, content, kind=TEXT):
        self.content = content
        self.kind = kind

    def next(self):
        return self.survey.questions\
                    .filter(Question.id > self.id)\
                    .order_by('id').first()


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    session_id = db.Column(db.String, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    recording_url = db.Column(db.String, nullable=False)
    recording_sid = db.Column(db.String, nullable=False)
    transcription_sid = db.Column(db.String, nullable=False)

    @classmethod
    def update_content(cls, session_id, question_id, content, recording_sid, recording_url, transcription_sid):
        existing_answer = cls.query.filter(Answer.session_id == session_id and
                                           Answer.question_id == question_id and Answer.recording_url == recording_url and
                                           Answer.recording_sid == recording_sid and Answer.transcription_sid == transcription_sid).first()
        try:
            int(content)
            if question_id == 3:
                1 <= int(content) <= 2
                parsed_content = content
            else:
                parsed_content = '1'
        #     if 1 <= int(content) <= 10:
        #         parsed_content = content
        #     else:
        #         parsed_content = content[0]
        except:
            parsed_content = content
        existing_answer.content = parsed_content
        db.session.add(existing_answer)
        db.session.commit()

    def __init__(self, content, question, session_id, recording_url, recording_sid, transcription_sid):
        self.content = content
        self.question = question
        self.session_id = session_id
        self.recording_url = recording_url
        self.recording_sid = recording_sid
        self.transcription_sid = transcription_sid
