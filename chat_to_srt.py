import pysrt
import sys
import re
import csv
import argparse
import os
import vtuber_list

parser = argparse.ArgumentParser()
parser.add_argument('log_file', help='YouTube chat log file (CSV)')
parser.add_argument('srt_file', help='SRT output path')
parser.add_argument('--colon', '-c', action='store_true', help='Use messages of the format <STREAMER: MSG>, more false positives, english only (default=False)')
parser.add_argument('--lang', '-l', default='en', help='Language (Default: en)')
parser.add_argument('--offset', '-o', default=15, help='Message negative offset, in seconds (default=15)')
parser.add_argument('--duration', '-d', default=5, help='Duration of sub, in seconds (default=5)')
args = parser.parse_args()

#open log file
log_file = open(args.log_file, 'r')

#create empty srt
if os.path.exists(args.srt_file):
    os.remove(args.srt_file)
open(args.srt_file, 'a')
sub_file = pysrt.open(args.srt_file)

index = 1
sub_count = 0

#translation tags
lang_dict = {'en': ['[en]', '[eng]', 'en:', 'eng:', '(en)', '(eng)', '[英訳/en]'],
            'es': ['[es]', '[esp]', 'es:', 'esp:', '(es)', '(esp)'],
            'ru': ['[ru]', '(ru)', 'ru:']}

#add spaced colon variants to name list
name_list = vtuber_list.vtuber_tl_list
for name in name_list:
    name_list = name_list + (name.replace(':', ' :'),)
    
#add single letter tags to name list
for letter in range(ord('a'), ord('z') + 1):
    name_list = name_list + ('[' + chr(letter) + ']',)

with open(sys.argv[1]) as f:
    records = csv.DictReader(f)
    for row in records:
        msg = row['message']
        msg_lower = row['message'].lower()
        for tag in lang_dict[args.lang.lower()]:
            if msg_lower.startswith(tag) or (msg_lower.startswith(name_list) and args.lang.lower() == 'en' and args.colon and msg_lower.count(':') < 2):
                sub = pysrt.SubRipItem()
                sub.index = index
                sub_start = int(row['time_in_seconds']) - args.offset
                sub.start.seconds = sub_start
                sub.end.seconds = sub_start + args.duration
                sub.text = msg.replace(tag, '').replace(tag.upper(), '').replace(tag.title(), '')
                if sub.text.startswith(": "):
                    sub.text = sub.text.replace(": ", "", 1)
                sub.text = sub.text.strip()
                sub_file.append(sub)
                index += 1
                sub_count += 1
                break
            
if not sub_count:
    print("No subtitles found")
else:
    print(sub_count, "subtitles generated")
    sub_file.save()
            
        

