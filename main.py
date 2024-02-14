import json
import time
import schedule
import time
from datetime import datetime
from argparse import ArgumentParser
from lib.Detector import Detector
from lib.SlackBot import SlackBot
# from flask import Flask

# app = Flask(__name__)

# @app.route('/main')
# def hello():
#     return 'Hello, Notification Bot!'

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)

def heartbeat():
    print(f'{datetime.now().strftime("%Y.%m.%d %H:%M:%S")} Good working :)')

def format_message(before_change: str, after_change: str) -> str:
    """
    App specific(Melon ticket) formatter.

    :param before_change:
    :param after_change:
    :return:
    """

    before = list(map(lambda x: (x['perfDay'], x['perfTimelist'][0]['seatGradelist'][0]['realSeatCntlk']),
                      json.loads(before_change)['data']['perfDaylist']))

    after = list(map(lambda x: (x['perfDay'], x['perfTimelist'][0]['seatGradelist'][0]['realSeatCntlk']),
                     json.loads(after_change)['data']['perfDaylist']))

    changes = []

    for i in range(len(before)):
        seats_before = before[i][1]
        seats_after = after[i][1]

        if seats_before != seats_after:
            changes.append(after[i])

    if len(changes) == 0:
        return 'realSeatCntlk 이외 변화 발생.'
        

    return '\n'.join(map(lambda x: f'{x[0]}일 공연 {x[1]}석 남음.', changes))


if __name__ == '__main__':
    parser = ArgumentParser(description='Watch for website changes')
    parser.add_argument('--target', required=True, dest='target', help='URL of the webpage to observe')
    parser.add_argument('--interval', required=True, dest='interval', help='Polling interval', type=float)
    parser.add_argument('--slack-webhook-url', required=True, dest='webhook_url',
                        help='Slack webhook URL where notification will be sent.')

    args = parser.parse_args()

    target = args.target
    interval = args.interval
    webhook_url = args.webhook_url

    slack_bot = SlackBot(webhook_url)
    detector = Detector(target, lambda prev, now: slack_bot.send(format_message(prev, now)))
    heartbeat()
    slack_bot.send('알림!!!')

    schedule.every(1).hours.do(heartbeat)
    schedule.every(interval).seconds.do(detector.tick)

    while True:
        schedule.run_pending()
        time.sleep(0.01)