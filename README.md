# Video to commentary podcast

## Overview

Video to commentary podcast app allows a user to create an AI conversation about a contents of a youtube video between two person.

## Usage

### Input: Youtube video url.


### Parameters

- `url`: 
  The URL of the YouTube video to be processed.

- `name1`:
  Name of speaker one in the conversation.

- `voice1`:
   Voice of speaker one in the conversation.

- `name2`:
  Name of speaker one in the conversation.

- `voice2`:
   Voice of speaker two in the conversation.

- `max_summary_length`: 
  The maximum length of the summary for the video that gets talked about.

## How it works
Upon receiving a youtube video link, the app first downloads the video , extracts the audio and then runs a speech-to-text process to transcribe the content. It then processes the transcript to generate the summary, using LLMs. 

The summary is further transformed into a conversational dialogue between two individuals, based on the provided names, using LLMs.

Finally, the generated conversation is converted into speech.

