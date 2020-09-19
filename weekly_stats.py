from pyyoutube import Api
import sys
sys.path.append("./chat-replay-downloader")
from chat_replay_downloader import get_chat_replay, get_youtube_messages
import vtuber_list
import csv
import dateutil.parser
import datetime
import pytz
import re
import emoji
import pandas as pd
from datetime import timedelta
from collections import Counter

api = Api(api_key='GOOGLE_API_KEY_HERE')

NAMES=['AZki', 'Miko', 'Roboco', 'Sora', 'Suisei', 'Mel', 'Haato', 'Fubuki', 'Matsuri', 'Aki', 'Shion', 'Aqua',
    'Ayame', 'Choco', 'ChocoSub', 'Subaru', 'Korone', 'Mio', 'Okayu', 'Noel', 'Rushia', 'Pekora', 'Flare', 'Marine',
    'Luna', 'Coco', 'Watame', 'Kanata', 'Towa', 'Lamy', 'Nene', 'Botan', 'Polka', 'Calli', 'Kiara', 'Ina', 'Gura',
    'Amelia']

PLAYLIST_IDS=['UU0TXe_LYZ4scaW2XMyi5_kw', 'UU-hM6YJuNYVAmUWxeIr9FeA', 'UUDqI2jOz0weumE8s7paEk6g', 'UUp6993wxpyDPHUpavwDFqgg',
    'UU5CwaMl1eIgY8h02uZw7u8A', 'UUD8HOxPs4Xvsm8H0ZxXGiBw', 'UU1CfXB_kRs3C-zaeTG3oGyg', 'UUdn5BQ06XqgXoAxIhbqw5Rg',
    'UUQ0UDLQCjY0rmuxCDE38FGg', 'UUFTLzh12_nrtzqBPsTCqenA', 'UUXTpFs_3PqI41qX2d9tL2Rw', 'UU1opHUrw8rvnsadT-iGp7Cg',
    'UU7fk0CB07ly8oSl0aqKkqFg', 'UU1suqwovbL1kzsoaZgFZLKg', 'UUp3tgHXw_HI0QMk1K8qh3gQ', 'UUvzGlP9oQwU--Y0r9id_jnA',
    'UUhAnqc_AY5_I3Px5dig3X1Q', 'UUp-5t9SrOQwXMU7iIjQfARg', 'UUvaTdHTWBGv3MKj3KVqJVCw', 'UUdyqAaZDKHXg4Ahi7VENThQ',
    'UUl_gCybOJRIgOXw6Qb4qJzQ', 'UU1DCedRgGHBdm81E1llLhOQ', 'UUvInZx9h3jC2JzsIzoOebWg', 'UUCzUftO8KOVkV4wQG1vkUvg',
    'UUa9Y57gfeY0Zro_noHRVrnw', 'UUS9uQI-jC3DE0L4IpXyvr6w', 'UUqm3BQLlJfvkTsX_hvm0UmA', 'UUZlDXzGoo7d44bwdNObFacg',
    'UU1uv2Oq6kNxgATlCiez59hw', 'UUFKOVgVbGmX65RxO3EtH3iw', 'UUAWSyEs_Io8MtpY3m-zqILA', 'UUUKD-uaobj9jiqB-VXt71mA',
    'UUK9V2B22uJYu3N7eR_BT9QA', 'UUL_qhgtOy0dy1Agp8vkySQg', 'UUHsx4Hqa-1ORjQTh9TYDhww', 'UUMwGHR0BTZuLsmjY_NT5Pwg',
    'UUoSrY_IQQVpmIRZ9Xf-y93g', 'UUyl1z3jo3XHR1riLFKG5UAg']

playlists={}
pl_idx = 0
name_list = vtuber_list.vtuber_tl_list
for name in name_list:
    name_list = name_list + (name.replace(':', ' :'),)
for letter in range(ord('a'), ord('z') + 1):
    name_list = name_list + ('[' + chr(letter) + ']',)
res_dict = {}
res_count = {}
jp_regex = "[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]"

#date calcs
jp_now = datetime.datetime.now().astimezone(pytz.timezone('Asia/Tokyo'))
if jp_now.weekday() == 6:
    start_date = jp_now - timedelta(days=7)
    end_date = jp_now - timedelta(days=1)
else:
    start_date = jp_now - timedelta(days=jp_now.weekday() + 8)
    end_date = jp_now - timedelta(days=jp_now.weekday() + 2)
start_range = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=pytz.timezone("Asia/Tokyo"))
end_range = datetime.datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=pytz.timezone("Asia/Tokyo"))
date_str = start_date.strftime("%Y-%m-%d")

