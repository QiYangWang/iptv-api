import re

def process_log(input_file, output_file):
    # 存储处理过的结果，字典的键是 'Name'，值是字典包含最大的Speed和相关的其他数据
    logs = {}

    # 打开输入文件并读取内容
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 使用正则表达式提取关键信息，排除掉与订阅和日期相关的部分
            match = re.match(r"Name: (.*?), URL: (.*?),.*?Delay: (.*?), Speed: (.*?),.*?Resolution: (.*)", line)
            if match:
                name = match.group(1)
                url = match.group(2)
                delay = match.group(3)
                speed = match.group(4)
                resolution = match.group(5)

                # 删除 URL 中 $ 后面的内容
                url = re.sub(r'\$.*', '', url).strip()

                # 过滤掉 Delay 为 -1ms 或 Speed 为 inf M/s，或者分辨率不符合要求
                if delay != "-1 ms" and speed != "inf M/s" and (resolution == "1920x1080" or resolution == "None"):
                    # 将Speed转为数字进行比较
                    try:
                        speed_value = float(speed.split()[0])  # 只取 Speed 的数值部分
                    except ValueError:
                        print(f"Skipping invalid Speed: {speed}")  # 如果转换失败，跳过
                        continue
                    
                    # 如果该 Name 已经存在，检查并更新最大Speed
                    if name in logs:
                        if speed_value > logs[name]['speed']:
                            logs[name] = {'speed': speed_value, 'url': url, 'delay': delay, 'resolution': resolution}
                    else:
                        logs[name] = {'speed': speed_value, 'url': url, 'delay': delay, 'resolution': resolution}

    # 打印最终的 logs 字典，确认数据是否正确保留
    # print(f"Final logs: {logs}")

    # 将筛选和排序后的数据写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        # 在文件的第一行添加特定的元数据行
        f.write('#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml" catchup="append" catchup-source="?playseek=${(b)yyyyMMddHHmmss}-${(e)yyyyMMddHHmmss}"\n')

        for name, data in logs.items():
            # 将 "CCTV-1" 改为 "CCTV1"
            name = name.replace("-", "")

            # 判断是否是 CCTV 系列
            if 'CCTV' in name:
                group_title = "📡央视频道"
            else:
                group_title = "📡卫视频道"
            
            # 在每一条有效记录前加上特定的元数据行
            extinf_line = f'#EXTINF:-1 tvg-name="{name}" tvg-logo="https://live.fanmingming.cn/tv/{name}.png" group-title="{group_title}",{name}\n'
            # 只保留URL并写入
            f.write(extinf_line)
            f.write(data['url'] + '\n')
