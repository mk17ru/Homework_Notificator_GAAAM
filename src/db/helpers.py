from src.db.connection import conn


def run_sql(sql, data=None):
    cur = conn.cursor()

    try:
        cur.execute(sql, data or ())
    except Exception as e:
        conn.commit()
        print(e)
        return None

    result = None
    try: 
        result = cur.fetchall()
    except Exception as e:
        print(e)

    conn.commit()
    return result


def get_full_relation(name):
    sql = f"SELECT * FROM {name};"
    return run_sql(sql)


def is_admin(username):
    sql = "SELECT is_admin from USERS WHERE username=%s"
    result = run_sql(sql, (username,))
    if result:
        return result[0][0]
    return False