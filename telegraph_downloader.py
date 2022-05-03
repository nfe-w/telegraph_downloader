# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Description: 下载 https://telegra.ph 的图片，并以序号命名
#
# @Time: 2022-05-03 16:50
import asyncio
import os
import re
import urllib.parse

import aiohttp
import requests

semaphore = 50  # 并发数
base_url = 'https://telegra.ph'


def query_title_and_file_url(web_url: str) -> (str, list):
    response = requests.get(web_url)
    html_text = response.content.decode("utf-8")
    pattern_title = re.compile(r'<title>[\S\s]*?</title>')
    title_dom = pattern_title.findall(html_text)
    pattern_img = re.compile(r'<img src[\S\s]*?>')
    url_dom = pattern_img.findall(html_text)
    return title_dom[0][7:-8], [base_url + item.split('"')[1] for item in url_dom]


def save_url_to_file(url, save_dir):
    decode_url = urllib.parse.unquote(url)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(save_dir + '/url.txt', 'w') as f:
        f.write(decode_url)


async def download_with_aiohttp(sem, pic_url, file_name, save_dir, client):
    async with sem:
        file_path = os.path.join(save_dir, file_name)
        if os.path.isfile(file_path):
            print(f'---{file_path}文件已存在...\r')
        else:
            print(f'---{file_path}开始下载...\r')
            async with client.get(pic_url) as response:
                if response.status == 200:
                    content = await response.content.read()
                    with open(file_path, 'wb') as f:
                        f.write(content)


async def async_main(pic_url_list, file_name_list, save_dir):
    sem = asyncio.Semaphore(semaphore)
    async with aiohttp.ClientSession() as client:
        tasks = [download_with_aiohttp(sem, pic_url_list[i], file_name_list[i], save_dir, client) for i in range(len(pic_url_list))]
        return await asyncio.gather(*tasks)


def main():
    url = input('请输入 telegra.ph 地址：')
    if not url:
        exit(0)
    title, pic_url_list = query_title_and_file_url(url)
    save_dir = './Download/' + title
    save_url_to_file(url, save_dir)

    # 构建文件名list
    file_name_list = []
    index = 1
    digits = len(str(len(pic_url_list)))
    for down_url in pic_url_list:
        file_name = str(index).zfill(digits) + '.' + down_url.split('/').pop().split('.')[1]
        file_name_list.append(file_name)
        index = index + 1

    asyncio.run(async_main(pic_url_list, file_name_list, save_dir))
    print(f'{save_dir}下载完成')


if __name__ == '__main__':
    while True:
        main()
