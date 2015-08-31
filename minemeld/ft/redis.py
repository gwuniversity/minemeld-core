from __future__ import absolute_import

import logging
import redis

from . import base
from .utils import utc_millisec

LOG = logging.getLogger(__name__)


class RedisSet(base.BaseFT):
    _ftclass = 'RedisSet'

    def __init__(self, name, chassis, config, reinit=True):
        super(RedisSet, self).__init__(name, chassis, config, reinit=reinit)

        self.redis_skey = self.name

        self.SR = redis.StrictRedis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            db=self.redis_db
        )

        self.SR.delete(self.redis_skey)

    def configure(self):
        super(RedisSet, self).configure()

        self.redis_host = self.config.get('redis_host', 'localhost')
        self.redis_port = self.config.get('redis_port', 6379)
        self.redis_password = self.config.get('redis_password', None)
        self.redis_db = self.config.get('redis_db', 0)
        self.scoring_attribute = self.config.get(
            'scoring_attribute',
            '_updated'
        )

    def connect(self, inputs, output):
        output = False
        super(RedisSet, self).connect(inputs, output)

    def _add_indicator(self, score, indicator, value):
        self.SR.zadd(self.redis_skey, score, indicator)

    def _delete_indicator(self, indicator):
        self.SR.zrem(self.redis_skey, indicator)

    def _update(self, source=None, indicator=None, value=None):
        score = 0
        if self.scoring_attribute is not None:
            value['_updated'] = utc_millisec()

            av = value.get(self.scoring_attribute, None)
            if type(av) == int:
                score = av
            else:
                LOG.error("scoring_attribute is not int: %s", type(av))

        self._add_indicator(score, indicator, value)

    def _withdraw(self, source=None, indicator=None, value=None):
        self._delete_indicator(indicator)

    def length(self, source=None):
        return self.SR.zcard(self.redis_skey)

    def start(self):
        pass

    def stop(self):
        pass
