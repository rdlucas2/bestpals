import docker
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)
docker_client_mock = MagicMock()
container_mock = MagicMock()
toggle_pause = '/toggle-pause'

@patch("main.get_docker_client", return_value=docker_client_mock)
def test_toggle_pause(mock_get_docker_client):
    # Configure the mock container based on the expected behavior
    # Initially, let's assume the container is running
    container_mock.status = "running"
    docker_client_mock.containers.get.return_value = container_mock

    # Call the endpoint
    response = client.get(toggle_pause)

    # The container was running, so we expect it to be paused
    assert response.status_code == 200
    assert response.json() == {"message": "Palworld server paused"}
    container_mock.pause.assert_called_once()

    # Reset mocks for the next part of the test
    container_mock.reset_mock()

    # Now, let's assume the container is paused
    container_mock.status = "paused"
    docker_client_mock.containers.get.return_value = container_mock

    # Call the endpoint again
    response = client.get(toggle_pause)

    # Now, the container was paused, so we expect it to be unpaused
    assert response.status_code == 200
    assert response.json() == {"message": "Palworld server unpaused"}
    container_mock.unpause.assert_called_once()


@patch("main.get_docker_client", return_value=docker_client_mock)
def test_toggle_pause_container_not_found(mock_get_docker_client):
    docker_client_mock.containers.get.side_effect = docker.errors.NotFound(
        "Container not found"
    )

    response = client.get(toggle_pause)

    assert response.status_code == 404
    assert response.json() == {"detail": "Container not found"}


@patch("main.get_docker_client", return_value=docker_client_mock)
def test_toggle_pause_docker_api_error(mock_get_docker_client):
    docker_client_mock.containers.get.side_effect = docker.errors.APIError(
        "Docker API error"
    )

    response = client.get("/toggle-pause")

    assert response.status_code == 500
    assert "Docker API error" in response.json()["detail"]
