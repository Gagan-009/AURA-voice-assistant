import os
import sys
import signal
from dotenv import load_dotenv

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from memory import SessionMemory

def main():
    # Load environment variables from the .env file
    load_dotenv()

    # Retrieve required environment variables
    api_key = os.getenv("ELEVENLABS_API_KEY")
    agent_id = os.getenv("AGENT_ID")

    if not agent_id:
        print("Error: AGENT_ID environment variable is missing.", file=sys.stderr)
        print("Please set it in your .env file or environment variables.", file=sys.stderr)
        sys.exit(1)

    # In-memory session context for tracking turns and conversation flow
    memory = SessionMemory()

    # Initialize the ElevenLabs client
    client = ElevenLabs(api_key=api_key) if api_key else ElevenLabs()

    # Initialize the audio interface to use the default microphone and speakers
    print("Setting up audio interface...", flush=True)
    audio_interface = DefaultAudioInterface()

    # Configure callbacks to update session memory and display turns
    def on_user_transcript(transcript):
        memory.add_turn("user", transcript)
        print(f"\n[You] (#{memory.turn_count}): {transcript}", flush=True)

    def on_agent_response(response):
        memory.add_turn("agent", response)
        print(f"\n[AURA] (#{memory.turn_count}): {response}", flush=True)

    # Set up the conversation
    print("Initializing AURA (ElevenLabs Agent)...", flush=True)
    conversation = Conversation(
        client=client,
        agent_id=agent_id,
        requires_auth=bool(api_key),
        audio_interface=audio_interface,
        callback_user_transcript=on_user_transcript,
        callback_agent_response=on_agent_response
    )

    # Handle Ctrl+C for clean shutdown
    def signal_handler(sig, frame):
        print("\nShutting down AURA...", flush=True)
        conversation.end_session()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Start the session
        print("\nStarting conversation... (Press Ctrl+C to stop)", flush=True)
        conversation.start_session()
        
        # Keep the program running until the conversation ends
        conversation_id = conversation.wait_for_session_end()
        print(f"\nConversation ended. (Session ID: {conversation_id})", flush=True)

        # Display in-memory session summary
        summary = memory.get_session_summary()
        print(
            f"Session Summary: {summary['total_turns']} total turns "
            f"({summary['user_turns']} user, {summary['agent_turns']} AURA) "
            f"over {summary['duration_seconds']}s",
            flush=True
        )
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
