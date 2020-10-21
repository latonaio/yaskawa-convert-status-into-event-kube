import re
import aion.mongo as mongo


MONGO_DB_NAME = "ServiceBroker"
COLLECTION_NAME = "AfterProcessing"
PRIOR_SERVICE_NAME_PREFIX = "GetRobotDataFromYasukawa"
KEY_IN_METADATA = "RobotData"

class YaskawaRobotModel(mongo.BaseMongoAccess):
    def __init__(self):
        super().__init__(MONGO_DB_NAME)
        self._collection_name = COLLECTION_NAME

    def get(self, timestamp=None):
        prior_service_regex = re.compile(
            "^%s" % PRIOR_SERVICE_NAME_PREFIX, re.IGNORECASE)
        fi = {'priorServiceName': prior_service_regex}

        if timestamp is not None:
            fi['finishAt'] = {'$gt': timestamp}

        # return type is cursor
        return self.find(
            self._collection_name,
            filter=fi,
            sort=[('finishAt', 1)] # asc
        )
