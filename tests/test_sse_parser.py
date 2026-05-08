import unittest

from backend.services.sse_parser import DoubaoSSEParser


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


class DoubaoSSEParserTests(unittest.TestCase):
    def test_parse_raw_sse_extracts_text_from_content_json(self):
        parser = DoubaoSSEParser()

        result = parser.parse_raw_sse(RAW_SSE_WITH_INLINE_TEXT)

        self.assertEqual(result.text, "OK")


if __name__ == "__main__":
    unittest.main()
