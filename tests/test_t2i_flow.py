import unittest

from backend.api.v1_chat import _detect_media_intent
from backend.core.account_pool import Account
from backend.services.doubao_client import DoubaoClient


RAW_SSE_WITH_IMAGE = """id: 0
event: SSE_ACK
data: {"ack_client_meta":{"conversation_id":"0","local_conversation_id":"local_x","section_id":"0"}}

id: 1
event: STREAM_MSG_NOTIFY
data: {"content":{"content_status":100,"content_type":9999,"content_block":[{"block_type":10000,"content":{"text_block":{"text":"正在为你生成图片\\n\\n"}}}],"ext":{}},"meta":{"message_id":"1","conversation_id":"0","section_id":"0","index_in_conv":0}}

id: 1
event: STREAM_CHUNK
data: {"message_id":"1","patch_op":[{"patch_object":1,"patch_type":3,"patch_value":{"content_block":[{"block_type":2074,"content":{"creation_block":{"creations":[{"image":{"image_ori_raw":{"url":"https://example.com/cat.png"}}}]}}}]}},{"patch_object":50,"patch_type":1,"patch_value":{"ext":{"is_finish":"1"}}}]}

id: 2
event: SSE_REPLY_END
data: {"end_type":3}
"""


class _DummyImageEngine:
    def __init__(self):
        self.fetch_chat_called = False
        self.fetch_image_called = False
        self.last_prompt = None

    async def fetch_chat(self, **kwargs):
        self.fetch_chat_called = True
        yield {"status": 200, "body": ""}

    async def fetch_image(self, **kwargs):
        self.fetch_image_called = True
        self.last_prompt = kwargs.get("prompt")
        yield {"status": 200, "body": RAW_SSE_WITH_IMAGE}


class _DummyAccountPool:
    def __init__(self):
        self.acc = Account(sessionid="sid", name="acc")
        self.released = False

    async def acquire_wait(self, timeout=60, exclude=None):
        return self.acc

    def release(self, acc):
        self.released = True

    def mark_success(self, acc):
        pass

    def mark_invalid(self, acc, reason="", error_message=""):
        raise AssertionError("mark_invalid should not be called")

    def mark_rate_limited(self, acc, error_message=""):
        raise AssertionError("mark_rate_limited should not be called")


class MediaIntentTests(unittest.TestCase):
    def test_detect_media_intent_matches_draw_an_animal_phrase(self):
        messages = [{"role": "user", "content": "画一只可爱的猫咪"}]

        self.assertEqual(_detect_media_intent(messages), "t2i")


class DoubaoClientT2ITests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_uses_image_engine_for_t2i_and_returns_image_urls(self):
        engine = _DummyImageEngine()
        pool = _DummyAccountPool()
        client = DoubaoClient(engine=engine, account_pool=pool)

        result, acc, session_id = await client.chat(
            text="画一只可爱的猫咪",
            bot_id="7338286299411103781",
            media_intent="t2i",
        )

        self.assertTrue(engine.fetch_image_called)
        self.assertFalse(engine.fetch_chat_called)
        self.assertEqual(engine.last_prompt, "画一只可爱的猫咪")
        self.assertEqual(result.image_urls, ["https://example.com/cat.png"])
        self.assertEqual(acc.sessionid, "sid")
        self.assertTrue(session_id)


if __name__ == "__main__":
    unittest.main()
