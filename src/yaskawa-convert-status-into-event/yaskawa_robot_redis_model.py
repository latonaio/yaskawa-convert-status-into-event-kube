import os
import redis
import dateutil
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse

# redis constants
IDENTIFIER = "YasukawaRobotData"
DEFAULT_REDIS_HOST = os.environ.get("REDIS_HOST", "redis-cluster")
DEFAULT_REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
DEFAULT_DB_NO = os.environ.get("REDIS_DB_NO", 0)

ZLIST_KEY_DELIMITER = ":"
ZLIST_IDENTIFIER = "key-list"

class YaskawaRobotRedisModel():
    def __init__(self):
        self.redis = redis.StrictRedis(host=DEFAULT_REDIS_HOST, port=DEFAULT_REDIS_PORT, db=DEFAULT_DB_NO, decode_responses=True)
   
    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, trace):
        pass

    def timestampToScore(self, timestamp):
        if timestamp:
            JST = timezone(timedelta(hours=+9), 'JST')
            dt = parse(str(timestamp)).astimezone(JST)
            return dt.timestamp() * (10 ** 6)
        else:
            return 0

    def get(self, command_no, array_no, score):
        value = None
        key = None
        # note: exists in z-list but not exists in h-list
        while True:
            z = self.redis.zrangebyscore(ZLIST_IDENTIFIER + ZLIST_KEY_DELIMITER + command_no + ZLIST_KEY_DELIMITER + str(array_no), score, "+inf", 1, 1, "WITHSCORE")
            if z:
                key, score = z[0]
            else:
                return None
            
            value = self.redis.hgetall(key)
            if value and value.get("RobotStatus"):
                break
        
        return {"key": key, "score": score, "value": value}
