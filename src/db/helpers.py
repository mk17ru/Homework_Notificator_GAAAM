from src.db.connection import conn

def get_full_relation(name):
    sql = f"SELECT * FROM {name};"

    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()
    return result