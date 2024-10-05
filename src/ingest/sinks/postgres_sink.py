import psycopg
from bytewax.outputs import FixedPartitionedSink, StatefulSinkPartition


class PsqlSink(StatefulSinkPartition):
    def __init__(self, db_url: str):
        self.conn = psycopg.connect(db_url)
        self.conn.set_session(autocommit=True)
        self.cur = self.conn.cursor()

    def write_batch(self, values):
        query_string = """
            INSERT INTO events (user_id, data)
            VALUES (%s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET data = %s;
        """
        self.cur.execute_values(query_string, values)

    def snapshot(self):
        pass

    def close(self):
        self.conn.close()


class PsqlOutput(FixedPartitionedSink):
    def list_parts(self):
        return ["single"]

    def build_part(self, step_id, for_part, resume_state):
        return PsqlSink()
