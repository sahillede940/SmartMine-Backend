import sqlite3

db = sqlite3.connect('crop_production.db')

con = db.cursor()

# Total 10 crop with highest production

con.execute("SELECT crop, SUM(production) FROM crop_production GROUP BY crop ORDER BY SUM(production) DESC LIMIT 10")

print(con.fetchall())