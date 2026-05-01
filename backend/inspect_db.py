import sqlite3
from pathlib import Path

path = Path('db.sqlite3')
print('db exists', path.exists())
if not path.exists():
    raise SystemExit(1)

conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print('tables', tables)
if 'django_migrations' in tables:
    cur.execute('SELECT app, name FROM django_migrations ORDER BY app, name')
    rows = cur.fetchall()
    print('migrations_count', len(rows))
    for r in rows:
        print(r)
conn.close()
