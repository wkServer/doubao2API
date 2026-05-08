import unittest

from backend.core.account_pool import Account
from backend.services.doubao_client import DoubaoClient


RAW_SSE_WITH_INLINE_TEXT = """id: 0
event: SSE_ACK
data: {"ack_client_meta":{"conversation_id":"0","local_conversation_id":"local_x","section_id":"0"}}

id: 1
event: STREAM_MSG_NOTIFY
data: {"content":{"content_status":100,"content_type":1,"content":"{\\"text\\":\\"OK\\",\\"text_tags\\":[]}","model_content":"OK","tts_content":"OK","ext":{}},"meta":{"message_id":"1","conversation_id":"0","section_id":"0","index_in_conv":0}}

id: 1
event: STREAM_CHUNK
data: {"message_id":"1","patch_op":[{"patch_object":1,"patch_type":3,"patch_value":{}},{"patch_object":3,"patch_type":2,"patch_value":{}},{"patch_object":50,"patch_type":1,"patch_value":{"ext":{"is_finish":"1"}}}]}
"""


class _DummyPool:
    def __init__(self):
        self.success_called = False
        self.released = False

    def mark_success(self, acc):
        self.success_called = True

    def release(self, acc):
        self.released = True

    def mark_invalid(self, acc, reason="", error_message=""):
        raise AssertionError("mark_invalid should not be called")


class DoubaoClientStreamTests(unittest.IsolatedAsyncioTestCase):
    async def test_stream_sse_yields_delta_from_stream_msg_notify_content_json(self):
        pool = _DummyPool()
        client = DoubaoClient(engine=None, account_pool=pool)
        session = client.session_store.create_session(bot_id="7338286299411103781")
        acc = Account(sessionid="sid", name="acc")

        events = []
        async for event in client._stream_sse(RAW_SSE_WITH_INLINE_TEXT, session.session_id, acc):
            events.append(event)

        self.assertIn({"type": "delta", "content": "OK"}, events)
        self.assertEqual(events[-1], {"type": "done"})
        self.assertTrue(pool.released)


if __name__ == "__main__":
    unittest.main()
