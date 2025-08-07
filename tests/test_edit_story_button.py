import pathlib

def test_edit_story_uses_closest():
    admin_html = pathlib.Path('templates/admin.html').read_text()
    assert ".closest('.edit-story-btn')" in admin_html
    assert ".closest('.delete-story-btn')" in admin_html
