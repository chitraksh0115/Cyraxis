"""
cyraxis/memory.py — conversation memory module
Module 3 of CYRAXIS: Grounded Research for Open Knowledge

ask_with_memory() maintains a running conversation history.
Each call appends to the history and sends the full history
to the LLM — so GROK remembers earlier turns.

WHY THIS MATTERS:
Without memory: every ask() call is stateless.
CYRAXIS treats each prompt as the first message it has ever seen.
With memory: GROK knows "earlier you said X, so now I understand Y."
This is how every real AI assistant (ChatGPT, Claude) works.

THE HISTORY FORMAT:
The Groq API (like all OpenAI-compatible APIs) expects messages
as a list of dicts: [{"role": "user", "content": "..."}, ...]
Roles: "system" (instructions), "user" (human turn), "assistant" (AI turn)
We maintain this list across calls and pass it every time.

"""

from cyraxis.core import ask, _get_client
import os


def create_conversation(system_prompt: str = None) -> list:
    """
    Create a new conversation history list.
    Optionally include a system message as the first entry.

    Returns:
        list: Empty conversation history, or with system message.
    """
    if system_prompt is None:
        system_prompt = (
            "You are GROK, an autonomous AI safety research agent. "
            "You remember everything said earlier in this conversation "
            "and use that context in your responses."
        )
    return [{"role": "system", "content": system_prompt}]


def ask_with_memory(
    prompt: str,
    history: list,
    model: str = "llama-3.1-8b-instant",
    max_tokens: int = 1024,
) -> tuple[str, list]:
    """
    Send a prompt to the LLM with full conversation history.

    Args:
        prompt:  The new user message.
        history: The conversation history list (from create_conversation
                 or a previous ask_with_memory call).
        model:   The model to use.
        max_tokens: Maximum response tokens.

    Returns:
        tuple: (response_text, updated_history)
        The updated history includes this prompt and response,
        ready to pass into the next ask_with_memory call.

    Design: fail-graceful — on error, returns error string
    and history with only the user message appended
    (so the conversation can continue).
    """
    # Add the new user message to history
    history = history + [{"role": "user", "content": prompt}]

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=model,
            messages=history,
            max_tokens=max_tokens,
        )
        reply = response.choices[0].message.content

        # Add assistant reply to history
        history = history + [{"role": "assistant", "content": reply}]
        return reply, history

    except Exception as e:
        error_msg = f"[CYRAXIS memory.py error: {type(e).__name__}: {e}]"
        return error_msg, history


def get_history_summary(history: list) -> str:
    """
    Return a readable summary of the conversation history.
    Useful for debugging and for the nightly audit module.
    """
    lines = []
    for msg in history:
        role = msg["role"].upper()
        content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
        if role != "SYSTEM":   # skip system prompt in summary
            lines.append(f"[{role}]: {content}")
    return "\n".join(lines) if lines else "(empty conversation)"


if __name__ == "__main__":
    print("Testing grok/memory.py — multi-turn conversation")
    print("=" * 55)

    # Start a new conversation
    history = create_conversation()

    # Turn 1
    reply, history = ask_with_memory(
        "My name is Chitraksh and I am studying AI safety.",
        history
    )
    print(f"Turn 1\nUser: My name is Chitraksh...\nGROK: {reply[:120]}...\n")

    # Turn 2 — does CYRAXIS remember the name?
    reply, history = ask_with_memory(
        "What is my name and what am I studying?",
        history
    )
    print(f"Turn 2\nUser: What is my name and what am I studying?")
    print(f"CYRAXIS: {reply}\n")

    # Turn 3 — build on earlier context
    reply, history = ask_with_memory(
        "What would be a good research project for someone with my background?",
        history
    )
    print(f"Turn 3\nUser: What would be a good research project...")
    print(f"CYRAXIS: {reply[:200]}...\n")

    # Show history summary
    print("=" * 55)
    print("Conversation history summary:")
    print(get_history_summary(history))
    print(f"\nTotal messages in history: {len(history)}")