from redis import Redis

class RedisRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    def add(self, name, time, value):
        self.redis.setex(name, time, value)

    def get(self, name):
        return self.redis.get(name)
    
    def remove(self, name):
        self.redis.delete(name)