import sys
import re
from collections import defaultdict, Counter
import csv
import emoji
import pandas as pd
from datetime import timedelta
from yattag import Doc
import i18n
import os
import vtuber_list

file = open(sys.argv[1], 'r')
info_dict = defaultdict(int)
line_count = 0
det_count = 0
time_index = 0
kusa_msg_count = 0
info_dict['tl_en'] = 0
info_dict['tl_es'] = 0
info_dict['tl_ru'] = 0
chat_names = []
not_jp_names = []
faq_list = []
faq_list.append([timedelta(seconds=0), 0])
kusa_list = []
kusa_list.append([timedelta(seconds=0), 0])
tete_list = []
tete_list.append([timedelta(seconds=0), 0])
tete_count = 0
faq_count = 0
vtuber_msg_list = []
doc, tag, text, line = Doc().ttl()
i18n.load_path.append(os.path.abspath("./i18n"))
jp_regex = "[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]"

#add spaced colon variants to name list
name_list = vtuber_list.vtuber_tl_list
for name in name_list:
    name_list = name_list + (name.replace(':', ' :'),)

def is_emoji(char):
    return char in emoji.UNICODE_EMOJI

#read file, gather stats
with open(sys.argv[1]) as f:
    records = csv.DictReader(f)
    for row in records:
        msg = row['message'].lower()
        
        #detect jp message
        has_jp = re.search(jp_regex, msg)
        if len(msg) >= 1:
            if has_jp or (msg.startswith(":") and msg.endswith(":")) or (is_emoji(msg[0]) and is_emoji(msg[-1])): 
                info_dict['jp_count'] += 1
            else:
                not_jp_names.append(row['author'])
                
        kusa_old = info_dict['kusa']
        
        #kusa counter
        info_dict['kusa'] += msg.count("草") + msg.count("kusa") + msg.count("grass") + msg.count("茶葉") + msg.count("_fbkcha")
        
        #live tl counter
        if '[en]' in msg or '[eng]' in msg or '(en)' in msg or '(eng)' in msg or msg.startswith('en:') or msg.startswith('eng:') or msg.startswith(name_list):
            info_dict['tl_en'] += 1
        elif '[es]' in msg or '[esp]' in msg or '(es)' in msg or '(esp)' in msg or msg.startswith('es:') or msg.startswith('esp:'):
            info_dict['tl_es'] += 1
        elif '[ru]' in msg or '(ru)' in msg or msg.startswith('ru:'):
            info_dict['tl_ru'] += 1
        chat_names.append(row['author'])
        
        #ending w counter
        if msg.endswith('w'):
            w_count = Counter(msg)['w']
            info_dict['kusa'] += w_count
            
        #kusa message counter, store for kusa agg
        if kusa_old != info_dict['kusa']:
            kusa_msg_count += 1
            kusa_list.append([timedelta(seconds=int(row['time_in_seconds'])), 1])
            
        #lol counter
        info_dict['lol'] += msg.count("lol") + msg.count("lmao")
        
        #faq message counter, store for faq agg
        if "faq" in msg:
            faq_list.append([timedelta(seconds=int(row['time_in_seconds'])), 1])
            faq_count += 1
            
        #tete message finder, store for tete agg
        if 'てぇてぇ' in msg:
            tete_list.append([timedelta(seconds=int(row['time_in_seconds'])), 1])
            tete_count += 1
        
        #vtuber message finder
        if row['author'] in vtuber_list.vtuber_list:
            vtuber_msg_list.append(row)
            
        line_count += 1
        time_index = row['time_in_seconds']

#post-read calculations
duration = int(time_index) / 60
not_jp = line_count - info_dict['jp_count']
chat_names = list(set(chat_names))
not_jp_names = list(set(not_jp_names))
faq_df = pd.DataFrame(faq_list, columns=['tstamp', 'count'])
kusa_df = pd.DataFrame(kusa_list, columns=['tstamp', 'count'])
tete_df = pd.DataFrame(tete_list, columns=['tstamp', 'count'])
kl_count = info_dict['kusa'] + info_dict['lol']

