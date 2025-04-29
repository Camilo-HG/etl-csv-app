from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine
from sqlmodel import Session

# Database engine
# TODO: Provide this info using an .env file
sqlite_file_name = "db/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Using check_same_thread=False allows FastAPI to use the same
# SQLite database in different threads.
# This is necessary as one single request could use more than one thread
connect_args = {"check_same_thread": False}
# TODO: Remove echo=True when in PRD
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


# A Session is what stores the objects in memory and keeps track of any
# changes needed in the data, then it uses the engine to communicate with the database.
#
# We will create a FastAPI dependency with yield that will provide a new Session for each request.
# This is what ensures that we use a single session per request.
#
# Then we create an Annotated dependency SessionDep to simplify the rest of the code
# that will use this dependency.
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
