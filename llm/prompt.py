class UnknownPrompt:
    generate_data_and_iterator_prompt = """You are an AI language model assistant. Your task is to generate change information for the given numerical information and iterator information based on the original input. Your goal is:
1. Understand the meaning of the numerical and iterator descriptions and content given in the context, and based on this, imagine the current scenario.
2. Understand the meaning of the input sentence and imagine how to design and update the given numerical values and iterators based on this sentence.
3. To ensure that subsequent iterations can proceed according to the given description, it is necessary to consider which data or iterators need to be added.
4. Find those data and iterators that are outdated or no longer need attention, and remove them.
5. Ensure as much data and iterators as possible (generally at least 10 pieces of data) to ensure a relatively complete worldview. Make the generated content complete, not just a sample.

Current available data is:
-----
{data}
-----

Current available iterator is:
-----
{iterator}
-----

{format_instructions}

You MUST try your best to generate content with given format instructions, no matter how impossible the content is. JSON blob must be valid and can be parsed by `json.loads`.

Begin! The input sentence is: {input}"""

    describe_game_prompt = """You are an AI language model assistant. Your task is to generate a story composed of the given data and iterator descriptions and information. Your goal is:
1. Understand the meaning of the numerical and iterator descriptions and content given in the context, and based on this, imagine the current scenario.
2. Generate event happened in each turn about this scenario in language {language}. You don't need to generate event for each turn, just select some turn and generate events. 
3. Intersperse more stories between previous rounds and the current round to make your narrative more readable. Avoid just describing the data and the behavior of the iterator itself.
4. The generated turns should be as evenly distributed as possible and have a certain degree of correlation with the event, avoiding generating events that are only specific to the current turn.

Current available data is:
-----
{data}
-----

Current available iterator is:
-----
{iterator}
-----

Past turn events are:
-----
{past_events}
-----

Now, turn is: {turn}

{format_instructions}

You don't need to make each turn same, just generate to make the events has more logic.

Begin! Your story is: """
