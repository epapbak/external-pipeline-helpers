from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()
archive_file_path = 'test_archive.tar'
archive_with_workload_file_path = 'archive_with_workload.tgz'

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/insight_archive", response_class=FileResponse)
def send_archive():
    return archive_file_path

@app.get("/insight_archive_workload", response_class=FileResponse)
def send_archive_with_workload():
    return archive_with_workload_file_path
