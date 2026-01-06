import numpy as np
from enum import Enum

channel = [i for i in range(10)]
apa_num = 3
upa_num = 8

scale = 1 # 放缩原始数据，现在在建图时放缩

apa_rxtx_pattern   = 'PDCMAPAEchoData_output._%d_.rxtx%c.%s._%d_'
apa_info_pattern    = 'PDCMAPAEchoData_output._%d_.%s'
upa_rxtx_pattern   = 'UssReportdata.curTarget._%d_.rxtx%c.%s._%d_'
upa_info_pattern    = 'UssReportdata.curTarget._%d_.%s'
parking_point_pattern = 'ParkingXYPointCv_%d'

dr_pattern = 'gDROutput.currentDR.%c' # a, x, y

filter_args_A19 = {
            'std_dis':     np.array([0, 217,228, 337, 762,935,1284,1632, 1980,2328,2676,3025,3373,3721,4069,5000]),
            'std_lsb_thld':np.array([30, 30, 40,2630,1050,580, 520, 380,  260, 200, 150, 130, 110, 110, 110, 110]),
            'std_lsb_grad':np.array([]),

            'adv_dis':        np.array([    0,   300, 500,1030,1221,1421,1628,1838,1985,2140,2302,2470,2642,2731,3500,5000]),
            'adv_lsb_thld':   np.array([26000, 26000,6100,5100,5100,3100,2800,1642,1269,1260,1160,1060, 933, 600, 500, 420]),
            'adv_lsb_grad':   np.array([]),

            'adv_confid_dis': np.array([0, 805,3742,4765,6484]),
            'adv_confid_thld':np.array([5,   5,   7,   7,   6]),
        }

filter_args_8255 = {
            'std_dis':     np.array([0, 217,228, 337, 762,935,1284,1632, 1980,2328,2676,3025,3373,3721,4069,5000]),
            'std_lsb_thld':np.array([30, 30, 40,2630,1050,580, 570, 515,  385, 270, 190, 140, 110, 110, 110, 110]),
            'std_lsb_grad':np.array([]),

            'adv_dis':        np.array([    0,   300, 500,1030,1221,1421,1628,1838,1985,2140,2302,2470,2642,2731,3500,5000]),
            'adv_lsb_thld':   np.array([26000, 26000,1500,2350,2750,3100,2800,2102,1669,1360,1160,1060, 933, 700, 500, 420]),
            'adv_lsb_grad':   np.array([]),

            'adv_confid_dis': np.array([0, 900,3742,4765,6484]),
            'adv_confid_thld':np.array([5,   5,   7,   7,   6]),
        }

class SnsId(Enum):
    """
    超声波雷达编号
    """
    FL  = 0
    FLM = 1
    FRM = 2
    FR  = 3
    RL  = 4
    RLM = 5
    RRM = 6
    RR  = 7
    FLS = 8
    FRS = 9
    RLS = 10
    RRS = 11

UssPos_A19 = {SnsId.FL.value: (-726.6 , 3646.9, 125), # x (mm), y (mm), angle(degree)
              SnsId.FLM.value:(-320.75,   3802, 97.5),
              SnsId.FRM.value:( 320.75,   3802, 82.5),
              SnsId.FR.value: ( 726.6 , 3646.9, 55),
              SnsId.RL.value: (-673   ,-934.8,  243),
              SnsId.RLM.value:(-227.2 ,-1030.6, 264),
              SnsId.RRM.value:( 227.2 ,-1030.6, 276),
              SnsId.RR.value: ( 673   , -934.8, 297),
              SnsId.FLS.value:(-941.5 , 3329.5, 174.5),
              SnsId.FRS.value:( 941.5 , 3329.5, 5.5),
              SnsId.RLS.value:(-885.2 ,   -607, 190),
              SnsId.RRS.value:( 885.2 ,   -607, 350),
          }

