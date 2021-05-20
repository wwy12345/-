import csv
import CG_system as cg_sys

# 构建轨迹数据实例
print('开始读取轨迹数据')
tra_reader = csv.reader(open('C:\\Users\\吴问宇\\Desktop\\轨迹数据处理\\results.csv'))
planno_trajobj = cg_sys.formtraj(tra_reader)
print('读取轨迹数据结束')

print("开始读取调度单和运单数据")
# plan_map {调度单号：调度单实体}
plan_reader = csv.reader(open("C:\\Users\\吴问宇\\Desktop\\轨迹数据处理\\ods_db_trans_t_plan.csv", encoding='utf-8'))
way_reader = csv.reader(open("C:\\Users\\吴问宇\\Desktop\\轨迹数据处理\\dwd_waybill.csv", encoding='utf-8'))
plan_map = cg_sys.plan_formed(plan_reader, way_reader)
print("读取调度单和运单数据结束")

print("开始获得point地点")
locreader = csv.reader(open('C:\\Users\\吴问宇\\Desktop\\轨迹数据处理\\ods_db_sys_t_point.csv', encoding = 'utf-8'))
point_location = cg_sys.location_formed(locreader)
print("获得point地点结束")



print("开始停留点提取")
# planno_staypoilist {调度单号：[staypoi实体]}
planno_staypoilist = cg_sys.staypoi_from_trajectory(planno_trajobj, 50, 480)
print(list(t.time for t in planno_staypoilist['DD201101002226'][0].staypoilist))
print(list(t.time for t in planno_staypoilist['DD201101002226'][1].staypoilist))
print('结束停留点提取')

print('开始生成销售点-调度单')
# endp_plannoobj {地点编号：[调度单实体]}
endp_plannoobj = cg_sys.form_endp_plannoobj(planno_staypoilist, plan_map, point_location)
print('结束生成销售点-调度单')

print('开始生成正确采购地点集')
# correct_point [正确的采购地点id]
correct_points, merge_correct_points= cg_sys.correcting_point(endp_plannoobj, 1, 0.4, planno_staypoilist, point_location, 0.0008, 2)
print(correct_points)
print(merge_correct_points)
print('结束生成正确采购地点集')

# 2 0.4 ['P000047319', 'P000015672', 'P000001904', 'P000044407', 'P000001436', 'P000006054', 'P000005591', 'P000020125', 'P000022393', 'P000006545', 'P000006176', 'P000000716', 'P000005440', 'P000014524', 'P000022797', 'P000003199', 'P000045042', 'P000003868', 'P000023347', 'P000045198', 'P000020464', 'P000005878', 'P000017907', 'P000000725', 'P000013817', 'P000002490', 'P000023168', 'P000015651', 'P000001310', 'PS10001629', 'P000023140', 'P000022755', 'P000022382', 'P000002806', 'P000023484', 'P000015184', 'PS10001436', 'P000005000', 'P000019288', 'P000009162', 'P000021581', 'P000003170', 'P000046003', 'P000023353', 'P000023165', 'P000022293', 'P000047275', 'P000021705', 'P000006674', 'P000003334', 'P000045504', 'P000002888', 'P000023013', 'P000011455', 'P000014531', 'P000018053', 'P000001098', 'P000005680', 'P000019190', 'P000044532', 'P000015045']