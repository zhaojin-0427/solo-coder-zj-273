from .constants import COLOR_COMBINATIONS, STYLE_MATCH


categories = ['项链', '耳环', '手链', '戒指', '胸针', '发饰', '其他']

materials = ['黄金', '白金', '玫瑰金', '纯银', '合金', '珍珠', '水晶', '宝石', '玉石', '布料', '皮革', '其他']

color_families = ['金色', '银色', '玫瑰金', '白色', '黑色', '红色', '粉色', '蓝色', '绿色', '紫色', '米色', '棕色', '灰色', '黄色']

styles = ['优雅', '休闲', '复古', '简约', '华丽', '波西米亚', '甜美', '民族风', '商务', '运动']

occasions = ['日常', '工作', '约会', '派对', '婚礼', '晚宴', '旅行', '运动', '节日', '正式场合']

accessory_statuses = [
    {'value': 'in_stock', 'label': '在库'},
    {'value': 'lent', 'label': '已借出'},
    {'value': 'overdue', 'label': '逾期未还'},
    {'value': 'maintenance', 'label': '保养中'},
    {'value': 'repair', 'label': '维修中'},
    {'value': 'lost', 'label': '已丢失'},
    {'value': 'inventory_exception', 'label': '盘点异常'}
]

maintenance_statuses = [
    {'value': 'excellent', 'label': '极佳'},
    {'value': 'good', 'label': '良好'},
    {'value': 'fair', 'label': '一般'},
    {'value': 'poor', 'label': '较差'}
]

cert_types = ['购买发票', '珠宝鉴定证书', '品牌证书', '保修卡', 'GIA证书', 'NGTC证书', '其他']

inventory_batch_types = [
    {'value': 'annual', 'label': '年度盘点'},
    {'value': 'quarterly', 'label': '季度盘点'},
    {'value': 'monthly', 'label': '月度盘点'},
    {'value': 'temporary', 'label': '临时盘点'}
]

inventory_exception_types = ['缺失', '损坏', '证书不全', '位置不符', '借出未登记', '其他']

insurance_statuses = [
    {'value': 'active', 'label': '有效'},
    {'value': 'expired', 'label': '已过期'},
    {'value': 'pending', 'label': '待续保'}
]

risk_levels = [
    {'value': 'low', 'label': '低风险'},
    {'value': 'medium', 'label': '中风险'},
    {'value': 'high', 'label': '高风险'},
    {'value': 'critical', 'label': '严重风险'}
]

purchase_channels = ['品牌专柜', '官方网店', '珠宝店', '代购', '二手市场', '亲友赠送', '其他']

insurance_companies = ['中国平安', '中国人保', '太平洋保险', '泰康保险', '友邦保险', '其他']


def get_color_score(acc_color_family, main_color):
    matches = COLOR_COMBINATIONS.get(main_color, [])
    if acc_color_family == main_color:
        return 10
    if acc_color_family in matches:
        return 8
    return 3


def get_style_score(acc_style, target_style):
    matches = STYLE_MATCH.get(target_style, [])
    if acc_style == target_style:
        return 10
    if acc_style in matches:
        return 6
    return 2


def get_occasion_score(acc, occasion):
    if not occasion:
        return 5
    acc_occasions = acc.occasions.split(',') if acc.occasions else []
    if occasion in acc_occasions:
        return 10
    return 4


def get_wear_frequency_label(wear_count):
    if wear_count >= 50:
        return '高频'
    elif wear_count >= 20:
        return '中频'
    elif wear_count >= 5:
        return '低频'
    return '极少'
