# 轨迹类
class Trajectory:
    def __init__(self, plan_no, car_mark):
        self.car_mark = car_mark  # 车牌号 str
        self.plan_no = plan_no  # 调度单号 str
        self.tra_poi_list = []  # 轨迹点列表 list
        self.noise_type = 0

# 轨迹点类
class TraPoi:
    def __init__(self, longitude, latitude, time, speed, height, direction, road_id, road_level, total_distance, distance_to_road):
        self.lon = longitude  # 经度 float
        self.lat = latitude  # 维度 float
        self.time = time  # 发生时间 datetime
        self.speed = speed  # 瞬时速度 float
        self.height = height  # 高度 float
        self.direction = direction  # 方向（0-360度） float
        self.road_id = road_id  # 匹配路段的id str
        self.road_level = road_level  # 匹配路段的级别 str
        self.total_distance = total_distance  # 总的行驶里程 float
        self.distance_to_road = distance_to_road  # 与最近路段的距离 float
        self.status = 0  # 接单-装货 0， 开始运输-返单 1 初始化为0 str
        self.isNoise = 0  # 正常轨迹点 0， 噪声轨迹点 1  初始化为0 str


# 运单
class Waybill:
    def __init__(self, truck_no, waybill_no, plan_no, start_point, end_point, consignee_company_id, weight, load_date, return_date,\
                 group_driver_name, product_name, consignee_company_name):
        self.truck_no = truck_no  # 车牌号 str
        self.waybill_no = waybill_no  # 运单号 str
        self.business_type = 0  # 运输业务类型 str 说明 0：销售运输业务（对应原始运单表中非012字段）；1：采购运输业务（对应原始运单表中的012字段）
        self.plan_no = plan_no  # 调度单号（唯一的运单标识）str
        self.start_point = start_point  # 起点id str
        self.end_point = end_point  # 终点id str
        self.consignee_company_id = consignee_company_id  # 收货单位 str
        self.consignee_company_name = consignee_company_name  # 收货单位名称 str
        self.weight = weight  # 重量 float
        self.load_date = load_date  # 出厂时间 datetime
        self.return_date = return_date  # 返单时间 datetime
        self.product_name = product_name  # 运输品种 str
        self.group_driver_name = group_driver_name  # 车队名


# 车次类 （调度单类）
class pro_vehicle:
    def __init__(self, plan_no, start_point, create_time, return_bill_date):
        self.plan_no = plan_no  # 主装车清单号 str
        self.waybillobjlist = []  # 运单实体列表 list
        self.business_type = 0  # 对应运单列表中运单的business_type值 （一个调度单对应的所有运单都只能是一种运输业务）初始化为销售运输业务
        self.start_point = start_point  # 起始地点列表 str （起始地点都只可能是一个地点）
        self.end_point_list = []  # 运输终点列表 list （由于销售运输业务中可能存在多个卸货点的情况）
        self.product_list = []  # 运输品种列表 list（由于对于一次销售运输业务可能涉及多个货物品种）
        self.create_time = create_time  # 调度单创建时间 datetime (比出厂时间即开始运输时间早)
        self.load_date = None  # 开始运输时间 获取waybillobjlist中运单实体的load_date datetime
        self.return_bill_date = return_bill_date  # 返单时间 datetime


# 地址类
class location:
    def __init__(self, company_id, address, province_name, city_name, district_name, longitude, latitude):
        self.company_id_list = [company_id]  # 该地址对应的公司 list
        self.point_type = 0  # 0：成品 1:采购 2：采购&成屏（默认成品） str
        self.address = address  # 详细地址 str
        self.province_name = province_name  # 省名 str
        self.city_name = city_name  # 市名 str
        self.district_name = district_name  # 区名 str
        self.longitude = longitude  # 经度 float
        self.latitude = latitude  # 纬度 float
        self.ischange = 0  # 经纬度是否被修改，默认没有被修改（0）,被修正（1），由于轨迹太少没有修正（2） str
        self.ismerge = 0  # 该终点是否被合并，默认没有合并 str
        self.isseparate = 0  # 该终点是否被分隔为多个运输终点，默认没有分隔 str
        self.formerlocid = None  # 地址库中修改之前的地址id str


# 停留点类
class staypoi:
    def __init__(self, cen_lon, cen_lat, staypoilist, start_staytime, plan_no, stay_time, truck_no):
        self.cen_lon = cen_lon  # 中心点经度 float
        self.cen_lat = cen_lat  # 中心点纬度 float
        self.staypoilist = staypoilist  # 低速轨迹点列表 list
        self.start_staytime = start_staytime  # 停留发生时间 datetime
        self.plan_no = plan_no  # 停留点对应的调度单号 str
        self.next_CGname = None  # 如果该运单对应的下一次运单为采购类型的运单，则为下一次采购地址的名称，如果下一次运单为成品，则为None str
        self.stay_time = stay_time  # 停留时间 float
        self.truck_no = truck_no  # 车牌号 str
        self.all_distance_to_startpoi = None


# 停留区域
class stayRegion:
    def __init__(self, vertex_list, staypoiobj_list, cen_lon, cen_lat):
        self.type = None  # 停留区域的类型（1：运输终点；2：限制型休息区；3：非限制型休息区；4：加油站）
        self.vertex_list = vertex_list  # 多边形顶点的列表（如由ABCD四个点组成的区域,则该属性表示为[(A.lon,A.lat),(B.lon,B.lat),(C.lon,C.lat),(D.lon,D .lat)]）
        self.cen_lon = cen_lon  # 区域的中心点经度
        self.cen_lat = cen_lat  # 区域的中心点纬度
        self.staypoiobj_list = staypoiobj_list  # 该区域中停留点实体(staypoi类的实体)的列表
        self.feature = []  # 特征向量