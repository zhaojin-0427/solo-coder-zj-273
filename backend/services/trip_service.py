from datetime import datetime, timedelta
from collections import Counter
from backend.models import Accessory
from backend.utils.constants import COLOR_COMBINATIONS, STYLE_MATCH
from backend.utils.helpers import get_color_score, get_style_score, get_occasion_score


def get_trip_item_score(acc, main_color, style, occasion, used_categories_today, trip_used_ids):
    score = 0
    score += get_color_score(acc.color_family, main_color) * 2
    score += get_style_score(acc.style, style) * 1.5
    score += get_occasion_score(acc, occasion)

    if acc.id in trip_used_ids:
        reuse_times = trip_used_ids.count(acc.id)
        score += reuse_times * 3
    else:
        score += 2

    if acc.category in used_categories_today:
        score -= 50

    if acc.wear_count <= 3:
        score += 4
    elif acc.wear_count <= 8:
        score += 2
    elif acc.wear_count >= 15:
        score -= 2

    return score


def generate_trip_packing(trip):
    try:
        start = datetime.strptime(trip.start_date, '%Y-%m-%d')
        end = datetime.strptime(trip.end_date, '%Y-%m-%d')
        total_days = (end - start).days + 1
    except:
        total_days = max(1, len(trip.days))
        start = None

    all_accessories = Accessory.query.all()
    available = [a for a in all_accessories if a.get_status() == 'in_stock']
    necklaces = [a for a in available if a.category == '项链']
    earrings = [a for a in available if a.category == '耳环']
    bracelets = [a for a in available if a.category == '手链']
    other_acc = [a for a in available if a.category not in ['项链', '耳环', '手链']]

    trip_used_ids = []
    day_plans = []

    for day_idx in range(total_days):
        if start:
            day_date = (start + timedelta(days=day_idx)).strftime('%Y-%m-%d')
        else:
            day_date = ''

        day_occasion = trip.main_occasion
        used_categories_today = set()
        day_items = []

        categories_to_pick = [('项链', necklaces), ('耳环', earrings), ('手链', bracelets)]
        for cat_name, cat_items in categories_to_pick:
            if not cat_items:
                continue

            scored = []
            for acc in cat_items:
                s = get_trip_item_score(acc, trip.main_color, trip.style, day_occasion, used_categories_today, trip_used_ids)
                scored.append((s, acc))
            scored.sort(key=lambda x: -x[0])

            if scored:
                chosen = scored[0][1]
                used_categories_today.add(chosen.category)
                if chosen.id in trip_used_ids:
                    reuse_count = trip_used_ids.count(chosen.id) + 1
                else:
                    reuse_count = 1
                trip_used_ids.append(chosen.id)

                reason_parts = []
                if chosen.color_family == trip.main_color or chosen.color_family in COLOR_COMBINATIONS.get(trip.main_color, []):
                    reason_parts.append(f'与主色调{trip.main_color}协调')
                if chosen.style == trip.style or chosen.style in STYLE_MATCH.get(trip.style, []):
                    reason_parts.append(f'{trip.style}风格匹配')
                if day_occasion and day_occasion in (chosen.occasions.split(',') if chosen.occasions else []):
                    reason_parts.append(f'适合{day_occasion}场合')
                reason = '；'.join(reason_parts) if reason_parts else '精选推荐单品'

                day_items.append({
                    'accessory': chosen,
                    'item_type': 'recommended',
                    'is_spare': False,
                    'reason': reason,
                    'reuse_count': reuse_count
                })

        spare_candidates = []
        for acc in other_acc + necklaces + earrings + bracelets:
            if acc.id not in [i['accessory'].id for i in day_items]:
                s = get_trip_item_score(acc, trip.main_color, trip.style, day_occasion, set(), trip_used_ids)
                spare_candidates.append((s, acc))
        spare_candidates.sort(key=lambda x: -x[0])

        for s, acc in spare_candidates[:2]:
            if acc.id in trip_used_ids:
                reuse_count = trip_used_ids.count(acc.id) + 1
            else:
                reuse_count = 1
            trip_used_ids.append(acc.id)
            day_items.append({
                'accessory': acc,
                'item_type': 'spare',
                'is_spare': True,
                'reason': f'备用单品：{acc.style}风格{acc.color_family}色系百搭款',
                'reuse_count': reuse_count
            })

        day_plans.append({
            'day_index': day_idx,
            'date': day_date,
            'occasion': day_occasion,
            'weather': f'{trip.temp_min}°C~{trip.temp_max}°C',
            'items': day_items
        })

    return day_plans


