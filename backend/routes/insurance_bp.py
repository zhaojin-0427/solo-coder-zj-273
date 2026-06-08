from flask import Blueprint, request, jsonify, current_app, Response
from datetime import datetime
import csv
import io
from backend.extensions import db
from backend.models import InsuranceItem, Accessory
from backend.services import calculate_valuation, export_insurance_list as export_insurance_service

bp = Blueprint('insurance', __name__, url_prefix='/api')


@bp.route('/insurance', methods=['GET'])
def get_insurance_items():
    status = request.args.get('status', '')
    query = InsuranceItem.query
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(InsuranceItem.created_at.desc()).all()
    return jsonify([i.to_dict() for i in items])


@bp.route('/insurance/<int:iid>', methods=['GET'])
def get_insurance_item(iid):
    item = InsuranceItem.query.get_or_404(iid)
    return jsonify(item.to_dict())


@bp.route('/insurance', methods=['POST'])
def create_insurance_item():
    data = request.get_json() or {}
    acc = Accessory.query.get_or_404(data.get('accessory_id'))
    valuation = calculate_valuation(acc)
    suggested = float(data['insurance_amount']) if 'insurance_amount' in data and data['insurance_amount'] is not None else valuation['insurance_suggestion']

    item = InsuranceItem(
        accessory_id=data.get('accessory_id'),
        insurance_type=data.get('insurance_type', '财产险'),
        policy_number=data.get('policy_number', ''),
        insurance_provider=data.get('insurance_provider', ''),
        insurance_amount=suggested,
        start_date=data.get('start_date', ''),
        end_date=data.get('end_date', ''),
        premium=float(data['premium']) if 'premium' in data and data['premium'] is not None else None,
        beneficiary=data.get('beneficiary', ''),
        status=data.get('status', 'active'),
        notes=data.get('notes', '')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@bp.route('/insurance/<int:iid>', methods=['PUT'])
def update_insurance_item(iid):
    item = InsuranceItem.query.get_or_404(iid)
    data = request.get_json() or {}
    fields = ['policy_number', 'insurance_company', 'start_date', 'end_date', 'status', 'notes']
    for f in fields:
        if f in data:
            setattr(item, f, data[f])
    if 'insurance_amount' in data and data['insurance_amount'] is not None:
        item.coverage_amount = float(data['insurance_amount'])
    if 'insurance_provider' in data:
        item.insurance_company = data['insurance_provider']
    if 'premium' in data and data['premium'] is not None:
        item.premium = float(data['premium'])
    db.session.commit()
    return jsonify(item.to_dict())


@bp.route('/insurance/<int:iid>', methods=['DELETE'])
def delete_insurance_item(iid):
    item = InsuranceItem.query.get_or_404(iid)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': '已删除'})


@bp.route('/insurance/export', methods=['GET'])
def export_insurance_list():
    status = request.args.get('status', '')
    query = InsuranceItem.query
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(InsuranceItem.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['饰品名称', '类别', '保单号', '保险公司', '保额', '保费', '开始日期', '到期日期', '状态', '备注'])

    status_map = {'active': '有效', 'expired': '已过期', 'expiring': '即将到期', 'cancelled': '已取消'}

    for item in items:
        acc = Accessory.query.get(item.accessory_id)
        name = acc.name if acc else ''
        category = acc.category if acc else ''
        writer.writerow([
            name,
            category,
            item.policy_number,
            item.insurance_company,
            item.coverage_amount,
            item.premium or '',
            item.start_date,
            item.end_date,
            status_map.get(item.status, item.status),
            item.notes or ''
        ])

    output.seek(0)
    output_bytes = io.BytesIO(output.getvalue().encode('utf-8-sig'))

    filename = f"insurance_list_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    return Response(
        output_bytes.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
