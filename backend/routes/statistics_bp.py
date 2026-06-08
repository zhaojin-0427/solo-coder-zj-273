from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
from backend.extensions import db
from backend.models import (
    Accessory,
    OutfitFavorite,
    TripPlan,
    TripDay,
    TripItem,
    LoanRecord,
    MaintenanceRecord,
    ValuationRecord,
    CertificateAttachment,
    InventoryBatch,
    InventoryItem,
    InventoryException,
    InsuranceItem
)
from backend.services import compute_statistics, calculate_valuation
from backend.utils.constants import status_label_map

bp = Blueprint('statistics', __name__, url_prefix='/api')


@bp.route('/statistics', methods=['GET'])
def get_statistics():
    all_acc = Accessory.query.filter_by(is_lost=False).all()
    total_count = len(all_acc)

    total_value = 0.0
    total_purchase = 0.0
    category_count = defaultdict(int)
    color_count = defaultdict(int)
    style_count = defaultdict(int)
    storage_count = defaultdict(int)
    status_count = defaultdict(int)

    for acc in all_acc:
        val = calculate_valuation(acc)
        total_value += val['estimated_value']
        total_purchase += float(acc.purchase_price or 0)
        category_count[acc.category or '未分类'] += 1
        color_count[acc.color_family or '未标记'] += 1
        style_count[acc.style or '未标记'] += 1
        storage_count[acc.storage_location or '未标记位置'] += 1
        status_count[status_label_map.get(acc.get_status(), acc.get_status())] += 1

    trip_count = TripPlan.query.count()
    favorite_count = OutfitFavorite.query.count()
    loan_count = LoanRecord.query.count()
    active_loan = LoanRecord.query.filter_by(returned=False).count()
    today_str = datetime.now().strftime('%Y-%m-%d')
    overdue_loan = LoanRecord.query.filter_by(returned=False).filter(
        LoanRecord.due_date != '',
        LoanRecord.due_date < today_str
    ).count()
    maintenance_count = MaintenanceRecord.query.count()
    active_maintenance = MaintenanceRecord.query.filter_by(completed=False).count()
    valuation_count = ValuationRecord.query.count()
    cert_count = CertificateAttachment.query.count()
    insurance_count = InsuranceItem.query.count()
    active_insurance = InsuranceItem.query.filter_by(status='active').count()
    expiring_insurance = InsuranceItem.query.filter(
        InsuranceItem.status == 'active',
        InsuranceItem.end_date != '',
        InsuranceItem.end_date <= (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    ).count()

    today = datetime.now()
    last_30_days = today - timedelta(days=30)
    wear_count_last_30 = 0
    for acc in all_acc:
        if acc.last_worn_date:
            try:
                last_worn = datetime.strptime(acc.last_worn_date, '%Y-%m-%d')
                if last_worn >= last_30_days:
                    wear_count_last_30 += 1
            except:
                pass

    unused_30 = total_count - wear_count_last_30

    active_batch_count = InventoryBatch.query.filter_by(status='in_progress').count()
    unresolved_exception = InventoryException.query.filter_by(resolved=False).count()

    category_stats = sorted([{'name': k, 'count': v, 'percentage': round(v / max(total_count, 1) * 100, 1)} for k, v in category_count.items()], key=lambda x: -x['count'])
    color_stats = sorted([{'name': k, 'count': v} for k, v in color_count.items()], key=lambda x: -x['count'])
    style_stats = sorted([{'name': k, 'count': v} for k, v in style_count.items()], key=lambda x: -x['count'])
    storage_stats = sorted([{'name': k, 'count': v} for k, v in storage_count.items()], key=lambda x: -x['count'])
    status_stats = [{'name': k, 'count': v} for k, v in status_count.items()]

    monthly_add = defaultdict(int)
    for acc in all_acc:
        if acc.purchase_date:
            try:
                key = acc.purchase_date[:7]
                monthly_add[key] += 1
            except:
                pass
    monthly_add_list = sorted([{'month': k, 'count': v} for k, v in monthly_add.items()], key=lambda x: x['month'])

    monthly_wear = defaultdict(int)
    for acc in all_acc:
        if acc.last_worn_date:
            try:
                key = acc.last_worn_date[:7]
                monthly_wear[key] += acc.wear_count or 0
            except:
                pass
    monthly_wear_list = sorted([{'month': k, 'count': v} for k, v in monthly_wear.items()], key=lambda x: x['month'])

    return jsonify({
        'total_accessories': total_count,
        'total_asset_value': round(total_value, 2),
        'total_purchase_value': round(total_purchase, 2),
        'average_value_per_item': round(total_value / max(total_count, 1), 2),
        'depreciation_rate': round((1 - total_value / max(total_purchase, 1)) * 100, 1) if total_purchase > 0 else 0,
        'category_distribution': category_stats,
        'color_distribution': color_stats,
        'style_distribution': style_stats,
        'storage_distribution': storage_stats,
        'status_distribution': status_stats,
        'trips': {
            'total_count': trip_count,
            'total_days': 0,
            'accessory_usage_rate': 0
        },
        'favorites': {
            'total_count': favorite_count,
            'top_accessories': []
        },
        'tracking': {
            'loan_total': loan_count,
            'loan_active': active_loan,
            'loan_overdue': overdue_loan,
            'maintenance_total': maintenance_count,
            'maintenance_active': active_maintenance
        },
        'valuation': {
            'total_records': valuation_count,
            'total_value': round(total_value, 2)
        },
        'certificates': {
            'total_count': cert_count
        },
        'insurance': {
            'total_count': insurance_count,
            'active_count': active_insurance,
            'expiring_count': expiring_insurance,
            'total_insured_value': round(sum((float(i.coverage_amount) for i in InsuranceItem.query.filter_by(status='active').all() if i.coverage_amount), 0.0), 2)
        },
        'wear_stats': {
            'wear_last_30_days': wear_count_last_30,
            'unused_30_days': unused_30,
            'unworn_count': len([a for a in all_acc if (a.wear_count or 0) == 0]),
            'monthly_wear_trend': monthly_wear_list
        },
        'inventory': {
            'active_batch_count': active_batch_count,
            'unresolved_exceptions': unresolved_exception
        },
        'monthly_growth_trend': monthly_add_list
    })


@bp.route('/meta', methods=['GET'])
def get_meta():
    all_acc = Accessory.query.filter_by(is_lost=False).all()
    categories = sorted(set([a.category for a in all_acc if a.category]))
    color_families = sorted(set([a.color_family for a in all_acc if a.color_family]))
    styles = sorted(set([a.style for a in all_acc if a.style]))
    storages = sorted(set([a.storage_location for a in all_acc if a.storage_location]))
    occasions = sorted(set([o.strip() for a in all_acc if a.occasions for o in a.occasions.split(',') if o.strip()]))

    today = datetime.now()
    cert_types = sorted(set([c.cert_type for c in CertificateAttachment.query.all() if c.cert_type]))
    insurance_providers = sorted(set([i.insurance_company for i in InsuranceItem.query.all() if i.insurance_company]))
    insurance_types = []
    maintenance_types = sorted(set([m.record_type for m in MaintenanceRecord.query.all() if m.record_type]))

    return jsonify({
        'categories': categories,
        'color_families': color_families,
        'styles': styles,
        'storage_locations': storages,
        'occasions': occasions,
        'statuses': [
            {'key': 'in_stock', 'label': '在库'},
            {'key': 'lent', 'label': '已借出'},
            {'key': 'overdue', 'label': '逾期未还'},
            {'key': 'maintenance', 'label': '保养中'},
            {'key': 'lost', 'label': '已丢失'}
        ],
        'certificate_types': ['鉴定证书', '购买凭证', '保险单据', '保修卡', '其他'] + [c for c in cert_types if c not in ['鉴定证书', '购买凭证', '保险单据', '保修卡', '其他']],
        'insurance_types': ['财产险', '运输险', '境外旅行险', '特殊藏品险'] + [t for t in insurance_types if t not in ['财产险', '运输险', '境外旅行险', '特殊藏品险']],
        'insurance_providers': insurance_providers,
        'maintenance_types': ['清洁', '保养', '维修', '翻新'] + [t for t in maintenance_types if t not in ['清洁', '保养', '维修', '翻新']],
        'maintenance_statuses': [
            {'key': 'scheduled', 'label': '已预约'},
            {'key': 'in_progress', 'label': '进行中'},
            {'key': 'completed', 'label': '已完成'}
        ],
        'loan_statuses': [
            {'key': 'lent', 'label': '借出中'},
            {'key': 'returned', 'label': '已归还'},
            {'key': 'overdue', 'label': '逾期未还'}
        ],
        'risk_levels': [
            {'key': 'low', 'label': '低风险'},
            {'key': 'medium', 'label': '中风险'},
            {'key': 'high', 'label': '高风险'},
            {'key': 'critical', 'label': '严重风险'}
        ],
        'wear_frequencies': [
            {'key': 'daily', 'label': '日常佩戴', 'days': 30},
            {'key': 'frequent', 'label': '经常佩戴', 'days': 90},
            {'key': 'occasional', 'label': '偶尔佩戴', 'days': 180},
            {'key': 'rare', 'label': '极少佩戴', 'days': 365},
            {'key': 'unused', 'label': '未使用', 'days': None}
        ],
        'valuation_date': today.strftime('%Y-%m-%d'),
        'today': today.strftime('%Y-%m-%d')
    })
