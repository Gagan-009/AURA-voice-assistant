import unittest
from memory import SessionMemory, ConversationTurn


class TestSessionMemory(unittest.TestCase):
    def setUp(self):
        self.memory = SessionMemory()

    def test_initial_state(self):
        self.assertEqual(self.memory.turn_count, 0)
        self.assertEqual(self.memory.get_history(), [])
        self.assertIsNone(self.memory.get_last_turn())

    def test_add_turns(self):
        self.memory.add_turn("user", "Hello AURA")
        self.assertEqual(self.memory.turn_count, 1)

        self.memory.add_turn("agent", "Hi! How can I help you today?")
        self.assertEqual(self.memory.turn_count, 2)

        last = self.memory.get_last_turn()
        self.assertIsNotNone(last)
        self.assertEqual(last["role"], "agent")
        self.assertEqual(last["text"], "Hi! How can I help you today?")

    def test_recent_context(self):
        self.memory.add_turn("user", "What is the weather?")
        self.memory.add_turn("agent", "It is sunny.")
        context = self.memory.get_recent_context()
        self.assertIn("You: What is the weather?", context)
        self.assertIn("AURA: It is sunny.", context)

    def test_summary_and_clear(self):
        self.memory.add_turn("user", "Question 1")
        self.memory.add_turn("agent", "Answer 1")
        summary = self.memory.get_session_summary()
        self.assertEqual(summary["total_turns"], 2)
        self.assertEqual(summary["user_turns"], 1)
        self.assertEqual(summary["agent_turns"], 1)

        self.memory.clear()
        self.assertEqual(self.memory.turn_count, 0)
        self.assertEqual(self.memory.get_history(), [])


if __name__ == "__main__":
    unittest.main()
