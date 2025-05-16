import requests
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os



#吧名
text = "华南理工大学"
# 文件路径
path = ""


now = datetime.now().strftime("%Y.%m.%d")
file_name = f"{now} tieba_rank_data.txt"
file_path=path+fr'{file_name}'
gbk_bytes = text.encode('gbk')
url_encoded = urllib.parse.quote_from_bytes(gbk_bytes)
url = f'https://tieba.baidu.com/f/like/furank?kw={url_encoded}&pn='
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}
existing_ranks = set()
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "排名:" in line:
                try:
                    rank = int(line.split("排名:")[1].split(",")[0])
                    existing_ranks.add(rank)
                except:
                    pass

with open(file_path, 'a', encoding='utf-8') as file:
    for i in range(1, 501):  # 第 i 页
        start_rank = (i - 1) * 20 + 1
        if start_rank in existing_ranks:
            print(f"跳过第 {i} 页，已存在排名 {start_rank}")
            continue

        for attempt in range(3):
            try:
                print(f"请求第 {i} 页（尝试第 {attempt+1} 次）...")
                response = session.get(url + str(i), headers=headers, timeout=10)
                response.encoding = "gbk"
                soup = BeautifulSoup(response.text, "html.parser")
                found_any = False
                for row in soup.find_all("tr", class_="drl_list_item"):
                    rank = row.find("p", class_="drl_item_index_nor") or row.find("p", class_="drl_item_index_1") or row.find("p", class_="drl_item_index_2") or row.find("p", class_="drl_item_index_3")
                    name = row.find("a", class_="drl_item_name_nor") or row.find("a", class_="drl_item_name_top")
                    exp = row.find("td", class_="drl_item_exp")
                    if rank and name and exp:
                        rank_num = int(rank.text.strip())
                        if rank_num in existing_ranks:
                            continue
                        line = f"排名:{rank_num}, 用户名: {name.text.strip()}, 经验值: {exp.text.strip()}\n"
                        file.write(line)
                        existing_ranks.add(rank_num)
                        found_any = True
                        print(line.strip())

                if found_any:
                    break
                else:
                    print(f"第 {i} 页未解析到数据，可能被屏蔽了")
            except Exception as e:
                print(f"第 {i} 页请求失败，原因：{e}")
                time.sleep(3)
