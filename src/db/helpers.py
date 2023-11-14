from src.db.connection import conn


def run_sql(sql):
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()
    return result


def get_full_relation(name):
    sql = f"SELECT * FROM {name};"

    return run_sql(sql)
