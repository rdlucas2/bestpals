from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import docker

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_docker_client():
    return docker.from_env()


palworld_container_name = "palworld-dedicated-server"


@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/dashboard-data")
def get_dashboard_data():
    server_status = get_server_status()
    players = show_players()
    server_info = server_info()
    backups = list_backups()

    return {"dashboard": [server_status, players, server_info, backups]}


@app.get("/status")
def get_server_status():
    client = get_docker_client()
    try:
        container = client.containers.get(palworld_container_name)
        return {"status": container.status}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"Docker API error: {e.explanation}"
        )


@app.get("/toggle-pause")
def toggle_pause_palworld():
    client = get_docker_client()
    try:
        container = client.containers.get(palworld_container_name)
        if container.status == "paused":
            container.unpause()
            return {"message": "Palworld server unpaused"}
        else:
            container.pause()
            return {"message": "Palworld server paused"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"Docker API error: {e.explanation}"
        )


@app.get("/show-players")
def show_players():
    client = get_docker_client()
    try:
        exec_id = client.api.exec_create(
            "palworld-dedicated-server", cmd=["rconcli", "showplayers"]
        )
        result = client.api.exec_start(exec_id=exec_id)
        return {"output": result.decode("utf-8")}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"Docker API error: {e.explanation}"
        )


@app.get("/server-info")
def server_info():
    client = get_docker_client()
    try:
        exec_id = client.api.exec_create(
            "palworld-dedicated-server", cmd=["rconcli", "info"]
        )
        result = client.api.exec_start(exec_id=exec_id)
        return {"output": result.decode("utf-8")}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"Docker API error: {e.explanation}"
        )


@app.get("/save-game")
def save_game():
    client = get_docker_client()
    try:
        exec_id = client.api.exec_create(
            "palworld-dedicated-server", cmd=["rconcli", "save"]
        )
        result = client.api.exec_start(exec_id=exec_id)
        return {"output": result.decode("utf-8")}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"Docker API error: {e.explanation}"
        )


@app.get("/create-backup")
def create_backup():
    client = get_docker_client()
    try:
        exec_id = client.api.exec_create("palworld-dedicated-server", cmd=["backup"])
        result = client.api.exec_start(exec_id=exec_id)
        return {"output": result.decode("utf-8")}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"Docker API error: {e.explanation}"
        )


@app.get("/list-backups")
def list_backups():
    client = get_docker_client()
    try:
        exec_id = client.api.exec_create(
            "palworld-dedicated-server", cmd=["backup", "list"]
        )
        result = client.api.exec_start(exec_id=exec_id)
        return {"output": result.decode("utf-8")}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"Docker API error: {e.explanation}"
        )


@app.get("/clean-backups/{days}")
def clean_backups(days: int):
    client = get_docker_client()
    try:
        exec_id = client.api.exec_create(
            "palworld-dedicated-server", cmd=["backup_clean", str(days)]
        )
        result = client.api.exec_start(exec_id=exec_id)
        return {"output": result.decode("utf-8")}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"Docker API error: {e.explanation}"
        )
