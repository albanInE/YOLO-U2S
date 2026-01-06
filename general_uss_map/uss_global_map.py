import cv2
import numpy as np
from uss_frame import UssPos
import math
import time

SideLength = 4000
MapSize = (SideLength,SideLength)
fov = 90
side_fov = 120
thickness = 2

init_trust = 1000 #地图初始化
step_trust = 10        #单次回波置信度
thld_trust = init_trust + step_trust*2 #置信度阈值

scale = 0.1

class UssGlobalMap:
    """
    厘米级地图
    记录坐标原点为某个时刻的dr坐标
    定义该坐标原点为图像中心位置: MapSize/2
    """
    def __init__(self) -> None:
        self.APA_strength_map = cv2.Mat(np.zeros(MapSize, np.uint16))
        self.APA_trust_map    = cv2.Mat(np.zeros(MapSize, np.uint16))
        self.UPA_strength_map = cv2.Mat(np.zeros(MapSize, np.uint16))
        self.UPA_trust_map    = cv2.Mat(np.zeros(MapSize, np.uint16))
        
        self.APA_trust_map.fill(init_trust)
        self.UPA_trust_map.fill(init_trust)

        self.global_adma_points = []
        self.global_uss_pos = {}
        self.global_car_pos = ()
        self.timestamps = 0.0
        self.ori_dr_point = [0,0,0]
        pass
    
    def clear(self):
        self.__init__()

    def update_ori_point(self, dr_point):
        # 建立全局图像和dr坐标系的映射 :以某个时刻的dr坐标作为全局坐标原点
        if (abs(dr_point[0] - self.ori_dr_point[0])*scale > MapSize[0] / 4 or 
            abs(dr_point[1] - self.ori_dr_point[1])*scale > MapSize[1] / 4):
            self.APA_strength_map = self.shift_global_map(dr_point, self.APA_strength_map, 0)
            self.APA_trust_map = self.shift_global_map(dr_point, self.APA_trust_map, init_trust)
            self.UPA_strength_map = self.shift_global_map(dr_point, self.UPA_strength_map, 0)
            self.UPA_trust_map = self.shift_global_map(dr_point, self.UPA_trust_map, init_trust)
            
            self.ori_dr_point = dr_point
            self.global_adma_points = []
            self.global_uss_pos = {}
            return True
        return False

    def shift_global_map(self, new_dr_point , Map, init_val):
        # 计算旧原点和新原点在图像中的坐标
        old_pos = np.array(self.ori_dr_point) * scale
        new_pos = np.array(new_dr_point) * scale

        # 计算平移量
        dx = old_pos[0] - new_pos[0]
        dy = old_pos[1] - new_pos[1]

        translation_matrix = np.float32([[1, 0, dx], [0, 1, dy]])
        shifted_map = cv2.warpAffine(Map, translation_matrix, MapSize, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=init_val)

        return shifted_map

    def update_global_car_pos(self, dr_car_pos):
        # 计算全局图像上车辆坐标
        self.update_ori_point(dr_car_pos)
        self.global_car_pos = self.dr2global(dr_car_pos)

    def dr2global(self, dr_point):
        # dr坐标系 转化为图像上的坐标
        x = int((dr_point[0]-self.ori_dr_point[0])*scale+MapSize[0]/2)
        y = int((dr_point[1]-self.ori_dr_point[1])*scale+MapSize[1]/2)
        rad = int(dr_point[2])
        return (x,y,rad)

    def vehicle2global(self, vehicle_point):
        car_x,car_y,degree = self.global_car_pos
        rad = degree * math.pi / 180
        cos_val = math.cos(rad)
        sin_val = math.sin(rad)
        #车辆坐标系 转化为图像上的坐标
        tx = vehicle_point[0]*scale
        ty = vehicle_point[1]*scale
        x = int(tx*cos_val-ty*sin_val+car_x)
        y = int(ty*cos_val+tx*sin_val+car_y)
        return (x,y)
    
    def load_global_adma_points(self, adma_points):
        self.global_adma_points = []
        for point in adma_points:
              self.global_adma_points.append(self.vehicle2global(point))

    def update_echo_to_map(self, frame:dict):

        snsID = frame['snsID']
        self.update_global_car_pos(frame['car_pos'])
        self.load_global_adma_points(frame['adma_points'])
        self.timestamps = float(frame['timestamp'])
        car_pos = self.global_car_pos

        uss_pos = np.array(self.vehicle2global(UssPos[snsID]))
        self.global_uss_pos[snsID]=uss_pos
        uss_angle = UssPos[snsID][2] + car_pos[2]

        dis = [int(echo['dis']*scale) for echo in frame['echo_list']] #放缩到cm级
        lsb = [int(echo['lsb']) for echo in frame['echo_list']]

        if(snsID<8):
            trust_map    = self.UPA_trust_map
            strength_map = self.UPA_strength_map
        else:
            trust_map    = self.APA_trust_map
            strength_map = self.APA_strength_map

        #------------------------- 画图 --------------------------------------
        if(len(dis)<1): return
        max_dis = dis[-1]
        trust_mask    = cv2.Mat(np.zeros(MapSize, np.int16))
        strength_mask = cv2.Mat(np.zeros(MapSize, np.uint16))
        last_echo_index = len(dis)-1
        for i in range(last_echo_index, -1, -1): #倒序画图
            _dis = dis[i]
            _lsb = lsb[i]
            trust = step_trust/2 # 除了第一个回波，其他回波只有一半的置信度
            if(0 == i): #处理到第一个回波
                trust = step_trust
                trust_mask =    cv2.ellipse(trust_mask,    uss_pos, (_dis, _dis), 0, uss_angle - fov/2, uss_angle+fov/2, (-trust/2), -1)
            trust_mask =    cv2.ellipse(trust_mask,    uss_pos, (_dis, _dis), 0, uss_angle - fov/2, uss_angle+fov/2, (trust), thickness)
            strength_mask = cv2.ellipse(strength_mask, uss_pos, (_dis, _dis), 0, uss_angle - fov/2, uss_angle+fov/2, (_lsb), thickness)

        # roi计算，降低运算量
        roi =  slice( uss_pos[1]-max_dis-5,uss_pos[1]+max_dis+5),slice(uss_pos[0]-max_dis-5,uss_pos[0]+max_dis+5) # y[],x[]
        
        #trust 直接更新
        np.add(trust_map[roi], trust_mask[roi], out=trust_map[roi], where=trust_map[roi]>step_trust, dtype=np.uint16, casting='unsafe')

        # strength 保持最大值
        np.maximum(strength_map[roi], strength_mask[roi], out=strength_map[roi])
    
    def save_ori_global_map(self):
        timestamp = int(self.timestamps*1000)  # 获取当前时间戳

        # 将16位图像归一化到8位
        apa_trust_map_8bit = cv2.normalize(self.APA_trust_map, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        upa_trust_map_8bit = cv2.normalize(self.UPA_trust_map, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

        # 创建一个空的 8 位 3 通道图像
        combined_map = np.zeros((MapSize[1], MapSize[0], 3), dtype=np.uint8)

        # 将信任图合并到 3 通道图像中
        combined_map[..., 0] = apa_trust_map_8bit  # 红色通道
        combined_map[..., 1] = upa_trust_map_8bit  # 绿色通道
        combined_map[..., 2] = 0  # 蓝色通道

        # 绘制 uss_pos
        for key, pos in self.global_uss_pos.items():
            cv2.circle(combined_map, pos, 5, (255, 255, 255), -1)  # 绘制白色圆点
            # cv2.putText(combined_map, f"{i}", point, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 1, cv2.LINE_AA)

        # 绘制 adma_points
        for i, point in enumerate(self.global_adma_points):
            cv2.circle(combined_map, point, 5, (0, 255, 255), -1)  # 绘制黄色圆点
            cv2.putText(combined_map, f"{i}", point, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 1, cv2.LINE_AA)

        # 保存图像
        cv2.imwrite(f'debug_global/test_global_combined_{timestamp}.png', combined_map)

if __name__ == '__main__':
    from uss_frame import UssFrame
    # import cv2
    import os
    os.system('rm debug_global/*')

    # csv_path = 'csv_data/XL/XL-20240306-001/XL-50-05-01.csv'
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
        if(fc%500==0):global_map.save_ori_global_map()
    global_map.save_ori_global_map()
    print("完成")   