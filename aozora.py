import aozoracli # From here: https://github.com/aozorahack/aozora-cli/
import aozoracli.client
import json
import re
import numpy as np

def get_kanji():
    '''Sort list of kanji from WK API into levels (downloaded separately)'''
    kanji_level_map = {}
    lkeys = range(1,61)
    level_kanji_map = dict(zip(lkeys, ([] for _ in lkeys)))

    with open('/Users/Emily/Desktop/Aozora/0120.json') as f:
        data = json.loads(f.read())
    for i in data["data"]:
        kanji_level_map[i['data']['characters']] = i['data']['level']
        level_kanji_map[int(i['data']['level'])].append(i['data']['characters'])
    f.close()

    with open('/Users/Emily/Desktop/Aozora/2140.json') as f:
        data = json.loads(f.read())
    for i in data["data"]:
        kanji_level_map[i['data']['characters']] = i['data']['level']
        level_kanji_map[int(i['data']['level'])].append(i['data']['characters'])
    f.close()

    with open('/Users/Emily/Desktop/Aozora/4160.json') as f:
        data = json.loads(f.read())
    for i in data["data"]:
        kanji_level_map[i['data']['characters']] = i['data']['level']
        level_kanji_map[int(i['data']['level'])].append(i['data']['characters'])
    f.close()

    return kanji_level_map, level_kanji_map

def get_book_id_list():
    '''not actually using this'''
    book_map = {}
    full_list = aozoracli.client.get_books().json() # only gives you 100, deal with this
    for i in full_list:
        book_map[i["book_id"]] = {'title':i["title"], 'authors':i["authors"]}
    return book_map

def get_level(book_id, kanji_level_map):
    '''Gets all of the kanji from the text and finds the lowest level needed to be able to
    read [pct]% of the unique kanji.'''
    bk_text = aozoracli.client.get_content(id=book_id).text
    bk_text = re.findall(r'[㐀-䶵一-鿋豈-頻]',bk_text)
    bk_text = set(bk_text)
    kanji_levels = []
    for item in bk_text:
        if item in kanji_level_map.keys():
            kanji_levels.append(kanji_level_map[item])
        else:
            kanji_levels.append(61)
    if kanji_levels == []:
        return []
    else:
        return [int(np.percentile(kanji_levels, 80)),int(np.percentile(kanji_levels, 85)),
        int(np.percentile(kanji_levels, 90)),int(np.percentile(kanji_levels, 95))]

def format_output(bk, lvl, title, authors):
    '''Formats output for printing'''
    if authors != '':
        main_author = authors[0]['last_name']+', '+authors[0]['first_name']
    else:
        main_author = ''
    for i in range(len(lvl)):
        if lvl[i]==61:
            lvl[i] = "X"
        else:
            lvl[i] = str(lvl[i])
    lvl = '\t'.join(lvl)
    return '%s\t%s\t%s\t%s\n' % (lvl, title, main_author, bk)

if __name__=="__main__":
    kanji_level_map, level_kanji_map = get_kanji()
    f = open('/Users/Emily/Desktop/Aozora/book_id_list_sorted.txt','r') # from https://www.aozora.gr.jp/index_pages/list_person_all_extended.zip
    w = open('/Users/Emily/Desktop/Aozora/output.tsv','w')
    w.write('WK Level 80\tWK Level 85\tWK Level 90\tWK Level 95\tTitle\tMain Author\tAB Book ID\n')
    bk = f.readline().strip()
    count = 0
    #get_level(59898, kanji_level_map, 90)
    while bk:
    #while count < 500:
        count += 1
        lvl = get_level(int(bk), kanji_level_map)
        if (lvl != []) and (min(lvl) != 61):
            bookinfo = aozoracli.client.get_books(id=int(bk)).json()
            booktitle = bookinfo['title']
            bookauthors = bookinfo.get('authors','')
            w.write(format_output(bk, lvl, booktitle, bookauthors))
        if count%50 == 0:
            print("Currently on book #%d..." % count)
        bk = f.readline().strip()