##shortcut just run python dbinit.py in terminal the db will automatically created

from website import db, create_app
app=create_app()
ctx=app.app_context()
ctx.push()
db.create_all()
quit()