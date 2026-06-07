from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random
import uuid
from itertools import product

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "accessories.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)


class Accessory(db.Model):
    __tablename__ = 'accessories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    material = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    color_family = db.Column(db.String(30), nullable=False)
    style = db.Column(db.String(50), nullable=False)
    occasions = db.Column(db.String(200), default='')
    storage_location = db.Column(db.String(100), default='')
    photo = db.Column(db.String(200), default='')
    last_worn_date = db.Column(db.String(20), default='')
    wear_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'material': self.material,
            'color': self.color,
            'color_family': self.color_family,
            'style': self.style,
            'occasions': self.occasions.split(',') if self.occasions else [],
            'storage_location': self.storage_location,
            'photo': self.photo,
            'last_worn_date': self.last_worn_date,
            'wear_count': self.wear_count,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }


class OutfitFavorite(db.Model):
    __tablename__ = 'outfit_favorites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    occasion = db.Column(db.String(50), default='')
    necklace_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=True)
    earring_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=True)
    bracelet_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=True)
    main_color = db.Column(db.String(50), default='')
    style = db.Column(db.String(50), default='')
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    use_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        necklace = Accessory.query.get(self.necklace_id) if self.necklace_id else None
        earring = Accessory.query.get(self.earring_id) if self.earring_id else None
        bracelet = Accessory.query.get(self.bracelet_id) if self.bracelet_id else None
        return {
            'id': self.id,
            'name': self.name,
            'occasion': self.occasion,
            'necklace': necklace.to_dict() if necklace else None,
            'earring': earring.to_dict() if earring else None,
            'bracelet': bracelet.to_dict() if bracelet else None,
            'necklace_id': self.necklace_id,
            'earring_id': self.earring_id,
            'bracelet_id': self.bracelet_id,
            'main_color': self.main_color,
            'style': self.style,
            'notes': self.notes,
            'use_count': self.use_count,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }


COLOR_COMBINATIONS = {
    '金色': ['白色', '黑色', '红色', '绿色', '蓝色', '紫色', '米色'],
    '银色': ['白色', '黑色', '蓝色', '紫色', '粉色', '灰色'],
    '玫瑰金': ['白色', '粉色', '米色', '红色', '紫色'],
    '白色': ['金色', '银色', '玫瑰金', '粉色', '蓝色'],
    '黑色': ['金色', '银色', '红色', '绿色', '紫色'],
    '红色': ['金色', '黑色', '白色', '绿色'],
    '粉色': ['玫瑰金', '银色', '白色', '紫色'],
    '蓝色': ['金色', '银色', '白色', '黄色'],
    '绿色': ['金色', '红色', '白色', '米色'],
    '紫色': ['金色', '银色', '粉色', '白色'],
    '米色': ['金色', '玫瑰金', '棕色', '白色'],
    '棕色': ['金色', '米色', '白色', '绿色'],
    '灰色': ['银色', '金色', '白色', '黑色'],
    '黄色': ['金色', '蓝色', '白色', '棕色']
}

STYLE_MATCH = {
    '优雅': ['优雅', '简约', '复古'],
    '休闲': ['休闲', '简约', '波西米亚'],
    '复古': ['复古', '优雅', '民族风'],
    '简约': ['简约', '优雅', '休闲'],
    '华丽': ['华丽', '优雅', '复古'],
    '波西米亚': ['波西米亚', '休闲', '民族风'],
    '甜美': ['甜美', '简约', '优雅'],
    '民族风': ['民族风', '复古', '波西米亚'],
    '商务': ['商务', '简约', '优雅'],
    '运动': ['运动', '休闲']
}


def get_color_score(acc_color_family, main_color):
    matches = COLOR_COMBINATIONS.get(main_color, [])
    if acc_color_family == main_color:
        return 10
    if acc_color_family in matches:
        return 8
    return 3


def get_style_score(acc_style, target_style):
    matches = STYLE_MATCH.get(target_style, [])
    if acc_style == target_style:
        return 10
    if acc_style in matches:
        return 6
    return 2


def get_occasion_score(acc, occasion):
    if not occasion:
        return 5
    occasions = acc.occasions.split(',') if acc.occasions else []
    if occasion in occasions:
        return 10
    return 4


