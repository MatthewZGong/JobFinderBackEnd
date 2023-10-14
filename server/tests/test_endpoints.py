
import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()


def test_hello():
    assert True


def test_update_user_info():
    data_to_send = {
        "user_id": 123,
        "data": {
            "username": "new_username",
            "email": "new_email@example.com"
        }
    }

    resp = TEST_CLIENT.put(f'/{ep.UPDATE_USER_INFO}', json=data_to_send)
    resp_json = resp.get_json()
    
    assert isinstance(resp_json, dict)
    assert 'status' in resp_json
    assert resp_json['status'] == 'success'
    assert 'message' in resp_json
    assert resp_json['message'] == f"User {data_to_send['user_id']} info updated"


def test_UpdateAvailableJobs():
    resp = TEST_CLIENT.put(f'/{ep.UPDATE_AVAILABLE_JOBS}')
    resp_json = resp.get_json()
    
    assert isinstance(resp_json, dict)
    assert 'status' in resp_json
    assert resp_json['status'] == 'success'
    assert 'message' in resp_json
    assert resp_json['message'] == "Jobs updated"


def test_keyword_search_database():
    keyword = "sample"
    resp = TEST_CLIENT.get(f'/{ep.KEYWORD_SEARCH}/{keyword}')
    resp_json = resp.get_json()

    assert isinstance(resp_json, dict)
    assert 'results' in resp_json
    assert isinstance(resp_json['results'], list)

    expected_results = [{"id": 1, "name": "Sample Data 1"},
                        {"id": 2, "name": "Sample Data 2"}]
    assert resp_json['results'] == expected_results
