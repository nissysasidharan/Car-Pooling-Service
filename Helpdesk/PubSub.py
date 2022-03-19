import redis
r=redis.Redis('127.0.0.1')

def pub(msg1):
    r.publish('ch-1', msg1)

def sub(channel):
    sub=r.pubsub()
    sub.subscribe(channel)
    for message in sub.listen():
        if message is not None and isinstance(message, dict):
            msg1=message.get('data')
            r.lpush('msg_scoreboard',msg1)
while True:
    sub('ch-1')
