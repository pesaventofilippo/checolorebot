from pony.orm import Database, Required, Optional, Set
from pony.orm import db_session, select
from modules.helpers import regionList

db = Database("sqlite", "../checolorebot.db", create_db=True)


class Regione(db.Entity):
    name = Required(str)
    color = Required(str, default="n/a")
    updatedTime = Optional(str, default="mai")
    users = Set("User")


class User(db.Entity):
    chatId = Required(int, sql_type='BIGINT')
    status = Required(str, default="selecting_region")
    wantsNotifications = Required(bool, default=True)
    dailyUpdatesTime = Required(str, default="08:00")
    region = Optional(Regione)


# Create database
db.generate_mapping(create_tables=True)

# Create regions
with db_session:
    dbRegions = select(r.name for r in Regione)[:]
    for reg in set(regionList) - set(dbRegions):
        Regione(name=reg)
