import re

def process_log(input_file, output_file):
    # 存储处理过的结果，字典的键是 'Name'，值是字典包含最大的Speed和相关的其他数据
    logs = {}

    # 打开输入文件并读取内容
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 使用正则表达式提取关键信息，排除掉与订阅和日期相关的部分
            match = re.match(r"Name: (.*?), URL: (.*?),.*?Delay: (.*?), Speed: (.*?),.*", line)
            if match:
                name = match.group(1)
                url = match.group(2)
                delay = match.group(3)
                speed = match.group(4)

                # 删除 URL 中 $ 后面的内容
                url = re.sub(r'\$.*', '', url).strip()

                # 打印调试信息，确保提取到的字段正确
                # print(f"Matched: Name: {name}, URL: {url}, Delay: {delay}, Speed: {speed}")

                # 过滤掉 Delay 为 -1ms 或 Speed 为 inf M/s 的项
                if delay != "-1 ms" and speed != "inf M/s":
                    # 将Speed转为数字进行比较
                    try:
                        speed_value = float(speed.split()[0])  # 只取 Speed 的数值部分
                    except ValueError:
                        print(f"Skipping invalid Speed: {speed}")  # 如果转换失败，跳过
                        continue
                    
                    # 如果该 Name 已经存在，检查并更新最大Speed
                    if name in logs:
                        if speed_value > logs[name]['speed']:
                            logs[name] = {'speed': speed_value, 'url': url}
                    else:
                        logs[name] = {'speed': speed_value, 'url': url}

    # 打印最终的 logs 字典，确认数据是否正确保留
    # print(f"Final logs: {logs}")

    # 将筛选和排序后的数据写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for name, data in logs.items():
            # 判断是否是 CCTV 系列
            if 'CCTV' in name:
                group_title = "📡央视频道"
            else:
                group_title = "📡卫视频道"
            
            # 在每一条有效记录前加上特定的元数据行
            extinf_line = f'#EXTINF:-1 tvg-name="{name}" tvg-logo="https://raw.githubusercontent.com/fanmingming/live/main/tv/{name}.png" group-title="{group_title}",{name}\n'
            # 只保留URL并写入
            f.write(extinf_line)
            f.write(data['url'] + '\n')

# 使用示例
process_log('output/sort.log', 'output/final_result.m3u')
