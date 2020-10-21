import aion.mysql as mysql

ROBOT_ID = 1

class YaskawaMaintenaceMysqlModel(mysql.BaseMysqlAccess):
    def __init__(self):
        super().__init__("Maintenance")

    def append(self, timestamp, array_no, event):
        sql = """
            INSERT INTO event_logs (
                robot_id,
                event_id,
                state,
                created,
                robot_status_1,
                robot_status_2
            ) values (
                %(robot_id)s,
                %(event_id)s,
                %(state)s,
                %(created)s,
                %(robot_status_1)s,
                %(robot_status_2)s
            )
            ON DUPLICATE KEY UPDATE
                robot_status_1 = %(robot_status_1)s,
                robot_status_2 = %(robot_status_2)s
            """

        args = {"robot_id": ROBOT_ID, "created": timestamp, "event_id": event["id"], "state": event["state"], "robot_status_1": event["robot_status_1"], "robot_status_2": event["robot_status_2"]}
        self.set_query(sql, args)

    def getNewest(self, key):
        sql = """
            SELECT  elog.created            created,
                    elog.robot_status_1     robot_status_1,
                    elog.robot_status_2     robot_status_2
            FROM    event_logs              elog
            INNER
            JOIN    (
                    select  max(created)    created
                    from    event_logs
                    where   robot_id        = %(robot_id)s
                    )           emax
            ON      emax.created            = elog.created
            LIMIT   1
            """
       
        args = {"robot_id": ROBOT_ID}
        rs = self.get_query(sql, args)
        if isinstance(rs, dict):
            return rs
        else:
            return None
    
    def extractKey(self, key):
        tokens = key.split(",")
        return {"type": tokens[0], "command_no": tokens[1], "timestamp": tokens[2], "array_no": tokens[3]}
