from flask import Blueprint, request, jsonify, send_from_directory
from backend.models import Accessory, OutfitFavorite
from backend.services import get_recommendations
from backend.extensions import db
from datetime import datetime

bp = Blueprint('recommend', __name__, url_prefix='/api')


@bp.route('/recommend', methods=['GET'])
def get_recommendation():
    main_color = request.args.get('main_color', '')
    style = request.args.get('style', '')
    occasion = request.args.get('occasion', '')
    results = get_recommendations(main_color, style, occasion)
    return jsonify(results)


@bp.route('/favorites', methods=['GET'])
def get_favorites():
    occasion = request.args.get('occasion', '')
    query = OutfitFavorite.query
    if occasion:
        query = query.filter(OutfitFavorite.occasion == occasion)
    favs = query.order_by(OutfitFavorite.created_at.desc()).all()
    return jsonify([f.to_dict() for f in favs])


@bp.route('/favorites', methods=['POST'])
def create_favorite():
    data = request.get_json() or {}
    fav = OutfitFavorite(
        name=data.get('name', f"搭配_{datetime.now().strftime('%Y%m%d%H%M')}"),
        occasion=data.get('occasion', ''),
        necklace_id=data.get('necklace_id'),
        earring_id=data.get('earring_id'),
        bracelet_id=data.get('bracelet_id'),
        main_color=data.get('main_color', ''),
        style=data.get('style', ''),
        notes=data.get('notes', '')
    )
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.to_dict()), 201


@bp.route('/favorites/<int:fid>/use', methods=['POST'])
def use_favorite(fid):
    fav = OutfitFavorite.query.get_or_404(fid)
    fav.use_count += 1
    for aid in [fav.necklace_id, fav.earring_id, fav.bracelet_id]:
        if aid:
            acc = Accessory.query.get(aid)
            if acc:
                acc.wear_count += 1
                acc.last_worn_date = datetime.now().strftime('%Y-%m-%d')
    db.session.commit()
    return jsonify(fav.to_dict())


@bp.route('/favorites/<int:fid>', methods=['DELETE'])
def delete_favorite(fid):
    fav = OutfitFavorite.query.get_or_404(fid)
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': '已删除'})
