import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random

# 定义比赛平台的链接
CODEFORCES_CONTESTS_URL = "https://codeforces.com/contests"
ATCODER_CONTESTS_URL = "https://atcoder.jp/contests/"
LEETCODE_CONTESTS_URL = "https://leetcode.com/contest/"
NOWCODER_CONTESTS_URL = 'https://ac.nowcoder.com/acm/contest/vip-index'

# 定义更新间隔宏（单位：秒）
UPDATE_INTERVAL = 60

# 随机 User-Agent 列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
]


# 获取随机 User-Agent
def get_random_user_agent():
    return random.choice(USER_AGENTS)


# 获取 LeetCode 即将到来的比赛
def get_leetcode_upcoming_contests():
    # 构建 GraphQL 查询
    query = """
    query {
        allContests {
            title
            startTime
            duration
            titleSlug
        }
    }
    """

    url = 'https://leetcode.com/graphql'
    headers = {
        'User-Agent': get_random_user_agent(),
        'Content-Type': 'application/json'
    }

    data = {
        'query': query
    }

    try:
        # 发送 GraphQL 请求，设置超时时间为 10 秒
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()

        # 解析响应数据
        result = response.json()
        contests = result.get('data', {}).get('allContests', [])

        # 获取当前时间
        current_time = datetime.utcnow().timestamp()

        # 筛选出即将到来的比赛
        upcoming_contests = []
        for contest in contests:
            start_time = float(contest.get('startTime', 0))
            if start_time > current_time:
                upcoming_contests.append(contest)

        return upcoming_contests
    except requests.RequestException as e:
        print(f'请求 LeetCode 数据出错: {e}')
    except Exception as e:
        print(f'处理 LeetCode 数据发生其他错误: {e}')
    return []


# 获取 Codeforces 即将到来的比赛
def get_codeforces_upcoming_contests():
    url = "https://codeforces.com/api/contest.list"
    headers = {
        'User-Agent': get_random_user_agent()
    }
    try:
        # 设置超时时间为 10 秒
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                contests = data["result"]
                upcoming_contests = [contest for contest in contests if contest["phase"] == "BEFORE"]
                upcoming_contests.sort(key=lambda x: x["startTimeSeconds"])
                return upcoming_contests
            else:
                print("请求成功，但获取 Codeforces 比赛数据失败:", data["status"])
        else:
            print("请求 Codeforces 数据失败，状态码:", response.status_code)
    except requests.RequestException as e:
        print(f'请求 Codeforces 数据出错: {e}')
    except Exception as e:
        print(f'处理 Codeforces 数据发生其他错误: {e}')
    return []


# 获取 AtCoder 即将到来的比赛
def get_atcoder_upcoming_contests():
    url = "https://atcoder.jp/home"
    headers = {
        'User-Agent': get_random_user_agent()
    }
    try:
        # 设置超时时间为 10 秒
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            contests = []
            for row in soup.select('#contest-table-upcoming tbody tr'):
                start_time = row.select_one('time.fixtime-short').text.strip()
                contest_name = row.select('td a')[1].text.strip()
                contests.append({
                    "Start Time": start_time,
                    "Contest Name": contest_name
                })
            return contests
        else:
            print("请求 AtCoder 页面失败，状态码:", response.status_code)
    except requests.RequestException as e:
        print(f'请求 AtCoder 数据出错: {e}')
    except Exception as e:
        print(f'处理 AtCoder 数据发生其他错误: {e}')
    return []


