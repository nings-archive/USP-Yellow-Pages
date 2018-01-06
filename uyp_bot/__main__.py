import database

db = database.Connection()
db.add_mod('UQF2101I', '2018-02-06', '2018-03-06', '111', 't.me/111')
print(db.get_mod('UQF2101I'))
