import obj_class as obj
import datetime
import utils
import numpy as np
import sklearn.cluster as sc
import time


# 形成{调度单号：轨迹实体}
def formtraj(tra_reader):
    planno_trajobj = {}
    for inx, lireader in enumerate(tra_reader):
        if inx % 100000 == 0:
            print('finish', inx)
        if inx == 0 or inx % 2 != 0 or lireader[0][: 2] == 'CG':
            continue
        plan_no = lireader[0]
        create_time = datetime.datetime.strptime(lireader[1], '%Y-%m-%d %H:%M:%S')
        load_date = datetime.datetime.strptime(lireader[2], '%Y-%m-%d %H:%M:%S')
        return_time = datetime.datetime.strptime(lireader[3], '%Y-%m-%d %H:%M:%S')
        truck_no = lireader[4]
        time = datetime.datetime.strptime(lireader[5], '%Y-%m-%d %H:%M:%S')
        lon = float(lireader[6])
        lat = float(lireader[7])
        speed = float(lireader[8])
        hei = float(lireader[9])
        direc = float(lireader[10])
        ttd = float(lireader[11])
        status = int(lireader[12])
        isnoise = int(lireader[13])

        # 形成轨迹点实体
        trapoi = obj.TraPoi(lon, lat, time, speed, hei, direc, None, None, ttd, None)
        trapoi.status = status
        trapoi.isNoise = isnoise

        # 形成轨迹实体加入planno_trajobj
        if plan_no not in planno_trajobj:
            trajobj = obj.Trajectory(plan_no, truck_no)
            trajobj.tra_poi_list.append(trapoi)
            planno_trajobj[plan_no] = trajobj
        else:
            planno_trajobj[plan_no].tra_poi_list.append(trapoi)

    return planno_trajobj

# 形成planmap
def plan_formed(plan_reader, way_reader):
    '''
    # truckno_planobjlist {车牌号:[调度单实体]}
    # planno_waybillobjlist {调度单号:[运单实体]}
    '''
    # 读调度单表 t_plan 生成 plan_map {调度单号:调度单实体}
    plan_map = {}
    for inx, lireader in enumerate(plan_reader):
        if inx == 0:  # 跳过第一行索引
            continue
        plan_no = lireader[2]
        start_point = lireader[7]
        create_time = datetime.datetime.strptime(lireader[18], '%d/%m/%Y %H:%M:%S')
        plan_obj = obj.pro_vehicle(plan_no, start_point, create_time, None)
        plan_map[plan_no] = plan_obj

    # truckno_planno_map {车牌号:[调度单号]}
    truckno_planno_map = {}

    # 读运单表waybill 生成planno_waybillobjlist {调度单号:[运单实体]}
    planno_waybillobjlist = {}
    for inx, lireader in enumerate(way_reader):
        if inx%100000==0:
            print(inx)
        if inx == 0:  # 跳过第一行索引
            continue
        plan_no = lireader[2]
        truck_no = lireader[11]

        if truckno_planno_map.__contains__(truck_no):
            truckno_planno_map[truck_no].append(plan_no)
        else:
            truckno_planno_map[truck_no] = [plan_no]

        waybill_no = lireader[4]
        start_point = lireader[19]
        end_point = lireader[20]
        consignee_company_id = lireader[16]
        weight = float(lireader[28])
        load_date = datetime.datetime.strptime(lireader[22], '%d/%m/%Y %H:%M:%S')
        if len(lireader[24]) == 0:
            return_date = None
        else:
            return_date = datetime.datetime.strptime(lireader[24], '%d/%m/%Y %H:%M:%S')
        group_driver_name = lireader[53]
        product_name = lireader[25]
        consignee_company_name = lireader[16]  # 未知！！！
        business_type = lireader[32]
        waybillobj = obj.Waybill(truck_no, waybill_no, plan_no, start_point, end_point, consignee_company_id, weight,
                                 load_date, return_date, group_driver_name, product_name, consignee_company_name)
        if planno_waybillobjlist.__contains__(plan_no):
            planno_waybillobjlist[plan_no].append(waybillobj)
        else:
            planno_waybillobjlist[plan_no] = [waybillobj]
    # 用运单的数据更新调度单实体的 返单时间、运输终点列表、运输品种列表、开始运输时间、business_type、运单实体列表
    cnt_plan_return_bill_date_None = 0
    cnt_plan_no_waybill = 0
    cnt_plan_load_date_None = 0
    for plan_no, plan in plan_map.items():
        if plan_no not in planno_waybillobjlist.keys():
            cnt_plan_no_waybill += 1
            continue
        plan.load_date = planno_waybillobjlist[plan_no][0].load_date
        plan.business_type = planno_waybillobjlist[plan_no][0].business_type

        for waybillobj in planno_waybillobjlist[plan_no]:
            plan.waybillobjlist.append(waybillobj)
            plan.end_point_list.append(waybillobj.end_point)
            plan.product_list.append(waybillobj.product_name)

        # 处理返单时间
        for waybillobj in planno_waybillobjlist[plan_no]:
            if waybillobj.return_date == None:
                continue
            if plan.return_bill_date == None:
                plan.return_bill_date = waybillobj.return_date
            else:
                plan.return_bill_date = max(waybillobj.return_date, plan.return_bill_date)
        if plan.return_bill_date == None:
            if plan.load_date == None:
                cnt_plan_load_date_None += 1
            else:
                plan.return_bill_date = plan.load_date + datetime.timedelta(days=1)
            cnt_plan_return_bill_date_None += 1

    return plan_map

