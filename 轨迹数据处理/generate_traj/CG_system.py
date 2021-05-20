import obj_class as obj
import datetime
import numpy as np
import bisect


# 形成 truckno_trapoilist  (input：tra_reader, month: '11/2020')
def traj_formed(tra_reader, month):
    truckno_trapoilist = {}
    for inx, lireader in enumerate(tra_reader):
        if inx%1000000==0:
            print('finish:',inx)
        if inx == 0 or lireader[2][lireader[2].index('/')+1 : lireader[2].index(' ')] != month: # 跳过第一行索引，只导出某个月数据
            continue
        truck_no = lireader[1] # 车牌号
        time = datetime.datetime.strptime(lireader[2], "%d/%m/%Y %H:%M:%S") # 时间
        latitude = float(lireader[3]) # 纬度
        longitude = float(lireader[4]) # 经度
        speed = float(lireader[6]) # 速度
        height = float(lireader[7]) # 海拔
        total_distance = float(lireader[5]) # 总行驶距离
        # 方向（有些数据没有方向）
        direction = float(lireader[8]) if lireader[8] != '' else ''
        # 创建轨迹点实例
        trapoi_new = obj.TraPoi(longitude, latitude, time, speed, height, direction, None, None, total_distance, None)
        if truckno_trapoilist.__contains__(truck_no): # 结构已包括该车牌
            truckno_trapoilist[truck_no].append(trapoi_new)
        else: # 结构未包括该车牌
            truckno_trapoilist[truck_no] = [trapoi_new]
    for trapoi in truckno_trapoilist.values():
        trapoi.sort(key = lambda x: x.time) # 对每个车牌号对应轨迹点按时间排序
    for truckno, trapoi in truckno_trapoilist.items():
        new_trajectoryobj = []
        new_trajectoryobj.append(trapoi[0]) # 轨迹初始点
        for inx, tra_poi in enumerate(trapoi[1:]):  # 对于重复的轨迹点进行删除
            if tra_poi.time != trapoi[inx].time:
                new_trajectoryobj.append(tra_poi)
        truckno_trapoilist[truckno] = new_trajectoryobj
    return truckno_trapoilist



def match_planno_trajobj(truckno_trapoilist, truckno_planobj):
    '''
    # truckno_trapoilist {车牌号:[轨迹点实体]}
    # truckno_planobj {车牌号:[调度单实体]}
    '''
    planno_trajobj = {}
    for truck_no in truckno_planobj.keys():
        if truck_no not in truckno_trapoilist.keys():
            continue
        plans = truckno_planobj[truck_no] # 车牌号对应调度单集

        all_trapoilist = truckno_trapoilist[truck_no] # 车牌号下所有轨迹点集
        for plan in plans:
            plan_no = plan.plan_no
            create_time = plan.create_time # 任务创建时间
            load_time = plan.load_date # 任务开始时间
            return_time = plan.return_bill_date # 任务返单时间

            # 轨迹分段（二分）
            times = list(tmp.time for tmp in all_trapoilist)
            leftbound = bisect.bisect_left(times, create_time)
            rightbound = bisect.bisect_left(times, return_time+datetime.timedelta(seconds=1))
            tmp_trapoilist = all_trapoilist[leftbound: rightbound]

            # 标记status
            for trapoi in tmp_trapoilist:
                trapoi.status = 1 if (trapoi.time < return_time and trapoi.time >= load_time)  else 0
            # 生成 {调度单号:轨迹实体}
            objtrage = obj.Trajectory(plan_no, truck_no)
            objtrage.tra_poi_list = tmp_trapoilist
            planno_trajobj[plan_no] = objtrage
    # 运单数据没有该时间段车牌号的情况
    wrongtrage_truckno = set(list(truckno_trapoilist.keys())) - set(list(truck.car_mark for truck in planno_trajobj.values()))
    #print(wrongtrage_truckno)
    return planno_trajobj


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
        if inx%10000==0:
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


    # 根据 truckno_planno_map {车牌号:[调度单号]} 生成 truckno_planobj {车牌号:[调度单实体]}
    # 从 plan_map {调度单号:调度单实体} 中找
    cnt_truckno_no_plan = 0
    truckno_planobjlist = {}
    for truck_no, planno_list in truckno_planno_map.items():
        planno_list = list(set(planno_list))  # 对 truckno_planno_map {车牌号:[调度单号]} 中的调度单号列表去重
        truckno_planobjlist[truck_no] = []
        for planno in planno_list:
            if plan_map.__contains__(planno):
                truckno_planobjlist[truck_no].append(plan_map[planno])
            else:
                cnt_truckno_no_plan += 1
        truckno_planobjlist[truck_no].sort(key=lambda x: x.create_time)

    print('车牌号有运单号，但运单表没有 的个数', cnt_truckno_no_plan)
    print('调度单总数', len(plan_map))
    print('调度单没有对应的运单的个数', cnt_plan_no_waybill)
    print('调度单的load_date为None的个数', cnt_plan_load_date_None)
    print('调度单返单时间为None的个数', cnt_plan_return_bill_date_None)
    return truckno_planobjlist, planno_waybillobjlist, plan_map



def tra_preprocess(planno_trajobj: {str: obj.Trajectory}, plan_map: {str: obj.pro_vehicle}):
    '''
    :param planno_trajobj:{调度单号:轨迹实体}
    :param plan_map: {调度单号:调度单实体}
    :return: planno_trajobj {调度单号:轨迹实体}
    '''
    cnt_traj_no_plan = 0
    cnt_tra_noise_1 = 0
    cnt_tra_noise_2 = 0
    cnt_speed_noise = 0
    for plan_no, trajobj in planno_trajobj.items():
        if plan_map.__contains__(plan_no) == False:
            cnt_traj_no_plan += 1
            continue
        planobj = plan_map[plan_no]  # type:obj.pro_vehicle
        create_time = planobj.create_time
        load_date = planobj.load_date
        return_bill_date = planobj.return_bill_date

        delta = return_bill_date - load_date  # type:datetime.datetime
        if delta.total_seconds() <= 600:
            cnt_tra_noise_1 += 1
            trajobj.noise_type = 1

        delta = load_date - create_time
        if delta.total_seconds() >= 24*3600:
            cnt_tra_noise_2 += 1
            trajobj.noise_type = 2

        # 判断轨迹点是否为噪声点
        for poi in trajobj.tra_poi_list:
            if poi.speed > 120:
                cnt_speed_noise += 1
                poi.isNoise = 1

    print('轨迹实体没有调度单信息的个数', cnt_traj_no_plan)
    print('开始即返单的情况个数', cnt_tra_noise_1)
    print('开始运输与运单创建间隔时间较长的个数', cnt_tra_noise_2)
    print('轨迹点噪声的个数', cnt_speed_noise)
    return planno_trajobj



