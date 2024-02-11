from fastapi import FastAPI, HTTPException
import docker

app = FastAPI()

def get_docker_client():
    return docker.from_env()

@app.get("/toggle-pause")
def toggle_pause_palworld():
    client = get_docker_client()
    try:
        container = client.containers.get("palworld-dedicated-server")
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
