import math
import cv2
import numpy as np
from config import *

def calculate_intersection_points(center, radius, focus1, focus2, semi_major):
    """
    计算圆和椭圆的交点
    参数:
        center: 第一个圆的圆心坐标 (x, y)
        radius: 第一个圆的半径
        focus1: 椭圆第一个焦点坐标 (x1, y1)
        focus2: 椭圆第二个焦点坐标 (x2, y2)
        semi_major: 椭圆半长轴
    返回:
        交点坐标 list（整数类型）
    """
    # 计算椭圆中心
    ellipse_center = ((focus1[0] + focus2[0]) // 2, (focus1[1] + focus2[1]) // 2)
    # 计算椭圆焦距
    focal_length = np.sqrt((focus2[0] - focus1[0]) ** 2 + (focus2[1] - focus1[1]) ** 2)
    # 计算椭圆半短轴
    semi_minor = np.sqrt(semi_major ** 2 - (focal_length / 2) ** 2)
    # 计算椭圆旋转角度
    ellipse_angle = int(np.degrees(np.arctan2(focus2[1] - focus1[1], focus2[0] - focus1[0])))
    if(math.isnan(semi_minor) or math.isnan(ellipse_angle)):return []
    # 创建空白图像
    image_size = int(max(radius, semi_major) * 2 + 200)
    image = np.zeros((image_size, image_size), dtype=np.uint8)
    image2 = np.zeros((image_size, image_size), dtype=np.uint8)

    # 计算图像中心
    image_center = (image_size // 2, image_size // 2)

    # 将圆心偏移到图像中心
    new_center = image_center
    # 计算偏移量
    offset_x = image_center[0] - center[0]
    offset_y = image_center[1] - center[1]
    new_focus1 = (focus1[0] + offset_x, focus1[1] + offset_y)
    new_focus2 = (focus2[0] + offset_x, focus2[1] + offset_y)
    new_ellipse_center = ((new_focus1[0] + new_focus2[0]) // 2, (new_focus1[1] + new_focus2[1]) // 2)

    # 绘制圆
    cv2.circle(image, new_center, radius, 100, 2)

    # 绘制椭圆
    cv2.ellipse(image2, new_ellipse_center, (int(semi_major), int(semi_minor)),
                ellipse_angle, 0, 360, 100, 2, cv2.LINE_AA)

    # 叠加圆和椭圆图像
    image = image+image2

    # 使用NumPy的where函数查找高像素值点的坐标
    y_coords, x_coords = np.where(image == 200)
    high_pixel_points = list(zip(x_coords, y_coords))

    # 将高像素值点的坐标映射回原始坐标系统
    intersection_points = [(x - offset_x, y - offset_y) for x, y in high_pixel_points]
        
    return intersection_points
    

def calculate_intersection_points2(center, radius, focus1, focus2, semi_major):
    """
    计算两个圆的交点，将椭圆近似为圆
    参数:
        center: 第一个圆的圆心坐标 (x, y)
        radius: 第一个圆的半径
        focus1: 椭圆第一个焦点坐标 (x1, y1)
        focus2: 椭圆第二个焦点坐标 (x2, y2)
        semi_major: 椭圆半长轴（用作第二个圆的半径）
    返回:
        两个圆的交点坐标（整数类型）
    """
    # 将输入转换为高精度浮点数
    x0, y0, angle0 = np.array(center, dtype=np.float64)
    x1, y1, angle1 = np.array(focus1, dtype=np.float64)
    x2, y2, angle2 = np.array(focus2, dtype=np.float64)
    radius = np.float64(radius)
    semi_major = np.float64(semi_major)
    
    # 计算第二个圆的圆心（椭圆中心）
    xc = (x1 + x2) / 2
    yc = (y1 + y2) / 2
    
    # 计算两个圆心之间的距离
    d = np.sqrt((xc - x0)**2 + (yc - y0)**2)
    
    # 检查两个圆是否相交
    if d > radius + semi_major or d < abs(radius - semi_major):
        return []
    
    # 计算交点
    # 使用余弦定理计算交点
    a = (radius**2 - semi_major**2 + d**2) / (2 * d)
    h = np.sqrt(radius**2 - a**2)
    
    # 计算交点坐标
    x2 = x0 + a * (xc - x0) / d
    y2 = y0 + a * (yc - y0) / d
    
    # 计算两个交点
    x3 = x2 + h * (yc - y0) / d
    y3 = y2 - h * (xc - x0) / d
    x4 = x2 - h * (yc - y0) / d
    y4 = y2 + h * (xc - x0) / d
    
    # 将结果转换为整数类型
    points = []
    points.append(np.array([x3, y3], dtype=np.int32))
    points.append(np.array([x4, y4], dtype=np.int32))
    
    return points
    # 根据探头角度筛选有效交点
    valid_solution = []
    min_angle_diff = float('inf')
    
    for point in points:
        x, y = point
        # 计算交点相对于探头的角度
        point_angle = np.degrees(np.arctan2(y - y0, x - x0))
        # 计算角度差
        angle_diff = abs(point_angle - angle0)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
            
        if angle_diff < min_angle_diff:
            min_angle_diff = angle_diff
            valid_solution = point
    
    return valid_solution


def distance_compensation(snsid, type, dis):
    k = disFixK[0][snsid*3+type]
    b = disFixB[0][snsid*3+type]
    return int(k*dis+b)
