import csv
import CG_system as cg_sys

print("开始读取轨迹数据")
# planno_trajectory实体  {调度单号:轨迹实体}
tra_reader = csv.reader(open('dd_truck_location_zjxl.csv', encoding= 'utf-8'))
truckno_trapoilist = cg_sys.traj_formed(tra_reader, '11/2020') # {调度单号: class{车牌号，轨迹点集}}
print("读取轨迹数据结束")

print("开始读取调度单和运单数据")
# plan_map {调度单号：调度单实体}
# truckno_planobjlist {车牌号:[调度单实体]}
# planno_waybillobjlist {调度单号:[运单实体]}
plan_reader = csv.reader(open("ods_db_trans_t_plan.csv", encoding='utf-8'))
way_reader = csv.reader(open("dwd_waybill.csv", encoding='utf-8'))
truckno_planobjlist, planno_waybillobjlist ,plan_map = cg_sys.plan_formed(plan_reader, way_reader)
print("读取调度单和运单数据结束")

# 车牌号：轨迹点实体 车牌号：调度单实体
planno_trajobj = cg_sys.match_planno_trajobj(truckno_trapoilist, truckno_planobjlist) # {调度单号：轨迹实体()}

# 噪声数据处理
planno_trajobj = cg_sys.tra_preprocess(planno_trajobj, plan_map)

# 写出csv文件
with open('results.csv','w') as f:
    spamwriter = csv.writer(f, dialect='excel')
    spamwriter.writerow(['planno', 'create_time', 'load_date', 'return_time', 'truckno', 'time', 'lon', 'lat', 'speed', 'height',
                         'direction', 'total_distance', 'status', 'isnoise'])
    for planno, trajobj in planno_trajobj.items():
        #planno
        create_time = str(plan_map[planno].create_time)
        load_date = str(plan_map[planno].load_date)
        return_time = str(plan_map[planno].return_bill_date)
        truckno = str(trajobj.car_mark)
        for trapoi in trajobj.tra_poi_list:
            time = str(trapoi.time)
            lon = str(trapoi.lon)
            lat = str(trapoi.lat)
            speed = str(trapoi.speed)
            height = str(trapoi.height)
            direction = str(trapoi.direction)
            total_distance = str(trapoi.total_distance)
            status = str(trapoi.status)
            isnoise = str(trapoi.isNoise)
            spamwriter.writerow([planno, create_time, load_date, return_time, truckno, time, lon, lat, speed, height,
                                 direction, total_distance, status, isnoise])

