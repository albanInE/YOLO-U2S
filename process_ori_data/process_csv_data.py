import pandas as pd
import glob
import os
import re

def process_csv_files():
    # 获取所有LF-*.csv文件
    csv_files = glob.glob('csv_data/正前方-固定26度/*.csv')
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 创建一个字典来存储文件名和对应的坐标
    file_coordinate_map = {}
    for file in csv_files:
        # 使用正则表达式提取坐标
        # match = re.search(r'LF(\d+)-(\d+)\.csv', file)
        match = re.search(r'(\d+)CM\.csv', file)
        if match:
            x = int(match.group(1))
            y = 0  # 由于文件名格式只包含一个数字，我们设置y为固定值
            file_coordinate_map[file] = (x, y)
    
    # 按坐标排序文件
    sorted_files = sorted(file_coordinate_map.items(), key=lambda x: (x[1][0], x[1][1]))
    
    # 定义要提取的列名映射
    column_mapping = {
        'UssReportdata.curTarget._1_.rxtx.dis._0_': 'de',
        'UssReportdata.curTarget._1_.rxtxL.dis._0_': 'lce',
        'UssReportdata.curTarget._1_.rxtxR.dis._0_': 'rce',
        # 可以在这里添加更多的列映射
    }
    
    # 创建一个空的DataFrame来存储结果
    result_dfs = {new_name: pd.DataFrame() for new_name in column_mapping.values()}
    
    # 处理每个文件
    for file, (x, y) in sorted_files:
        print(f"\n处理文件: {file}")
        # 读取CSV文件
        df = pd.read_csv(file)
        print("文件列名:")
        print(df.columns.tolist())
        
        # 处理每个目标列
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                print(f"找到目标列: {old_name}")
                column_name = f"({x},{y})_{new_name}"
                
                # 如果是第一个文件，创建结果DataFrame
                if result_dfs[new_name].empty:
                    result_dfs[new_name] = pd.DataFrame(df[old_name])
                    result_dfs[new_name].columns = [column_name]
                else:
                    # 将新列添加到结果DataFrame
                    result_dfs[new_name][column_name] = df[old_name]
            else:
                print(f"未找到目标列: {old_name}")
    
    # 保存结果到新的CSV文件
    for new_name, df in result_dfs.items():
        if not df.empty:
            output_file = f'combined_{new_name}_data.csv'
            df.to_csv(output_file, index=False)
            print(f"\n{new_name}数据处理完成，结果已保存到 {output_file}")
            print("列名:", df.columns.tolist())
        else:
            print(f"\n没有找到任何匹配的{new_name}数据")

if __name__ == "__main__":
    process_csv_files()
