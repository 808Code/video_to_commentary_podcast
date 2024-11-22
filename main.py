import sieve
from azure_llm_calls import get_conversation_structured, get_conversation_unstructured
import ffmpeg


def video_to_commentary_podcast(
          url :str, 
          male_name : str, 
          female_name: str, 
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



    conversation_unstructured = get_conversation_unstructured(summary, male_name, female_name)
    print("A conversation has been generated needing JSON parsing.")
    conversation_structured = get_conversation_structured(conversation_unstructured)
    print("A conversation generated has been parsed to json.")


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
            if(male_name == dialogue_object['name']):
                voice = male_voice
            dialogue_object['job'] = tts.push(voice, dialogue_object['dialogue'], reference_audio, emotion, pace, stability, style, word_timestamps)
            

    inputs = [ffmpeg.input(file_name) for file_name in [dialogue_object['job'].result().path for dialogue_object in conversation_structured['dialogues']]]
    ffmpeg.concat(*inputs, v=0, a=1).output('output.wav').run()
    return sieve.Audio(path="output.wav")