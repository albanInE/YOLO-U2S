import pandas as pd
from asammdf import MDF
import os
import numpy as np

IgnoredKeys = ['EgoXY', 'Inv_Path_Radius', 'Video','disInfo','GUPA','GAPA','CAN_DataFrame']

def convert_mf4_to_csv(mf4_path, csv_path):
    """
    将MF4文件转换为CSV格式
    
    Args:
        mf4_path (str): MF4文件路径
        csv_path (str): 输出CSV文件路径
    """
    try:
        mdf = MDF(mf4_path)
    except Exception:
        return
    max_group_index = np.argmax([len(group.channels) for group in mdf.groups])
    t = mdf.get('t', group=max_group_index)
    time_series = pd.Series(t.samples, index=t.timestamps, name='t')
    data_dict = {}
    data_dict['t'] = time_series

    for index, group in enumerate(mdf.groups):
        for channel in group.channels:
            data = mdf.get(channel.name, group=index)
            #-----------------------------------------------------
            # ignore_flag = False
            if(channel.name in ['t','Comment'] or len(data.samples)<1 or any(key in channel.name for key in IgnoredKeys)):continue
            # for key in IgnoredKeys:
                # if(key in channel.name): ignore_flag = True
            # if(ignore_flag):continue
            #-----------------------------------------------------
            if isinstance(data.samples[0], np.record): # 多维数据
                array_view = data.samples.view(np.float64).reshape(len(data.samples), -1)
                x, y = array_view[:, 0], array_view[:, 1]
                x_series = pd.Series(x, index=data.timestamps, name=channel.name+'[0]')
                y_series = pd.Series(y, index=data.timestamps, name=channel.name+'[1]')
                x_series = x_series.reindex(time_series.index, method='nearest', tolerance=0.1)
                y_series = y_series.reindex(time_series.index, method='nearest', tolerance=0.1)
                data_dict[channel.name+'[0]']=x_series
                data_dict[channel.name+'[1]']=y_series
                
            else: #一维数据
                s = pd.Series(data.samples, index=data.timestamps, name=channel.name)
                aligned_s = s.reindex(time_series.index, method='nearest', tolerance=0.1)
                data_dict[channel.name]=aligned_s

    df = pd.DataFrame(data_dict)
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    import glob
    
    # 输入和输出目录
    input_dir = "mf4_data"
    output_dir = "csv_data"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 使用glob搜索所有mf4文件
    mf4_files = glob.glob(os.path.join(input_dir, "**", "*.mf4"), recursive=True)
    
    # if not mf4_files:
        # print(f"警告：在 {input_dir} 目录下没有找到.mf4文件")
    
    # 处理每个mf4文件
    for mf4_path in mf4_files:
        # 构建输出CSV文件路径
        relative_path = os.path.relpath(os.path.dirname(mf4_path), input_dir)
        output_subdir = os.path.join(output_dir, relative_path)
        os.makedirs(output_subdir, exist_ok=True)
        
        csv_path = os.path.join(output_subdir, os.path.splitext(os.path.basename(mf4_path))[0] + '.csv')
        
        # 转换文件
        print(f"\n正在处理文件: {mf4_path}")
        convert_mf4_to_csv(mf4_path, csv_path)