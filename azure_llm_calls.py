import json

class AzureCall:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

    def complete_chat(self, prompt, temperature=0):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    def make_function_call(self, prompt, function, function_name):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Donot put any empty string value for the provided json."},
                {"role": "user", "content": prompt}
            ],
            functions=function,
            function_call={"name": function_name}
        )
        return json.loads(response.choices[0].message.function_call.arguments)

    def get_conversation_unstructured(self, summary, name1, name2):
        PROMPT = f'''
        Given is a summary of a YouTube video.

        
        ::::::::::::::summary::::::::::::::::

        {summary}

        :::::::::::::::::::::::::::::::::::::

        Now create a real-world conversation between two people whose names are {name1} and {name2}, where they talk about the video whose summary I have provided you above.

        Note {name1} and {name2} aren't part of the video but just talk about it.

        Output me in this pattern: 

        :::::::::conversation::::::::::

        .............here give me the conversation... where it's dialogue followed after name.    

        :::::::::::::::::::::::::::::::

        Note the conversation must be between these two people only.

        Both {name1} and {name2} should take turns in the conversation.
        '''
        return self.complete_chat(PROMPT)

    def get_conversation_structured(self, conversation_unstructured):
        prompt = (f'''Structure the below context:

        :::::::::context::::::

        {conversation_unstructured}

        :::::::::::::::::::::::::::

        Convert this into a structured JSON format with the key 'dialogues'.
        Each entry should be a dictionary with 'name' and 'dialogue' keys.

        Use the provided data as it is, do not make up anything.

        Make sure the order of each dialogue is maintained.
        ''')
        function_name = 'structured_conversation'
        extract_all_structured_conversation = [
            {
                'name': function_name,
                'description': """
                Converts the unstructured conversation into a structured dialogue list based on the provided schema.
                """,
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'dialogues': {
                            'type': 'array',
                            'description': 'List of structured dialogues',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {
                                        'type': 'string',
                                        'description': 'The name of the speaker.'
                                    },
                                    'dialogue': {
                                        'type': 'string',
                                        'description': 'The dialogue said by the speaker.'
                                    },
                                },
                                'required': ['name', 'dialogue'],
                            }
                        }
                    },
                    'required': ['dialogues'],
                }
            }
        ]
        response = self.make_function_call(prompt, extract_all_structured_conversation, function_name)
        return response
