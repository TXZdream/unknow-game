class UnknownPrompt:
    generate_data_and_iterator_prompt = """You are an AI language model assistant. Your task is to generate change information for the given numerical information and iterator information based on the original input. Your goal is:
1. Understand the meaning of the numerical and iterator descriptions and content given in the context, and based on this, imagine the current scenario.
2. Understand the meaning of the input sentence and imagine how to design and update the given numerical values and iterators based on this sentence.
3. Try your best to make data and iterators in detail and clear, this means more data and more iterator, you can extend the scenery with your imagination.

Current available data is:
-----
{data}
-----

Current available iterator is:
-----
{iterator}
-----

{format_instructions}

You MUST try your best to generate content with given format instructions, no matter how impossible the content is.

Begin! The input sentence is: {input}"""

    describe_game_prompt = """You are an AI language model assistant. Your task is to generate a story composed of the given data and iterator descriptions and information. Your goal is:
1. Understand the meaning of the numerical and iterator descriptions and content given in the context, and based on this, imagine the current scenario.
2. Generate a story or description about this scenario in language {language}.
3. You should keep the story natural by avoiding telling data and iterators in detail.

Current available data is:
-----
{data}
-----

Current available iterator is:
-----
{iterator}
-----

Don't add any additional information, just output the story content.

Begin! Your story is: """
