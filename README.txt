================================================================================
YOLO-U2S: Physics-Embedded Ultrasonic-Spatial Encoding Framework 
           for Real-Time Parking Space Detection
================================================================================

项目概述
--------
本项目实现了 YOLO-U2S（YOLO for Ultrasonic-to-Spatial Perception）检测框架，
通过将车载稀疏超声波信号编码为鸟瞰视角（BEV）图像表征，结合深度学习模型，
实现稳定可靠的障碍物和空间车位检测。

核心创新：
1. 空间编码器：基于超声波反射物理特性及器件视场角（FOV）约束，完成一维信号
   的空间特征解译与维度升维
2. 建图输入层：融合车辆动态定位信息，构建适配YOLO系列模型的输入范式
3. YOLO-OBB检测：实现车位边界及障碍物的实时精准定位

项目结构
--------
YOLO-U2S/
├── README.txt                        # 本文档
│
├── process_ori_data/                 # 数据预处理模块
│   ├── config.py                     # 配置文件（传感器位置、标定参数等）
│   ├── read_mf4_to_csv.py            # MF4格式转CSV工具
│   ├── process_csv_data.py           # CSV数据处理工具
│   ├── uss_math.py                   # 超声波数学计算工具
│   ├── decode_mf4.ipynb              # MF4解码Jupyter Notebook
│   ├── de_ce_height.ipynb            # 高度补偿分析Notebook
│   └── 数据补偿参数/                 # 标定参数Excel文件
│       └── FLM.xls
│
└── general_uss_map/                  # 核心建图模块（空间编码器+建图输入层）
    ├── config.py                     # 配置文件（传感器位置、过滤参数等）
    ├── uss_frame.py                  # 超声波回波帧数据结构
    ├── uss_global_map.py             # 全局地图构建（BEV表征生成）
    ├── uss_roi_map.py                # ROI地图提取（YOLO输入生成）
    └── uss_math_and_coordinate.py    # 坐标变换和几何计算工具

核心功能模块说明
----------------

1. 数据预处理模块 (process_ori_data/)

2. 核心建图模块 (general_uss_map/)

   功能：实现空间编码器和建图输入层，将一维超声波信号转换为BEV图像表征


依赖项
------

Python 3.7+
numpy >= 1.19.0
opencv-python >= 4.5.0
pandas >= 1.2.0
asammdf >= 5.20.0

安装依赖：
```bash
pip install numpy opencv-python pandas asammdf
```

论文引用
--------
如果使用本代码库，请引用以下论文：

Physics-Embedded Ultrasonic-Spatial Encoding Framework for 
Real-Time Parking Space Detection.

联系方式
--------
如有问题或建议，请联系作者。

更新日志
--------
v1.0 (2026-01-07)
- 初始版本发布
- 实现空间编码器和建图输入层
- 支持MF4数据预处理
- 完成全局地图和ROI地图构建

================================================================================
