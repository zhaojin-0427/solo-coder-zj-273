from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
from backend.extensions import db
from backend.models import LoanRecord, MaintenanceRecord, Accessory

bp = Blueprint('tracking', __name__, url_prefix='/api')


@bp.route('/loans', methods=['GET'])
def get_loans():
    status = request.args.get('status', '')
    query = LoanRecord.query
    if status == 'active':
        query = query.filter_by(returned=False)
    elif status == 'returned':
        query = query.filter_by(returned=True)
    elif status == 'overdue':
        today = datetime.now().strftime('%Y-%m-%d')
        query = query.filter_by(returned=False).filter(LoanRecord.due_date < today)
    loans = query.order_by(LoanRecord.created_at.desc()).all()
    return jsonify([l.to_dict() for l in loans])


@bp.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json() or {}
    acc = Accessory.query.get_or_404(data.get('accessory_id'))
    if acc.get_status() != 'in_stock':
        return jsonify({'error': '该饰品当前状态不支持借出'}), 400
    loan = LoanRecord(
        accessory_id=data.get('accessory_id'),
        borrower_name=data.get('borrower_name', ''),
        borrower_phone=data.get('borrower_phone', ''),
        borrower_contact=data.get('borrower_contact', ''),
        loan_date=data.get('loan_date', datetime.now().strftime('%Y-%m-%d')),
        due_date=data.get('due_date', ''),
        deposit=float(data.get('deposit', 0)),
        notes=data.get('notes', '')
    )
    if not loan.borrower_name:
        return jsonify({'error': '请填写借用人姓名'}), 400
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201


@bp.route('/loans/<int:lid>/return', methods=['POST'])
def return_loan(lid):
    loan = LoanRecord.query.get_or_404(lid)
    data = request.get_json() or {}
    loan.returned = True
    loan.return_date = data.get('return_date', datetime.now().strftime('%Y-%m-%d'))
    if 'deposit_returned' in data:
        loan.deposit_returned = bool(data['deposit_returned'])
    else:
        loan.deposit_returned = True
    db.session.commit()
    return jsonify(loan.to_dict())


@bp.route('/loans/<int:lid>', methods=['PUT'])
def update_loan(lid):
    loan = LoanRecord.query.get_or_404(lid)
    data = request.get_json() or {}
    fields = ['borrower_name', 'borrower_phone', 'borrower_contact', 'loan_date', 'due_date', 'deposit', 'notes']
    for f in fields:
        if f in data:
            if f == 'deposit':
                setattr(loan, f, float(data[f]))
            else:
                setattr(loan, f, data[f])
    db.session.commit()
    return jsonify(loan.to_dict())


@bp.route('/loans/<int:lid>', methods=['DELETE'])
def delete_loan(lid):
    loan = LoanRecord.query.get_or_404(lid)
    db.session.delete(loan)
    db.session.commit()
    return jsonify({'message': '已删除'})


@bp.route('/maintenance', methods=['GET'])
def get_maintenance():
    status = request.args.get('status', '')
    record_type = request.args.get('type', '')
    query = MaintenanceRecord.query
    if status == 'active':
        query = query.filter_by(completed=False)
    elif status == 'completed':
        query = query.filter_by(completed=True)
    if record_type:
        query = query.filter_by(record_type=record_type)
    records = query.order_by(MaintenanceRecord.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@bp.route('/maintenance', methods=['POST'])
def create_maintenance():
    data = request.get_json() or {}
    acc = Accessory.query.get_or_404(data.get('accessory_id'))
    current_status = acc.get_status()
    if current_status in ['lent', 'overdue']:
        return jsonify({'error': '该饰品已借出，无法送修'}), 400
    if current_status in ['maintenance', 'repair']:
        return jsonify({'error': '该饰品已在保养/维修中'}), 400
    record = MaintenanceRecord(
        accessory_id=data.get('accessory_id'),
        record_type=data.get('record_type', 'maintenance'),
        title=data.get('title', ''),
        description=data.get('description', ''),
        cost=float(data.get('cost', 0)),
        shop=data.get('shop', ''),
        sent_date=data.get('sent_date', datetime.now().strftime('%Y-%m-%d')),
        notes=data.get('notes', '')
    )
    if not record.title:
        return jsonify({'error': '请填写标题'}), 400
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@bp.route('/maintenance/<int:mid>/complete', methods=['POST'])
def complete_maintenance(mid):
    record = MaintenanceRecord.query.get_or_404(mid)
    data = request.get_json() or {}
    record.completed = True
    record.completed_date = data.get('completed_date', datetime.now().strftime('%Y-%m-%d'))
    if 'cost' in data:
        record.cost = float(data['cost'])
    if 'notes' in data:
        record.notes = data['notes']
    db.session.commit()
    return jsonify(record.to_dict())


@bp.route('/maintenance/<int:mid>', methods=['PUT'])
def update_maintenance(mid):
    record = MaintenanceRecord.query.get_or_404(mid)
    data = request.get_json() or {}
    fields = ['record_type', 'title', 'description', 'shop', 'sent_date', 'notes']
    for f in fields:
        if f in data:
            setattr(record, f, data[f])
    if 'cost' in data:
        record.cost = float(data['cost'])
    db.session.commit()
    return jsonify(record.to_dict())


@bp.route('/maintenance/<int:mid>', methods=['DELETE'])
def delete_maintenance(mid):
    record = MaintenanceRecord.query.get_or_404(mid)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '已删除'})


@bp.route('/tracking/summary', methods=['GET'])
def get_tracking_summary():
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')

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
    all_acc = Accessory.query.all()
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

    return jsonify({
        'active_loan_count': len(active_loans),
        'overdue_loan_count': len(overdue_loans),
        'active_maintenance_count': len([m for m in active_maint if m.record_type == 'maintenance']),
        'active_repair_count': len([m for m in active_maint if m.record_type == 'repair']),
        'total_maintenance_cost': round(total_maint_cost, 2),
        'cost_trend': cost_trend,
        'high_risk_accessories': high_risk,
        'maintenance_reminders_30d': maintenance_reminders
    })
