class UnknownPrompt:
    generate_data_and_iterator_prompt = """You are an AI language model assistant. Your task is to generate change information for the given numerical information and iterator information based on the original input. Your goal is:
1. Understand the meaning of the numerical and iterator descriptions and content given in the context, and based on this, imagine the current scenario.
2. Understand the meaning of the input sentence and imagine how to design and update the given numerical values and iterators based on this sentence.

Current data is:
-----
{data}
-----

Current iterator is:
-----
{iterator}
-----

{format_instructions}

Begin! The input sentence is: {input}"""
