from openai import AzureOpenAI
import sieve
from azure_llm_calls import get_conversation_structured, get_conversation_unstructured
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
        sieve.Env(name="AZURE_OPENAI_API_KEY", description="AZURE_OPENAI_API_KEY of your AZURE account."),
        sieve.Env(name="AZURE_API_VERSION", description="AZURE_API_VERSION of your AZURE account."),
        sieve.Env(name="AZURE_OPEN_API_URL", description="AZURE_OPEN_API_URL of your AZURE account."),
        sieve.Env(name="AZURE_DEPLOYMENT_NAME", description="AZURE_DEPLOYMENT_NAME of your AZURE account."),
    ],
    metadata=metadata
)
def video_to_commentary_podcast(
          url :str, 
          male_name : str = 'sam', 
          female_name: str = 'jane', 
          max_summary_length: int = 10
    ) -> sieve.File:

    """
    Converts a YouTube video into a commentary podcast by generating dialogues from its summary 
    and synthesizing audio for each dialogue.

    :param url: YouTube video URL.
    :param male_name: Name of the male speaker in the conversation.
    :param female_name: Name of the female speaker in the conversation.
    :param max_summary_length: Maximum length of the video summary.
    :return: Generated audio file of the commentary podcast.
    """
    client = AzureOpenAI(
    api_key= get_azure_openai_api_key(),
    api_version = get_azure_api_version(),
    azure_endpoint= get_azure_open_api_url(),
    azure_deployment = get_azure_deployment_name()
    )

    downloader = sieve.function.get("sieve/youtube_to_mp4")
    video_link = downloader.run(url)

    file = sieve.File(path = video_link.path)
    
    llm_backend = "gpt-4o-2024-08-06"
    generate_chapters = False
    generate_highlights = False
    max_title_length = 10
    num_tags = 5
    denoise_audio = False
    use_vad = False
    speed_boost = True
    highlight_search_phrases = "Most interesting"
    return_as_json_file = False

    video_transcript_analyzer = sieve.function.get("sieve/video_transcript_analyzer")
    output = video_transcript_analyzer.run(file, llm_backend, generate_chapters, generate_highlights, max_summary_length, max_title_length, num_tags, denoise_audio, use_vad, speed_boost, highlight_search_phrases, return_as_json_file)

    for output_object in output:
        if 'summary' in output_object:
            summary = output_object['summary']
            print("Summary of the video Has been generated.")



    conversation_unstructured = get_conversation_unstructured(client, summary, male_name, female_name)
    print("A conversation has been generated needing JSON parsing.")
    conversation_structured = get_conversation_structured(client, conversation_unstructured)
    print(f"A conversation generated has been parsed to json that is {len(conversation_structured['dialogues'])}.")
    
    #TODO : ADD Voice selection for each person.
    male_voice = "cartesia-friendly-reading-man"
    female_voice = "cartesia-australian-woman"

    #TODO : Referece Audio Not needed here.
    reference_audio = sieve.File(url="https://storage.googleapis.com/sieve-prod-us-central1-public-file-upload-bucket/482b91af-e737-48ea-b76d-4bb22d77fb56/caa0664b-f530-4406-858a-99837eb4b354-input-reference_audio.wav")
    emotion = "normal"
    pace = "normal"
    stability = 0.9
    style = 0.4
    word_timestamps = False


    tts = sieve.function.get("sieve/tts")

   
    for dialogue_object in conversation_structured['dialogues']:        
            voice = female_voice
            if(male_name.lower() == dialogue_object['name'].lower()):
                voice = male_voice
            dialogue_object['job'] = tts.push(voice, dialogue_object['dialogue'], reference_audio, emotion, pace, stability, style, word_timestamps)

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
    sieve_audio_object = video_to_commentary_podcast("https://www.youtube.com/watch?v=EW9TUqOgjmQ", "Alpha", "Omega", 10)
    print(sieve_audio_object)
