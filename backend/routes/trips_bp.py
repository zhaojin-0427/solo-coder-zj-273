from flask import Blueprint, request, jsonify, send_from_directory
from backend.models import TripPlan, TripDay, TripItem, Accessory, OutfitFavorite
from backend.services import generate_trip_packing, compute_missing_risk, compute_storage_locations, export_trip_content
from backend.extensions import db
from backend.utils.constants import status_label_map
from datetime import datetime

bp = Blueprint('trips', __name__, url_prefix='/api')


@bp.route('/trips', methods=['GET'])
def get_trips():
    status = request.args.get('status', '')
    query = TripPlan.query
    if status:
        query = query.filter(TripPlan.status == status)
    trips = query.order_by(TripPlan.created_at.desc()).all()
    return jsonify([t.to_dict() for t in trips])


@bp.route('/trips/<int:tid>', methods=['GET'])
def get_trip(tid):
    trip = TripPlan.query.get_or_404(tid)
    data = trip.to_dict()
    data['missing_risks'] = compute_missing_risk(trip)
    data['storage_locations'] = compute_storage_locations(trip)

    unique_ids = set()
    reuse_stats = {}
    total_items = 0
    packed_items = 0
    for day in trip.days:
        for item in day.items:
            acc = Accessory.query.get(item.accessory_id)
            if not acc or acc.get_status() != 'in_stock':
                continue
            total_items += 1
            if item.packed:
                packed_items += 1
            unique_ids.add(item.accessory_id)
            if item.accessory_id not in reuse_stats:
                reuse_stats[item.accessory_id] = 0
            reuse_stats[item.accessory_id] = max(reuse_stats[item.accessory_id], item.reuse_count)

    total_reuses = sum(v for v in reuse_stats.values() if v > 1)
    data['packing_rate'] = round(packed_items / max(total_items, 1) * 100, 1)
    data['packed_count'] = packed_items
    data['total_item_count'] = total_items
    data['unique_accessory_count'] = len(unique_ids)
    data['reuse_rate'] = round(len([v for v in reuse_stats.values() if v > 1]) / max(len(unique_ids), 1) * 100, 1)
    data['total_reuses'] = total_reuses

    return jsonify(data)


@bp.route('/trips', methods=['POST'])
def create_trip():
    data = request.get_json() or {}
    trip = TripPlan(
        name=data.get('name', f'行程_{datetime.now().strftime("%Y%m%d")}'),
        destination=data.get('destination', ''),
        start_date=data.get('start_date', ''),
        end_date=data.get('end_date', ''),
        temp_min=int(data.get('temp_min', 20)),
        temp_max=int(data.get('temp_max', 28)),
        main_occasion=data.get('main_occasion', ''),
        main_color=data.get('main_color', ''),
        style=data.get('style', ''),
        notes=data.get('notes', ''),
        status=data.get('status', 'planning')
    )
    db.session.add(trip)
    db.session.flush()

    day_plans = generate_trip_packing(trip)
    for dp in day_plans:
        day = TripDay(
            trip_id=trip.id,
            day_index=dp['day_index'],
            date=dp['date'],
            occasion=dp['occasion'],
            weather=dp['weather'],
            generated=True
        )
        db.session.add(day)
        db.session.flush()
        for it in dp['items']:
            item = TripItem(
                day_id=day.id,
                accessory_id=it['accessory'].id,
                item_type=it['item_type'],
                is_spare=it['is_spare'],
                reason=it['reason'],
                reuse_count=it['reuse_count'],
                packed=False
            )
            db.session.add(item)

    db.session.commit()
    return jsonify(trip.to_dict()), 201


@bp.route('/trips/<int:tid>', methods=['PUT'])
def update_trip(tid):
    trip = TripPlan.query.get_or_404(tid)
    data = request.get_json() or {}
    fields = ['name', 'destination', 'start_date', 'end_date', 'main_occasion', 'main_color', 'style', 'notes', 'status']
    for f in fields:
        if f in data:
            setattr(trip, f, data[f])
    if 'temp_min' in data:
        trip.temp_min = int(data['temp_min'])
    if 'temp_max' in data:
        trip.temp_max = int(data['temp_max'])
    db.session.commit()
    return jsonify(trip.to_dict())


