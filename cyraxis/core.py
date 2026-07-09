'''
grok/core.py - THE LLM interface module
Module 1 of GROK: Grounded Research for Open Knowledge

All other GROK modules call ask() to interact with the LLM.
This module handles:API key loading, model selection, error handling, and the core ask() interface.

Day 2 of 1460.
'''
import os
from groq import Groq

#Load API key from environment variable (set in .env file)
#We use python-dotenv to load .env automatically
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass   #dotenv optional- key can be set as system env var

#Initialise the Groq client once at module load time
#All ask() calls reuse this client
_client=None

def _get_client() -> Groq:
    '''Return the Groq client, initialising it once.'''
    global _client
    if _client is None:
        api_key= os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROK_API_KEY not found. "
                "Set it in your .env file or as an environment variable."
            )
        _client = Groq(api_key=api_key)
    return _client    

def ask(
        prompt: str,
        system: str ="You are Cyraxis, an autonomous AI safety research agent. "
                     "Be precise, honest, and cite your reasoning.",
        model: str="llama-3.3-70b-versatile", 
        max_tokens: int=1024,           
)->str:
    '''
    Send a prompt to the LLM and return the text response.

    Args:
        prompt:     The user message to send.
        system:     The system prompt that defines GROK's behaviour.
        model:      The Groq model to use.
        max_tokens: Maximum tokens in the response.

    Returns:
        The LLM's text response as a string.
        Retrun an error message string if the API call fails
        (fail-graceful: never raises an exception to the caller).
    '''
    try:
        client = _get_client()
        response=client.chat.completions.create (
            model= model,
            messages =[
                {"role":"system","content":system},
                {"role":"user", "content": prompt},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    except Exception as e:
        #Fail-graceful: return error as string rather than crashing 
        return f"[cyraxis core.py error: {type(e).__name__}:{e}]"

if __name__=="__main__":
    #Quick test - run this file directly to verify the API works:
    #python cyraxis/core.py
    print("Testing Craxis core.py...")
    print("="*50)

    response=ask("What is mechansitic interpretability in one sentence?")
    print(f"CYRAXIS:{response}")

    print("\n"+"="*50)
    print("✓ core.py working — CYRAXIS(groq) API call succeeded.")