import os
import asyncio

from distributors.llm_model.consumer import llm_generate_answer


if __name__ == "__main__":
    asyncio.run(llm_generate_answer())