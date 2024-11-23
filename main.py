from typing import Literal
from openai import AzureOpenAI
import sieve
from azure_llm_calls import AzureCall
import ffmpeg
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

def get_azure_openai_endpoint():
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    if AZURE_OPENAI_ENDPOINT is None or AZURE_OPENAI_ENDPOINT == "":
        raise Exception("AZURE_OPENAI_ENDPOINT environment variable not set")
    return AZURE_OPENAI_ENDPOINT

def get_azure_deployment_name():
    AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
    if AZURE_DEPLOYMENT_NAME is None or AZURE_DEPLOYMENT_NAME == "":
        raise Exception("AZURE_DEPLOYMENT_NAME environment variable not set")
    return AZURE_DEPLOYMENT_NAME

VoiceOptions =  Literal['elevenlabs-voice-cloning', 'cartesia-voice-cloning', 'cartesia-japanese-man-book', 'cartesia-german-conversational-woman', 'cartesia-reflective-woman', 'cartesia-ted', 'cartesia-spanish-narrator-lady', 'cartesia-friendly-reading-man', 'cartesia-sweet-lady', 'cartesia-nonfiction-man', 'cartesia-commercial-lady', 'cartesia-chinese-commercial-man', 'cartesia-british-customer-support-lady', 'cartesia-commercial-man', 'cartesia-teacher-lady', 'cartesia-friendly-sidekick', 'cartesia-tutorial-man', 'cartesia-asmr-lady', 'cartesia-chinese-woman-narrator', 'cartesia-midwestern-woman', 'cartesia-sportsman', 'cartesia-storyteller-lady', 'cartesia-french-conversational-lady', 'cartesia-french-narrator-lady', 'cartesia-french-narrator-man', 'cartesia-stern-french-man', 'cartesia-german-storyteller-man', 'cartesia-friendly-german-man', 'cartesia-german-reporter-woman', 'cartesia-german-conversation-man', 'cartesia-friendly-brazilian-man', 'cartesia-german-woman', 'cartesia-southern-belle', 'cartesia-california-girl', 'cartesia-reading-man', 'cartesia-british-reading-lady', 'cartesia-british-narration-lady', 'cartesia-wise-man', 'cartesia-announcer-man', 'cartesia-doctor-mischief', 'cartesia-anime-girl', 'cartesia-wise-guide-man', 'cartesia-the-merchant', 'cartesia-madame-mischief', 'cartesia-calm-french-woman', 'cartesia-new-york-man', 'cartesia-new-york-woman', 'cartesia-female-nurse', 'cartesia-laidback-woman', 'cartesia-alabama-male', 'cartesia-midwestern-man', 'cartesia-kentucky-man', 'cartesia-japanese-children-book', 'cartesia-kentucky-woman', 'cartesia-chinese-commercial-woman', 'cartesia-japanese-male-conversational', 'cartesia-japanese-woman-conversational', 'cartesia-brazilian-young-man', 'cartesia-spanish-narrator-man', 'cartesia-helpful-french-lady', 'cartesia-chinese-female-conversational', 'cartesia-chinese-call-center-man', 'cartesia-german-reporter-man', 'cartesia-friendly-french-man', 'cartesia-pleasant-brazilian-lady', 'cartesia-salesman', 'cartesia-customer-support-lady', 'cartesia-australian-male', 'cartesia-australian-woman', 'cartesia-indian-customer-support-lady', 'cartesia-indian-lady', 'cartesia-confident-british-man', 'cartesia-middle-eastern-woman', 'cartesia-yogaman', 'cartesia-movieman', 'cartesia-wizardman', 'cartesia-southern-man', 'cartesia-pilot-over-intercom', 'cartesia-reading-lady', 'cartesia-classy-british-man', 'cartesia-newsman', 'cartesia-child', 'cartesia-maria', 'cartesia-barbershop-man', 'cartesia-meditation-lady', 'cartesia-newslady', 'cartesia-1920’s-radioman', 'cartesia-british-lady', 'cartesia-hannah', 'cartesia-wise-lady', 'cartesia-calm-lady', 'cartesia-indian-man', 'cartesia-princess', 'elevenlabs-rachel', 'elevenlabs-alberto', 'elevenlabs-gabriela', 'elevenlabs-darine', 'elevenlabs-maxime', 'openai-alloy', 'openai-echo', 'openai-onyx', 'openai-nova', 'openai-shimmer', 'openai-alloy-hd', 'openai-echo-hd', 'openai-onyx-hd', 'openai-nova-hd', 'openai-shimmer-hd']         

