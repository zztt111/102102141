import urllib.parse
import urllib.request
from time import sleep
import json
from threading import Thread, Lock
from bs4 import BeautifulSoup as bs
import requests
import re
import jieba
import wordcloud
import os
from re import match
import matplotlib.pyplot as plt
import pandas as pd
import time
import cProfile
import os


class Pachong_blbl_Danmu:
    def __init__(self):
        # 对象运行需要,用于多线程任务
        self.key = ''
        self.cids = set()
        self.bvs = []
        self.dms = []
        self.stopwords = set()
        self.count = 0
        self.size = 0
        self.dict2xlsx=[]
        try:
            with open('D:\\MyCode\\软件工程\\第二次作业\\stopwords.txt', encoding='utf-8') as src:
                for word in src:
                    word = word.strip()
                    self.stopwords.add(word)
        except:
            pass
        # 检查是否存在并创建output文件夹用于存放
        output_exist_flag = False
        for path in os.listdir('./'):
            # check if current path is a file
            if os.path.isdir(os.path.join('./', path)) and path == 'output':
                output_exist_flag = True
                break
        if output_exist_flag == False:
            os.mkdir('./output')
        # B站F12复制cookie
        self.cookie = "buvid3=50B45F26-C1C7-4A8B-BAD9-A59F63E8C873167616infoc; b_nut=1631882019; LIVE_BUVID=AUTO8916362047322314; i-wanna-go-back=-1; buvid4=B09C41B2-D46D-C9AB-2E00-E8E761685B2807218-022041123-m4T90WVXeajSb5Qweli6sw%3D%3D; CURRENT_BLACKGAP=0; buvid_fp_plain=undefined; is-2022-channel=1; _uuid=B10FAA4106-410DC-55F4-92E9-1098C917D5FAD93547infoc; b_nut=100; hit-new-style-dyn=0; rpdid=|(u)luk)~)||0J'uYYmJ~mR)u; header_theme_version=CLOSE; CURRENT_QUALITY=80; CURRENT_PID=cbc07e10-c99a-11ed-a8b7-1b14770e3369; FEED_LIVE_VERSION=V8; home_feed_column=4; nostalgia_conf=-1; DedeUserID=386422473; DedeUserID__ckMd5=5c2209c3f1d5e240; b_ut=5; CURRENT_FNVAL=4048; fingerprint=f17c80fed65d8328f73f79c586478fee; buvid_fp=f17c80fed65d8328f73f79c586478fee; SESSDATA=570b9a49%2C1710152905%2C27544%2A92CjDD9UY2ElcGCB1tskSAmHY61QR6QlkT1_0gTa7PWAqRHeZf0pSfAejRhp09DPvPYssSVjNfY1hCS0loUUlJcHl2bTdfVndQa0JDT040QlpFLXJ4bGxkZ1Z3clJaS29rNzlybjBpSExPMEFfeDUyYlBMSEVRX3FEU3Qxb0M2NkRfbkVRSWhOZ21RIIEC; bili_jct=05b41328627ea87a78624081e77e7b62; PVID=1; innersign=0; b_lsid=5A10B10A85_18A937ED2A1; bsource=search_360; browser_resolution=646-682; sid=6dwpug8c; bp_video_offset_386422473=841157344816529522"

    def add_cid_from_bur(self, bur, lock):
        cid = self.get_cid(bur)
        lock.acquire()
        self.cids.add(cid)
        print('cids.add:', cid, 'len(cids)=', len(self.cids))
        lock.release()

    # 指定key, page, order, lock, 获取对应搜索结果的b站号并存放于self.bur
    def get_bur(self, key, page, order, lock):
        try:
            if page >= 25:
                return
            url = 'https://api.bilibili.com/x/web-interface/wbi/search/type?&page_size=42&search_type=video&keyword=' + \
                str(key) + '&page='+str(page) + '&order=' + order
            print(url)
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/84.0.4147.89 Safari/537.36",
            }
            headers['cookie'] = self.cookie
            data = requests.get(url=url, headers=headers).text
            BVs = re.findall('BV..........', data)
            lock.acquire()
            try:
                for bvid in BVs:
                    self.bvs.append(bvid)
                lock.release()
            except Exception as err:
                print(err)
                lock.release()
                return None
        except Exception as err:
            print(err)
            return None

    # 指定b站号, 获取对应视频的所有弹幕并存放于self.dms
    def add_dm_from_bur(self, bv, lock):
        try:
            cid = self.get_id(bv)
            if cid != None:
                dms = self.get_dm(cid)
                if dms != None:
                    lock.acquire()
                    try:
                        self.dms += dms
                        self.count += 1
                        if int(self.count * 100/self.size) > int((self.count - 1) * 100/self.size):
                            print('爬虫进度：' +
                                  str(int(0.1+self.count/self.size*100)) + '%')
                        lock.release()
                    except Exception as err:
                        lock.release()
                        print(err)
                        return None
        except Exception as err:
            print(err)
            return None

    # 输入oid号，返回该视频所有弹幕组成的list，若出错则返回None
    def get_dm(self, oid):
        try:
            if type(oid) != 'string':
                oid = str(oid)
            url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + oid
            data = requests.get(url=url)
            data.encoding = 'utf-8'
            data = data.text
            soup = bs(data)
            data = soup.find_all('d')
            for i, t in enumerate(data):
                data[i] = t.text
            return data
        except Exception as err:
            print(err)
            return None

    def get_bvs(self, keyword, page=1):
        try:
            url = 'https://api.bilibili.com/x/web-interface/wbi/search/type?&page_size=42&search_type=video&keyword=' + \
                str(keyword) + '&page='+str(page)
            print(url)
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/84.0.4147.89 Safari/537.36",
            }
            headers['cookie'] = self.cookie
            data = requests.get(url=url, headers=headers).text
            BVs = re.findall('BV..........', data)
            BVs = sorted(set(BVs))
            return BVs
        except Exception as err:
            print(err)
            return None

    # 将bur号转为cid，cid与oid等价
    def get_id(self, burid):
        try:
            url = "https://api.bilibili.com/x/player/pagelist?bvid="+burid+"&jsonp=jsonp"
            html = urllib.request.urlopen(url)
            html = html.read()
            html = json.loads(html)
            return html['data'][0]['cid']
        except Exception as err:
            print(err)
            return None

    def list2(self, dt, name):
    # 当data数量过大时进行切片
        if len(dt) > 1000000:
            i = 1
            while 1000000*i < len(dt):
                self.list2(dt[(i-1)*1000000:i*1000000], name + '_part' + str(i))
                i += 1
            self.list2(dt[(i-1)*1000000:i*1000000], name + '_part' + str(i))
            return
        
        pf = pd.DataFrame(dt)
        # 指定生成的Excel表格名称
        file_path = './output/' + name + '.xlsx'
        
        # 防止重复覆盖已存在的文件
        index = 1
        while os.path.exists(file_path):
            file_path = './output/' + name + '_' + str(index) + '.xlsx'
            index += 1
        
        # 输出
        file_path_out = pd.ExcelWriter(file_path)
        pf.to_excel(file_path_out, encoding='utf-8', index=False, engine='openpyxl')
        # 保存表格
        file_path_out.save()
    
    # 获取string类型格式化的时间
    def get_time(self):
        return time.strftime('%Y%m%d', time.localtime())

    # 获取前10个出现频率最高的弹幕
    def qian10(self, dm):
        dmk = {}
        for i in dm:
            if i not in dmk:
                dmk[i] = 1
            else:
                dmk[i] += 1
        return sorted(dmk.items(), key=lambda x: x[1], reverse=True)[:min(len(dmk), 20)]
    
    # 输入关键词key,最大爬取视频数量,返回根据搜索结果而爬取的至多max个视频的所有弹幕，list类型。
    def sousuo_dm(self, key, max=1) -> list:
        try:
            self.key = key
            bvs = set()
            lock = Lock()
            threads = set()

            # 获取bur号，当需要的bur号超过1000个时，尝试使用其他搜索order来获取更多bur号
            for ord in ['default', 'ranklevel', 'click', 'scores', 'damku', 'stow', 'pubdate', 'senddate', 'id']:

                for num in range(min(int(max/40)+1, 25)):
                    t = Thread(target=self.get_bur,
                               args=(key, num+1, ord, lock))
                    t.start()
                    threads.add(t)
                while len(threads) > 0:
                    threads.pop().join()
                if len(set(self.bvs)) >= max:
                    break

            self.size = len(set(self.bvs))
            print('已经采集到'+str(self.size)+'个B站号')

            # 对于每个bur号，创建一个线程用于获取bv号对应视频的弹幕
            for bvid in self.bvs:
                if bvid not in bvs:
                    bvs.add(bvid)
                    t = Thread(target=self.add_dm_from_bur,
                               args=(bvid, lock))
                    t.start()
                    threads.add(t)
                    if len(bvs) == max:
                        break
            self.size = len(bvs)
            while len(threads) > 0:
                threads.pop().join()

            dms = self.dms[:]
            print('爬取弹幕总数:', len(dms))
            self.list2(dms, key+'_dms_'+self.get_time())
            self.reinit()
            return dms
        except Exception as e:
            print(e)
            return []

    # 输入list类型的弹幕,根据弹幕将其转换为xlsx文件和wordcloud图片
    def sc_dm(self, dms, key=None):
        if key == None or type(key) != type('miao'):
            key = self.key
        word_count = {}
        len_dms = len(dms)
        for i, s in enumerate(dms):
            s1 = ''.join(re.findall('[\u4e00-\u9fa5]', s))
            for w in jieba.lcut(s1):
                if w in self.stopwords or len(w) == 1 or '哈' in w:
                    continue
                if w not in word_count:
                    word_count[w] = 1
                else:
                    word_count[w] += 1
            if int(i * 100/len_dms) > int((i - 1) * 100/len_dms):
                print('处理弹幕进度：' +
                      str(int(0.1+i * 100/len_dms)) + '%')
        word_count = sorted(word_count.items(),
                            key=lambda x: x[1], reverse=True)
        self.dict2xlsx(word_count, key+'_WordCount_'+self.get_time())

        max_words_num = 300
        index = 1
        text = {}
        for w in word_count[:max(len(word_count), max_words_num)]:
            text[w[0]] = w[1]
        wc = wordcloud.WordCloud(font_path="msyh.ttc",
                                 width=int(1440*index),
                                 height=int(960*index),
                                 background_color='white',
                                 max_words=max_words_num,
                                 relative_scaling=0.5,
                                 min_font_size=1,
                                 prefer_horizontal=1
                                 #  stopwords=s
                                 )
        wc.generate_from_frequencies(text)
        file_name = key + '_' + self.get_time() + '.png'
        wc.to_file('./output/'+file_name)


if __name__ == '__main__':
    c = Pachong_blbl_Danmu()
    key = '日本核污染水排海'
    dm = c.sousuo_dm(key, 300)
    print(c.qian10(dm))
    c.sc_dm(dm)