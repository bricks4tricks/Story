import pathlib


def test_topic_buttons_present():
    admin_html = pathlib.Path('templates/iygighukijh.html').read_text()
    assert ".closest('.edit-topic-btn')" in admin_html
    assert ".closest('.delete-topic-btn')" in admin_html

