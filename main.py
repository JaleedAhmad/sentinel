import asyncio
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not set in environment.")
        
    from orchestrator import run_attack_pipeline
    asyncio.run(run_attack_pipeline())

if __name__ == "__main__":
    main()
