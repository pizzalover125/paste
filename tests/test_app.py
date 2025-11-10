import os
import tempfile
import pytest
from app import create_app


@pytest.fixture
def client(tmp_path):
    db_fd, db_path = tempfile.mkstemp(dir=tmp_path)
    os.close(db_fd)
    app = create_app({'TESTING': True, 'DATABASE': db_path})

    # initialize schema
    app.init_db()

    with app.test_client() as client:
        yield client


def test_create_and_view_paste(client):
    # create
    resp = client.post('/paste/new', data={'title': 'Hello', 'content': 'Testing paste content'}, follow_redirects=False)
    assert resp.status_code in (302, 303)
    loc = resp.headers['Location']
    assert '/paste/' in loc
    pid = loc.rsplit('/', 1)[-1]

    # view
    resp = client.get(f'/paste/{pid}')
    assert resp.status_code == 200
    assert b'Testing paste content' in resp.data