@bp.route('/trips/<int:tid>', methods=['DELETE'])
def delete_trip(tid):
    trip = TripPlan.query.get_or_404(tid)
    db.session.delete(trip)
    db.session.commit()
    return jsonify({'message': '已删除'})


@bp.route('/trips/<int:tid>/regenerate', methods=['POST'])
def regenerate_trip(tid):
    trip = TripPlan.query.get_or_404(tid)

    for day in trip.days:
        for item in day.items:
            db.session.delete(item)
        db.session.delete(day)
    db.session.flush()

    day_plans = generate_trip_packing(trip)
    for dp in day_plans:
        day = TripDay(
            trip_id=trip.id,
            day_index=dp['day_index'],
            date=dp['date'],
            occasion=dp['occasion'],
            weather=dp['weather'],
            generated=True
        )
        db.session.add(day)
        db.session.flush()
        for it in dp['items']:
            item = TripItem(
                day_id=day.id,
                accessory_id=it['accessory'].id,
                item_type=it['item_type'],
                is_spare=it['is_spare'],
                reason=it['reason'],
                reuse_count=it['reuse_count'],
                packed=False
            )
            db.session.add(item)

    db.session.commit()
    return jsonify(trip.to_dict())


@bp.route('/trips/items/<int:iid>/pack', methods=['POST'])
def toggle_pack_item(iid):
    item = TripItem.query.get_or_404(iid)
    acc = Accessory.query.get(item.accessory_id)
    if acc and acc.get_status() != 'in_stock':
        return jsonify({'error': f'该饰品当前状态为「{status_label_map.get(acc.get_status(), acc.get_status())}」，无法打包'}), 400
    data = request.get_json() or {}
    if 'packed' in data:
        item.packed = bool(data['packed'])
    else:
        item.packed = not item.packed
    db.session.commit()
    return jsonify(item.to_dict())


@bp.route('/trips/<int:tid>/pack-all', methods=['POST'])
def pack_all_items(tid):
    trip = TripPlan.query.get_or_404(tid)
    total = 0
    packed = 0
    for day in trip.days:
        for item in day.items:
            total += 1
            acc = Accessory.query.get(item.accessory_id)
            if acc and acc.get_status() == 'in_stock':
                item.packed = True
                packed += 1
    db.session.commit()
    return jsonify({'message': f'已打包 {packed}/{total} 件在库饰品', 'packed_count': packed, 'total_count': total})


@bp.route('/trips/<int:tid>/save-favorite', methods=['POST'])
def save_trip_day_as_favorite(tid):
    data = request.get_json() or {}
    day_id = data.get('day_id')
    if not day_id:
        return jsonify({'error': '缺少 day_id'}), 400
    day = TripDay.query.get_or_404(day_id)
    necklace_id = None
    earring_id = None
    bracelet_id = None
    skipped = 0
    for item in day.items:
        if item.is_spare:
            continue
        acc = Accessory.query.get(item.accessory_id)
        if not acc:
            continue
        if acc.get_status() != 'in_stock':
            skipped += 1
            continue
        if acc.category == '项链' and not necklace_id:
            necklace_id = acc.id
        elif acc.category == '耳环' and not earring_id:
            earring_id = acc.id
        elif acc.category == '手链' and not bracelet_id:
            bracelet_id = acc.id
    if not necklace_id and not earring_id and not bracelet_id:
        return jsonify({'error': '该日搭配中的饰品均不在库，无法收藏'}), 400

    trip = TripPlan.query.get(tid)
    fav = OutfitFavorite(
        name=data.get('name', f'{trip.name if trip else "行程"}搭配'),
        occasion=day.occasion or (trip.main_occasion if trip else ''),
        necklace_id=necklace_id,
        earring_id=earring_id,
        bracelet_id=bracelet_id,
        main_color=trip.main_color if trip else '',
        style=trip.style if trip else '',
        notes=data.get('notes', f'来自行程「{trip.name if trip else ""}」第{day.day_index + 1}天搭配')
    )
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.to_dict()), 201


@bp.route('/trips/<int:tid>/export', methods=['GET'])
def export_trip(tid):
    trip = TripPlan.query.get_or_404(tid)
    result = export_trip_content(trip)
    return jsonify(result)
