import docker
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)
docker_client_mock = MagicMock()
container_mock = MagicMock()
toggle_route = "/toggle-pause"
status_route = "/status"
palworld_container_name = "palworld-dedicated-server"


@patch("main.get_docker_client", return_value=docker_client_mock)
def test_toggle_pause(mock_get_docker_client):
    # Configure the mock container based on the expected behavior
    # Initially, let's assume the container is running
    container_mock.status = "running"
    docker_client_mock.containers.get.return_value = container_mock

    # Call the endpoint
    response = client.get(toggle_route)

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
    response = client.get(toggle_route)

    # Now, the container was paused, so we expect it to be unpaused
    assert response.status_code == 200
    assert response.json() == {"message": "Palworld server unpaused"}
    container_mock.unpause.assert_called_once()


@patch("main.get_docker_client", return_value=docker_client_mock)
def test_toggle_pause_container_not_found(mock_get_docker_client):
    docker_client_mock.containers.get.side_effect = docker.errors.NotFound(
        "Container not found"
    )

    response = client.get(toggle_route)

    assert response.status_code == 404
    assert response.json() == {"detail": "Container not found"}


@patch("main.get_docker_client", return_value=docker_client_mock)
def test_toggle_pause_docker_api_error(mock_get_docker_client):
    docker_client_mock.containers.get.side_effect = docker.errors.APIError(
        "Docker API error"
    )

    response = client.get(toggle_route)

    assert response.status_code == 500
    assert "Docker API error" in response.json()["detail"]


@patch("main.get_docker_client", return_value=docker_client_mock)
def test_get_server_status_not_found(mock_get_docker_client):
    docker_client_mock.containers.get.side_effect = docker.errors.NotFound(
        "Container not found"
    )

    response = client.get(status_route)

    assert response.status_code == 404
    assert response.json() == {"detail": "Container not found"}


@patch("main.get_docker_client", return_value=docker_client_mock)
def test_get_server_status_docker_api_error(mock_get_docker_client):
    docker_client_mock.containers.get.side_effect = docker.errors.APIError(
        "Docker API error"
    )

    response = client.get(status_route)

    assert response.status_code == 500
    assert "Docker API error" in response.json()["detail"]


@pytest.fixture
def mock_docker_client():
    # Create a mock Docker client
    client_mock = MagicMock()
    container_mock = MagicMock()
    container_mock.status = "running"  # Set a sample status
    client_mock.containers.get.return_value = container_mock
    return client_mock


@patch("main.get_docker_client")
def test_get_server_status_success(mock_get_docker_client, mock_docker_client):
    # Configure the mock to return the mock Docker client
    mock_get_docker_client.return_value = mock_docker_client

    # Call the '/status' endpoint
    response = client.get(status_route)

    # Check that the response status code is 200 and the body contains the container's status
    assert response.status_code == 200
    assert response.json() == {"status": "running"}

    # Verify that the Docker client's containers.get method was called with the correct container name
    mock_docker_client.containers.get.assert_called_once_with(palworld_container_name)  # Adjust this to the actual variable or value used in your app