csv_file = open('./stream_stats_' + date_str + '.csv', 'w')
w = csv.writer(csv_file, delimiter=',')
w.writerow(['streamer', 'title', 'thumbnail', 'chat_users', 'eng_tl_msg_per_min', 'jp_tl_msg_per_min', 'not_jp_user_%', 'adj_kusa_per_min', 'humor_score', 'tete_per_usr', 'faq_count', 'marry_per_usr', 'most_kusa_tstamp', 'most_humor_tstamp', 'most_faq_tstamp', 'most_tete_tstamp'])
csv_file.flush()

def is_emoji(char):
    return char in emoji.UNICODE_EMOJI

#get video playlists from yt api
for name in NAMES:
    playlists[name] = []
    playlists[name]= api.get_playlist_items(playlist_id=PLAYLIST_IDS[pl_idx], count=50)
    pl_idx += 1

for key, val in playlists.items():
    for vid in val.items:
        pub_date = vid.contentDetails.videoPublishedAt
        pub_dt = dateutil.parser.isoparse(pub_date).astimezone(pytz.timezone("Asia/Tokyo"))

        if (start_range <= pub_dt <= end_range):
            kusa_count = 0
            tete_count = 0
            faq_count = 0
            marry_count = 0
            humor_count = 0
            all_users = []
            not_jp_user = []
            faq_list = []
            faq_list.append([timedelta(seconds=0), 0])
            kusa_list = []
            kusa_list.append([timedelta(seconds=0), 0])
            tete_list = []
            tete_list.append([timedelta(seconds=0), 0])
            humor_list = []
            humor_list.append([timedelta(seconds=0), 0])
            faq_tstamp = ""
            tete_tstamp = ""
            kusa_tstamp = ""
            
            #get chat message 
            try:
                print("Downloading chat for: " + key + " - " + vid.snippet.title)
                chat = get_youtube_messages(vid.snippet.resourceId.videoId, message_type='all')
            except:
                #write streamer, vid title only if no chat replay available
                w.writerow([key, vid.snippet.title])
                csv_file.flush()
                continue
            
            tl_count = 0
            jp_tl_count = 0
            for msg in chat:
                #check for null messages from SCs
                if msg['message']:
                    msg_lower = msg['message'].lower()
                else:
                    msg_lower = ""
                    
                #kusa counters
                kusa_old = kusa_count
                humor_old = humor_count
                kusa_count += msg_lower.count("草") + msg_lower.count("kusa") + msg_lower.count("grass") + msg_lower.count("茶葉") + msg_lower.count("_fbkcha")
                if msg_lower.endswith('w') or msg_lower.endswith('ｗ'):
                    w_count = Counter(msg_lower)['w'] + Counter(msg_lower)['ｗ']
                    kusa_count += w_count
                if kusa_old != kusa_count:
                    kusa_list.append([msg['time_in_seconds'], 1])
                    humor_count += 1
                
                    
                #tete counters
                tete_old = tete_count
                tete_count += msg_lower.count("てぇてぇ") + msg_lower.count(':_tee::_tee:') + msg_lower.count('tee tee') + msg_lower.count('teetee')
                if tete_old != tete_count:
                    tete_list.append([msg['time_in_seconds'], 1])
                    
                #faq counters
                faq_old = faq_count
                faq_count += msg_lower.count("faq")
                if faq_old != faq_count:
                    faq_list.append([msg['time_in_seconds'], 1])
                    
                #humor counter
                if "_lol" in msg_lower or "lmao" in msg_lower or "haha" in msg_lower or "🤣" in msg_lower or "😆" in msg_lower or "jaja" in msg_lower:
                    humor_count += 1
                else:
                    for sub in msg_lower.split():
                        if sub.startswith('lol'):
                            humor_count += 1
                if humor_old != humor_count:
                    humor_list.append([msg['time_in_seconds'], 1])
                    
                #marry counter
                marry_count += msg_lower.count("marry me") + msg_lower.count("cásate")
                    
                #user counters
                all_users.append(msg['author'])
                has_jp = re.search(jp_regex, msg_lower)
                is_not_null = len(msg_lower) >= 1
                if is_not_null:
                    is_not_jp = not has_jp
                    is_not_yt_emoji = not (msg_lower.startswith(':') and msg_lower.endswith(':'))
                    is_not_utf_emoji = not (is_emoji(msg_lower[0]) and is_emoji(msg_lower[-1]))
                    is_not_number = not msg_lower.isnumeric()
                    if is_not_jp and is_not_yt_emoji and is_not_utf_emoji and is_not_number:
                        not_jp_user.append(msg['author'])
                
                #live tl counter
                tl_tags = ('en:', 'eng:', 'en :', 'eng :', 'en-', 'tl:', 'tl eng:', 'tl :', 'tl eng :')
                if '[en]' in msg_lower or '[eng]' in msg_lower or '(en)' in msg_lower or '(eng)' in msg_lower or '[英訳/en]' in msg_lower or msg_lower.startswith(tl_tags) or msg_lower.startswith(name_list):
                    tl_count += 1
                    
                if '[jp]' in msg_lower or '[訳す]' in msg_lower or '【訳す】' in msg_lower or '【jp】' in msg_lower:
                    jp_tl_count += 1
                        
            #calc tl msg per minute
            end_time = chat[-1]['time_in_seconds'] / 60
            msg_per_min = round(tl_count / end_time, 2)
            jp_msg_per_min = round(jp_tl_count / end_time, 2)
            
            #user calcs
            user_count = len(set(all_users))
            not_jp_count = len(set(not_jp_user))
            not_jp_per = round((not_jp_count / user_count) * 100, 2)
            
            #kusa calc
            adj_kpm = round(((kusa_count / user_count) / end_time) * 1000, 2)
            
            #tete calc
            tete_user = round((tete_count / user_count) * 1000, 2)
            
            #humor calc 
            humor_score = round(((humor_count / user_count) / end_time) * 1000, 2)
            
            #marry calc
            marry_score = ((marry_count / not_jp_count) / end_time) * 1000
            
            #dataframe stuff for finding groupings
            faq_df = pd.DataFrame(faq_list, columns=['tstamp', 'count'])
            kusa_df = pd.DataFrame(kusa_list, columns=['tstamp', 'count'])
            tete_df = pd.DataFrame(tete_list, columns=['tstamp', 'count'])
            humor_df = pd.DataFrame(humor_list, columns=['tstamp', 'count'])
            kusa_df = kusa_df.set_index(['tstamp'])
            faq_df = faq_df.set_index(['tstamp'])
            tete_df = tete_df.set_index(['tstamp'])
            humor_df = humor_df.set_index(['tstamp'])
            kusa_df.index = pd.to_timedelta(kusa_df.index, unit='s')
            faq_df.index = pd.to_timedelta(faq_df.index, unit='s')
            tete_df.index = pd.to_timedelta(tete_df.index, unit='s')
            humor_df.index = pd.to_timedelta(humor_df.index, unit='s')
            kusa_df = kusa_df.groupby(['tstamp']).sum()
            kusa_df = kusa_df.resample("30S").sum()
            kusa_df = kusa_df[kusa_df['count'] != 0]
            kusa_df.sort_values(by=['count'], inplace=True, ascending=False)
            faq_df = faq_df.groupby(['tstamp']).sum()
            faq_df = faq_df.resample("30S").sum()
            faq_df = faq_df[faq_df['count'] != 0]
            faq_df.sort_values(by=['count'], inplace=True, ascending=False)
            tete_df = tete_df.groupby(['tstamp']).sum()
            tete_df = tete_df.resample("30S").sum()
            tete_df = tete_df[tete_df['count'] != 0]
            tete_df.sort_values(by=['count'], inplace=True, ascending=False)
            humor_df = humor_df.groupby(['tstamp']).sum()
            humor_df = humor_df.resample("30S").sum()
            humor_df = humor_df[humor_df['count'] != 0]
            humor_df.sort_values(by=['count'], inplace=True, ascending=False)
            kusa_df.reset_index(inplace=True)
            faq_df.reset_index(inplace=True)
            tete_df.reset_index(inplace=True)
            humor_df.reset_index(inplace=True)
            
            if len(faq_df):
                faq_tstamp = str(faq_df.iloc[0][0]).split('days')[1].strip()
            if len(kusa_df):
                kusa_tstamp = str(kusa_df.iloc[0][0]).split('days')[1].strip()
            if len(tete_df):
                tete_tstamp = str(tete_df.iloc[0][0]).split('days')[1].strip()
            if len(humor_df):
                humor_tstamp = str(humor_df.iloc[0][0]).split('days')[1].strip()
            
            #write csv row
            w.writerow([key, vid.snippet.title, "https://i.ytimg.com/vi/" + vid.snippet.resourceId.videoId + "/mqdefault.jpg", str(user_count), str(msg_per_min), str(jp_msg_per_min), str(not_jp_per), str(adj_kpm), str(humor_score), str(tete_user), str(faq_count), str(marry_score), kusa_tstamp, humor_tstamp, faq_tstamp, tete_tstamp])
            csv_file.flush()