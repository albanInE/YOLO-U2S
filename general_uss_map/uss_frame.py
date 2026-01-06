# from asammdf import MDF
import csv
import math
import os
import pickle
import numpy as np
from config import *

filter_args = filter_args_A19
UssPos = UssPos_A19
# filter_args = filter_args_8255
# UssPos = UssPos_8255


"""
    一个回波帧
    echo_frame = {
        snsID: 0-11
        uss_pos: (x,y,angle)
        car_pos: (x,y,angle)
        snsMode: std, adv
        echo_list: [echo,],
        echo_listL: [],
        echo_listR: [],
    }
    一个回波
    echo = {
        dis: int,
        lsb: int,
        width: int,
        confid: int,
    }
"""

class UssFrame: 
    
    def __init__(self) -> None:
        self.echo_frames = []
        self.file_name   = ''
        pass
    
    def load_data(self, file_path, update=False, filter_data=True): # update cache or not
        self.file_name = file_path
        self.echo_frames = []
        #是否有cache
        cache_file_path = file_path+'.cache'
        if(not update): update = not os.path.exists(cache_file_path)
        
        #若无则从文件提取数据
        if(update): self.__load_data_from_csv_file(file_path)
        else :self.__load_data_from_cache(cache_file_path)

        if(filter_data):self.filter_data()
        #保存数据到cache文件
        if(update): self.__save_data(cache_file_path)
    
    def __load_data_from_cache(self, cache_file_path):
        # self.echo_frames = []
        with open(cache_file_path, 'rb') as file:
            self.echo_frames = pickle.load(file)


    def __save_data(self, cache_file_path):
        with open(cache_file_path,'wb') as file:
            pickle.dump(self.echo_frames, file)

    def __load_data_from_csv_file(self, file_path):
        self.echo_frames = []
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                car_x = float(row['DR_X'])*1000
                car_y = float(row['DR_Y'])*1000
                car_degree = float(row['DR_YAW'])
                car_pos = (car_x, car_y, car_degree)
                timestamp = float(row['t'])
                
                for uss_index in range(upa_num + apa_num):
                    if uss_index < upa_num:
                        pattern = upa_rxtx_pattern
                        info_pattern = upa_info_pattern
                    else:
                        pattern = apa_rxtx_pattern
                        info_pattern = apa_info_pattern
                        uss_index = uss_index - upa_num
                    
                    # 使用format构造key
                    snsID = int(row[info_pattern.format(uss_index, 'snsID')])
                    snsMode = eval(row[info_pattern.format(uss_index, 'snsMode')])
                    update_flag = int(row[info_pattern.format(uss_index, 'updateFlag')])
                    
                    echo_list = []
                    echo_listL = []
                    echo_listR = []
                    
                    def decode_echo_data(result_list, num, side):
                        for i in range(num):
                            dis = int(row[pattern.format(uss_index, side, 'dis', i)])
                            lsb = int(row[pattern.format(uss_index, side, 'lsb', i)])
                            # width = int(row[pattern.format(uss_index, side, 'echoWidth', i)])
                            echo = {
                                'dis': dis,
                                'lsb': lsb,
                                # 'echoWidth': width,
                                # 'confidenceLevel': confid
                            }

                            confid = row.get(pattern.format(uss_index, side, 'confidenceLevel', i))
                            if confid != None:
                                echo['confidenceLevel'] = int(confid)
                            result_list.append(echo)

                    # 处理主回波数据
                    num = int(row[info_pattern.format(uss_index, 'rxtx.disNum')])
                    decode_echo_data(echo_list, num, '')
                    
                    # 处理左侧回波数据
                    num = row.get(info_pattern.format(uss_index, 'rxtxL.disNum'))
                    if None != num:
                        decode_echo_data(echo_listL, int(num), 'L')
                    
                    # 处理右侧回波数据
                    num = row.get(info_pattern.format(uss_index, 'rxtxR.disNum'))
                    if None != num:
                        decode_echo_data(echo_listR, int(num), 'R')

                    #加载 adma 真值点数据
                    adma_points = []
                    for i in range(40):
                        try:
                            x = int(float(row[parking_point_pattern.format(i,0)])*1000) #切换成毫米级单位
                            y = int(float(row[parking_point_pattern.format(i,1)])*1000)
                            adma_points.append([x,y])
                        except KeyError:
                            pass

                    self.echo_frames.append({
                        'snsID': snsID,
                        'car_pos': car_pos,
                        'snsMode': snsMode,
                        'echo_list': echo_list,
                        'echo_listL': echo_listL,
                        'echo_listR': echo_listR,
                        'update_flag': update_flag,
                        'timestamp':timestamp,
                        'adma_points' : adma_points
                    })


    """
    数据过滤
    """    
    def filter_data(self):
        filter_args['std_lsb_grad'] = self.__filter_cal_args(filter_args['std_dis'],
                                                                      filter_args['std_lsb_thld'])
        filter_args['adv_lsb_grad'] = self.__filter_cal_args(filter_args['adv_dis'],
                                                                      filter_args['adv_lsb_thld'])


        for frame in self.echo_frames:     #每帧都三个echo_list,
            mode  =  'std' if frame['snsMode'] == b'EN_DIRECT_BY_STD' else 'adv'
            # 递归计算不同的接收的回波
            for side, dis_scale, val_scale in [('', 1, 1),('L', 0.5, 4/3),('R', 0.5, 4/3)]:
                echo_list = frame['echo_list'+side] # 每个 echo_list 有十个回波{}

                # true_list = [True]*len(echo_list)
                dis = np.array([e['dis'] for e in echo_list])*dis_scale
                lsb = np.array([e['lsb'] for e in echo_list])*val_scale
                confid = [ e.get('confidenceLevel') if e.get('confidenceLevel') else 10 for e in echo_list]

                # 针对参数 lsb， confid 进行过滤
                true_list_a = self.__fliter_lsb(filter_args[mode+'_dis'], filter_args[mode+'_lsb_thld'], filter_args[mode+'_lsb_grad'],
                                                dis, lsb) #对回波的lsb进行过滤
                
                if(mode == 'adv'):
                    true_list_b = self.__fliter_confid(filter_args[mode+'_dis'], filter_args[mode+'_confid_thld'],
                                                   dis, confid)
                    
                    true_list = np.array(true_list_a) * np.array(true_list_b)
                else:
                    true_list = np.array(true_list_a)

                # 根据过滤结果，去除不通过的回波
                frame['echo_list'+side] = np.array(echo_list)[true_list] # 去除不符合条件的回波

    def __filter_cal_args(self, thld_dis_list, thld_val_list):
        thld_val_grad = np.subtract(thld_val_list[1:], thld_val_list[:-1])/np.subtract(thld_dis_list[1:], thld_dis_list[:-1])
        thld_val_grad = np.append(thld_val_grad, 0)
        return thld_val_grad

                
    def __fliter_lsb(self, thld_dis_list, thld_val_list, thld_val_grad, dis_list, val_list):
        order_index = np.searchsorted(thld_dis_list, dis_list)-1
        a_x = np.take(thld_dis_list, order_index,  mode='clip')
        a_y = np.take(thld_val_list, order_index,  mode='clip')
        c_x = dis_list
        c_y = val_list

        dx = c_x - a_x
        dy = c_y - a_y
        grad = np.divide(dy,dx)

        return grad >= np.take(thld_val_grad, order_index, mode='clip')
    
    def __fliter_confid(self,thld_dis_list, thld_val_list, dis_list, val_list):
        order_index = np.searchsorted(thld_dis_list, dis_list)-1
        return val_list >= np.take(thld_val_list, order_index, mode='clip')



def __test():
    csv_path = 'std_data/CZ-CC-50-05-01.mf4'
    print(f"\n正在处理文件: {csv_path}")
    uss_frame = UssFrame()
    uss_frame.load_data(csv_path)
    frame_data = uss_frame.echo_frames
    return frame_data


if __name__ == "__main__":
    # 只处理一个文件进行测试
    __test()

