import time
import requests
from worker import app
from monitor import PrometheusMonitor
from celery.utils.log import get_task_logger
from multiprocessing import Process

logger = get_task_logger(__name__)

def monitor():
    # turn on the monitor
    broker = 'amqp://user:password@127.0.0.1:5672//'
    daemon = PrometheusMonitor(app=app, broker=broker)
    daemon.run_loop()

def tasks():

    # stock symbol
    symbols = ['TSLA']
    # article category
    categorys = ['105','111','102','104','101','113','114','110']

    # get cookies
    result = app.send_task('tasks.spider.get_cookies', queue='crawl_queue')
    while not result.ready():
        time.sleep(1)
    cookies = result.get()

    # send tasks
    for symbol in symbols:
        app.send_task('tasks.spider.comment', [cookies, symbol], queue='crawl_queue')
    for category in categorys:
        app.send_task('tasks.spider.article', [cookies, category], queue='crawl_queue')

def test():

    # subprocess
    p = Process(target=monitor, args=())
    p.start()

    time.sleep(10)
    tasks()

    p.join()

if __name__ == "__main__":
    test()