def location_formed(point_reader):
    pointid_location = {}
    for inx, lireader in enumerate(point_reader):
        if inx == 0:
            continue
        pointid = lireader[2]  # 地点位置id（string）
        if lireader[16] != '' and lireader[17] != '':
            longitude = float(lireader[16])  # 地点位置经度（float）
            latitude = float(lireader[17])  # 地点位置纬度（float）
            end_longitude = utils.gcj02towgs84(longitude, latitude)[0]
            end_latitude = utils.gcj02towgs84(longitude, latitude)[1]
        if pointid not in pointid_location:
            objloc = obj.location(None, None, None, None, None, end_longitude, end_latitude)
            pointid_location[pointid] = objloc
    return pointid_location




# 对销售业务的所有轨迹进行停留点提取
# planno_staypoilist {调度单号：[staypoi实体]}
# 参数： dis_threshold 距离参数（单位：m）； staytime_threshold 停留时间参数 （单位：s）
def staypoi_from_trajectory(planno_trajectory, dis_threshold, staytime_threshold):
    planno_staypoilist = {}
    for planno in planno_trajectory.keys():  # 对于其中的每一条轨迹
        former_trajpoi = -1  # 前序轨迹点为低速的轨迹点(-1：前序轨迹点不为低速轨迹点，否则为锚点的index)
        for idx, trajpoi in enumerate(planno_trajectory[planno].tra_poi_list[1:]):  # 对于这条轨迹的每个轨迹点
            poi_idx = idx + 1  # 当前POI在tra_poi_list的角标
            if former_trajpoi == -1:  # 如果当前没有锚点
                dis = utils.geo_distance(trajpoi.lat, trajpoi.lon, planno_trajectory[planno].tra_poi_list[idx].lat, planno_trajectory[planno].tra_poi_list[idx].lon)  # 与前一个轨迹点的距离
            else:  # 如果有锚点
                dis = utils.geo_distance(trajpoi.lat, trajpoi.lon, planno_trajectory[planno].tra_poi_list[former_trajpoi].lat, planno_trajectory[planno].tra_poi_list[former_trajpoi].lon)  # 与锚点的距离
            if dis < dis_threshold and former_trajpoi == -1 and poi_idx < len(planno_trajectory[planno].tra_poi_list) - 1:  # 如果该轨迹点还没有锚点且与前序轨迹点的距离小于距离阈值且不是最后一个轨迹点
                staypoint_list = [planno_trajectory[planno].tra_poi_list[idx]]  # 基于当前轨迹点的前序轨迹点创建一个新的停留轨迹点列表
                staypoint_list.append(trajpoi) # 把该点也加入停留点列表
                former_trajpoi = poi_idx # 锚点为后者点
                continue
            if dis < dis_threshold and former_trajpoi != -1 and poi_idx < len(planno_trajectory[planno].tra_poi_list) - 1:  # 如果有锚点且该轨迹点与锚点的距离小于距离阈值且不是最后一个轨迹点
                staypoint_list.append(trajpoi)
                continue
            # 一段停留点提取以后
            if (dis > dis_threshold and former_trajpoi != -1 and poi_idx < len(planno_trajectory[planno].tra_poi_list) - 1) \
                    or (poi_idx == len(planno_trajectory[planno].tra_poi_list) - 1 and former_trajpoi != -1):  # 如果有锚点且该轨迹点与锚点的距离大于距离阈值或者（该轨迹点是最后一个轨迹点且在有锚点的情况下）
                former_trajpoi = -1  # 锚点的标识符改为-1，即没有锚点

                # 取平均经纬度
                lon_all = 0
                lat_all = 0
                for poi in staypoint_list:
                    lon_all += poi.lon
                    lat_all += poi.lat
                lon_avg = lon_all / len(staypoint_list)
                lat_avg = lat_all / len(staypoint_list)

                start_satytime = staypoint_list[0].time  # 取出该停留行为的开始时间（停留时段）
                stay_time = (staypoint_list[-1].time - staypoint_list[0].time).seconds  # 计算该停留行为的停留时间， 单位为秒
                if stay_time > staytime_threshold:  # 如果停留时长大于给定时间阈值
                    truck_no = planno_trajectory[planno].car_mark
                    staypoint = obj.staypoi(lon_avg, lat_avg, staypoint_list, start_satytime, planno, stay_time, truck_no)
                    if planno_staypoilist.__contains__(planno):  # 如果planno_staypoilist中包含planno
                        planno_staypoilist[planno].append(staypoint)
                    else:  # 如果planno_staypoilist中不包含planno
                        planno_staypoilist[planno] = [staypoint]
    return planno_staypoilist

