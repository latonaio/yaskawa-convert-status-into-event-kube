# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import time
import os
import json

from aion.microservice import main_decorator, Options
from aion.kanban import Kanban
from aion.logger import lprint, initialize_logger

from .yaskawa_maintenace_mysql_model import YaskawaMaintenaceMysqlModel
from .yaskawa_robot_redis_model import YaskawaRobotRedisModel

SERVICE_NAME = "yaskawa-convert-status-into-event"
YASKAWA_COMMAND_NO = "0x0072"
YASKAWA_ARRAY_NO = 1
COMMAND_NO = "eventlog"
INTERVAL = 0.5
initialize_logger(SERVICE_NAME)

def unpack(byte):
    return [
        (byte >> 7) & 0x1,
        (byte >> 6) & 0x1,
        (byte >> 5) & 0x1,
        (byte >> 4) & 0x1,
        (byte >> 3) & 0x1,
        (byte >> 2) & 0x1,
        (byte >> 1) & 0x1,
        (byte >> 0) & 0x1
    ]


def pack(bits):
    return (
        (bits[0] & 0x1) << 7 |
        (bits[1] & 0x1) << 6 |
        (bits[2] & 0x1) << 5 |
        (bits[3] & 0x1) << 4 |
        (bits[4] & 0x1) << 3 |
        (bits[5] & 0x1) << 2 |
        (bits[6] & 0x1) << 1 |
        (bits[7] & 0x1) << 0
    )


def extractEvent(status1, status2, prevStatus1, prevStatus2):
    status = status1 + status2
    prevStatus = prevStatus1 + prevStatus2
    events = []

    for i in range(len(status)):
        if status[i] == prevStatus[i]:
            continue

        events.append({
            "id": i + 1,
            "state": status[i],
            "robot_status_1": pack(status1),
            "robot_status_2": pack(status2)
        })
    return events


def appendToMysql(db, timestamp, array_no, status1, status2, prevStatus1, prevStatus2):
    events = extractEvent(status1, status2, prevStatus1, prevStatus2)
    # write to MySQL
    for event in events:
        db.append(timestamp, array_no, event)


@main_decorator(SERVICE_NAME)
def main_without_kanban(opt: Options):
    lprint("start main_without_kanban()")
    # get cache kanban
    conn = opt.get_conn()
    num = opt.get_number()
    kanban: Kanban = conn.set_kanban(SERVICE_NAME, num)

    ######### main function #############
    with YaskawaMaintenaceMysqlModel() as db:

        # mysqlから最新のステータスを取得
        rs = db.getNewest(COMMAND_NO)
        if rs:
            created = rs["created"]
            robot_status_1 = rs["robot_status_1"]
            robot_status_2 = rs["robot_status_2"]

        if rs:
            prevTimestamp = created
            prevStatus1 = unpack(robot_status_1)
            prevStatus2 = unpack(robot_status_2)
        else:
            prevTimestamp = None
            prevStatus1 = [-1, -1, -1, -1, -1, -1, -1, -1]
            prevStatus2 = [-1, -1, -1, -1, -1, -1, -1, -1]

        mgcur = None
        with YaskawaRobotRedisModel() as redis:
            # get last timestamp
            score = redis.timestampToScore(prevTimestamp)
            lprint(f"score: {score}")

            while True:
                # redisDBからprevTimestamp以降の最初のデータを取得
                data = redis.get(YASKAWA_COMMAND_NO, YASKAWA_ARRAY_NO, score)

                if not data:
                    time.sleep(INTERVAL)
                    continue

                keys = db.extractKey(data["key"])
                command_no = keys["command_no"]
                timestamp = keys["timestamp"]
                array_no = keys["array_no"]

                score = data["score"]

                robotStatus = json.loads(data["value"]["RobotStatus"])
                status1 = robotStatus[0]
                status2 = robotStatus[1]

                # status break
                if prevStatus1 != status1 or prevStatus2 != status2:
                    appendToMysql(db, timestamp, array_no, status1,
                                  status2, prevStatus1, prevStatus2)
                    db.commit_query()
                    lprint("wrote in event_logs")

                prevTimestamp = timestamp
                prevStatus1 = status1
                prevStatus2 = status2
