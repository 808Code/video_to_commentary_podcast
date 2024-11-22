import json
from openai import AzureOpenAI
import os



def get_azure_openai_api_key():
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    if AZURE_OPENAI_API_KEY is None or AZURE_OPENAI_API_KEY == "":
        raise Exception("AZURE_OPENAI_API_KEY environment variable not set")
    return AZURE_OPENAI_API_KEY

def get_azure_api_version():
    AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
    if AZURE_API_VERSION is None or AZURE_API_VERSION == "":
        raise Exception("AZURE_API_VERSION environment variable not set")
    return AZURE_API_VERSION

def get_azure_open_api_url():
    AZURE_OPEN_API_URL = os.getenv("AZURE_OPEN_API_URL")
    if AZURE_OPEN_API_URL is None or AZURE_OPEN_API_URL == "":
        raise Exception("AZURE_OPEN_API_URL environment variable not set")
    return AZURE_OPEN_API_URL

def get_azure_deployment_name():
    AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
    if AZURE_DEPLOYMENT_NAME is None or AZURE_DEPLOYMENT_NAME == "":
        raise Exception("AZURE_DEPLOYMENT_NAME environment variable not set")
    return AZURE_DEPLOYMENT_NAME

client = AzureOpenAI(
    api_key= get_azure_openai_api_key(),
    api_version=get_azure_api_version(),
    azure_endpoint=get_azure_open_api_url(),
    azure_deployment=get_azure_deployment_name()
)


def complete_chat(prompt , temperature = 0):
    response = client.chat.completions.create(
        #TODO Allow Any model type.
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
            {"role": "user", "content": prompt}
        ],
         temperature = temperature,
    )
    return response.choices[0].message.content



def make_function_call(prompt, function, function_name):
    response = client.chat.completions.create(
        #TODO Allow Any model type.
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Donot put any empty string value for the provided json."},
            {"role": "user", "content": prompt}
        ],
        functions=function,
        function_call = {"name":  function_name}
    )
    return json.loads(response.choices[0].message.function_call.arguments)


def get_conversation_unstructured(summary, name1, name2):
    PROMPT = f'''
    Given is a summary of an youtube video.

    
    ::::::::::::::summary::::::::::::::::

    {summary}

    :::::::::::::::::::::::::::::::::::::

    Now create a real world conversation between two people whose name are {name1} and {name2} where they talk about the video whose summary i have provided you above.

    Note {name1} and {name2} aren't part of the video but just talk about it.

    output me in this pattern : 

    :::::::::conversation::::::::::

    .............here give me the conversation... where its dialogue follwed after name.    

    :::::::::::::::::::::::::::::::
    '''
   
    return complete_chat(PROMPT)



def get_conversation_structured(conversation_unstructured):
    
    prompt = (f'''Structure the below context:

    :::::::::context::::::

    {conversation_unstructured}

    :::::::::::::::::::::::::::

    Convert this into a structured JSON format with the key 'dialogues'.
    Each entry should be a dictionary with 'name' and 'dialogue' keys.

    Use the provided data as it is, do not make up anything.

    Make sure order of each dialogue is maintained.
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

    response = make_function_call(prompt, extract_all_structured_conversation, function_name)
    return response

