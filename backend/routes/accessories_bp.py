from flask import Blueprint, request, jsonify, send_from_directory
from backend.models import Accessory
from backend.extensions import db
from datetime import datetime
import os
import uuid
import ast

bp = Blueprint('accessories', __name__, url_prefix='/api')

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


@bp.route('/accessories', methods=['GET'])
def get_accessories():
    category = request.args.get('category', '')
    color_family = request.args.get('color_family', '')
    style = request.args.get('style', '')
    occasion = request.args.get('occasion', '')
    storage = request.args.get('storage_location', '')
    status = request.args.get('status', '')

    query = Accessory.query
    if category:
        query = query.filter(Accessory.category == category)
    if color_family:
        query = query.filter(Accessory.color_family == color_family)
    if style:
        query = query.filter(Accessory.style == style)
    if storage:
        query = query.filter(Accessory.storage_location == storage)

    items = query.all()
    if occasion:
        items = [a for a in items if occasion in (a.occasions.split(',') if a.occasions else [])]
    if status:
        items = [a for a in items if a.get_status() == status]

    return jsonify([a.to_dict() for a in items])


@bp.route('/accessories/<int:aid>', methods=['GET'])
def get_accessory(aid):
    acc = Accessory.query.get_or_404(aid)
    return jsonify(acc.to_dict())


@bp.route('/accessories', methods=['POST'])
def create_accessory():
    data = request.form.to_dict()
    photo_filename = ''
    if 'photo' in request.files:
        f = request.files['photo']
        if f and f.filename:
            ext = os.path.splitext(f.filename)[1]
            photo_filename = f"acc_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:8]}{ext}"
            f.save(os.path.join(UPLOAD_FOLDER, photo_filename))

    occasions = request.form.get('occasions', '')
    if isinstance(occasions, str) and occasions.startswith('['):
        try:
            occ_list = ast.literal_eval(occasions)
            occasions = ','.join(occ_list)
        except:
            pass

    acc = Accessory(
        name=data.get('name', ''),
        category=data.get('category', ''),
        material=data.get('material', ''),
        color=data.get('color', ''),
        color_family=data.get('color_family', ''),
        style=data.get('style', ''),
        occasions=occasions,
        storage_location=data.get('storage_location', ''),
        photo=photo_filename,
        last_worn_date=data.get('last_worn_date', ''),
        wear_count=int(data.get('wear_count', 0)),
        next_maintenance_date=data.get('next_maintenance_date', ''),
        maintenance_cycle_days=int(data.get('maintenance_cycle_days', 0)),
        purchase_channel=data.get('purchase_channel', ''),
        purchase_price=float(data.get('purchase_price', 0) or 0),
        brand=data.get('brand', ''),
        purchase_date=data.get('purchase_date', ''),
        valuation_notes=data.get('valuation_notes', ''),
        precious_metal_weight=float(data.get('precious_metal_weight', 0) or 0),
        gemstone_params=data.get('gemstone_params', ''),
        is_lost=False,
        maintenance_status=data.get('maintenance_status', 'good')
    )
    db.session.add(acc)
    db.session.commit()
    return jsonify(acc.to_dict()), 201


@bp.route('/accessories/<int:aid>', methods=['PUT'])
def update_accessory(aid):
    acc = Accessory.query.get_or_404(aid)
    data = request.form.to_dict()

    if 'photo' in request.files:
        f = request.files['photo']
        if f and f.filename:
            if acc.photo:
                old_path = os.path.join(UPLOAD_FOLDER, acc.photo)
                if os.path.exists(old_path):
                    os.remove(old_path)
            ext = os.path.splitext(f.filename)[1]
            photo_filename = f"acc_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:8]}{ext}"
            f.save(os.path.join(UPLOAD_FOLDER, photo_filename))
            acc.photo = photo_filename

    if 'name' in data:
        acc.name = data['name']
    if 'category' in data:
        acc.category = data['category']
    if 'material' in data:
        acc.material = data['material']
    if 'color' in data:
        acc.color = data['color']
    if 'color_family' in data:
        acc.color_family = data['color_family']
    if 'style' in data:
        acc.style = data['style']
    if 'occasions' in data:
        occasions = data['occasions']
        if isinstance(occasions, str) and occasions.startswith('['):
            try:
                occ_list = ast.literal_eval(occasions)
                occasions = ','.join(occ_list)
            except:
                pass
        acc.occasions = occasions
    if 'storage_location' in data:
        acc.storage_location = data['storage_location']
    if 'last_worn_date' in data:
        acc.last_worn_date = data['last_worn_date']
    if 'wear_count' in data:
        acc.wear_count = int(data['wear_count'])
    if 'next_maintenance_date' in data:
        acc.next_maintenance_date = data['next_maintenance_date']
    if 'maintenance_cycle_days' in data:
        acc.maintenance_cycle_days = int(data['maintenance_cycle_days'])
    if 'purchase_channel' in data:
        acc.purchase_channel = data['purchase_channel']
    if 'purchase_price' in data:
        acc.purchase_price = float(data['purchase_price'] or 0)
    if 'brand' in data:
        acc.brand = data['brand']
    if 'purchase_date' in data:
        acc.purchase_date = data['purchase_date']
    if 'valuation_notes' in data:
        acc.valuation_notes = data['valuation_notes']
    if 'precious_metal_weight' in data:
        acc.precious_metal_weight = float(data['precious_metal_weight'] or 0)
    if 'gemstone_params' in data:
        acc.gemstone_params = data['gemstone_params']
    if 'is_lost' in data:
        acc.is_lost = str(data['is_lost']).lower() in ('true', '1', 'yes')
    if 'maintenance_status' in data:
        acc.maintenance_status = data['maintenance_status']

    db.session.commit()
    return jsonify(acc.to_dict())


@bp.route('/accessories/<int:aid>/wear', methods=['POST'])
def wear_accessory(aid):
    acc = Accessory.query.get_or_404(aid)
    acc.wear_count += 1
    acc.last_worn_date = datetime.now().strftime('%Y-%m-%d')
    db.session.commit()
    return jsonify(acc.to_dict())


@bp.route('/accessories/<int:aid>', methods=['DELETE'])
def delete_accessory(aid):
    acc = Accessory.query.get_or_404(aid)
    if acc.photo:
        photo_path = os.path.join(UPLOAD_FOLDER, acc.photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    db.session.delete(acc)
    db.session.commit()
    return jsonify({'message': '已删除'})


@bp.route('/accessories/<int:aid>/set-maintenance', methods=['POST'])
def set_maintenance_date(aid):
    acc = Accessory.query.get_or_404(aid)
    data = request.get_json() or {}
    if 'next_maintenance_date' in data:
        acc.next_maintenance_date = data['next_maintenance_date']
    if 'maintenance_cycle_days' in data:
        acc.maintenance_cycle_days = int(data['maintenance_cycle_days'])
    db.session.commit()
    return jsonify(acc.to_dict())


@bp.route('/storage_locations', methods=['GET'])
def get_storage_locations():
    locations = db.session.query(Accessory.storage_location).filter(
        Accessory.storage_location != ''
    ).distinct().all()
    loc_list = [l[0] for l in locations]
    result = []
    for loc in loc_list:
        items = Accessory.query.filter_by(storage_location=loc).all()
        result.append({
            'name': loc,
            'count': len(items),
            'accessories': [a.to_dict() for a in items]
        })
    return jsonify(result)
