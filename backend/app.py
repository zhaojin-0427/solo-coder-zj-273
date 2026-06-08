from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "accessories.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

from backend.extensions import db
db.init_app(app)

from backend.routes import (
    accessories_bp, recommend_bp, trips_bp, tracking_bp,
    valuations_bp, certificates_bp, inventory_bp, insurance_bp, statistics_bp
)
app.register_blueprint(accessories_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(trips_bp)
app.register_blueprint(tracking_bp)
app.register_blueprint(valuations_bp)
app.register_blueprint(certificates_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(insurance_bp)
app.register_blueprint(statistics_bp)


@app.route('/')
def index():
    return jsonify({'message': '饰品管理平台 API 已启动'})


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


with app.app_context():
    db.create_all()

    from sqlalchemy import inspect, text
    from backend.models import Accessory

    inspector = inspect(db.engine)
    existing_cols = [c['name'] for c in inspector.get_columns('accessories')]
    new_cols = {
        'next_maintenance_date': "VARCHAR(20) DEFAULT ''",
        'maintenance_cycle_days': "INTEGER DEFAULT 0",
        'purchase_channel': "VARCHAR(100) DEFAULT ''",
        'purchase_price': "FLOAT DEFAULT 0.0",
        'brand': "VARCHAR(100) DEFAULT ''",
        'purchase_date': "VARCHAR(20) DEFAULT ''",
        'valuation_notes': "TEXT DEFAULT ''",
        'precious_metal_weight': "FLOAT DEFAULT 0.0",
        'gemstone_params': "TEXT DEFAULT ''",
        'is_lost': "BOOLEAN DEFAULT 0",
        'maintenance_status': "VARCHAR(20) DEFAULT 'good'"
    }
    for col, col_def in new_cols.items():
        if col not in existing_cols:
            try:
                db.session.execute(text(f"ALTER TABLE accessories ADD COLUMN {col} {col_def}"))
                db.session.commit()
            except:
                pass

    if Accessory.query.count() == 0:
        sample_data = [
            {'name': '经典黄金项链', 'category': '项链', 'material': '黄金', 'color': '亮金色', 'color_family': '金色', 'style': '优雅', 'occasions': '日常,工作,约会', 'storage_location': '首饰盒A层', 'wear_count': 12, 'last_worn_date': '2026-06-01', 'purchase_channel': '品牌专柜', 'purchase_price': 8800.0, 'brand': '周大福', 'purchase_date': '2024-03-15', 'precious_metal_weight': 12.5, 'maintenance_status': 'good'},
            {'name': '珍珠耳钉', 'category': '耳环', 'material': '珍珠', 'color': '奶白色', 'color_family': '白色', 'style': '优雅', 'occasions': '工作,正式场合,婚礼', 'storage_location': '首饰盒A层', 'wear_count': 8, 'last_worn_date': '2026-06-03', 'purchase_channel': '品牌专柜', 'purchase_price': 3200.0, 'brand': 'Tiffany', 'purchase_date': '2024-08-20', 'maintenance_status': 'good'},
            {'name': '银色流苏手链', 'category': '手链', 'material': '纯银', 'color': '银白色', 'color_family': '银色', 'style': '休闲', 'occasions': '日常,约会,旅行', 'storage_location': '首饰盒B层', 'wear_count': 5, 'last_worn_date': '2026-05-20', 'purchase_channel': '官方网店', 'purchase_price': 680.0, 'brand': '其他', 'purchase_date': '2025-01-10', 'precious_metal_weight': 8.2, 'maintenance_status': 'fair'},
            {'name': '玫瑰金心形吊坠', 'category': '项链', 'material': '玫瑰金', 'color': '粉金色', 'color_family': '玫瑰金', 'style': '甜美', 'occasions': '约会,日常,派对', 'storage_location': '首饰盒A层', 'wear_count': 15, 'last_worn_date': '2026-06-05', 'purchase_channel': '品牌专柜', 'purchase_price': 5600.0, 'brand': 'Cartier', 'purchase_date': '2024-02-14', 'precious_metal_weight': 6.8, 'maintenance_status': 'good'},
            {'name': '复古绿宝石耳环', 'category': '耳环', 'material': '宝石', 'color': '祖母绿', 'color_family': '绿色', 'style': '复古', 'occasions': '派对,晚宴,正式场合', 'storage_location': '首饰盒C层', 'wear_count': 3, 'last_worn_date': '2026-04-15', 'purchase_channel': '珠宝店', 'purchase_price': 15800.0, 'brand': 'Van Cleef', 'purchase_date': '2023-12-01', 'gemstone_params': '祖母绿 2.5ct 椭圆形切割', 'maintenance_status': 'good'},
            {'name': '简约金色手镯', 'category': '手链', 'material': '黄金', 'color': '哑光金', 'color_family': '金色', 'style': '简约', 'occasions': '日常,工作', 'storage_location': '首饰盒B层', 'wear_count': 20, 'last_worn_date': '2026-06-06', 'purchase_channel': '品牌专柜', 'purchase_price': 12000.0, 'brand': '周生生', 'purchase_date': '2024-06-18', 'precious_metal_weight': 25.0, 'maintenance_status': 'good'},
            {'name': '波西米亚水晶项链', 'category': '项链', 'material': '水晶', 'color': '天蓝色', 'color_family': '蓝色', 'style': '波西米亚', 'occasions': '旅行,日常,派对', 'storage_location': '挂架-左侧', 'wear_count': 2, 'last_worn_date': '2026-03-10', 'purchase_channel': '代购', 'purchase_price': 450.0, 'brand': '其他', 'purchase_date': '2025-09-01', 'maintenance_status': 'good'},
            {'name': '粉色水晶耳坠', 'category': '耳环', 'material': '水晶', 'color': '樱花粉', 'color_family': '粉色', 'style': '甜美', 'occasions': '约会,日常,节日', 'storage_location': '首饰盒C层', 'wear_count': 6, 'last_worn_date': '2026-05-28', 'purchase_channel': '官方网店', 'purchase_price': 380.0, 'brand': '其他', 'purchase_date': '2025-11-11', 'maintenance_status': 'good'},
            {'name': '商务款银色领带夹', 'category': '其他', 'material': '纯银', 'color': '亮银色', 'color_family': '银色', 'style': '商务', 'occasions': '工作,正式场合', 'storage_location': '抽屉-右侧', 'wear_count': 1, 'last_worn_date': '2026-02-01', 'purchase_channel': '亲友赠送', 'purchase_price': 880.0, 'brand': 'Gucci', 'purchase_date': '2025-05-20', 'precious_metal_weight': 15.0, 'maintenance_status': 'good'},
            {'name': '紫色宝石手链', 'category': '手链', 'material': '宝石', 'color': '紫罗兰', 'color_family': '紫色', 'style': '华丽', 'occasions': '晚宴,派对,婚礼', 'storage_location': '首饰盒B层', 'wear_count': 4, 'last_worn_date': '2026-05-15', 'purchase_channel': '珠宝店', 'purchase_price': 22000.0, 'brand': 'Bvlgari', 'purchase_date': '2023-10-08', 'gemstone_params': '紫水晶 3.8ct 圆形切割', 'maintenance_status': 'excellent'}
        ]
        for d in sample_data:
            db.session.add(Accessory(**d))
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9202, debug=True)
