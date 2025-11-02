"""
LiveKit Voice Agent - Quick Start
==================================
The simplest possible LiveKit voice agent to get you started.
Uses OpenRouter API with Microsoft Phi-4 Multimodal Instruct model.
Requires OpenRouter API key and Sarvam API credentials.
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, sarvam, silero
import os

# Load environment variables
load_dotenv(".env")

class Assistant(Agent):
    """Basic voice assistant with Airbnb booking capabilities."""

    def __init__(self):
        super().__init__(
            instructions="""You are a helpful and friendly Airbnb voice assistant.
            You can help users search for Airbnbs in different cities and book their stays.
            Keep your responses concise and natural, as if having a conversation."""
        )


async def entrypoint(ctx: agents.JobContext):
    """Entry point for the agent."""

    # Configure the voice pipeline with the essentials
    session = AgentSession(
        #stt=deepgram.STT(model="nova-2"),
        stt=sarvam.STT(
            language="hi-IN",
            model="saarika:v2.5",
        ),
        llm=openai.LLM.with_openrouter(
            model="microsoft/phi-4-multimodal-instruct",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            site_url=os.getenv("OPENROUTER_SITE_URL", "https://your-site.com"),
            app_name=os.getenv("OPENROUTER_APP_NAME", "LiveKit Voice Agent"),
        ),

        tts=sarvam.TTS(
            target_language_code="hi-IN",
            speaker="anushka"
        ),
        vad=silero.VAD.load(),
    )


    # Start the session
    await session.start(
        room=ctx.room,
        agent=Assistant()
    )

    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the user warmly and ask how you can help."
    )

if __name__ == "__main__":
    # Run the agent
    # Usage:
    #   python livekit_basic_agent.py console  # Test in console (no LiveKit server needed)
    #   python livekit_basic_agent.py dev       # Development mode (requires LiveKit server)
    #   python livekit_basic_agent.py start     # Production mode (requires LiveKit server)
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))