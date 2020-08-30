# VTuber Chat Utilities

These are a couple of utilities for working with VTuber chat logs from YouTube. 

# Setup
Ensure you have python3 and pip3 installed. Checkout or download this repo and run the following command from inside the project directory to download all dependencies:

    pip3 install -r requirements.txt

# Obtaining a Chat Log
You will first need to download a chat log using the [chat-replay-downloader](https://github.com/xenova/chat-replay-downloader). Download the log as a CSV file with all message types:

    python3 chat_replay_downloader.py <YOUTUBE_URL> -o log_file.csv -message_type all


# chat_info.py

Takes a YouTube chat log CSV file and generates an HTML report. Usage:

    python3 chat_info.py log_file.csv report.html
   
## Current Features

 - kusa (草) stats: count, per minute, and an adjusted score
 - lol stats: count, per minute, and an adjusted score
 - User stats: unique chat users, estimated number and percentage of non-JP users
 - Live translation stats: number and translations per minute, for supported languages (English, Spanish, Russian)
 - Top 10 kusa 30 second aggregate. Find 30 second increments where kusa counts are the highest. Potentially useful for finding clipable material
 - Top 10 FAQ 30 second aggregate (displays only when FAQs are detected).
 - Chat messages from a list of known VTubers. Japanese messages are hyperlinked to the DeepL translation. Caution: This may show impostors.
 - i18n support, see the i18n folder
 
# chat_to_srt.py
Generate an SRT file from the YouTube chat log using detected live translations. The SRT can be used with YouTube using [this Chrome extension](https://chrome.google.com/webstore/detail/subtitles-for-youtube/oanhbddbfkjaphdibnebkklpplclomal). Basic usage:

    python3 chat_to_srt.py log_file.csv subs.srt
  
  ## Options
 
 - --lang, -l   Set language (default: en) (supported: en, es, ru)
 - --offset, -o  Negative offset of sub from original chat message (default: 15s)
 - --duration, -d  Time the sub will remain on screen (default: 5s)
