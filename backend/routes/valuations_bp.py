from flask import Blueprint, request, jsonify
from datetime import datetime
from collections import defaultdict
from backend.extensions import db
from backend.models import ValuationRecord, Accessory
from backend.services import calculate_valuation

bp = Blueprint('valuations', __name__, url_prefix='/api')


@bp.route('/valuations/calculate/<int:aid>', methods=['GET'])
def calculate_accessory_valuation(aid):
    acc = Accessory.query.get_or_404(aid)
    result = calculate_valuation(acc)
    return jsonify({
        'accessory_id': aid,
        **result
    })


@bp.route('/valuations', methods=['GET'])
def get_valuations():
    accessory_id = request.args.get('accessory_id', '')
    query = ValuationRecord.query
    if accessory_id:
        query = query.filter_by(accessory_id=int(accessory_id))
    records = query.order_by(ValuationRecord.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@bp.route('/valuations/<int:vid>', methods=['GET'])
def get_valuation(vid):
    record = ValuationRecord.query.get_or_404(vid)
    return jsonify(record.to_dict())


@bp.route('/valuations', methods=['POST'])
def create_valuation():
    data = request.get_json() or {}
    acc = Accessory.query.get_or_404(data.get('accessory_id'))
    auto_calc = calculate_valuation(acc)

    estimated_value = float(data['estimated_value']) if 'estimated_value' in data and data['estimated_value'] is not None else auto_calc['estimated_value']
    insurance_suggestion = float(data['insurance_suggestion']) if 'insurance_suggestion' in data and data['insurance_suggestion'] is not None else auto_calc['insurance_suggestion']
    depreciation_reason = data.get('depreciation_reason') if data.get('depreciation_reason') else auto_calc['depreciation_reason']
    risk_level = data.get('risk_level') if data.get('risk_level') else auto_calc['risk_level']
    wear_frequency = data.get('wear_frequency') if data.get('wear_frequency') else auto_calc['wear_frequency']
    repair_count = int(data['repair_count']) if 'repair_count' in data and data['repair_count'] is not None else auto_calc['repair_count']
    condition_note = data.get('condition_note', '') or data.get('notes', '')

    record = ValuationRecord(
        accessory_id=data.get('accessory_id'),
        valuation_date=data.get('valuation_date', datetime.now().strftime('%Y-%m-%d')),
        estimated_value=estimated_value,
        depreciation_reason=depreciation_reason,
        insurance_suggestion=insurance_suggestion,
        risk_level=risk_level,
        wear_frequency=wear_frequency,
        repair_count=repair_count,
        condition_note=condition_note
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@bp.route('/valuations/<int:vid>', methods=['DELETE'])
def delete_valuation(vid):
    record = ValuationRecord.query.get_or_404(vid)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '已删除'})


@bp.route('/valuations/overview', methods=['GET'])
def get_valuation_overview():
    all_acc = Accessory.query.filter_by(is_lost=False).all()
    total_value = 0.0
    total_purchase = 0.0
    value_by_category = {}
    value_by_risk = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    valuation_details = []

    for acc in all_acc:
        val = calculate_valuation(acc)
        total_value += val['estimated_value']
        total_purchase += float(acc.purchase_price or 0)
        cat = acc.category or '其他'
        if cat not in value_by_category:
            value_by_category[cat] = 0.0
        value_by_category[cat] += val['estimated_value']
        if val['risk_level'] in value_by_risk:
            value_by_risk[val['risk_level']] += val['estimated_value']
        valuation_details.append({
            'accessory': acc.to_dict(),
            'estimated_value': val['estimated_value'],
            'depreciation_reason': val['depreciation_reason'],
            'insurance_suggestion': val['insurance_suggestion'],
            'risk_level': val['risk_level'],
            'wear_frequency': val['wear_frequency']
        })

    valuation_details.sort(key=lambda x: -x['estimated_value'])

    historical_records = ValuationRecord.query.order_by(ValuationRecord.created_at.asc()).all()
    trend_map = defaultdict(float)
    for r in historical_records:
        try:
            key = r.created_at.strftime('%Y-%m')
            trend_map[key] += r.estimated_value
        except:
            pass
    trend = sorted([{'month': k, 'value': round(v, 2)} for k, v in trend_map.items()])
    current_month = datetime.now().strftime('%Y-%m')
    if trend and trend[-1]['month'] == current_month:
        trend[-1]['value'] = round(total_value, 2)
    else:
        trend.append({'month': current_month, 'value': round(total_value, 2)})
    trend.sort(key=lambda x: x['month'])

    category_distribution = sorted([
        {'category': k, 'value': round(v, 2), 'percentage': round(v / max(total_value, 1) * 100, 1)}
        for k, v in value_by_category.items()
    ], key=lambda x: -x['value'])

    risk_distribution = [
        {'level': k, 'label': {'low': '低风险', 'medium': '中风险', 'high': '高风险', 'critical': '严重风险'}[k],
         'value': round(v, 2), 'percentage': round(v / max(total_value, 1) * 100, 1)}
        for k, v in value_by_risk.items()
    ]

    return jsonify({
        'total_asset_value': round(total_value, 2),
        'total_purchase_value': round(total_purchase, 2),
        'depreciation_rate': round((1 - total_value / max(total_purchase, 1)) * 100, 1) if total_purchase > 0 else 0,
        'accessory_count': len(all_acc),
        'category_distribution': category_distribution,
        'risk_distribution': risk_distribution,
        'valuation_trend': trend,
        'top_valuable': valuation_details[:20],
        'all_valuations': valuation_details
    })