metadata = sieve.Metadata(
    title="Youtube video to conversational podcast",
    description="Given a youtube video url generate a conversational podcast.",
    tags=["Video", "Audio"],
    image=sieve.Image(
        path="logo.jpg"
    ),
    readme=open("README.md", "r").read(),
)
@sieve.function(
    name="video_to_commentary_podcast",
    python_packages=["openai", "ffmpeg-python"],
    system_packages=["ffmpeg"],
    python_version="3.10.12",
    environment_variables=[
        sieve.Env(name="AZURE_OPENAI_API_KEY", description="AZURE_OPENAI_API_KEY is the API key of your deployed model"),
        sieve.Env(name="AZURE_API_VERSION", description="AZURE_API_VERSION of your deployed endpoint."),
        sieve.Env(name="AZURE_OPENAI_ENDPOINT", description="AZURE_OPENAI_ENDPOINT is the endpoint of your deployed model."),
        sieve.Env(name="AZURE_DEPLOYMENT_NAME", description="AZURE_DEPLOYMENT_NAME of your deployed model."),
    ],
    metadata=metadata
)
def video_to_commentary_podcast(
          url :str, 
          name1 : str = 'sam',          
          voice1: VoiceOptions = 'cartesia-friendly-reading-man', 
          name2: str = 'jane', 
          voice2: VoiceOptions = 'cartesia-australian-woman',
          max_summary_length: int = 10,
          azure_model_name: str = 'gpt-4o'
    ) -> sieve.File:

    """
    Converts a YouTube video into a commentary podcast by generating dialogues from its summary 
    and synthesizing audio for each dialogue.

    :param url: YouTube video URL.
    :param name1: Name of speaker one in the conversation.
    :param voice1: Voice of speaker one in the conversation.
    :param name2: Name of speaker two in the conversation.
    :param voice2: Voice of speaker two in the conversation.
    :param max_summary_length: Maximum length of the video summary.
    :return: Generated audio file of the commentary podcast.
    """
    client = AzureOpenAI(
    api_key = get_azure_openai_api_key(),
    api_version = get_azure_api_version(),
    azure_endpoint = get_azure_openai_endpoint(),
    azure_deployment = get_azure_deployment_name()
    )
    
    azure_call = AzureCall(client, azure_model_name)

    downloader = sieve.function.get("sieve/youtube_to_mp4")
    video_link = downloader.run(url)

    file = sieve.File(path = video_link.path)
    
    analyzer_settings = {        
        "llm_backend": "gpt-4o-2024-08-06",
        "generate_chapters": False,
        "generate_highlights": False,
        "max_title_length": 10,
        "num_tags": 5,
        "denoise_audio": False,
        "use_vad": False,
        "speed_boost": True,
        "highlight_search_phrases": "Most interesting",
        "return_as_json_file": False,
    }

    video_transcript_analyzer = sieve.function.get("sieve/video_transcript_analyzer")
    output = video_transcript_analyzer.run(**analyzer_settings, file = file, max_summary_length = max_summary_length)
    for output_object in output:
        if 'summary' in output_object:
            summary = output_object['summary']
            print("Summary of the video Has been generated.")



    conversation_unstructured = azure_call.get_conversation_unstructured(summary, name1, name2)
    print("A conversation has been generated needing JSON parsing.")
    conversation_structured = azure_call.get_conversation_structured(conversation_unstructured)
    print(f"A conversation generated has been parsed to json that is of length {len(conversation_structured['dialogues'])}.")
    
    #TODO : Referece Audio Not needed here.
    tts_settings = {
        'reference_audio': sieve.File(url="https://storage.googleapis.com/sieve-prod-us-central1-public-file-upload-bucket/482b91af-e737-48ea-b76d-4bb22d77fb56/caa0664b-f530-4406-858a-99837eb4b354-input-reference_audio.wav"),
        'emotion': "normal",
        'pace': "normal",
        'stability': 0.9,
        'style': 0.4,
        'word_timestamps': False,
    }


    tts = sieve.function.get("sieve/tts")
   
    for dialogue_object in conversation_structured['dialogues']:        
            voice = voice2
            if(name1.lower() == dialogue_object['name'].lower()):
                voice = voice1
            dialogue_object['job'] = tts.push(voice, dialogue_object['dialogue'], **tts_settings)

    inputs = [ffmpeg.input(file_name) for file_name in [dialogue_object['job'].result().path for dialogue_object in conversation_structured['dialogues']]]
    
    try:
        ffmpeg.concat(*inputs, v=0, a=1).output('output.wav', acodec='pcm_s16le', format='wav', **{'y': None}).run(quiet=False, capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        if e.stderr:
            print("FFmpeg Error:", e.stderr.decode('utf-8'))
        else:
            print("FFmpeg Error: No stderr output available")
        raise
    return sieve.Audio(path="output.wav")

if __name__=="__main__":
    sieve_audio_object = video_to_commentary_podcast("https://www.youtube.com/watch?v=EW9TUqOgjmQ", "Alpha", "cartesia-german-conversational-woman", "Omega", "cartesia-commercial-man", 10, 'gpt-4o')
    print(sieve_audio_object)
