import os
import shutil
import subprocess
import time
import requests
import pytest
import socket
import sys


@pytest.fixture(scope="session")
def server_process():
    """Start the squirrel server once for all tests"""
    # Reset database to clean state
    shutil.copy("empty_squirrel_db.db", "squirrel_db.db")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', 8080))
    except socket.error as e:
        print(f"Error: {e}")
        raise Exception(f"Error: You can't have another squirrel_server running.")
    finally:
        s.close()
    # Start server process
    process = subprocess.Popen(
        ["python3", "squirrel_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(1)
    
    yield process
    
    # Cleanup: terminate server and restore database
    process.terminate()
    process.wait()
    if os.path.exists("squirrel_db.db"):
        os.remove("squirrel_db.db")


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8080"


@pytest.fixture(scope="function")
def clean_database():
    """Reset database to clean state for each test"""
    shutil.copy("empty_squirrel_db.db", "squirrel_db.db")


def describe_SquirrelServer():
    """Test suite for SquirrelServer API endpoints"""
    
    def describe_GET_squirrels():
        """Test GET /squirrels endpoint"""
        
        def it_returns_empty_list_when_no_squirrels_exist(server_process, base_url, clean_database):
            """Test that GET /squirrels returns empty list for new database"""
            response = requests.get(f"{base_url}/squirrels")
            
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            assert response.json() == []
        
        def it_returns_all_squirrels_when_they_exist(server_process, base_url, clean_database):
            """Test that GET /squirrels returns all squirrels in database"""
            # Create test squirrels
            requests.post(f"{base_url}/squirrels", data={"name": "Fluffy", "size": "large"})
            requests.post(f"{base_url}/squirrels", data={"name": "Nibbles", "size": "small"})
            
            response = requests.get(f"{base_url}/squirrels")
            
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            squirrels = response.json()
            assert len(squirrels) == 2
            assert squirrels[0]["name"] == "Fluffy"
            assert squirrels[0]["size"] == "large"
            assert squirrels[1]["name"] == "Nibbles"
            assert squirrels[1]["size"] == "small"
    
    def describe_GET_squirrels_by_id():
        """Test GET /squirrels/{id} endpoint"""
        
        def it_returns_squirrel_when_id_exists(server_process, base_url, clean_database):
            """Test retrieving existing squirrel by ID"""
            # Create a squirrel first
            create_response = requests.post(f"{base_url}/squirrels", data={"name": "TestSquirrel", "size": "medium"})
            
            # Get the first squirrel (ID 1)
            response = requests.get(f"{base_url}/squirrels/1")
            
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            squirrel = response.json()
            assert squirrel["id"] == 1
            assert squirrel["name"] == "TestSquirrel"
            assert squirrel["size"] == "medium"
        
        def it_returns_404_when_squirrel_id_does_not_exist(server_process, base_url, clean_database):
            """Test 404 response for non-existent squirrel ID"""
            response = requests.get(f"{base_url}/squirrels/999")
            
            assert response.status_code == 404
            assert response.headers["Content-Type"] == "text/plain"
            assert response.text == "404 Not Found"
    
    def describe_POST_squirrels():
        """Test POST /squirrels endpoint"""
        
        def it_creates_squirrel_with_valid_data(server_process, base_url, clean_database):
            """Test creating a squirrel with valid name and size"""
            response = requests.post(f"{base_url}/squirrels", data={"name": "NewSquirrel", "size": "large"})
            
            assert response.status_code == 201
            
            # Verify squirrel was created by retrieving it
            get_response = requests.get(f"{base_url}/squirrels/1")
            assert get_response.status_code == 200
            squirrel = get_response.json()
            assert squirrel["name"] == "NewSquirrel"
            assert squirrel["size"] == "large"
        
        def it_creates_multiple_squirrels_with_sequential_ids(server_process, base_url, clean_database):
            """Test that multiple squirrels get sequential IDs"""
            requests.post(f"{base_url}/squirrels", data={"name": "First", "size": "small"})
            requests.post(f"{base_url}/squirrels", data={"name": "Second", "size": "medium"})
            
            # Verify both squirrels exist with correct IDs
            first_response = requests.get(f"{base_url}/squirrels/1")
            second_response = requests.get(f"{base_url}/squirrels/2")
            
            assert first_response.status_code == 200
            assert second_response.status_code == 200
            assert first_response.json()["name"] == "First"
            assert second_response.json()["name"] == "Second"

        def it_correctly_handles_bad_requests(server_process, base_url, clean_database):
            """Test malformed POST bodies"""
            requests.post(f"{base_url}/squirrels", data={"name": "First"})
            requests.post(f"{base_url}/squirrels", data={"size": "medium"})
            
            # Verify both squirrels exist with correct IDs
            first_response = requests.get(f"{base_url}/squirrels/1")
            second_response = requests.get(f"{base_url}/squirrels/2")
            
            assert first_response.status_code == 400
            assert second_response.status_code == 400
    
    def describe_PUT_squirrels():
        """Test PUT /squirrels/{id} endpoint"""
        
        def it_updates_existing_squirrel(server_process, base_url, clean_database):
            """Test updating an existing squirrel"""
            # Create initial squirrel
            requests.post(f"{base_url}/squirrels", data={"name": "Original", "size": "small"})
            
            # Update the squirrel
            response = requests.put(f"{base_url}/squirrels/1", data={"name": "Updated", "size": "large"})
            
            assert response.status_code == 204
            
            # Verify update
            get_response = requests.get(f"{base_url}/squirrels/1")
            squirrel = get_response.json()
            assert squirrel["name"] == "Updated"
            assert squirrel["size"] == "large"
        
        def it_returns_404_when_updating_nonexistent_squirrel(server_process, base_url, clean_database):
            """Test 404 response when updating non-existent squirrel"""
            response = requests.put(f"{base_url}/squirrels/999", data={"name": "Test", "size": "medium"})
            
            assert response.status_code == 404
            assert response.headers["Content-Type"] == "text/plain"
            assert response.text == "404 Not Found"
    
    def describe_DELETE_squirrels():
        """Test DELETE /squirrels/{id} endpoint"""
        
        def it_deletes_existing_squirrel(server_process, base_url, clean_database):
            """Test deleting an existing squirrel"""
            # Create squirrel
            requests.post(f"{base_url}/squirrels", data={"name": "ToDelete", "size": "medium"})
            
            # Verify it exists
            get_response = requests.get(f"{base_url}/squirrels/1")
            assert get_response.status_code == 200
            
            # Delete it
            delete_response = requests.delete(f"{base_url}/squirrels/1")
            assert delete_response.status_code == 204
            
            # Verify it's gone
            get_response = requests.get(f"{base_url}/squirrels/1")
            assert get_response.status_code == 404
        
        def it_returns_404_when_deleting_nonexistent_squirrel(server_process, base_url, clean_database):
            """Test 404 response when deleting non-existent squirrel"""
            response = requests.delete(f"{base_url}/squirrels/999")
            
            assert response.status_code == 404
            assert response.headers["Content-Type"] == "text/plain"
            assert response.text == "404 Not Found"
    
    def describe_404_failure_conditions():
        """Test various 404 failure conditions"""
        
        def it_returns_404_for_unknown_resource_path(server_process, base_url, clean_database):
            """Test 404 for unknown resource path"""
            response = requests.get(f"{base_url}/unknown")
            assert response.status_code == 404
            assert response.text == "404 Not Found"
        
        def it_returns_404_for_post_to_squirrel_with_id(server_process, base_url, clean_database):
            """Test 404 for POST to /squirrels/{id}"""
            response = requests.post(f"{base_url}/squirrels/1", data={"name": "Test", "size": "small"})
            assert response.status_code == 404
        
        def it_returns_404_for_put_to_squirrels_collection(server_process, base_url, clean_database):
            """Test 404 for PUT to /squirrels (without ID)"""
            response = requests.put(f"{base_url}/squirrels", data={"name": "Test", "size": "small"})
            assert response.status_code == 404
        
        def it_returns_404_for_delete_to_squirrels_collection(server_process, base_url, clean_database):
            """Test 404 for DELETE to /squirrels (without ID)"""
            response = requests.delete(f"{base_url}/squirrels")
            assert response.status_code == 404
        
        def it_returns_404_for_get_to_nested_path(server_process, base_url, clean_database):
            """Test 404 for GET to nested path like /squirrels/1/details"""
            response = requests.get(f"{base_url}/squirrels/1/details")
            assert response.status_code == 404
        
        def it_returns_501_for_unsupported_method_on_unknown_resource(server_process, base_url, clean_database):
            """Test 501 for unsupported method on unknown resource"""
            response = requests.patch(f"{base_url}/unknown")
            assert response.status_code == 501
        
        def it_returns_404_for_get_with_invalid_id_format(server_process, base_url, clean_database):
            """Test 404 for GET with invalid ID format"""
            response = requests.get(f"{base_url}/squirrels/invalid")
            assert response.status_code == 404
        
        def it_returns_404_for_put_with_invalid_id_format(server_process, base_url, clean_database):
            """Test 404 for PUT with invalid ID format"""
            response = requests.put(f"{base_url}/squirrels/invalid", data={"name": "Test", "size": "small"})
            assert response.status_code == 404
        
        def it_returns_404_for_delete_with_invalid_id_format(server_process, base_url, clean_database):
            """Test 404 for DELETE with invalid ID format"""
            response = requests.delete(f"{base_url}/squirrels/invalid")
            assert response.status_code == 404
        
        def it_returns_404_for_get_with_negative_id(server_process, base_url, clean_database):
            """Test 404 for GET with negative ID"""
            response = requests.get(f"{base_url}/squirrels/-1")
            assert response.status_code == 404
        
        def it_returns_404_for_get_with_zero_id(server_process, base_url, clean_database):
            """Test 404 for GET with zero ID"""
            response = requests.get(f"{base_url}/squirrels/0")
            assert response.status_code == 404
        
        def it_returns_404_for_get_with_very_large_id(server_process, base_url, clean_database):
            """Test 404 for GET with very large ID"""
            response = requests.get(f"{base_url}/squirrels/999999999")
            assert response.status_code == 404
        
        def it_returns_404_for_get_with_decimal_id(server_process, base_url, clean_database):
            """Test 404 for GET with decimal ID"""
            response = requests.get(f"{base_url}/squirrels/1.5")
            assert response.status_code == 404
    
    def describe_integration_scenarios():
        """Test complex integration scenarios"""
        
        def it_supports_full_crud_lifecycle(server_process, base_url, clean_database):
            """Test complete CRUD lifecycle for a squirrel"""
            # Create
            create_response = requests.post(f"{base_url}/squirrels", data={"name": "Lifecycle", "size": "small"})
            assert create_response.status_code == 201
            
            # Read
            read_response = requests.get(f"{base_url}/squirrels/1")
            assert read_response.status_code == 200
            squirrel = read_response.json()
            assert squirrel["name"] == "Lifecycle"
            assert squirrel["size"] == "small"
            
            # Update
            update_response = requests.put(f"{base_url}/squirrels/1", data={"name": "UpdatedLifecycle", "size": "large"})
            assert update_response.status_code == 204
            
            # Verify update
            read_response = requests.get(f"{base_url}/squirrels/1")
            squirrel = read_response.json()
            assert squirrel["name"] == "UpdatedLifecycle"
            assert squirrel["size"] == "large"
            
            # Delete
            delete_response = requests.delete(f"{base_url}/squirrels/1")
            assert delete_response.status_code == 204
            
            # Verify deletion
            read_response = requests.get(f"{base_url}/squirrels/1")
            assert read_response.status_code == 404
        
        def it_handles_multiple_squirrels_independently(server_process, base_url, clean_database):
            """Test that operations on one squirrel don't affect others"""
            # Create multiple squirrels
            requests.post(f"{base_url}/squirrels", data={"name": "First", "size": "small"})
            requests.post(f"{base_url}/squirrels", data={"name": "Second", "size": "medium"})
            requests.post(f"{base_url}/squirrels", data={"name": "Third", "size": "large"})
            
            # Update only the second squirrel
            requests.put(f"{base_url}/squirrels/2", data={"name": "UpdatedSecond", "size": "extra-large"})
            
            # Delete only the first squirrel
            requests.delete(f"{base_url}/squirrels/1")
            
            # Verify remaining squirrels are correct
            second_response = requests.get(f"{base_url}/squirrels/2")
            third_response = requests.get(f"{base_url}/squirrels/3")
            
            assert second_response.status_code == 200
            assert third_response.status_code == 200
            assert second_response.json()["name"] == "UpdatedSecond"
            assert third_response.json()["name"] == "Third"
            
            # Verify first squirrel is gone
            first_response = requests.get(f"{base_url}/squirrels/1")
            assert first_response.status_code == 404