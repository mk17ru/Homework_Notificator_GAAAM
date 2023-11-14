from src.db.connection import conn


def run_sql(sql, data):
    cur = conn.cursor()
    cur.execute(sql, data)
    result = None
    try: 
        result = cur.fetchall()
    except Exception as e:
        print(e)
    conn.commit()
    return result


def get_full_relation(name):
    sql = f"SELECT * FROM {name};"

    return run_sql(sql, ())
