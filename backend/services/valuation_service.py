from datetime import datetime
from backend.models import MaintenanceRecord
from backend.utils.constants import MATERIAL_VALUE_FACTOR, BRAND_PREMIUM
from backend.utils.helpers import get_wear_frequency_label


def calculate_valuation(acc):
    base_price = float(acc.purchase_price or 0)
    if base_price <= 0:
        base_price = 500.0

    today = datetime.now()
    depreciation_reasons = []

    material_factor = MATERIAL_VALUE_FACTOR.get(acc.material, 0.1)
    brand_factor = 1.0
    for brand_key, premium in BRAND_PREMIUM.items():
        if brand_key.lower() in (acc.brand or '').lower():
            brand_factor = premium
            break

    estimated_value = base_price * material_factor * brand_factor

    if acc.purchase_date:
        try:
            purchase_dt = datetime.strptime(acc.purchase_date, '%Y-%m-%d')
            years_owned = (today - purchase_dt).days / 365.25
            annual_depreciation = 0.05
            if years_owned > 0:
                depreciation = min(0.5, annual_depreciation * years_owned)
                estimated_value *= (1 - depreciation)
                if depreciation > 0:
                    depreciation_reasons.append(f"已持有{round(years_owned, 1)}年，时间折损{round(depreciation * 100, 1)}%")
        except:
            pass

    wear_count = acc.wear_count or 0
    wear_freq = get_wear_frequency_label(wear_count)
    if wear_count >= 50:
        wear_depreciation = 0.25
    elif wear_count >= 20:
        wear_depreciation = 0.15
    elif wear_count >= 5:
        wear_depreciation = 0.08
    else:
        wear_depreciation = 0.0
    if wear_depreciation > 0:
        estimated_value *= (1 - wear_depreciation)
        depreciation_reasons.append(f"累计佩戴{wear_count}次（{wear_freq}使用），折损{round(wear_depreciation * 100, 1)}%")

    repair_count = MaintenanceRecord.query.filter_by(
        accessory_id=acc.id, record_type='repair'
    ).count()
    if repair_count >= 3:
        repair_depreciation = 0.25
    elif repair_count >= 2:
        repair_depreciation = 0.15
    elif repair_count >= 1:
        repair_depreciation = 0.08
    else:
        repair_depreciation = 0.0
    if repair_depreciation > 0:
        estimated_value *= (1 - repair_depreciation)
        depreciation_reasons.append(f"维修记录{repair_count}次，折损{round(repair_depreciation * 100, 1)}%")

    if acc.maintenance_status == 'poor':
        condition_depreciation = 0.2
        depreciation_reasons.append("保养状况较差，折损20%")
    elif acc.maintenance_status == 'fair':
        condition_depreciation = 0.1
        depreciation_reasons.append("保养状况一般，折损10%")
    else:
        condition_depreciation = 0.0

    estimated_value *= (1 - condition_depreciation)
    estimated_value = round(estimated_value, 2)

    if acc.is_lost:
        risk_level = 'critical'
    elif repair_count >= 3 or acc.maintenance_status == 'poor':
        risk_level = 'high'
    elif repair_count >= 1 or wear_count >= 30:
        risk_level = 'medium'
    else:
        risk_level = 'low'

    if acc.is_lost:
        depreciation_reasons.insert(0, "饰品已标记为丢失")

    insurance_suggestion = round(estimated_value * 1.1, 2)
    if estimated_value >= 5000:
        insurance_suggestion = round(estimated_value * 1.2, 2)

    if not depreciation_reasons:
        depreciation_reasons.append("饰品整体状况良好，折损较少")

    return {
        'estimated_value': estimated_value,
        'depreciation_reason': '；'.join(depreciation_reasons),
        'insurance_suggestion': insurance_suggestion,
        'risk_level': risk_level,
        'wear_frequency': wear_freq,
        'repair_count': repair_count,
        'condition_note': acc.maintenance_status
    }
