import json
import pandas as pd
import os
import yaml
import glob

def load_config(config_path):
    """加载 YAML 配置文件"""
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def parse_logs(log_directory, output_csv, columns):
    # 创建一个空DataFrame来存储所有提取的数据
    data = pd.DataFrame(columns=columns)

    # 遍历指定目录下的所有日志文件
    for log_file in glob.glob(os.path.join(log_directory, '*.log')):
        with open(log_file, 'r', encoding='utf-8') as file:
            for line in file:
                # 过滤包含"processStatus":0的关键字的日志行
                if '"processStatus":0' in line:
                    # 解析日志行中的JSON数据
                    try:
                        # 假设日志格式为：[其他信息] : {"result": {"proofreadResult": [...], ...}}
                        log_data = json.loads(line.split("WebLogAspect       :", 1)[1].strip())
                        proofread_results = log_data['result']['data']['proofreadResult']

                        # 遍历proofreadResults中的每个元素
                        for result in proofread_results:
                            # 提取所需字段
                            entry = {
                                '句子': result.get('sentence'),
                                '错误开始位置': result.get('offset'),
                                '错误词': result.get('errorWord'),
                                '建议词': result.get('rightWords'),
                                '模块': result.get('model'),
                                '错误类型': result.get('subClass'),
                                '错误原因': result.get('reason')
                            }
                            # 使用pd.concat添加新行到data DataFrame
                            data = pd.concat([data, pd.DataFrame([entry])], ignore_index=True)

                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from line: {line}. Error: {e}")
                    except KeyError as e:
                        print(f"Key not found: {e}")

    # 将数据保存到CSV文件
    data.to_csv(output_csv, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    # 加载配置文件
    config = load_config('config.yaml')
    
    # 从配置文件中获取参数
    log_directory = config['log_directory']
    output_csv = config['output_csv']
    columns = config['columns']
    
    parse_logs(log_directory, output_csv, columns)
    print(f"Data has been saved to {output_csv}")