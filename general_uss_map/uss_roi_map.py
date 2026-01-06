"""

设定roi,从global map 截取、合并map。需要在local map上标注出 车辆位置和uss位置和真值位置。

"""
from uss_global_map import UssGlobalMap
import numpy as np
import cv2

class USSRoiMap:

    def __init__(self, global_map:UssGlobalMap) -> None:
        # self.global_car_pos = pos # convert to roi pos
        self.global_map = global_map  # 用于存储全局地图

    def copy_map_from_global(self):
        # 从全局地图复制地图
        # 复制地图和roi坐标系转换
        self.mapA = self.global_map.APA_trust_map[self.roi].copy()
        self.mapB = self.global_map.UPA_trust_map[self.roi].copy()
        
        # pass


    def set_plv_roi(self):
        # 设立roi以及坐标系转化
        x, y ,degree = self.global_map.global_car_pos
        size = 1280
        self.roi = slice(int(y-size/2), int(y+size/2)), slice(int(x-size/2), int(x+size/2)) # range of (y[],x[])
        # self.roi = roi
        self.roi_car_pos = (size/2, size/2, degree)
        dx = size/2 - x
        dy = size/2 - y
        self.MapSize = (size,size)
        self.timestemps = self.global_map.timestamps
        self.roi_uss_pos = [(int(pos[0]+dx), int(pos[1]+dy)) for key, pos in self.global_map.global_uss_pos.items()]
        self.roi_adma_points = [(int(pos[0]+dx),int(pos[1]+dy)) for pos in self.global_map.global_adma_points]

        self.copy_map_from_global()

    def save_ori_map(self):
        timestamp = int(self.timestemps*1000)
        
        # 将16位图像归一化到8位
        mapA_8bit = cv2.normalize(self.mapA, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        mapB_8bit = cv2.normalize(self.mapB, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

        # 创建一个空的 8 位 3 通道图像
        combined_map = np.zeros((self.MapSize[1], self.MapSize[0], 3), dtype=np.uint8)

        # 将信任图合并到 3 通道图像中
        combined_map[..., 0] = mapA_8bit  # 红色通道
        combined_map[..., 1] = mapB_8bit  # 绿色通道
        combined_map[..., 2] = 0  # 蓝色通道

        # 绘制 uss_pos
        for pos in self.roi_uss_pos:
            cv2.circle(combined_map, pos, 5, (255, 255, 255), -1)  # 绘制白色圆点

        # 绘制 adma_points
        for point in self.roi_adma_points:
            cv2.circle(combined_map, point, 5, (0, 255, 255), -1)  # 绘制黄色圆点

        # 保存图像
        cv2.imwrite(f'debug_roi/test_roi_combined_{timestamp}.png', combined_map)

        pass

    def set_od_roi(self, pos):
        # 设置 OD ROI 的逻辑
        pass  # 具体实现根据需求

    def set_sdw_roi(self, pos):
        # 设置 SDW ROI 的逻辑
        pass  # 具体实现根据需求


if __name__ == '__main__':
    # from uss_global_map import UssGlobalMap
    from uss_frame import UssFrame

    csv_path = 'aligned_data.csv'
    print(f"\n正在处理文件: {csv_path}")
    uss_frame = UssFrame()
    uss_frame.load_data(csv_path,True, True)
    frame_data  = uss_frame.echo_frames
    print("读取完毕, 开始建图")

    global_map = UssGlobalMap()
    fc = 0
    for frame in uss_frame.echo_frames:
        global_map.update_echo_to_map(frame)
        fc = fc+1
        if(fc%500==0):
            roi_map = USSRoiMap(global_map)
            roi_map.set_plv_roi()
            roi_map.save_ori_map()

            # global_map.save_ori_global_map()
    global_map.save_ori_global_map()
    print("完成")   



    pass