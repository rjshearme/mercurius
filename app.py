import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, render_template, jsonify, abort
from flask_api import status

# from freecycle import FreecycleChecker

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
RECIPIENT_ID = os.environ.get('RECIPIENT_ID')

logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_url_path='')


# freecycle_checker = FreecycleChecker()
# freecycle_scheduler = BackgroundScheduler()
# freecycle_scheduler.add_job(freecycle_checker.scan_freecycle, "interval", seconds=10, coalesce=True, )

@app.route('/api/v1/health')
def home():
    return {"msg": "OK"}, status.HTTP_200_OK


def verify_fb_token():
    token_sent = request.args.get("hub.verify_token")
    return request.args.get("hub.challenge") if token_sent == VERIFY_TOKEN else 'Invalid verification token'


def handle_fb_message():
    output = request.get_json()
    for event in output['entry']:
        messaging = event.get('messaging', [])
        for message in messaging:
            logging.info(f"Message:  {message}")
            if message['sender']['id'] != RECIPIENT_ID:
                return "wrong user"
            user_input = message.get('message', {})
            postback = message.get('postback', {})
            quick_reply = user_input.get('quick_reply', {})
            incoming_text = ''

            # for quick replies
            if quick_reply:
                incoming_text = quick_reply.get('payload')

            # for user input not using button or quick reply (standard message)
            elif user_input:
                incoming_text = user_input.get('text')

            # for buttons
            elif postback:
                incoming_text = postback.get('payload')

    return {"msg": "Message processed"}, status.HTTP_200_OK


@app.route("/token", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        return verify_fb_token()
    else:
        return handle_fb_message()


if __name__ == "__main__":
    app.run(debug=True, port=8000)