# 获取 Nowcoder 即将到来的比赛
def get_nowcoder_upcoming_contests():
    url = NOWCODER_CONTESTS_URL
    headers = {
        'User-Agent': get_random_user_agent()
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        platform_mod = soup.find('div', class_='platform-mod js-current')
        contests = []
        for platform_item in platform_mod.find_all('div', class_='platform-item js-item'):
            contest_info = {}
            data_json = json.loads(platform_item['data-json'].replace('&quot;', '"'))
            contest_info['contestName'] = data_json.get('contestName')
            contest_info['participants'] = data_json.get('signUpCount')
            start_time = data_json.get('contestStartTime')
            if start_time:
                contest_info['startTime'] = datetime.fromtimestamp(start_time / 1000).strftime('%Y-%m-%d %H:%M')
            end_time = data_json.get('contestEndTime')
            if end_time:
                contest_info['endTime'] = datetime.fromtimestamp(end_time / 1000).strftime('%Y-%m-%d %H:%M')
            link = platform_item.find('div', class_='platform-item-main').find('h4').find('a')
            if link:
                contest_info['link'] = 'https://ac.nowcoder.com' + link['href']
            contests.append(contest_info)
        return contests
    else:
        print(f"请求 Nowcoder 数据失败，状态码: {response.status_code}")
    return []


# 创建 HTML 文件
def create_html(leetcode_contests, codeforces_contests, atcoder_contests, nowcoder_contests, last_update_time):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html_content = f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OIpage-即将到来的比赛</title>
    <style>
        body {{
            font-family: 'Open Sans', sans-serif;
            background: linear-gradient(to bottom, #f9f9f9, #e1e1e1);
            color: #333;
            margin: 0;
            padding: 0;
        }}

       .header {{
            background-color: #2c3e50;
            color: white;
            text-align: center;
            padding: 2rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}

       .header h1 {{
            font-size: 2.5rem;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}

       .info-section {{
            text-align: center;
            padding: 1rem 0;
            background-color: rgba(255, 255, 255, 0.8);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

       .info-section p {{
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }}

       .container {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}

       .contest-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 2rem;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            background-color: white;
        }}

       .contest-table th,
       .contest-table td {{
            padding: 1.2rem;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}

       .contest-table th {{
            background-color: #34495e;
            color: white;
            font-weight: 600;
        }}

       .contest-table tr:hover {{
            background-color: #f5f5f5;
            transition: background-color 0.3s ease;
        }}

       .contest-table a {{
            color: #3498db;
            text-decoration: none;
        }}

       .contest-table a:hover {{
            text-decoration: underline;
        }}

        h2 {{
            font-size: 1.8rem;
            color: #2c3e50;
            margin-bottom: 1rem;
        }}
    </style>
</head>

<body>
    <div class="header">
        <h1>OIpage-即将到来的比赛</h1>
    </div>
    <div class="info-section">
        <p>上次更新时间: {last_update_time}</p>
        <p>当前时间: <span id="current-time">{current_time}</span></p>
        <p>网站作者: <a href="https://tommyjin.cn">Tommyjin(Jink)</a></p>
    </div>
    <div class="container">
        <h2>LeetCode 即将到来的比赛</h2>
        <table class="contest-table">
            <thead>
                <tr>
                    <th>比赛名称</th>
                    <th>开始时间</th>
                    <th>持续时间（小时）</th>
                </tr>
            </thead>
            <tbody>
    """

    for contest in leetcode_contests:
        contest_name = contest["title"]
        start_time = datetime.fromtimestamp(float(contest["startTime"])).strftime('%Y-%m-%d %H:%M:%S')
        # 将持续时间从秒转换为小时
        duration = round(contest["duration"] / 3600, 2)
        html_content += f"""
                <tr>
                    <td><a href="{LEETCODE_CONTESTS_URL}{contest['titleSlug']}" target="_blank">{contest_name}</a></td>
                    <td>{start_time}</td>
                    <td>{duration}</td>
                </tr>
        """

    html_content += f"""
            </tbody>
        </table>

        <h2>Codeforces 即将到来的比赛</h2>
        <table class="contest-table">
            <thead>
                <tr>
                    <th>比赛名称</th>
                    <th>比赛类型</th>
                    <th>开始时间</th>
                    <th>持续时间（小时）</th>
                </tr>
            </thead>
            <tbody>
    """

    for contest in codeforces_contests:
        contest_name = contest["name"]
        contest_type = contest["type"]
        start_time = datetime.fromtimestamp(contest["startTimeSeconds"]).strftime('%Y-%m-%d %H:%M:%S')
        # 将持续时间从秒转换为小时
        duration = round(contest["durationSeconds"] / 3600, 2)
        html_content += f"""
                <tr>
                    <td><a href="{CODEFORCES_CONTESTS_URL}" target="_blank">{contest_name}</a></td>
                    <td>{contest_type}</td>
                    <td>{start_time}</td>
                    <td>{duration}</td>
                </tr>
        """

    html_content += f"""
            </tbody>
        </table>

        <h2>AtCoder 即将到来的比赛</h2>
        <table class="contest-table">
            <thead>
                <tr>
                    <th>比赛名称</th>
                    <th>开始时间</th>
                </tr>
            </thead>
            <tbody>
    """

    for contest in atcoder_contests:
        contest_name = contest["Contest Name"]
        start_time = contest["Start Time"]
        html_content += f"""
                <tr>
                    <td><a href="{ATCODER_CONTESTS_URL}" target="_blank">{contest_name}</a></td>
                    <td>{start_time}</td>
                </tr>
        """

    html_content += f"""
            </tbody>
        </table>

        <h2>Nowcoder 即将到来的比赛</h2>
        <table class="contest-table">
            <thead>
                <tr>
                    <th>比赛名称</th>
                    <th>开始时间</th>
                    <th>结束时间</th>
                    <th>参加人数</th>
                </tr>
            </thead>
            <tbody>
    """

    for contest in nowcoder_contests:
        contest_name = contest["contestName"]
        participants = contest["participants"]
        start_time = contest["startTime"]
        end_time = contest.get('endTime', 'N/A')
        link = contest["link"]
        html_content += f"""
                <tr>
                    <td><a href="{link}" target="_blank">{contest_name}</a></td>
                    <td>{start_time}</td>
                    <td>{end_time}</td>
                    <td>{participants}</td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>
    </div>
    <script>
        function updateTime() {
            const currentTimeElement = document.getElementById('current-time');
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const currentTime = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            currentTimeElement.textContent = currentTime;
        }

        // 每秒更新一次时间
        setInterval(updateTime, 1000);
        // 页面加载时先更新一次时间
        updateTime();
    </script>
</body>

</html>
    """

    try:
        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(html_content)
    except Exception as e:
        print(f"写入 HTML 文件时出错: {e}")


# 定时任务函数，按指定间隔执行
def update_contests_periodically():
    last_update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    while True:
        try:
            leetcode_upcoming_contests = get_leetcode_upcoming_contests()
            codeforces_upcoming_contests = get_codeforces_upcoming_contests()
            atcoder_upcoming_contests = get_atcoder_upcoming_contests()
            nowcoder_upcoming_contests = get_nowcoder_upcoming_contests()

            print("LeetCode 即将开始的比赛数量:", len(leetcode_upcoming_contests))
            print("Codeforces 即将开始的比赛数量:", len(codeforces_upcoming_contests))
            print("AtCoder 即将开始的比赛数量:", len(atcoder_upcoming_contests))
            print("Nowcoder 即将开始的比赛数量:", len(nowcoder_upcoming_contests))

            if (leetcode_upcoming_contests or codeforces_upcoming_contests 
                or atcoder_upcoming_contests or nowcoder_upcoming_contests):
                create_html(leetcode_upcoming_contests, codeforces_upcoming_contests, 
                            atcoder_upcoming_contests, nowcoder_upcoming_contests, 
                            last_update_time)
                print(f"已更新 index.html 文件，包含相应的比赛信息。")
            else:
                print("没有获取到任何比赛数据，无法更新 index.html 文件。")

            last_update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"定时任务出现异常: {e}")
        # 按指定间隔执行
        time.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    update_contests_periodically()