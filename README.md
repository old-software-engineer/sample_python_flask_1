.virtualenv venv

.source venv/bin/activate

.pip install -r requirements.txt

. Run `source .env`

.python manage.py db upgrade


.python manage.py dbseed

. python manage.py runserver
go to https://www.twilio.com/console/phone-numbers click on phone number and in voice section fill "ngrokurl/voice" in A CALL COMES IN nd set it to HTTP GET
after saving the url in twilio make a call on twilio number