def generate_reason(necklace, earring, bracelet, main_color, style, occasion):
    reasons = []
    pieces = [('项链', necklace), ('耳环', earring), ('手链', bracelet)]
    pieces = [(n, p) for n, p in pieces if p]

    color_match_count = sum(1 for _, p in pieces if p.color_family in COLOR_COMBINATIONS.get(main_color, []) or p.color_family == main_color)
    if color_match_count == len(pieces):
        reasons.append(f"所有饰品的色系都与主色调{main_color}完美协调")
    elif color_match_count > 0:
        reasons.append(f"部分饰品与主色调{main_color}形成和谐搭配")

    style_match_count = sum(1 for _, p in pieces if p.style == style or p.style in STYLE_MATCH.get(style, []))
    if style_match_count == len(pieces):
        reasons.append(f"整体风格统一为{style}风")
    elif style_match_count > 0:
        reasons.append(f"主要单品契合{style}风格定位")

    if occasion:
        occ_match = [n for n, p in pieces if occasion in (p.occasions.split(',') if p.occasions else [])]
        if occ_match:
            reasons.append(f"{'、'.join(occ_match)}适合{occasion}场合佩戴")

    materials = list(set(p.material for _, p in pieces))
    if len(materials) == 1:
        reasons.append(f"材质统一为{materials[0]}，整体质感一致")
    elif len(materials) == 2:
        reasons.append(f"{materials[0]}与{materials[1]}材质碰撞，产生层次感")

    if not reasons:
        reasons.append("整体搭配简洁大方，适合日常佩戴")

    return '；'.join(reasons) + '。'


@app.route('/')
def index():
    return jsonify({'message': '饰品管理平台 API 已启动'})


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/accessories', methods=['GET'])
def get_accessories():
    category = request.args.get('category', '')
    color_family = request.args.get('color_family', '')
    style = request.args.get('style', '')
    occasion = request.args.get('occasion', '')
    storage = request.args.get('storage_location', '')

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

    return jsonify([a.to_dict() for a in items])


@app.route('/api/accessories/<int:aid>', methods=['GET'])
def get_accessory(aid):
    acc = Accessory.query.get_or_404(aid)
    return jsonify(acc.to_dict())


@app.route('/api/accessories', methods=['POST'])
def create_accessory():
    data = request.form.to_dict()
    photo_filename = ''
    if 'photo' in request.files:
        f = request.files['photo']
        if f and f.filename:
            ext = os.path.splitext(f.filename)[1]
            photo_filename = f"acc_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:8]}{ext}"
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    occasions = request.form.get('occasions', '')
    if isinstance(occasions, str) and occasions.startswith('['):
        import ast
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
        wear_count=int(data.get('wear_count', 0))
    )
    db.session.add(acc)
    db.session.commit()
    return jsonify(acc.to_dict()), 201


@app.route('/api/accessories/<int:aid>', methods=['PUT'])
def update_accessory(aid):
    acc = Accessory.query.get_or_404(aid)
    data = request.form.to_dict()

    if 'photo' in request.files:
        f = request.files['photo']
        if f and f.filename:
            if acc.photo:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], acc.photo)
                if os.path.exists(old_path):
                    os.remove(old_path)
            ext = os.path.splitext(f.filename)[1]
            photo_filename = f"acc_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:8]}{ext}"
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
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
            import ast
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

    db.session.commit()
    return jsonify(acc.to_dict())


@app.route('/api/accessories/<int:aid>/wear', methods=['POST'])
def wear_accessory(aid):
    acc = Accessory.query.get_or_404(aid)
    acc.wear_count += 1
    acc.last_worn_date = datetime.now().strftime('%Y-%m-%d')
    db.session.commit()
    return jsonify(acc.to_dict())


@app.route('/api/accessories/<int:aid>', methods=['DELETE'])
def delete_accessory(aid):
    acc = Accessory.query.get_or_404(aid)
    if acc.photo:
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], acc.photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    db.session.delete(acc)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/storage_locations', methods=['GET'])
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


