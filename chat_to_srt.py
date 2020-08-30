import pysrt
import sys
import re
import csv
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('log_file', help='YouTube chat log file (CSV)')
parser.add_argument('srt_file', help='SRT output path')
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

lang_dict = {'en': ['[en]', '[eng]', 'en:', 'eng:', '(en)', '(eng)'],
            'es': ['[es]', '[esp]', 'es:', 'esp:', '(es)', '(esp)'],
            'ru': ['[ru]', '(ru)', 'ru:']}

with open(sys.argv[1]) as f:
    records = csv.DictReader(f)
    for row in records:
        msg = row['message']
        msg_lower = row['message'].lower()
        if ('[' in msg and ']' in msg) or ('(' in msg and ')' in msg) or ':' in msg:
            for tag in lang_dict[args.lang.lower()]:
                if tag in msg_lower:
                    sub = pysrt.SubRipItem()
                    sub.index = index
                    sub_start = int(row['time_in_seconds']) - args.offset
                    sub.start.seconds = sub_start
                    sub.end.seconds = sub_start + args.duration
                    sub.text = re.sub("[\[\(].*?[\]\)]", "", msg)
                    sub_file.append(sub)
                    index += 1
            
sub_file.save()
            
        