def compute_missing_risk(trip):
    all_ids = []
    for day in trip.days:
        for item in day.items:
            acc = Accessory.query.get(item.accessory_id)
            if acc and acc.get_status() == 'in_stock':
                all_ids.append(item.accessory_id)

    id_counts = Counter(all_ids)
    total_days = len(trip.days) if trip.days else 1

    risks = []
    for acc_id, count in id_counts.items():
        acc = Accessory.query.get(acc_id)
        if not acc:
            continue
        usage_ratio = count / total_days
        risk_level = '低'
        risk_score = 0
        if usage_ratio >= 0.8:
            risk_level = '高'
            risk_score = 3
        elif usage_ratio >= 0.5:
            risk_level = '中'
            risk_score = 2
        elif usage_ratio >= 0.3:
            risk_level = '低'
            risk_score = 1
        if risk_score > 0:
            risks.append({
                'accessory': acc.to_dict(),
                'usage_days': count,
                'total_days': total_days,
                'usage_ratio': round(usage_ratio * 100, 1),
                'risk_level': risk_level,
                'risk_score': risk_score,
                'suggestion': f'该饰品预计使用{count}天，占行程{round(usage_ratio * 100, 1)}%，建议携带同款备用或做好保养' if risk_level != '低' else '使用率适中'
            })
    risks.sort(key=lambda x: -x['risk_score'])
    return risks


def compute_storage_locations(trip):
    loc_map = {}
    for day in trip.days:
        for item in day.items:
            acc = Accessory.query.get(item.accessory_id)
            if not acc or acc.get_status() != 'in_stock':
                continue
            loc = acc.storage_location or '未标记位置'
            if loc not in loc_map:
                loc_map[loc] = set()
            loc_map[loc].add(acc.id)
    result = []
    for loc, acc_ids in loc_map.items():
        items = [Accessory.query.get(aid).to_dict() for aid in acc_ids if Accessory.query.get(aid)]
        result.append({
            'location': loc,
            'count': len(items),
            'accessories': items
        })
    result.sort(key=lambda x: -x['count'])
    return result


def export_trip_content(trip):
    lines = []
    lines.append(f'📋 行程饰品打包清单：{trip.name}')
    lines.append(f'📍 目的地：{trip.destination or "未指定"}')
    lines.append(f'📅 日期：{trip.start_date} ~ {trip.end_date}')
    lines.append(f'🌡 温度：{trip.temp_min}°C ~ {trip.temp_max}°C')
    lines.append(f'🎨 主色调：{trip.main_color or "未指定"}')
    lines.append(f'✨ 风格：{trip.style or "未指定"}')
    if trip.main_occasion:
        lines.append(f'🎭 主要场合：{trip.main_occasion}')
    lines.append('')
    lines.append('=' * 40)

    total_items = 0
    packed_count = 0
    skipped_items = 0
    for day in trip.days:
        lines.append(f'\n📅 第 {day.day_index + 1} 天 ({day.date or ""})')
        if day.occasion:
            lines.append(f'   🎭 场合：{day.occasion}')
        if day.weather:
            lines.append(f'   🌤 天气：{day.weather}')
        lines.append('   --- 推荐搭配 ---')
        for item in day.items:
            acc = Accessory.query.get(item.accessory_id)
            if not acc:
                continue
            if acc.get_status() != 'in_stock':
                skipped_items += 1
                continue
            total_items += 1
            if item.packed:
                packed_count += 1
            prefix = '✅' if item.packed else '⬜'
            tag = '[备用]' if item.is_spare else '      '
            lines.append(f'   {prefix} {tag} {acc.category}：{acc.name} ({acc.color_family}·{acc.style})')
            if item.reason:
                lines.append(f'          💡 {item.reason}')
            if item.reuse_count > 1:
                lines.append(f'          🔁 本次行程复用第{item.reuse_count}次')

    if skipped_items > 0:
        lines.append(f'\n⚠️ 注：已自动排除 {skipped_items} 件不在库（借出/维修/保养中）的饰品')

    lines.append('')
    lines.append('=' * 40)
    lines.append(f'\n📦 打包进度：{packed_count}/{total_items} ({round(packed_count/max(total_items,1)*100, 1)}%)')

    storage = compute_storage_locations(trip)
    if storage:
        lines.append('\n🗂 收纳取件指引：')
        for s in storage:
            lines.append(f'   📍 {s["location"]}（{s["count"]}件）')
            for a in s['accessories']:
                lines.append(f'      · {a["name"]}')

    risks = compute_missing_risk(trip)
    high_risks = [r for r in risks if r['risk_level'] in ['高', '中']]
    if high_risks:
        lines.append('\n⚠️ 缺失风险提醒：')
        for r in high_risks:
            lines.append(f'   [{r["risk_level"]}风险] {r["accessory"]["name"]}：使用率{r["usage_ratio"]}%，{r["suggestion"]}')

    return {'content': '\n'.join(lines), 'lines': lines}
