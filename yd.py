# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/10/7 16:22
# @Author  : ziyou
# -------------------------------
# 注册地址 http://www.pooltea.com/pages/login/index?uper=5fxwfq&team_id=1
# 每日2毛 2元可提现 
# cron "1 8,22 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('悦读')
# 抓包 zhizhitech.com 下 Authorization 的值
# 悦读
# export yuedu_authorization='Bearer eyJ0e&Bearer eyJ0e*******',多账号使用换行或&
# 青龙拉取命令 ql raw https://ghproxy.com/https://raw.githubusercontent.com/q7q7q7q7q7q7q7/ziyou/main/悦读.py
# https://t.me/q7q7q7q7q7q7q7_ziyou

import concurrent.futures
import json
import os
import random
import sys
import time

import requests

ck_list = []

# 设置最大线程数
MAX_WORKERS = 2
ck_signal_list = []


# 加载环境变量
def get_env():
    global ck_list

    env_str = os.getenv("yuedu_authorization")
    if env_str:
        ck_list += env_str.replace("&", "\n").split("\n")


class YueDu:
    def __init__(self, ck, index):
        self.ck = ck
        self.index = index
        self.headers = {
            'Host': 'www.zhizhitech.com',
            'Authorization': self.ck,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; 22041211AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5279 MMWEBSDK/20230805 MMWEBID/5750 MicroMessenger/8.0.41.2441(0x28002951) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Origin': 'http://www.pooltea.com',
            'X-Requested-With': 'com.tencent.mm',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://servicewechat.com/wxcdac9be54ca9673f/6/page-frame.html',
        }

    # 获取个人信息
    def get_infomation(self):
        headers = self.headers
        index = self.index

        url = 'https://www.zhizhitech.com/api/get_user'
        response = requests.get(url, headers=headers)
        response_dict = response.json()
        if response_dict.get('status') != 1:
            ck_signal_list[index] = False
            return
        nickname = response_dict.get('data').get('nickname')
        money = response_dict.get('data').get('money')
        print(f'[账号{index + 1}] {nickname} 阅币：{money}')

    # 获取任务列表
    def get_task_list(self):
        headers = self.headers

        _json = {
            'type': 1,
        }
        response = requests.post(
            'https://www.zhizhitech.com/api/create_activity',
            headers=headers, json=_json)
        response_dict = response.json()
        issue = response_dict.get('data').get('issue')
        activity_str = response_dict.get('data').get('activity_json')
        activity_json = json.loads(activity_str)
        return activity_json, issue

    # 观看视频广告任务
    def watch_video_ads(self):
        headers = self.headers
        index = self.index

        tasks, issue = self.get_task_list()
        response_dict = tasks.get('ad')
        goal = response_dict.get('goal')
        finish = response_dict.get('finish')
        if finish >= goal:
            print(f'[账号{index + 1}] 观看任务已全部完成')
            return
        count = goal - finish
        for _ in range(count):
            json_data = {
                'type': 1,
                'issue': issue,
                'reward_type': 'ad',
            }
            response = requests.post(
                'https://www.zhizhitech.com/api/get_activity_reward',
                headers=headers, json=json_data)
            response_dict = response.json()
            if response_dict.get('status') == 1:
                print(f'[账号{index + 1}] 观看视频广告成功')
                time.sleep(1)
                continue
            print(f'[账号{index + 1}] 观看视频广告失败 {response_dict}')
            break

    # 获取经验任务 每天可得200阅币
    def get_exp_task(self):
        headers = self.headers
        index = self.index

        tasks, issue = self.get_task_list()
        # print(tasks)
        response_dict = tasks.get('exp')
        exp = response_dict.get('exp')
        if exp == 1:
            print(f'[账号{index + 1}] 获取经验任务已全部完成')
            return
        goal = response_dict.get('goal')
        finish = response_dict.get('finish')
        count = int((goal - finish) / 300 + random.randint(2, 5))
        for i in range(1, count + 1):
            _json = {}
            response = requests.post(
                'https://www.zhizhitech.com/api/get_exp_reward',
                headers=headers, json=_json)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('status') == 1:
                print(f'[账号{index + 1}] 第{i}次 获取经验成功')
                time.sleep(1)
                continue
            print(f'[账号{index + 1}] 第{i}次 获取经验失败 {response_dict}')
            break
        json_data = {
            'type': 1,
            'issue': issue,
            'reward_type': 'exp',
        }
        response = requests.post(
            'https://www.zhizhitech.com/api/get_activity_reward',
            headers=headers, json=json_data)
        response_dict = response.json()
        if response_dict.get('status') == 1:
            print(f'[账号{index + 1}] 领取经验值任务奖励成功')
            return
        print(f'[账号{index + 1}] 领取经验值任务奖励失败 {response_dict}')


def threading_task(func):
    # 创建线程池并设置最大线程数
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_WORKERS) as executor:
        futures = []
        for index, ck in enumerate(ck_list):
            if not ck_signal_list[index]:
                continue
            task = YueDu(ck, index)
            task_func = getattr(task, func)
            future = executor.submit(task_func)
            futures.append(future)
        # 等待线程池中的所有任务完成
        concurrent.futures.wait(futures)


def threading_main():
    print('')
    print("============开始获取用户信息============")
    threading_task('get_infomation')
    print('')
    print("============开始观看视频广告============")
    threading_task('watch_video_ads')
    print('')
    print(f"============开始完成获取经验============")
    threading_task('get_exp_task')
    print('')
    print("============开始获取用户信息============")
    threading_task('get_infomation')
    print('')


def main():
    global ck_list
    global ck_signal_list

    get_env()
    ck_list = [x for x in ck_list if x.strip() != ""]
    if not ck_list:
        print('没有获取到账号！')
        return
    ck_count = len(ck_list)
    ck_signal_list = [True] * ck_count
    print(f'获取到{ck_count}个账号！')
    threading_main()


if __name__ == '__main__':
    main()
    sys.exit()
