from datetime import datetime, timedelta
from collections import defaultdict
from backend.models import (
    Accessory, OutfitFavorite, TripPlan, TripItem, LoanRecord,
    MaintenanceRecord, ValuationRecord, CertificateAttachment,
    InventoryBatch, InventoryException, InsuranceItem
)
from backend.services.valuation_service import calculate_valuation


def compute_statistics():
    all_acc = Accessory.query.all()
    total = len(all_acc)

    color_stats = {}
    category_stats = {}
    for acc in all_acc:
        color_stats[acc.color_family] = color_stats.get(acc.color_family, 0) + 1
        category_stats[acc.category] = category_stats.get(acc.category, 0) + 1

    color_distribution = [
        {'color': c, 'count': cnt, 'percentage': round(cnt / total * 100, 1) if total else 0}
        for c, cnt in sorted(color_stats.items(), key=lambda x: -x[1])
    ]

    favs = OutfitFavorite.query.order_by(OutfitFavorite.use_count.desc()).limit(10).all()
    frequent_combos = [f.to_dict() for f in favs if f.use_count > 0]

    today = datetime.now()
    long_unworn = []
    for acc in all_acc:
        if not acc.last_worn_date:
            days = (today - acc.created_at).days if acc.created_at else 999
        else:
            try:
                lw = datetime.strptime(acc.last_worn_date, '%Y-%m-%d')
                days = (today - lw).days
                if days < 0:
                    days = 0
            except:
                days = 999
        if days >= 30:
            d = acc.to_dict()
            d['days_unworn'] = days
            long_unworn.append(d)
    long_unworn.sort(key=lambda x: -x['days_unworn'])

    total_wears = sum(a.wear_count for a in all_acc)
    utilization_rate = round(total_wears / max(total, 1) / max(1, 30) * 100, 1)

    worn_30d = 0
    for acc in all_acc:
        if acc.last_worn_date:
            try:
                lw = datetime.strptime(acc.last_worn_date, '%Y-%m-%d')
                days_diff = (today - lw).days
                if 0 <= days_diff <= 30:
                    worn_30d += 1
            except:
                pass
    active_rate = round(worn_30d / max(total, 1) * 100, 1)

    all_trips = TripPlan.query.all()
    trip_count = len(all_trips)
    trip_packing_stats = []
    trip_color_stats = {}
    unpacked_reminders = []
    total_trip_items = 0
    total_trip_packed = 0
    total_trip_unique_acc = set()
    trip_acc_usage_count = {}

    for trip in all_trips:
        trip_total = 0
        trip_packed = 0
        trip_unique = set()
        for day in trip.days:
            for item in day.items:
                trip_total += 1
                total_trip_items += 1
                if item.packed:
                    trip_packed += 1
                    total_trip_packed += 1
                else:
                    acc = Accessory.query.get(item.accessory_id)
                    if acc and acc.get_status() == 'in_stock':
                        unpacked_reminders.append({
                            'trip_id': trip.id,
                            'trip_name': trip.name,
                            'day_index': day.day_index + 1,
                            'date': day.date,
                            'accessory': acc.to_dict(),
                            'item_id': item.id,
                            'is_spare': item.is_spare
                        })
                trip_unique.add(item.accessory_id)
                total_trip_unique_acc.add(item.accessory_id)
                acc = Accessory.query.get(item.accessory_id)
                if acc:
                    if acc.color_family not in trip_color_stats:
                        trip_color_stats[acc.color_family] = 0
                    trip_color_stats[acc.color_family] += 1
                    if acc.id not in trip_acc_usage_count:
                        trip_acc_usage_count[acc.id] = 0
                    trip_acc_usage_count[acc.id] += 1

        trip_packing_stats.append({
            'trip_id': trip.id,
            'trip_name': trip.name,
            'destination': trip.destination,
            'start_date': trip.start_date,
            'end_date': trip.end_date,
            'status': trip.status,
            'total_items': trip_total,
            'packed_items': trip_packed,
            'unique_count': len(trip_unique),
            'packing_rate': round(trip_packed / max(trip_total, 1) * 100, 1)
        })

    trip_packing_stats.sort(key=lambda x: x['start_date'], reverse=True)

    total_trip_color_count = sum(trip_color_stats.values())
    trip_color_distribution = [
        {'color': c, 'count': cnt, 'percentage': round(cnt / max(total_trip_color_count, 1) * 100, 1)}
        for c, cnt in sorted(trip_color_stats.items(), key=lambda x: -x[1])
    ]

    trip_plan_utilization = round(len(total_trip_unique_acc) / max(total, 1) * 100, 1) if total > 0 else 0

    upcoming_trips = []
    today_str = today.strftime('%Y-%m-%d')
    for trip in all_trips:
        if trip.start_date and trip.start_date >= today_str:
            upcoming_trips.append({
                'id': trip.id,
                'name': trip.name,
                'destination': trip.destination,
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'status': trip.status
            })
    upcoming_trips.sort(key=lambda x: x['start_date'])

    all_loans = LoanRecord.query.all()
    active_loans = [l for l in all_loans if not l.returned]
    overdue_loans = []
    for l in active_loans:
        if l.due_date:
            try:
                due = datetime.strptime(l.due_date, '%Y-%m-%d')
                if today > due:
                    overdue_loans.append(l)
            except:
                pass

    all_maint = MaintenanceRecord.query.all()
    active_maint = [m for m in all_maint if not m.completed]
    completed_maint = [m for m in all_maint if m.completed]
    total_maint_cost = sum(m.cost for m in completed_maint)

    monthly_cost = defaultdict(float)
    for m in completed_maint:
        if m.completed_date:
            try:
                d = datetime.strptime(m.completed_date, '%Y-%m-%d')
                key = d.strftime('%Y-%m')
                monthly_cost[key] += m.cost
            except:
                pass
    cost_trend = sorted([{'month': k, 'cost': round(v, 2)} for k, v in monthly_cost.items()])

    repair_count = defaultdict(int)
    for m in all_maint:
        if m.record_type == 'repair':
            repair_count[m.accessory_id] += 1
    high_risk = []
    for aid, cnt in repair_count.items():
        if cnt >= 2:
            acc = Accessory.query.get(aid)
            if acc:
                d = acc.to_dict()
                d['repair_count'] = cnt
                total_cost = sum(m.cost for m in all_maint if m.accessory_id == aid)
                d['total_repair_cost'] = round(total_cost, 2)
                high_risk.append(d)
    high_risk.sort(key=lambda x: -x['repair_count'])

    maintenance_reminders = []
    future_30d = (today + timedelta(days=30)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    for acc in all_acc:
        if acc.next_maintenance_date:
            try:
                nd = datetime.strptime(acc.next_maintenance_date, '%Y-%m-%d')
                if today_str <= acc.next_maintenance_date <= future_30d:
                    d = acc.to_dict()
                    d['days_until'] = (nd - today).days
                    maintenance_reminders.append(d)
            except:
                pass
    maintenance_reminders.sort(key=lambda x: x['next_maintenance_date'])

    status_stats = defaultdict(int)
    for acc in all_acc:
        status_stats[acc.get_status()] += 1
    status_distribution = [
        {'status': s, 'count': c, 'percentage': round(c / max(total, 1) * 100, 1)}
        for s, c in sorted(status_stats.items(), key=lambda x: -x[1])
    ]

    total_asset_value = 0.0
    valuation_trend = defaultdict(float)
    high_value_uninsured = []
    total_purchase_value = 0.0

    all_valuations = ValuationRecord.query.order_by(ValuationRecord.created_at.asc()).all()
    for v in all_valuations:
        try:
            month_key = v.created_at.strftime('%Y-%m')
            valuation_trend[month_key] += v.estimated_value
        except:
            pass

    all_insurance = InsuranceItem.query.filter_by(status='active').all()
    insured_ids = set(i.accessory_id for i in all_insurance)

    cert_count = CertificateAttachment.query.count()
    cert_missing_count = 0
    high_value_threshold = 3000.0

    for acc in all_acc:
        total_purchase_value += float(acc.purchase_price or 0)
        val = calculate_valuation(acc)
        total_asset_value += val['estimated_value']
        acc_certs = CertificateAttachment.query.filter_by(accessory_id=acc.id).count()
        if acc_certs == 0 and float(acc.purchase_price or 0) >= 1000:
            cert_missing_count += 1
        if val['estimated_value'] >= high_value_threshold and acc.id not in insured_ids and not acc.is_lost:
            hv_item = acc.to_dict()
            hv_item['current_value'] = val['estimated_value']
            hv_item['insurance_suggestion'] = val['insurance_suggestion']
            hv_item['risk_level'] = val['risk_level']
            high_value_uninsured.append(hv_item)

    high_value_uninsured.sort(key=lambda x: -x['current_value'])
    valuation_trend_list = sorted([{'month': k, 'value': round(v, 2)} for k, v in valuation_trend.items()])
    current_month = datetime.now().strftime('%Y-%m')
    if valuation_trend_list and valuation_trend_list[-1]['month'] == current_month:
        valuation_trend_list[-1]['value'] = round(total_asset_value, 2)
    else:
        valuation_trend_list.append({'month': current_month, 'value': round(total_asset_value, 2)})
    valuation_trend_list.sort(key=lambda x: x['month'])

    all_batches = InventoryBatch.query.all()
    completed_batches = [b for b in all_batches if b.status == 'completed']
    total_inventory_checked = sum(b.checked_count for b in completed_batches)
    total_inventory_target = sum(b.total_count for b in completed_batches)
    inventory_completion_rate = round(total_inventory_checked / max(total_inventory_target, 1) * 100, 1)

    all_exceptions = InventoryException.query.all()
    unresolved_exceptions = [e for e in all_exceptions if not e.resolved]
    exception_by_type = defaultdict(int)
    for e in all_exceptions:
        exception_by_type[e.exception_type] += 1
    exception_distribution = [
        {'type': t or '未分类', 'count': c, 'percentage': round(c / max(len(all_exceptions), 1) * 100, 1)}
        for t, c in sorted(exception_by_type.items(), key=lambda x: -x[1])
    ]

    total_insurance_coverage = sum(i.coverage_amount for i in all_insurance)

    return {
        'total': total,
        'category_distribution': [
            {'category': c, 'count': cnt, 'percentage': round(cnt / total * 100, 1) if total else 0}
            for c, cnt in sorted(category_stats.items(), key=lambda x: -x[1])
        ],
        'color_distribution': color_distribution,
        'frequent_combos': frequent_combos,
        'long_unworn': long_unworn,
        'utilization_rate': min(utilization_rate, 100),
        'active_rate': active_rate,
        'total_wears': total_wears,
        'active_count': worn_30d,
        'trip_count': trip_count,
        'trip_packing_stats': trip_packing_stats,
        'trip_packing_rate': round(total_trip_packed / max(total_trip_items, 1) * 100, 1),
        'trip_total_items': total_trip_items,
        'trip_packed_items': total_trip_packed,
        'trip_plan_utilization': trip_plan_utilization,
        'trip_unique_count': len(total_trip_unique_acc),
        'trip_color_distribution': trip_color_distribution,
        'upcoming_trips': upcoming_trips,
        'unpacked_reminders': unpacked_reminders[:50],
        'status_distribution': status_distribution,
        'active_loan_count': len(active_loans),
        'overdue_loan_count': len(overdue_loans),
        'active_maintenance_count': len([m for m in active_maint if m.record_type == 'maintenance']),
        'active_repair_count': len([m for m in active_maint if m.record_type == 'repair']),
        'total_maintenance_cost': round(total_maint_cost, 2),
        'cost_trend': cost_trend,
        'high_risk_accessories': high_risk,
        'maintenance_reminders_30d': maintenance_reminders,
        'total_asset_value': round(total_asset_value, 2),
        'total_purchase_value': round(total_purchase_value, 2),
        'valuation_trend': valuation_trend_list,
        'high_value_uninsured': high_value_uninsured[:20],
        'high_value_uninsured_count': len(high_value_uninsured),
        'cert_missing_count': cert_missing_count,
        'cert_missing_rate': round(cert_missing_count / max(total, 1) * 100, 1),
        'total_cert_count': cert_count,
        'inventory_completion_rate': inventory_completion_rate,
        'total_inventory_batches': len(all_batches),
        'completed_inventory_batches': len(completed_batches),
        'unresolved_exception_count': len(unresolved_exceptions),
        'exception_distribution': exception_distribution,
        'total_insurance_coverage': round(total_insurance_coverage, 2),
        'insured_accessory_count': len(insured_ids)
    }
