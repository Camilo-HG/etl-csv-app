from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from db.connection import engine
from db.connection import SessionDep  # noqa: F401
from db.models import Departments  # noqa: F401
from db.models import HiredEmployees  # noqa: F401
from db.models import Jobs  # noqa: F401


def create_db_and_tables():
    """
    This function uses SQLModel.metadata.create_all(engine)
    to create the tables for all the table models.

    Notes:
        According to SQLModel docs, you have to import the module
        that has the models before calling SQLModel.metadata.create_all().

        When you import SQLModel alone, Python doesn't execute all the code
        creating the classes inheriting from it, so SQLModel.metadata is still empty.

        But if you import the models before calling SQLModel.metadata.create_all(),
        Python executes all the code creating the classes inheriting from SQLModel
        and registering them in the SQLModel.metadata, and then
        SQLModel.metadata.create_all() will work as charm.
    """
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    lifespan function.

    Used to define startup and shutdown logic.

    More info: https://fastapi.tiangolo.com/advanced/events/#async-context-manager
    """
    # Everything before the yield, will be executed at startup,
    # i.e. before the application starts.
    create_db_and_tables()
    yield
    # Everything after the yield, will be executed at shutdown,
    # i.e. after the application has finished.
    pass


# Define the app
app = FastAPI(lifespan=lifespan)


# Define Routes
@app.get("/")
async def root():
    return {"message": "Hello World"}
