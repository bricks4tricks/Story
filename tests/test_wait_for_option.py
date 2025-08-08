import pathlib

def test_wait_for_option_used_in_story_edit():
    admin_html = pathlib.Path('templates/iygighukijh.html').read_text()
    assert 'const waitForOption' in admin_html
    assert 'await waitForOption(storySelectors.unitSelect' in admin_html
    assert 'await waitForOption(storySelectors.topicSelect' in admin_html
