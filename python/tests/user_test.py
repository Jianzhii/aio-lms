from app import app


def test_get_all_user():    
    # Create a test client using the Flask application configured for testing
    with app.test_client() as test_client:
        response = test_client.get('/test')
        print(response)
        assert response.status_code == 200

def test_get_role():
    with app.test_client() as test_client:
        response = test_client.get('/user_role')
        print(response)
        assert response.status_code == 200

def test_gesponst_trainer():
    with app.test_client() as test_client:
        response = test_client.get('/all_trainer')
        print(response)
        assert ree.status_code == 200