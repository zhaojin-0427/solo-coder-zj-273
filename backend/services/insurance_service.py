from datetime import datetime
from backend.models import Accessory, InsuranceItem
from backend.services.valuation_service import calculate_valuation


def export_insurance_list():
    all_acc = Accessory.query.filter_by(is_lost=False).all()
    insured_ids = set()
    active_insurance = InsuranceItem.query.filter_by(status='active').all()
    insurance_map = {}
    for ins in active_insurance:
        insured_ids.add(ins.accessory_id)
        insurance_map[ins.accessory_id] = ins

    export_items = []
    total_coverage = 0.0
    total_suggested = 0.0

    for acc in all_acc:
        val = calculate_valuation(acc)
        insured = insurance_map.get(acc.id)
        export_items.append({
            'accessory': acc.to_dict(),
            'estimated_value': val['estimated_value'],
            'insurance_suggestion': val['insurance_suggestion'],
            'risk_level': val['risk_level'],
            'has_insurance': acc.id in insured_ids,
            'current_coverage': insured.coverage_amount if insured else 0,
            'policy_number': insured.policy_number if insured else '',
            'insurance_company': insured.insurance_company if insured else '',
            'insurance_start_date': insured.start_date if insured else '',
            'insurance_end_date': insured.end_date if insured else '',
            'insurance_notes': insured.notes if insured else ''
        })
        total_suggested += val['insurance_suggestion']
        if insured:
            total_coverage += insured.coverage_amount

    export_items.sort(key=lambda x: -x['estimated_value'])

    lines = []
    lines.append(f'📋 珠宝饰品保险申报清单')
    lines.append(f'📅 生成日期：{datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append(f'📊 饰品总数：{len(all_acc)} 件')
    lines.append(f'💰 总估值：¥{round(sum(v["estimated_value"] for v in export_items), 2)}')
    lines.append(f'💡 建议总保额：¥{round(total_suggested, 2)}')
    lines.append(f'🛡  当前保额：¥{round(total_coverage, 2)}')
    lines.append('')
    lines.append('=' * 60)
    for idx, item in enumerate(export_items, 1):
        acc = item['accessory']
        lines.append(f'\n{idx}. {acc["name"]}（{acc["category"]}）')
        lines.append(f'   材质：{acc["material"]} · 品牌：{acc.get("brand", "未填写") or "未填写"}')
        lines.append(f'   当前估值：¥{item["estimated_value"]}')
        lines.append(f'   建议保额：¥{item["insurance_suggestion"]}')
        risk_label = {'low': '低', 'medium': '中', 'high': '高', 'critical': '严重'}.get(item['risk_level'], item['risk_level'])
        lines.append(f'   风险等级：{risk_label}')
        if item['has_insurance']:
            lines.append(f'   已投保：{item["insurance_company"]} 保单号 {item["policy_number"]} 保额 ¥{item["current_coverage"]}')
            if item['insurance_start_date']:
                lines.append(f'   保险生效：{item["insurance_start_date"]}')
            if item['insurance_end_date']:
                lines.append(f'   保险到期：{item["insurance_end_date"]}')
            if item['insurance_notes']:
                lines.append(f'   备注：{item["insurance_notes"]}')
        else:
            lines.append(f'   ⚠️ 未投保，建议尽快办理')

    return {
        'items': export_items,
        'total_coverage': round(total_coverage, 2),
        'total_suggested': round(total_suggested, 2),
        'uninsured_count': len(all_acc) - len(insured_ids),
        'content': '\n'.join(lines)
    }
