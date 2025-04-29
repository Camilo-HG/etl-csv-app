from contextlib import asynccontextmanager
from io import StringIO

import pandas as pd
from fastapi import FastAPI
from fastapi import UploadFile
from sqlmodel import select
from sqlmodel import SQLModel

from db.connection import engine
from db.connection import SessionDep
from db.models import Department
from db.models import HiredEmployee
from db.models import Job


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


@app.post("/migrate/departments")
async def migrate_departments(departments_file: UploadFile, session: SessionDep) -> list[Department]:
    """
    Endpoint to migrate departments from a departments.csv file.
    """
    contents = await departments_file.read()

    # Convert bytes to string and then to DataFrame
    data_str = contents.decode("utf-8")

    # The file comes without header
    # Set the header manually
    columns = ["department"]
    df = pd.read_csv(StringIO(data_str), header=None, names=columns)

    for row in df.itertuples():
        department = Department(department=row.department)
        session.add(department)

        # To ensure batches up to 1000 rows
        if row.Index % 1000:
            session.commit()

    # To commit uncommited transactions
    session.commit()

    # Select part of the Departments we just migrated
    departments = session.exec(select(Department).limit(20)).all()

    return departments


@app.post("/migrate/jobs")
async def migrate_jobs(jobs_file: UploadFile, session: SessionDep) -> list[Job]:
    """
    Endpoint to migrate jobs from a jobs.csv file.
    """
    contents = await jobs_file.read()

    # Convert bytes to string and then to DataFrame
    data_str = contents.decode("utf-8")

    # The file comes without header
    # Set the header manually
    columns = ["job"]
    df = pd.read_csv(StringIO(data_str), header=None, names=columns)

    for row in df.itertuples():
        job = Job(job=row.job)
        session.add(job)

        # To ensure batches up to 1000 rows
        if row.Index % 1000:
            session.commit()

    # To commit uncommited transactions
    session.commit()

    # Select part of the Jobs we just migrated
    jobs = session.exec(select(Job).limit(20)).all()

    return jobs


@app.post("/migrate/hired_employees")
async def migrate_hired_employees(
    hired_employees_file: UploadFile, session: SessionDep
) -> list[HiredEmployee]:
    """
    Endpoint to migrate HiredEmployees from a hired_employees.csv file.
    """
    contents = await hired_employees_file.read()

    # Convert bytes to string and then to DataFrame
    data_str = contents.decode("utf-8")

    # The file comes without header
    # Set the header manually
    columns = ["name", "datetime", "department_id", "job_id"]
    df = pd.read_csv(StringIO(data_str), header=None, names=columns)

    # Convert the "datetime" column to datetime
    df["datetime"] = pd.to_datetime(df["datetime"])

    # You must cast floats to integers
    # Check: https://stackoverflow.com/questions/70778065/how-to-preserve-dtype-int-when-reading-integers-with-nan-in-pandas  # noqa: E501
    df = df.astype({"department_id": "Int64", "job_id": "Int64"})
    df[["datetime", "department_id", "job_id"]] = df[["datetime", "department_id", "job_id"]].fillna(value=-1)

    # You must change pandas NaN to None
    # Check: https://stackoverflow.com/questions/14162723/replacing-pandas-or-numpy-nan-with-a-none-to-use-with-mysqldb  # noqa: E501
    # df = df.where(pd.notnull(df), None)

    for row in df.itertuples():
        hired_employee = HiredEmployee(
            name=row.name,
            # datetime=row.datetime,
            # department_id=row.department_id,
            # job_id=row.job_id
            datetime=None if row.datetime == -1 else row.datetime,
            department_id=None if row.department_id == -1 else row.department_id,
            job_id=None if row.job_id == -1 else row.job_id,
        )
        session.add(hired_employee)

        # To ensure batches up to 1000 rows
        if row.Index % 1000:
            session.commit()

    # To commit uncommited transactions
    session.commit()

    # Select part of the HiredEmployees we just migrated
    hired_employee = session.exec(select(HiredEmployee).limit(20)).all()

    return hired_employee