@app.route('/api/recommend', methods=['GET'])
def get_recommendation():
    main_color = request.args.get('main_color', '')
    style = request.args.get('style', '')
    occasion = request.args.get('occasion', '')

    necklaces = Accessory.query.filter_by(category='项链').all()
    earrings = Accessory.query.filter_by(category='耳环').all()
    bracelets = Accessory.query.filter_by(category='手链').all()

    def score_item(acc):
        if not acc:
            return 0
        s = 0
        if main_color:
            s += get_color_score(acc.color_family, main_color) * 2
        if style:
            s += get_style_score(acc.style, style) * 1.5
        if occasion:
            s += get_occasion_score(acc, occasion)
        s += min(acc.wear_count, 5) * 0.2
        return s

    def pick_best(items, top_n=3):
        scored = [(score_item(it), it) for it in items]
        scored.sort(key=lambda x: -x[0])
        return [it for _, it in scored[:top_n]]

    top_necklaces = pick_best(necklaces)
    top_earrings = pick_best(earrings)
    top_bracelets = pick_best(bracelets)

    combos = list(product(top_necklaces or [None], top_earrings or [None], top_bracelets or [None]))
    combos = [c for c in combos if any(c)]

    def combo_score(combo):
        n, e, b = combo
        s = 0
        for p in [n, e, b]:
            s += score_item(p)
        colors = set(p.color_family for p in [n, e, b] if p)
        if len(colors) <= 2:
            s += 5
        materials = set(p.material for p in [n, e, b] if p)
        if len(materials) == 1:
            s += 3
        return s

    max_per_item = 0
    if main_color:
        max_per_item += 10 * 2
    if style:
        max_per_item += 10 * 1.5
    if occasion:
        max_per_item += 10
    max_per_item += 1
    piece_count = 3 if (necklaces and earrings and bracelets) else (
        2 if ((necklaces and earrings) or (necklaces and bracelets) or (earrings and bracelets)) else 1
    )
    max_combo_score = max_per_item * piece_count + 8
    if max_combo_score == 0:
        max_combo_score = 1

    combos.sort(key=combo_score, reverse=True)
    top_combos = combos[:5]

    results = []
    for idx, combo in enumerate(top_combos):
        n, e, b = combo
        raw_score = combo_score(combo)
        results.append({
            'id': idx + 1,
            'score': round(raw_score, 1),
            'score_percent': min(100, round(raw_score / max_combo_score * 100)),
            'necklace': n.to_dict() if n else None,
            'earring': e.to_dict() if e else None,
            'bracelet': b.to_dict() if b else None,
            'reason': generate_reason(n, e, b, main_color, style, occasion)
        })

    return jsonify(results)


@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    occasion = request.args.get('occasion', '')
    query = OutfitFavorite.query
    if occasion:
        query = query.filter(OutfitFavorite.occasion == occasion)
    favs = query.order_by(OutfitFavorite.created_at.desc()).all()
    return jsonify([f.to_dict() for f in favs])


@app.route('/api/favorites', methods=['POST'])
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


@app.route('/api/favorites/<int:fid>/use', methods=['POST'])
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


@app.route('/api/favorites/<int:fid>', methods=['DELETE'])
def delete_favorite(fid):
    fav = OutfitFavorite.query.get_or_404(fid)
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    all_acc = Accessory.query.all()
    total = len(all_acc)

    color_stats = {}
    category_stats = {}
    for acc in all_acc:
        color_stats[acc.color_family] = color_stats.get(acc.color_family, 0) + 1
        category_stats[acc.category] = category_stats.get(acc.category, 0) + 1

    color_distribution = [
        {'color': c, 'count': cnt, 'percentage': round(cnt / total * 100, 1) if total else 0}
        for c, cnt in sorted(color_stats.items(), key=lambda x: -x[1])
    ]

    favs = OutfitFavorite.query.order_by(OutfitFavorite.use_count.desc()).limit(10).all()
    frequent_combos = [f.to_dict() for f in favs if f.use_count > 0]

    from datetime import datetime, timedelta
    today = datetime.now()
    long_unworn = []
    for acc in all_acc:
        if not acc.last_worn_date:
            days = (today - acc.created_at).days if acc.created_at else 999
        else:
            try:
                lw = datetime.strptime(acc.last_worn_date, '%Y-%m-%d')
                days = (today - lw).days
                if days < 0:
                    days = 0
            except:
                days = 999
        if days >= 30:
            d = acc.to_dict()
            d['days_unworn'] = days
            long_unworn.append(d)
    long_unworn.sort(key=lambda x: -x['days_unworn'])

    total_wears = sum(a.wear_count for a in all_acc)
    utilization_rate = round(total_wears / max(total, 1) / max(1, 30) * 100, 1)

    worn_30d = 0
    for acc in all_acc:
        if acc.last_worn_date:
            try:
                lw = datetime.strptime(acc.last_worn_date, '%Y-%m-%d')
                days_diff = (today - lw).days
                if 0 <= days_diff <= 30:
                    worn_30d += 1
            except:
                pass
    active_rate = round(worn_30d / max(total, 1) * 100, 1)

    return jsonify({
        'total': total,
        'category_distribution': [
            {'category': c, 'count': cnt, 'percentage': round(cnt / total * 100, 1) if total else 0}
            for c, cnt in sorted(category_stats.items(), key=lambda x: -x[1])
        ],
        'color_distribution': color_distribution,
        'frequent_combos': frequent_combos,
        'long_unworn': long_unworn,
        'utilization_rate': min(utilization_rate, 100),
        'active_rate': active_rate,
        'total_wears': total_wears,
        'active_count': worn_30d
    })


