"""
Various bits of code used in various testing places.
"""


def get_and_check_content(client, url, code=200, includes=(), excludes=()):
    """
    Send a get to the client with the url, check that all the values are in the returned HTML.
    """
    rv = client.get(url)
    assert rv is not None
    assert rv.status_code == code, '######## Status code was {}, expected {}'.format(rv.status_code, code)
    rvd = rv.get_data().decode('utf-8')
    for item in includes:
        assert item in rvd, '######## `{}` not in\n{}'.format(item, rvd)
    for item in excludes:
        assert item not in rvd, '######## `{}` in\n{}'.format(item, rvd)
    return rvd


def post_and_check_content(client, url, data, content_type=None, code=200, includes=(), excludes=(), follow_redirects=False):
    """
    Send a post to the client with the url and data, of the content_type, and the check that all the values
    are in the returned HTML.
    """
    rv = client.post(url, data=data, content_type=content_type, follow_redirects=follow_redirects)
    assert rv is not None
    assert rv.status_code == code, '######## Status code was {}, expected {}'.format(rv.status_code, code)
    rvd = rv.get_data().decode('utf-8')
    for item in includes:
        assert item in rvd, '######## `{}` not in\n{}'.format(item, rvd)
    for item in excludes:
        assert item not in rvd, '######## `{}` in\n{}'.format(item, rvd)
    return rvd
