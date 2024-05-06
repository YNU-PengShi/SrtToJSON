import json
import os


def parse_time(time_str):
    minutes, seconds = map(int, time_str.split(':')[:-1])
    milliseconds = float(time_str.split(':')[-1])
    total_seconds = seconds * 60 + milliseconds
    return f"{total_seconds:.2f}"


def parse_srt_file(file_path):
    captions = []
    current_caption = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                if line.isdigit():
                    # 忽略可能是行号或索引的数字行
                    continue
                elif '-->' in line:
                    # 如果是时间戳行，则结束当前字幕（如果存在）并开始新字幕
                    if current_caption:
                        captions.append(current_caption)
                    current_caption = {
                        'text': [],
                        'start': None,
                        'end': None,
                        'duration': None
                    }
                    start, end = line.split(' --> ')
                    current_caption['start'] = parse_time(start)
                    current_caption['start'] = float(current_caption['start'])
                    current_caption['end'] = parse_time(end)
                    current_caption['end'] = float(current_caption['end'])
                else:
                    # 如果是字幕文本行，则添加到当前字幕的text列表中
                    current_caption['text'].append(line)

                    # 添加最后一个字幕（如果存在）
        if current_caption:
            captions.append(current_caption)

            # 计算字幕时长并合并文本行
    for caption in captions:
        caption['text'] = '\n'.join(caption['text'])
        if caption['start'] is not None and caption['end'] is not None:
            caption['duration'] = caption['end'] - caption['start']
        else:
            caption['duration'] = 0.0
    return captions


def write_to_json(captions, json_file_path):
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(captions, f, ensure_ascii=False, indent=4)


def convert_srt_folder_to_json(srt_folder_path, json_output_folder):
    if not os.path.exists(json_output_folder):
        os.makedirs(json_output_folder)

    for srt_file in os.listdir(srt_folder_path):
        if srt_file.endswith('.srt'):
            srt_file_path = os.path.join(srt_folder_path, srt_file)
            json_file_name = os.path.splitext(srt_file)[0] + '.json'
            json_file_path = os.path.join(json_output_folder, json_file_name)
            captions = parse_srt_file(srt_file_path)
            write_to_json(captions, json_file_path)
            print(f"Captions from {srt_file} have been written to {json_file_path}")


def merge_json_files_in_folder(folder_path, output_file_path):
    merged_data = {}

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        print(filename)
        if filename.endswith('.json'):  # 确保文件是JSON文件
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    # 读取JSON文件内容
                    data = json.load(f)
                    # 将文件内容包装在其文件名作为键的字典中
                    merged_data[filename[:-5]] = data  # 去除.json后缀作为键
                except json.JSONDecodeError as e:
                    print(f"Error decoding {filename}: {e}")

                    # 将合并后的数据写入新的JSON文件
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)  # 格式化输出


srt_folder_path = 'subtitles'
json_output_folder = 'subtitle_json'
convert_srt_folder_to_json(srt_folder_path, json_output_folder)
JSON_folder_path = 'subtitle_json'  # 替换为你的JSON文件所在的文件夹路径
output_file_path = 'subtitle.json'  # 替换为你想要保存合并后JSON文件的路径
merge_json_files_in_folder(JSON_folder_path, output_file_path)