@app.route('/api/meta', methods=['GET'])
def get_meta():
    return jsonify({
        'categories': ['项链', '耳环', '手链', '戒指', '胸针', '发饰', '其他'],
        'materials': ['黄金', '白金', '玫瑰金', '纯银', '合金', '珍珠', '水晶', '宝石', '玉石', '布料', '皮革', '其他'],
        'color_families': ['金色', '银色', '玫瑰金', '白色', '黑色', '红色', '粉色', '蓝色', '绿色', '紫色', '米色', '棕色', '灰色', '黄色'],
        'styles': ['优雅', '休闲', '复古', '简约', '华丽', '波西米亚', '甜美', '民族风', '商务', '运动'],
        'occasions': ['日常', '工作', '约会', '派对', '婚礼', '晚宴', '旅行', '运动', '节日', '正式场合']
    })


with app.app_context():
    db.create_all()

    if Accessory.query.count() == 0:
        sample_data = [
            {'name': '经典黄金项链', 'category': '项链', 'material': '黄金', 'color': '亮金色', 'color_family': '金色', 'style': '优雅', 'occasions': '日常,工作,约会', 'storage_location': '首饰盒A层', 'wear_count': 12, 'last_worn_date': '2026-06-01'},
            {'name': '珍珠耳钉', 'category': '耳环', 'material': '珍珠', 'color': '奶白色', 'color_family': '白色', 'style': '优雅', 'occasions': '工作,正式场合,婚礼', 'storage_location': '首饰盒A层', 'wear_count': 8, 'last_worn_date': '2026-06-03'},
            {'name': '银色流苏手链', 'category': '手链', 'material': '纯银', 'color': '银白色', 'color_family': '银色', 'style': '休闲', 'occasions': '日常,约会,旅行', 'storage_location': '首饰盒B层', 'wear_count': 5, 'last_worn_date': '2026-05-20'},
            {'name': '玫瑰金心形吊坠', 'category': '项链', 'material': '玫瑰金', 'color': '粉金色', 'color_family': '玫瑰金', 'style': '甜美', 'occasions': '约会,日常,派对', 'storage_location': '首饰盒A层', 'wear_count': 15, 'last_worn_date': '2026-06-05'},
            {'name': '复古绿宝石耳环', 'category': '耳环', 'material': '宝石', 'color': '祖母绿', 'color_family': '绿色', 'style': '复古', 'occasions': '派对,晚宴,正式场合', 'storage_location': '首饰盒C层', 'wear_count': 3, 'last_worn_date': '2026-04-15'},
            {'name': '简约金色手镯', 'category': '手链', 'material': '黄金', 'color': '哑光金', 'color_family': '金色', 'style': '简约', 'occasions': '日常,工作', 'storage_location': '首饰盒B层', 'wear_count': 20, 'last_worn_date': '2026-06-06'},
            {'name': '波西米亚水晶项链', 'category': '项链', 'material': '水晶', 'color': '天蓝色', 'color_family': '蓝色', 'style': '波西米亚', 'occasions': '旅行,日常,派对', 'storage_location': '挂架-左侧', 'wear_count': 2, 'last_worn_date': '2026-03-10'},
            {'name': '粉色水晶耳坠', 'category': '耳环', 'material': '水晶', 'color': '樱花粉', 'color_family': '粉色', 'style': '甜美', 'occasions': '约会,日常,节日', 'storage_location': '首饰盒C层', 'wear_count': 6, 'last_worn_date': '2026-05-28'},
            {'name': '商务款银色领带夹', 'category': '其他', 'material': '纯银', 'color': '亮银色', 'color_family': '银色', 'style': '商务', 'occasions': '工作,正式场合', 'storage_location': '抽屉-右侧', 'wear_count': 1, 'last_worn_date': '2026-02-01'},
            {'name': '紫色宝石手链', 'category': '手链', 'material': '宝石', 'color': '紫罗兰', 'color_family': '紫色', 'style': '华丽', 'occasions': '晚宴,派对,婚礼', 'storage_location': '首饰盒B层', 'wear_count': 4, 'last_worn_date': '2026-05-15'}
        ]
        for d in sample_data:
            d['occasions'] = d['occasions']
            db.session.add(Accessory(**d))
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9202, debug=True)
