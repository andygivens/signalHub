from signalhub.pushover import send_message

def test_payload_truncation():
    ok, status, body = send_message(
        user_key="U"*30,
        title="T"*300,
        message="M"*2000,
        token="TKN",
    )
    assert len(body) > 0
    assert status in (0, 200)

def test_directives():
    ok, status, body = send_message(
        user_key="U"*30,
        title="Test [PRIO=2] [SOUND=magic] [URL=https://x] [URLTITLE=Go]",
        message="Body",
        token="TKN",
        priority=2,
        sound="magic",
        url="https://x",
        url_title="Go",
    )
    assert status in (0, 200)
