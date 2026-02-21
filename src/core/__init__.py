from init import app, log
log.info("Importing subapp v1")
from handlers.v1.utils.subapp import v1


app.add_subapp("/v1", v1)
log.info("Attached subapp v1")