# 形成{销售地点：[调度单实体]}
def form_endp_plannoobj(planno_staypoilist, plan_map, point_location):
    endp_plannoobj = {}
    for planno in planno_staypoilist:# 对每个调度单号
        for end_point in plan_map[planno].end_point_list: # 对调度单号对应的所有销售终点
            if point_location[end_point].longitude == '' and point_location[end_point].latitude == '':
                continue
            if endp_plannoobj.__contains__ (end_point):
                endp_plannoobj[end_point].append(planno)
            else:
                endp_plannoobj[end_point] = [planno]
    return endp_plannoobj


# 形成正确的销售地点[]
def correcting_point(endp_plannoboj, tra_num, ratio, planno_staypoilist, point_location, eps, min_samples):
    correct_points = []
    for end_point, plans in endp_plannoboj.items():
        if len(plans) < tra_num:
            continue
        for plan_no in plans:
            count_c = 0
            for staypoint in planno_staypoilist[plan_no]:
                ed_lat, ed_lon = point_location[end_point].latitude, point_location[end_point].longitude
                dis = utils.geo_distance(staypoint.cen_lat, staypoint.cen_lon, ed_lat, ed_lon)  # 百度坐标系 计算与销售点的距离
                print(dis)
                if dis < 5000:
                    count_c += 1
                    break
        if float(count_c)/float(len(plans)) > ratio:
            correct_points.append(end_point)
    # 对正确的销售地点集进行聚类
    merge_correct_points = []
    cluster_data = []  # 用于存储聚类的数据 格式[[P1.lat,P1.lon], ....,[Pn.lat,Pn.lon]]
    for point in correct_points:
        cluster_data.append([point_location[point].latitude, point_location[point].longitude])
    X = np.array(cluster_data)
    db = sc.DBSCAN(eps, min_samples).fit(X)
    labels = db.labels_  # 返回聚类簇标号列表
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)  # 获取的簇的数量（除去簇标号-1）
    for i in range(n_clusters_):  # 对于每一个簇
        index_in_poilist = np.where(labels == i)[0]  # 取出在labels中为簇标签i的下标，返回数组
        one_cluster_stpid = []
        for idx in index_in_poilist:
            one_cluster_stpid.append(correct_points[idx])
        merge_correct_points.append(one_cluster_stpid)
    return correct_points, merge_correct_points



