from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.extensions import db
from backend.models import InventoryBatch, InventoryItem, InventoryException, Accessory

bp = Blueprint('inventory', __name__, url_prefix='/api')


@bp.route('/inventory/batches', methods=['GET'])
def get_inventory_batches():
    status = request.args.get('status', '')
    query = InventoryBatch.query
    if status:
        query = query.filter_by(status=status)
    batches = query.order_by(InventoryBatch.created_at.desc()).all()
    return jsonify([b.to_dict() for b in batches])


@bp.route('/inventory/batches/<int:bid>', methods=['GET'])
def get_inventory_batch(bid):
    batch = InventoryBatch.query.get_or_404(bid)
    return jsonify(batch.to_dict())


@bp.route('/inventory/batches', methods=['POST'])
def create_inventory_batch():
    data = request.get_json() or {}
    today = datetime.now().strftime('%Y-%m-%d')
    batch = InventoryBatch(
        batch_name=data.get('batch_name', f'盘点_{today}'),
        batch_type=data.get('batch_type', 'annual'),
        period=data.get('period', ''),
        start_date=data.get('start_date', today),
        end_date=data.get('end_date', ''),
        status='in_progress',
        total_count=0,
        checked_count=0,
        exception_count=0,
        operator=data.get('operator', ''),
        notes=data.get('notes', '')
    )
    db.session.add(batch)
    db.session.flush()

    all_acc = Accessory.query.filter_by(is_lost=False).all()
    batch.total_count = len(all_acc)
    for acc in all_acc:
        item = InventoryItem(
            batch_id=batch.id,
            accessory_id=acc.id,
            expected_location=acc.storage_location or '',
            actual_location='',
            status='pending',
            check_method='manual',
            checked_at='',
            notes=''
        )
        db.session.add(item)

    db.session.commit()
    return jsonify(batch.to_dict()), 201


@bp.route('/inventory/batches/<int:bid>/complete', methods=['POST'])
def complete_inventory_batch(bid):
    batch = InventoryBatch.query.get_or_404(bid)
    batch.status = 'completed'
    batch.end_date = datetime.now().strftime('%Y-%m-%d')
    db.session.commit()
    return jsonify(batch.to_dict())


@bp.route('/inventory/batches/<int:bid>', methods=['DELETE'])
def delete_inventory_batch(bid):
    batch = InventoryBatch.query.get_or_404(bid)
    db.session.delete(batch)
    db.session.commit()
    return jsonify({'message': '已删除'})


@bp.route('/inventory/items/<int:iid>/check', methods=['POST'])
def check_inventory_item(iid):
    item = InventoryItem.query.get_or_404(iid)
    data = request.get_json() or {}
    item.status = data.get('status', 'checked')
    item.actual_location = data.get('actual_location', item.expected_location)
    item.check_method = data.get('check_method', 'manual')
    item.checked_at = datetime.now().strftime('%Y-%m-%d %H:%M')
    if 'notes' in data:
        item.notes = data['notes']

    batch = InventoryBatch.query.get(item.batch_id)
    if batch:
        checked = InventoryItem.query.filter_by(batch_id=batch.id, status='checked').count()
        batch.checked_count = checked
        exceptions = InventoryException.query.filter_by(batch_id=batch.id, resolved=False).count()
        batch.exception_count = exceptions

    db.session.commit()
    return jsonify(item.to_dict())


@bp.route('/inventory/exceptions', methods=['GET'])
def get_inventory_exceptions():
    resolved = request.args.get('resolved', '')
    exception_type = request.args.get('exception_type', '')
    query = InventoryException.query
    if resolved == 'true':
        query = query.filter_by(resolved=True)
    elif resolved == 'false':
        query = query.filter_by(resolved=False)
    if exception_type:
        query = query.filter_by(exception_type=exception_type)
    records = query.order_by(InventoryException.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@bp.route('/inventory/exceptions/<int:eid>', methods=['GET'])
def get_inventory_exception(eid):
    record = InventoryException.query.get_or_404(eid)
    return jsonify(record.to_dict())


@bp.route('/inventory/exceptions', methods=['POST'])
def create_inventory_exception():
    data = request.get_json() or {}
    acc = Accessory.query.get_or_404(data.get('accessory_id'))
    record = InventoryException(
        batch_id=data.get('batch_id'),
        accessory_id=data.get('accessory_id'),
        exception_type=data.get('exception_type', ''),
        description=data.get('description', ''),
        reported_at=data.get('reported_at', datetime.now().strftime('%Y-%m-%d')),
        resolved=False,
        resolved_at='',
        resolution='',
        handler=data.get('handler', '')
    )
    db.session.add(record)

    if record.exception_type == '缺失':
        acc.is_lost = True

    if data.get('batch_id'):
        batch = InventoryBatch.query.get(data['batch_id'])
        if batch:
            exceptions = InventoryException.query.filter_by(batch_id=batch.id, resolved=False).count()
            batch.exception_count = exceptions + 1

    db.session.commit()
    return jsonify(record.to_dict()), 201


@bp.route('/inventory/exceptions/<int:eid>/resolve', methods=['POST'])
def resolve_inventory_exception(eid):
    record = InventoryException.query.get_or_404(eid)
    data = request.get_json() or {}
    record.resolved = True
    record.resolved_at = datetime.now().strftime('%Y-%m-%d')
    record.resolution = data.get('resolution', '')
    record.handler = data.get('handler', record.handler)

    acc = Accessory.query.get(record.accessory_id)
    if acc and record.exception_type == '缺失' and data.get('found', False):
        acc.is_lost = False

    if record.batch_id:
        batch = InventoryBatch.query.get(record.batch_id)
        if batch:
            exceptions = InventoryException.query.filter_by(batch_id=batch.id, resolved=False).count()
            batch.exception_count = exceptions

    db.session.commit()
    return jsonify(record.to_dict())


@bp.route('/inventory/exceptions/<int:eid>', methods=['DELETE'])
def delete_inventory_exception(eid):
    record = InventoryException.query.get_or_404(eid)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '已删除'})
