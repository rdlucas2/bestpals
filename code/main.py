from fastapi import FastAPI, HTTPException
import docker
import subprocess

app = FastAPI()


def get_docker_client():
    return docker.from_env()


palworld_container_name = "palworld-dedicated-server"


@app.get("/dashboard")
def get_dashboard():
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
    try:
        result = subprocess.run(
            ["docker", "exec", palworld_container_name, "rconcli", "showplayers"],
            capture_output=True,
            text=True,
            check=True,
        )
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/server-info")
def server_info():
    try:
        result = subprocess.run(
            ["docker", "exec", palworld_container_name, "rconcli", "info"],
            capture_output=True,
            text=True,
            check=True,
        )
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/save-game")
def save_game():
    try:
        result = subprocess.run(
            ["docker", "exec", palworld_container_name, "rconcli", "save"],
            capture_output=True,
            text=True,
            check=True,
        )
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/create-backup")
def create_backup():
    try:
        result = subprocess.run(
            ["docker", "exec", palworld_container_name, "backup"],
            capture_output=True,
            text=True,
            check=True,
        )
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/list-backups")
def list_backups():
    try:
        result = subprocess.run(
            ["docker", "exec", palworld_container_name, "backup", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/clean-backups/{days}")
def clean_backups(days: int):
    try:
        result = subprocess.run(
            ["docker", "exec", palworld_container_name, "backup_clean", str(days)],
            capture_output=True,
            text=True,
            check=True,
        )
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