UssPos_8255 = {SnsId.FL.value:(-666.0, 3556.6, 125), # x (mm), y (mm), angle(degree)
              SnsId.FLM.value:(-343.9, 3691.1, 100),
              SnsId.FRM.value:( 343.9, 3691.1,  80),
              SnsId.FR.value: ( 666.0, 3556.6,  55),
              SnsId.RL.value: (-638.0, -956.7, 244),
              SnsId.RLM.value:(-300.0,-1017.5, 263),
              SnsId.RRM.value:( 300.0,-1017.5, 277),
              SnsId.RR.value: ( 638.0, -956.7, 296),
              SnsId.FLS.value:(-913.7, 3315.9, 170),
              SnsId.FRS.value:( 913.7, 3315.9,  10),
              SnsId.RLS.value:(-906.4, -596.4, 185),
              SnsId.RRS.value:( 906.4, -596.4, 355),
          }

NextSnsId_R = {
            SnsId.FLS.value:SnsId.FL.value,
            SnsId.FL.value:SnsId.FLM.value,
            SnsId.FLM.value:SnsId.FRM.value,
            SnsId.FRM.value:SnsId.FR.value,
            SnsId.FR.value:SnsId.FRS.value,
            SnsId.FRS.value:SnsId.RRS.value,
            SnsId.RRS.value:SnsId.RR.value,
            SnsId.RR.value:SnsId.RRM.value,
            SnsId.RRM.value:SnsId.RLM.value,
            SnsId.RLM.value:SnsId.RL.value,
            SnsId.RL.value:SnsId.RLS.value,
            SnsId.RLS.value:SnsId.FLS.value, 
             }
NextSnsId_L = {SnsId.RLS.value:SnsId.RL.value,
             SnsId.RL.value:SnsId.RLM.value,
             SnsId.RLM.value:SnsId.RRM.value,
             SnsId.RRM.value:SnsId.RR.value,
             SnsId.RR.value:SnsId.RRS.value,
             SnsId.RRS.value:SnsId.FRS.value,
             SnsId.FRS.value:SnsId.FR.value,
             SnsId.FR.value:SnsId.FRM.value,
             SnsId.FRM.value:SnsId.FLM.value,
             SnsId.FLM.value:SnsId.FL.value,
             SnsId.FL.value:SnsId.FLS.value,
             SnsId.FLS.value:SnsId.RLS.value,
             }

disFixK = [
    # 近场
    [
        # 前部
        0.98085, 0, 0.98759, 0.78238, 0.98981, 2.5108, 0.78238, 2.5108, 0.98981, 0.98085, 0.98759, 0,
        # 后部
        1.0998, 0, 1.0091, 0.89812, 0.93966, 0.97062, 0.89812, 0.97062, 0.93966, 1.0998, 1.0091, 0,
        # APA
        0.9736, 0, 0.9810, 0.9736, 0.9810, 0, 0.8933, 0, 0.8801, 0.8933, 0.8801, 0
    ],
    # 远场
    [
        # 前部
        1.0092, 1.0124, 1.0189, 1.0088, 1.0203, 1.0236, 1.0088, 1.0236, 1.0203, 1.0092, 1.0189, 1.0124,
        # 后部
        1.0009, 1.0141, 0.99955, 1.0003, 0.99657, 1.0001, 1.0003, 1.0001, 0.99657, 1.0009, 0.99955, 1.0141,
        # APA
        1.0049, 0, 0.9825, 1.0049, 0.9825, 0, 1.0102, 0, 0.9385, 1.0102, 0.9385, 0
    ]
]

disFixB = [
    # 近场
    [
        # 前部
        1.2306, 0, -13.2924, 86.0698, -16.8283, -819.475, 86.0698, -819.475, -16.8283, 1.2306, -13.2924, 0,
        # 后部
        -94.7905, 0, -117.4007, -3.3762, -63.6143, -107.3551, -3.3762, -107.3551, -63.6143, -94.7905, -117.4007, 0,
        # APA
        33.1790, 0, 50.0818, 33.1790, 50.0818, 0, 48.8810, 0, 36.4352, 48.8810, 36.4352, 0
    ],
    # 远场
    [
        # 前部
        -14.1844, -25.7876, -22.3985, -6.3917, -22.2357, -40.1099, -6.3917, -40.1099, -22.2357, -14.1844, -22.3985, -25.7876,
        # 后部
        -48.4992, -88.6972, -91.445, -45.0792, -88.4818, -91.7778, -45.0792, -91.7778, -88.4818, -48.4992, -91.445, -88.6972,
        # APA
        27.8800, 0, 73.5794, 27.8800, 73.5794, 0, -7.5242, 0, 48.0221, -7.5242, 48.0221, 0
    ]
]