#generate html
with tag('html'):
    with tag('head'):
        with tag('link', rel='stylesheet', href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'):
            pass
    with tag('body'):
        with tag('div', klass='row justify-content-center'):
            with tag('div', klass='col-auto'):
                with tag('h1'):
                    text(i18n.t('chat_info.main_header'))
                with tag('h2'):
                    text(i18n.t('chat_info.gen_stats'))
                with tag('table', id='gen-stats', klass='table table-bordered'):
                    with tag('tr'):
                        line('td', i18n.t('chat_info.line_count'))
                        line('td', str(line_count))
                with tag('h2'):
                    text('KUSA Stats')
                with tag('table', id='kusa-table', klass='table table-bordered'):
                    with tag('tr'):
                        line('td', i18n.t('chat_info.kusa_count'))
                        line('td', str(info_dict['kusa']))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.kusa_per_min'))
                        line('td', str(round(info_dict['kusa']/duration, 2)))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.adj_kpm'), title=i18n.t('chat_info.akpm_tooltip'))
                        line('td', str(round(((info_dict['kusa']/len(chat_names))/duration)*1000, 2)))
                with tag('h2'):
                    text(i18n.t('chat_info.lol_stats'))
                with tag('table', id='lol-table', klass='table table-bordered'):
                    with tag('tr'):
                        line('td', i18n.t('chat_info.lol_count'))
                        line('td', str(info_dict['lol']))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.lol_per_min'))
                        line('td', str(round(info_dict['lol']/duration, 2)))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.adj_lpm'), title=i18n.t('chat_info.alpm_tooltip'))
                        line('td', str(round(((info_dict['lol']/len(chat_names))/duration)*1000, 2)))
                with tag('h2'):
                    text(i18n.t('chat_info.user_stats'))
                with tag('table', id='user-table', klass='table table-bordered'):
                    with tag('tr'):
                        line('td', i18n.t('chat_info.unique_users'))
                        line('td', str(len(chat_names)))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.non_jp_users'))
                        line('td', str(len(not_jp_names)))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.non_jp_user_per'))
                        line('td', str(round(((len(not_jp_names)/len(chat_names))*100), 2)))
                with tag('h2'):
                    text(i18n.t('chat_info.tl_stats'))
                with tag('table', id='tl-table', klass='table table-bordered'):
                    with tag('tr'):
                        line('td', i18n.t('chat_info.en_tl_count'))
                        line('td', str(info_dict['tl_en']))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.en_tl_per_min'))
                        line('td', str(round((info_dict['tl_en']/duration), 2)))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.es_tl_count'))
                        line('td', str(info_dict['tl_es']))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.es_tl_per_min'))
                        line('td', str(round((info_dict['tl_es']/duration), 2)))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.ru_tl_count'))
                        line('td', str(info_dict['tl_ru']))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.ru_tl_per_min'))
                        line('td', str(round((info_dict['tl_ru']/duration), 2)))
                with tag('h2'):
                    text(i18n.t('chat_info.misc_stats'))
                with tag('table', id='misc-table', klass='table table-bordered'):
                    with tag('tr'):
                        line('td', i18n.t('chat_info.faq_count'))
                        line('td', str(faq_count))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.tete_count'))
                        line('td', str(tete_count))
                    with tag('tr'):
                        line('td', i18n.t('chat_info.tete_score'))
                        line('td', str(round((tete_count/len(chat_names)*1000), 2)))
                if kusa_msg_count:
                    with tag('h2'):
                        text(i18n.t('chat_info.kusa_agg'))
                    kusa_df = kusa_df.groupby(['tstamp']).sum()
                    kusa_df = kusa_df.resample("30S").sum()
                    kusa_df = kusa_df[kusa_df['count'] != 0]
                    kusa_df.sort_values(by=['count'], inplace=True, ascending=False)
                    kusa_df.reset_index(inplace=True)
                    kusa_df.rename(columns={'tstamp': i18n.t('chat_info.agg_tstamp'), 'count': i18n.t('chat_info.agg_count')}, inplace=True)
                    doc.asis(kusa_df.head(10).to_html(index=False, classes=['table', 'table-bordered']))
                if faq_count > 10:
                    with tag('h2'):
                        text(i18n.t('chat_info.faq_agg'))
                    faq_df = faq_df.groupby(['tstamp']).sum()
                    faq_df = faq_df.resample("30S").sum()
                    faq_df = faq_df[faq_df['count'] != 0]
                    faq_df.sort_values(by=['count'], inplace=True, ascending=False)
                    faq_df.reset_index(inplace=True)
                    faq_df.rename(columns={'tstamp': i18n.t('chat_info.agg_tstamp'), 'count': i18n.t('chat_info.agg_count')}, inplace=True)
                    doc.asis(faq_df.head(10).to_html(index=False, classes=['table', 'table-bordered']))
                if tete_count:
                    with tag('h2'):
                        text(i18n.t('chat_info.tete_agg'))
                    tete_df = tete_df.groupby(['tstamp']).sum()
                    tete_df = tete_df.resample("30S").sum()
                    tete_df = tete_df[tete_df['count'] != 0]
                    tete_df.sort_values(by=['count'], inplace=True, ascending=False)
                    tete_df.reset_index(inplace=True)
                    tete_df.rename(columns={'tstamp': i18n.t('chat_info.agg_tstamp'), 'count': i18n.t('chat_info.agg_count')}, inplace=True)
                    doc.asis(tete_df.head(10).to_html(index=False, classes=['table', 'table-bordered']))
                if vtuber_msg_list:
                    with tag('h2'):
                        text(i18n.t('chat_info.vtuber_msgs'))
                    with tag('h3'):
                        text(i18n.t('chat_info.vt_imposter_warn'))
                    with tag('table', id='msg-table', klass='table table-bordered'):
                        with tag('tr'):
                            line('th', i18n.t('chat_info.vt_msg_timestamp'))
                            line('th', i18n.t('chat_info.vt_msg_author'))
                            line('th', i18n.t('chat_info.vt_msg'))
                        for item in vtuber_msg_list:
                            with tag('tr'):
                                line('td', item['time_text'])
                                line('td', item['author'])
                                with tag('td'):
                                    if re.search(jp_regex, item['message']):
                                        line('a', item['message'], href="https://www.deepl.com/translator#ja/" + i18n.t('chat_info.dl_lang') +
                                            "/" + item['message'])
                                    else:
                                        text(item['message'])
                    
out_file = open(sys.argv[2], 'w')
out_file.write(doc.getvalue())
out_file.close()
            