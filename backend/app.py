from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
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

status_label_map = {
    'in_stock': '在库',
    'lent': '已借出',
    'overdue': '逾期未还',
    'maintenance': '保养中',
    'repair': '维修中',
    'lost': '已丢失',
    'inventory_exception': '盘点异常'
}


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
    next_maintenance_date = db.Column(db.String(20), default='')
    maintenance_cycle_days = db.Column(db.Integer, default=0)
    purchase_channel = db.Column(db.String(100), default='')
    purchase_price = db.Column(db.Float, default=0.0)
    brand = db.Column(db.String(100), default='')
    purchase_date = db.Column(db.String(20), default='')
    valuation_notes = db.Column(db.Text, default='')
    precious_metal_weight = db.Column(db.Float, default=0.0)
    gemstone_params = db.Column(db.Text, default='')
    is_lost = db.Column(db.Boolean, default=False)
    maintenance_status = db.Column(db.String(20), default='good')

    def get_status(self):
        if self.is_lost:
            return 'lost'
        today = datetime.now()
        active_loan = LoanRecord.query.filter_by(
            accessory_id=self.id, returned=False
        ).first()
        if active_loan:
            try:
                due = datetime.strptime(active_loan.due_date, '%Y-%m-%d')
                if today > due:
                    return 'overdue'
            except:
                pass
            return 'lent'
        active_maint = MaintenanceRecord.query.filter_by(
            accessory_id=self.id, completed=False
        ).first()
        if active_maint:
            if active_maint.record_type == 'maintenance':
                return 'maintenance'
            else:
                return 'repair'
        pending_exception = InventoryException.query.filter_by(
            accessory_id=self.id, resolved=False
        ).first()
        if pending_exception:
            return 'inventory_exception'
        return 'in_stock'

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
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
            'status': self.get_status(),
            'next_maintenance_date': self.next_maintenance_date,
            'maintenance_cycle_days': self.maintenance_cycle_days,
            'purchase_channel': self.purchase_channel,
            'purchase_price': self.purchase_price,
            'brand': self.brand,
            'purchase_date': self.purchase_date,
            'valuation_notes': self.valuation_notes,
            'precious_metal_weight': self.precious_metal_weight,
            'gemstone_params': self.gemstone_params,
            'is_lost': self.is_lost,
            'maintenance_status': self.maintenance_status
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


class TripPlan(db.Model):
    __tablename__ = 'trip_plans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), default='')
    start_date = db.Column(db.String(20), default='')
    end_date = db.Column(db.String(20), default='')
    temp_min = db.Column(db.Integer, default=20)
    temp_max = db.Column(db.Integer, default=28)
    main_occasion = db.Column(db.String(50), default='')
    main_color = db.Column(db.String(50), default='')
    style = db.Column(db.String(50), default='')
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='planning')

    days = db.relationship('TripDay', backref='trip', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'destination': self.destination,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'temp_min': self.temp_min,
            'temp_max': self.temp_max,
            'main_occasion': self.main_occasion,
            'main_color': self.main_color,
            'style': self.style,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
            'days': [d.to_dict() for d in sorted(self.days, key=lambda x: x.day_index)]
        }


class TripDay(db.Model):
    __tablename__ = 'trip_days'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip_plans.id'), nullable=False)
    day_index = db.Column(db.Integer, default=0)
    date = db.Column(db.String(20), default='')
    occasion = db.Column(db.String(50), default='')
    weather = db.Column(db.String(50), default='')
    generated = db.Column(db.Boolean, default=False)

    items = db.relationship('TripItem', backref='day', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'day_index': self.day_index,
            'date': self.date,
            'occasion': self.occasion,
            'weather': self.weather,
            'generated': self.generated,
            'items': [i.to_dict() for i in self.items]
        }


class TripItem(db.Model):
    __tablename__ = 'trip_items'
    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey('trip_days.id'), nullable=False)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    item_type = db.Column(db.String(20), default='recommended')
    packed = db.Column(db.Boolean, default=False)
    is_spare = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(200), default='')
    reuse_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        acc = Accessory.query.get(self.accessory_id)
        return {
            'id': self.id,
            'accessory_id': self.accessory_id,
            'item_type': self.item_type,
            'packed': self.packed,
            'is_spare': self.is_spare,
            'reason': self.reason,
            'reuse_count': self.reuse_count,
            'accessory': acc.to_dict() if acc else None
        }


class LoanRecord(db.Model):
    __tablename__ = 'loan_records'
    id = db.Column(db.Integer, primary_key=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    borrower_name = db.Column(db.String(100), nullable=False)
    borrower_phone = db.Column(db.String(50), default='')
    borrower_contact = db.Column(db.String(200), default='')
    loan_date = db.Column(db.String(20), default='')
    due_date = db.Column(db.String(20), default='')
    return_date = db.Column(db.String(20), default='')
    deposit = db.Column(db.Float, default=0.0)
    deposit_returned = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, default='')
    returned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        acc = Accessory.query.get(self.accessory_id)
        is_overdue = False
        days_overdue = 0
        if not self.returned and self.due_date:
            try:
                due = datetime.strptime(self.due_date, '%Y-%m-%d')
                today = datetime.now()
                if today > due:
                    is_overdue = True
                    days_overdue = (today - due).days
            except:
                pass
        return {
            'id': self.id,
            'accessory_id': self.accessory_id,
            'accessory': acc.to_dict() if acc else None,
            'borrower_name': self.borrower_name,
            'borrower_phone': self.borrower_phone,
            'borrower_contact': self.borrower_contact,
            'loan_date': self.loan_date,
            'due_date': self.due_date,
            'return_date': self.return_date,
            'deposit': self.deposit,
            'deposit_returned': self.deposit_returned,
            'notes': self.notes,
            'returned': self.returned,
            'is_overdue': is_overdue,
            'days_overdue': days_overdue,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_records'
    id = db.Column(db.Integer, primary_key=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    record_type = db.Column(db.String(20), default='maintenance')
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    cost = db.Column(db.Float, default=0.0)
    shop = db.Column(db.String(100), default='')
    sent_date = db.Column(db.String(20), default='')
    completed_date = db.Column(db.String(20), default='')
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        acc = Accessory.query.get(self.accessory_id)
        return {
            'id': self.id,
            'accessory_id': self.accessory_id,
            'accessory': acc.to_dict() if acc else None,
            'record_type': self.record_type,
            'title': self.title,
            'description': self.description,
            'cost': self.cost,
            'shop': self.shop,
            'sent_date': self.sent_date,
            'completed_date': self.completed_date,
            'completed': self.completed,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


class ValuationRecord(db.Model):
    __tablename__ = 'valuation_records'
    id = db.Column(db.Integer, primary_key=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    valuation_date = db.Column(db.String(20), default='')
    estimated_value = db.Column(db.Float, default=0.0)
    depreciation_reason = db.Column(db.Text, default='')
    insurance_suggestion = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='low')
    wear_frequency = db.Column(db.String(20), default='')
    repair_count = db.Column(db.Integer, default=0)
    condition_note = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        acc = Accessory.query.get(self.accessory_id)
        return {
            'id': self.id,
            'accessory_id': self.accessory_id,
            'accessory': acc.to_dict() if acc else None,
            'valuation_date': self.valuation_date,
            'estimated_value': self.estimated_value,
            'depreciation_reason': self.depreciation_reason,
            'insurance_suggestion': self.insurance_suggestion,
            'risk_level': self.risk_level,
            'wear_frequency': self.wear_frequency,
            'repair_count': self.repair_count,
            'condition_note': self.condition_note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


class CertificateAttachment(db.Model):
    __tablename__ = 'certificate_attachments'
    id = db.Column(db.Integer, primary_key=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    cert_type = db.Column(db.String(50), default='')
    file_name = db.Column(db.String(200), default='')
    file_path = db.Column(db.String(300), default='')
    cert_number = db.Column(db.String(100), default='')
    issue_date = db.Column(db.String(20), default='')
    issuer = db.Column(db.String(100), default='')
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        acc = Accessory.query.get(self.accessory_id)
        return {
            'id': self.id,
            'accessory_id': self.accessory_id,
            'accessory': acc.to_dict() if acc else None,
            'cert_type': self.cert_type,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'cert_number': self.cert_number,
            'issue_date': self.issue_date,
            'issuer': self.issuer,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


class InventoryBatch(db.Model):
    __tablename__ = 'inventory_batches'
    id = db.Column(db.Integer, primary_key=True)
    batch_name = db.Column(db.String(200), nullable=False)
    batch_type = db.Column(db.String(20), default='annual')
    period = db.Column(db.String(50), default='')
    start_date = db.Column(db.String(20), default='')
    end_date = db.Column(db.String(20), default='')
    status = db.Column(db.String(20), default='pending')
    total_count = db.Column(db.Integer, default=0)
    checked_count = db.Column(db.Integer, default=0)
    exception_count = db.Column(db.Integer, default=0)
    operator = db.Column(db.String(100), default='')
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('InventoryItem', backref='batch', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'batch_name': self.batch_name,
            'batch_type': self.batch_type,
            'period': self.period,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status,
            'total_count': self.total_count,
            'checked_count': self.checked_count,
            'exception_count': self.exception_count,
            'operator': self.operator,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'completion_rate': round(self.checked_count / max(self.total_count, 1) * 100, 1),
            'items': [i.to_dict() for i in self.items]
        }


class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=False)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    expected_location = db.Column(db.String(100), default='')
    actual_location = db.Column(db.String(100), default='')
    status = db.Column(db.String(20), default='pending')
    check_method = db.Column(db.String(20), default='manual')
    checked_at = db.Column(db.String(20), default='')
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        acc = Accessory.query.get(self.accessory_id)
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'accessory_id': self.accessory_id,
            'accessory': acc.to_dict() if acc else None,
            'expected_location': self.expected_location,
            'actual_location': self.actual_location,
            'status': self.status,
            'check_method': self.check_method,
            'checked_at': self.checked_at,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


class InventoryException(db.Model):
    __tablename__ = 'inventory_exceptions'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    exception_type = db.Column(db.String(30), default='')
    description = db.Column(db.Text, default='')
    reported_at = db.Column(db.String(20), default='')
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.String(20), default='')
    resolution = db.Column(db.Text, default='')
    handler = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        acc = Accessory.query.get(self.accessory_id)
        batch = InventoryBatch.query.get(self.batch_id) if self.batch_id else None
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'batch_name': batch.batch_name if batch else '',
            'accessory_id': self.accessory_id,
            'accessory': acc.to_dict() if acc else None,
            'exception_type': self.exception_type,
            'description': self.description,
            'reported_at': self.reported_at,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at,
            'resolution': self.resolution,
            'handler': self.handler,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


class InsuranceItem(db.Model):
    __tablename__ = 'insurance_items'
    id = db.Column(db.Integer, primary_key=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    insurance_company = db.Column(db.String(100), default='')
    policy_number = db.Column(db.String(100), default='')
    coverage_amount = db.Column(db.Float, default=0.0)
    premium = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.String(20), default='')
    end_date = db.Column(db.String(20), default='')
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        acc = Accessory.query.get(self.accessory_id)
        return {
            'id': self.id,
            'accessory_id': self.accessory_id,
            'accessory': acc.to_dict() if acc else None,
            'insurance_company': self.insurance_company,
            'policy_number': self.policy_number,
            'coverage_amount': self.coverage_amount,
            'premium': self.premium,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


MATERIAL_VALUE_FACTOR = {
    '黄金': 1.0, '白金': 0.95, '玫瑰金': 0.9, '纯银': 0.15,
    '合金': 0.05, '珍珠': 0.4, '水晶': 0.2, '宝石': 0.8,
    '玉石': 0.6, '布料': 0.02, '皮革': 0.03, '其他': 0.05
}

BRAND_PREMIUM = {
    'Tiffany': 1.5, 'Cartier': 1.6, 'Van Cleef': 1.7, 'Bvlgari': 1.55,
    'Chanel': 1.5, 'Dior': 1.45, 'Hermes': 1.6, 'Gucci': 1.35,
    '周大福': 1.2, '周生生': 1.18, '老凤祥': 1.15, '其他': 1.0
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
    if wear_count >= 50:
        wear_depreciation = 0.25
        wear_freq = '高频'
    elif wear_count >= 20:
        wear_depreciation = 0.15
        wear_freq = '中频'
    elif wear_count >= 5:
        wear_depreciation = 0.08
        wear_freq = '低频'
    else:
        wear_depreciation = 0.0
        wear_freq = '极少'
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


def get_wear_frequency_label(wear_count):
    if wear_count >= 50:
        return '高频'
    elif wear_count >= 20:
        return '中频'
    elif wear_count >= 5:
        return '低频'
    return '极少'


def get_trip_item_score(acc, main_color, style, occasion, used_categories_today, trip_used_ids):
    score = 0
    score += get_color_score(acc.color_family, main_color) * 2
    score += get_style_score(acc.style, style) * 1.5
    score += get_occasion_score(acc, occasion)

    if acc.id in trip_used_ids:
        reuse_times = trip_used_ids.count(acc.id)
        score += reuse_times * 3
    else:
        score += 2

    if acc.category in used_categories_today:
        score -= 50

    if acc.wear_count <= 3:
        score += 4
    elif acc.wear_count <= 8:
        score += 2
    elif acc.wear_count >= 15:
        score -= 2

    return score


def generate_trip_packing(trip):
    from datetime import datetime, timedelta

    try:
        start = datetime.strptime(trip.start_date, '%Y-%m-%d')
        end = datetime.strptime(trip.end_date, '%Y-%m-%d')
        total_days = (end - start).days + 1
    except:
        total_days = max(1, len(trip.days))
        start = None

    all_accessories = Accessory.query.all()
    available = [a for a in all_accessories if a.get_status() == 'in_stock']
    necklaces = [a for a in available if a.category == '项链']
    earrings = [a for a in available if a.category == '耳环']
    bracelets = [a for a in available if a.category == '手链']
    other_acc = [a for a in available if a.category not in ['项链', '耳环', '手链']]

    trip_used_ids = []
    day_plans = []

    for day_idx in range(total_days):
        if start:
            day_date = (start + timedelta(days=day_idx)).strftime('%Y-%m-%d')
        else:
            day_date = ''

        day_occasion = trip.main_occasion
        used_categories_today = set()
        day_items = []

        categories_to_pick = [('项链', necklaces), ('耳环', earrings), ('手链', bracelets)]
        for cat_name, cat_items in categories_to_pick:
            if not cat_items:
                continue

            scored = []
            for acc in cat_items:
                s = get_trip_item_score(acc, trip.main_color, trip.style, day_occasion, used_categories_today, trip_used_ids)
                scored.append((s, acc))
            scored.sort(key=lambda x: -x[0])

            if scored:
                chosen = scored[0][1]
                used_categories_today.add(chosen.category)
                if chosen.id in trip_used_ids:
                    reuse_count = trip_used_ids.count(chosen.id) + 1
                else:
                    reuse_count = 1
                trip_used_ids.append(chosen.id)

                reason_parts = []
                if chosen.color_family == trip.main_color or chosen.color_family in COLOR_COMBINATIONS.get(trip.main_color, []):
                    reason_parts.append(f'与主色调{trip.main_color}协调')
                if chosen.style == trip.style or chosen.style in STYLE_MATCH.get(trip.style, []):
                    reason_parts.append(f'{trip.style}风格匹配')
                if day_occasion and day_occasion in (chosen.occasions.split(',') if chosen.occasions else []):
                    reason_parts.append(f'适合{day_occasion}场合')
                reason = '；'.join(reason_parts) if reason_parts else '精选推荐单品'

                day_items.append({
                    'accessory': chosen,
                    'item_type': 'recommended',
                    'is_spare': False,
                    'reason': reason,
                    'reuse_count': reuse_count
                })

        spare_candidates = []
        for acc in other_acc + necklaces + earrings + bracelets:
            if acc.id not in [i['accessory'].id for i in day_items]:
                s = get_trip_item_score(acc, trip.main_color, trip.style, day_occasion, set(), trip_used_ids)
                spare_candidates.append((s, acc))
        spare_candidates.sort(key=lambda x: -x[0])

        for s, acc in spare_candidates[:2]:
            if acc.id in trip_used_ids:
                reuse_count = trip_used_ids.count(acc.id) + 1
            else:
                reuse_count = 1
            trip_used_ids.append(acc.id)
            day_items.append({
                'accessory': acc,
                'item_type': 'spare',
                'is_spare': True,
                'reason': f'备用单品：{acc.style}风格{acc.color_family}色系百搭款',
                'reuse_count': reuse_count
            })

        day_plans.append({
            'day_index': day_idx,
            'date': day_date,
            'occasion': day_occasion,
            'weather': f'{trip.temp_min}°C~{trip.temp_max}°C',
            'items': day_items
        })

    return day_plans


def compute_missing_risk(trip):
    all_ids = []
    for day in trip.days:
        for item in day.items:
            acc = Accessory.query.get(item.accessory_id)
            if acc and acc.get_status() == 'in_stock':
                all_ids.append(item.accessory_id)

    from collections import Counter
    id_counts = Counter(all_ids)
    total_days = len(trip.days) if trip.days else 1

    risks = []
    for acc_id, count in id_counts.items():
        acc = Accessory.query.get(acc_id)
        if not acc:
            continue
        usage_ratio = count / total_days
        risk_level = '低'
        risk_score = 0
        if usage_ratio >= 0.8:
            risk_level = '高'
            risk_score = 3
        elif usage_ratio >= 0.5:
            risk_level = '中'
            risk_score = 2
        elif usage_ratio >= 0.3:
            risk_level = '低'
            risk_score = 1
        if risk_score > 0:
            risks.append({
                'accessory': acc.to_dict(),
                'usage_days': count,
                'total_days': total_days,
                'usage_ratio': round(usage_ratio * 100, 1),
                'risk_level': risk_level,
                'risk_score': risk_score,
                'suggestion': f'该饰品预计使用{count}天，占行程{round(usage_ratio * 100, 1)}%，建议携带同款备用或做好保养' if risk_level != '低' else '使用率适中'
            })
    risks.sort(key=lambda x: -x['risk_score'])
    return risks


def compute_storage_locations(trip):
    loc_map = {}
    for day in trip.days:
        for item in day.items:
            acc = Accessory.query.get(item.accessory_id)
            if not acc or acc.get_status() != 'in_stock':
                continue
            loc = acc.storage_location or '未标记位置'
            if loc not in loc_map:
                loc_map[loc] = set()
            loc_map[loc].add(acc.id)
    result = []
    for loc, acc_ids in loc_map.items():
        items = [Accessory.query.get(aid).to_dict() for aid in acc_ids if Accessory.query.get(aid)]
        result.append({
            'location': loc,
            'count': len(items),
            'accessories': items
        })
    result.sort(key=lambda x: -x['count'])
    return result


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

    all_acc = Accessory.query.all()
    available = [a for a in all_acc if a.get_status() == 'in_stock']
    necklaces = [a for a in available if a.category == '项链']
    earrings = [a for a in available if a.category == '耳环']
    bracelets = [a for a in available if a.category == '手链']

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


@app.route('/api/trips', methods=['GET'])
def get_trips():
    status = request.args.get('status', '')
    query = TripPlan.query
    if status:
        query = query.filter(TripPlan.status == status)
    trips = query.order_by(TripPlan.created_at.desc()).all()
    return jsonify([t.to_dict() for t in trips])


@app.route('/api/trips/<int:tid>', methods=['GET'])
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


@app.route('/api/trips', methods=['POST'])
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


@app.route('/api/trips/<int:tid>', methods=['PUT'])
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


@app.route('/api/trips/<int:tid>', methods=['DELETE'])
def delete_trip(tid):
    trip = TripPlan.query.get_or_404(tid)
    db.session.delete(trip)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/trips/<int:tid>/regenerate', methods=['POST'])
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


@app.route('/api/trips/items/<int:iid>/pack', methods=['POST'])
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


@app.route('/api/trips/<int:tid>/pack-all', methods=['POST'])
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


@app.route('/api/trips/<int:tid>/save-favorite', methods=['POST'])
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


@app.route('/api/trips/<int:tid>/export', methods=['GET'])
def export_trip(tid):
    trip = TripPlan.query.get_or_404(tid)
    lines = []
    lines.append(f'📋 行程饰品打包清单：{trip.name}')
    lines.append(f'📍 目的地：{trip.destination or "未指定"}')
    lines.append(f'📅 日期：{trip.start_date} ~ {trip.end_date}')
    lines.append(f'🌡 温度：{trip.temp_min}°C ~ {trip.temp_max}°C')
    lines.append(f'🎨 主色调：{trip.main_color or "未指定"}')
    lines.append(f'✨ 风格：{trip.style or "未指定"}')
    if trip.main_occasion:
        lines.append(f'🎭 主要场合：{trip.main_occasion}')
    lines.append('')
    lines.append('=' * 40)

    total_items = 0
    packed_count = 0
    skipped_items = 0
    for day in trip.days:
        lines.append(f'\n📅 第 {day.day_index + 1} 天 ({day.date or ""})')
        if day.occasion:
            lines.append(f'   🎭 场合：{day.occasion}')
        if day.weather:
            lines.append(f'   🌤 天气：{day.weather}')
        lines.append('   --- 推荐搭配 ---')
        for item in day.items:
            acc = Accessory.query.get(item.accessory_id)
            if not acc:
                continue
            if acc.get_status() != 'in_stock':
                skipped_items += 1
                continue
            total_items += 1
            if item.packed:
                packed_count += 1
            prefix = '✅' if item.packed else '⬜'
            tag = '[备用]' if item.is_spare else '      '
            lines.append(f'   {prefix} {tag} {acc.category}：{acc.name} ({acc.color_family}·{acc.style})')
            if item.reason:
                lines.append(f'          💡 {item.reason}')
            if item.reuse_count > 1:
                lines.append(f'          🔁 本次行程复用第{item.reuse_count}次')

    if skipped_items > 0:
        lines.append(f'\n⚠️ 注：已自动排除 {skipped_items} 件不在库（借出/维修/保养中）的饰品')

    lines.append('')
    lines.append('=' * 40)
    lines.append(f'\n📦 打包进度：{packed_count}/{total_items} ({round(packed_count/max(total_items,1)*100, 1)}%)')

    storage = compute_storage_locations(trip)
    if storage:
        lines.append('\n🗂 收纳取件指引：')
        for s in storage:
            lines.append(f'   📍 {s["location"]}（{s["count"]}件）')
            for a in s['accessories']:
                lines.append(f'      · {a["name"]}')

    risks = compute_missing_risk(trip)
    high_risks = [r for r in risks if r['risk_level'] in ['高', '中']]
    if high_risks:
        lines.append('\n⚠️ 缺失风险提醒：')
        for r in high_risks:
            lines.append(f'   [{r["risk_level"]}风险] {r["accessory"]["name"]}：使用率{r["usage_ratio"]}%，{r["suggestion"]}')

    return jsonify({'content': '\n'.join(lines), 'lines': lines})


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

    all_trips = TripPlan.query.all()
    trip_count = len(all_trips)
    trip_packing_stats = []
    trip_color_stats = {}
    unpacked_reminders = []
    total_trip_items = 0
    total_trip_packed = 0
    total_trip_unique_acc = set()
    trip_acc_usage_count = {}

    for trip in all_trips:
        trip_total = 0
        trip_packed = 0
        trip_unique = set()
        for day in trip.days:
            for item in day.items:
                trip_total += 1
                total_trip_items += 1
                if item.packed:
                    trip_packed += 1
                    total_trip_packed += 1
                else:
                    acc = Accessory.query.get(item.accessory_id)
                    if acc and acc.get_status() == 'in_stock':
                        unpacked_reminders.append({
                            'trip_id': trip.id,
                            'trip_name': trip.name,
                            'day_index': day.day_index + 1,
                            'date': day.date,
                            'accessory': acc.to_dict(),
                            'item_id': item.id,
                            'is_spare': item.is_spare
                        })
                trip_unique.add(item.accessory_id)
                total_trip_unique_acc.add(item.accessory_id)
                acc = Accessory.query.get(item.accessory_id)
                if acc:
                    if acc.color_family not in trip_color_stats:
                        trip_color_stats[acc.color_family] = 0
                    trip_color_stats[acc.color_family] += 1
                    if acc.id not in trip_acc_usage_count:
                        trip_acc_usage_count[acc.id] = 0
                    trip_acc_usage_count[acc.id] += 1

        trip_packing_stats.append({
            'trip_id': trip.id,
            'trip_name': trip.name,
            'destination': trip.destination,
            'start_date': trip.start_date,
            'end_date': trip.end_date,
            'status': trip.status,
            'total_items': trip_total,
            'packed_items': trip_packed,
            'unique_count': len(trip_unique),
            'packing_rate': round(trip_packed / max(trip_total, 1) * 100, 1)
        })

    trip_packing_stats.sort(key=lambda x: x['start_date'], reverse=True)

    total_trip_color_count = sum(trip_color_stats.values())
    trip_color_distribution = [
        {'color': c, 'count': cnt, 'percentage': round(cnt / max(total_trip_color_count, 1) * 100, 1)}
        for c, cnt in sorted(trip_color_stats.items(), key=lambda x: -x[1])
    ]

    trip_plan_utilization = round(len(total_trip_unique_acc) / max(total, 1) * 100, 1) if total > 0 else 0

    upcoming_trips = []
    today_str = today.strftime('%Y-%m-%d')
    for trip in all_trips:
        if trip.start_date and trip.start_date >= today_str:
            upcoming_trips.append({
                'id': trip.id,
                'name': trip.name,
                'destination': trip.destination,
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'status': trip.status
            })
    upcoming_trips.sort(key=lambda x: x['start_date'])

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

    from collections import defaultdict
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
    today_str = today.strftime('%Y-%m-%d')
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

    status_stats = defaultdict(int)
    for acc in all_acc:
        status_stats[acc.get_status()] += 1
    status_distribution = [
        {'status': s, 'count': c, 'percentage': round(c / max(total, 1) * 100, 1)}
        for s, c in sorted(status_stats.items(), key=lambda x: -x[1])
    ]

    total_asset_value = 0.0
    valuation_trend = defaultdict(float)
    high_value_uninsured = []
    total_purchase_value = 0.0

    all_valuations = ValuationRecord.query.order_by(ValuationRecord.created_at.asc()).all()
    for v in all_valuations:
        try:
            month_key = v.created_at.strftime('%Y-%m')
            valuation_trend[month_key] += v.estimated_value
        except:
            pass

    all_insurance = InsuranceItem.query.filter_by(status='active').all()
    insured_ids = set(i.accessory_id for i in all_insurance)

    cert_count = CertificateAttachment.query.count()
    cert_missing_count = 0
    high_value_threshold = 3000.0

    for acc in all_acc:
        total_purchase_value += float(acc.purchase_price or 0)
        val = calculate_valuation(acc)
        total_asset_value += val['estimated_value']
        acc_certs = CertificateAttachment.query.filter_by(accessory_id=acc.id).count()
        if acc_certs == 0 and float(acc.purchase_price or 0) >= 1000:
            cert_missing_count += 1
        if val['estimated_value'] >= high_value_threshold and acc.id not in insured_ids and not acc.is_lost:
            hv_item = acc.to_dict()
            hv_item['current_value'] = val['estimated_value']
            hv_item['insurance_suggestion'] = val['insurance_suggestion']
            hv_item['risk_level'] = val['risk_level']
            high_value_uninsured.append(hv_item)

    high_value_uninsured.sort(key=lambda x: -x['current_value'])
    valuation_trend_list = sorted([{'month': k, 'value': round(v, 2)} for k, v in valuation_trend.items()])
    current_month = datetime.now().strftime('%Y-%m')
    if valuation_trend_list and valuation_trend_list[-1]['month'] == current_month:
        valuation_trend_list[-1]['value'] = round(total_asset_value, 2)
    else:
        valuation_trend_list.append({'month': current_month, 'value': round(total_asset_value, 2)})
    valuation_trend_list.sort(key=lambda x: x['month'])

    all_batches = InventoryBatch.query.all()
    completed_batches = [b for b in all_batches if b.status == 'completed']
    total_inventory_checked = sum(b.checked_count for b in completed_batches)
    total_inventory_target = sum(b.total_count for b in completed_batches)
    inventory_completion_rate = round(total_inventory_checked / max(total_inventory_target, 1) * 100, 1)

    all_exceptions = InventoryException.query.all()
    unresolved_exceptions = [e for e in all_exceptions if not e.resolved]
    exception_by_type = defaultdict(int)
    for e in all_exceptions:
        exception_by_type[e.exception_type] += 1
    exception_distribution = [
        {'type': t or '未分类', 'count': c, 'percentage': round(c / max(len(all_exceptions), 1) * 100, 1)}
        for t, c in sorted(exception_by_type.items(), key=lambda x: -x[1])
    ]

    total_insurance_coverage = sum(i.coverage_amount for i in all_insurance)

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
        'active_count': worn_30d,
        'trip_count': trip_count,
        'trip_packing_stats': trip_packing_stats,
        'trip_packing_rate': round(total_trip_packed / max(total_trip_items, 1) * 100, 1),
        'trip_total_items': total_trip_items,
        'trip_packed_items': total_trip_packed,
        'trip_plan_utilization': trip_plan_utilization,
        'trip_unique_count': len(total_trip_unique_acc),
        'trip_color_distribution': trip_color_distribution,
        'upcoming_trips': upcoming_trips,
        'unpacked_reminders': unpacked_reminders[:50],
        'status_distribution': status_distribution,
        'active_loan_count': len(active_loans),
        'overdue_loan_count': len(overdue_loans),
        'active_maintenance_count': len([m for m in active_maint if m.record_type == 'maintenance']),
        'active_repair_count': len([m for m in active_maint if m.record_type == 'repair']),
        'total_maintenance_cost': round(total_maint_cost, 2),
        'cost_trend': cost_trend,
        'high_risk_accessories': high_risk,
        'maintenance_reminders_30d': maintenance_reminders,
        'total_asset_value': round(total_asset_value, 2),
        'total_purchase_value': round(total_purchase_value, 2),
        'valuation_trend': valuation_trend_list,
        'high_value_uninsured': high_value_uninsured[:20],
        'high_value_uninsured_count': len(high_value_uninsured),
        'cert_missing_count': cert_missing_count,
        'cert_missing_rate': round(cert_missing_count / max(total, 1) * 100, 1),
        'total_cert_count': cert_count,
        'inventory_completion_rate': inventory_completion_rate,
        'total_inventory_batches': len(all_batches),
        'completed_inventory_batches': len(completed_batches),
        'unresolved_exception_count': len(unresolved_exceptions),
        'exception_distribution': exception_distribution,
        'total_insurance_coverage': round(total_insurance_coverage, 2),
        'insured_accessory_count': len(insured_ids)
    })


@app.route('/api/loans', methods=['GET'])
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


@app.route('/api/loans', methods=['POST'])
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


@app.route('/api/loans/<int:lid>/return', methods=['POST'])
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


@app.route('/api/loans/<int:lid>', methods=['PUT'])
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


@app.route('/api/loans/<int:lid>', methods=['DELETE'])
def delete_loan(lid):
    loan = LoanRecord.query.get_or_404(lid)
    db.session.delete(loan)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/maintenance', methods=['GET'])
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


@app.route('/api/maintenance', methods=['POST'])
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


@app.route('/api/maintenance/<int:mid>/complete', methods=['POST'])
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


@app.route('/api/maintenance/<int:mid>', methods=['PUT'])
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


@app.route('/api/maintenance/<int:mid>', methods=['DELETE'])
def delete_maintenance(mid):
    record = MaintenanceRecord.query.get_or_404(mid)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/accessories/<int:aid>/set-maintenance', methods=['POST'])
def set_maintenance_date(aid):
    acc = Accessory.query.get_or_404(aid)
    data = request.get_json() or {}
    if 'next_maintenance_date' in data:
        acc.next_maintenance_date = data['next_maintenance_date']
    if 'maintenance_cycle_days' in data:
        acc.maintenance_cycle_days = int(data['maintenance_cycle_days'])
    db.session.commit()
    return jsonify(acc.to_dict())


@app.route('/api/tracking/summary', methods=['GET'])
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

    from collections import defaultdict
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


@app.route('/api/valuations/calculate/<int:aid>', methods=['GET'])
def calculate_accessory_valuation(aid):
    acc = Accessory.query.get_or_404(aid)
    result = calculate_valuation(acc)
    return jsonify({
        'accessory_id': aid,
        **result
    })


@app.route('/api/valuations', methods=['GET'])
def get_valuations():
    accessory_id = request.args.get('accessory_id', '')
    query = ValuationRecord.query
    if accessory_id:
        query = query.filter_by(accessory_id=int(accessory_id))
    records = query.order_by(ValuationRecord.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@app.route('/api/valuations/<int:vid>', methods=['GET'])
def get_valuation(vid):
    record = ValuationRecord.query.get_or_404(vid)
    return jsonify(record.to_dict())


@app.route('/api/valuations', methods=['POST'])
def create_valuation():
    data = request.get_json() or {}
    acc = Accessory.query.get_or_404(data.get('accessory_id'))
    auto_calc = calculate_valuation(acc)
    record = ValuationRecord(
        accessory_id=data.get('accessory_id'),
        valuation_date=data.get('valuation_date', datetime.now().strftime('%Y-%m-%d')),
        estimated_value=float(data.get('estimated_value') or auto_calc['estimated_value']),
        depreciation_reason=data.get('depreciation_reason', auto_calc['depreciation_reason']),
        insurance_suggestion=float(data.get('insurance_suggestion') or auto_calc['insurance_suggestion']),
        risk_level=data.get('risk_level', auto_calc['risk_level']),
        wear_frequency=data.get('wear_frequency', auto_calc['wear_frequency']),
        repair_count=int(data.get('repair_count', auto_calc['repair_count'])),
        condition_note=data.get('condition_note', auto_calc['condition_note'])
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@app.route('/api/valuations/<int:vid>', methods=['DELETE'])
def delete_valuation(vid):
    record = ValuationRecord.query.get_or_404(vid)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/valuations/overview', methods=['GET'])
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
    from collections import defaultdict
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


@app.route('/api/certificates', methods=['GET'])
def get_certificates():
    accessory_id = request.args.get('accessory_id', '')
    cert_type = request.args.get('cert_type', '')
    query = CertificateAttachment.query
    if accessory_id:
        query = query.filter_by(accessory_id=int(accessory_id))
    if cert_type:
        query = query.filter_by(cert_type=cert_type)
    records = query.order_by(CertificateAttachment.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@app.route('/api/certificates/<int:cid>', methods=['GET'])
def get_certificate(cid):
    record = CertificateAttachment.query.get_or_404(cid)
    return jsonify(record.to_dict())


@app.route('/api/certificates', methods=['POST'])
def create_certificate():
    data = request.form.to_dict()
    file_path = ''
    file_name = ''
    if 'file' in request.files:
        f = request.files['file']
        if f and f.filename:
            ext = os.path.splitext(f.filename)[1]
            file_name = f.filename
            file_path = f"cert_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:8]}{ext}"
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], file_path))

    acc = Accessory.query.get_or_404(data.get('accessory_id'))
    record = CertificateAttachment(
        accessory_id=data.get('accessory_id'),
        cert_type=data.get('cert_type', ''),
        file_name=file_name,
        file_path=file_path,
        cert_number=data.get('cert_number', ''),
        issue_date=data.get('issue_date', ''),
        issuer=data.get('issuer', ''),
        notes=data.get('notes', '')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@app.route('/api/certificates/<int:cid>', methods=['PUT'])
def update_certificate(cid):
    record = CertificateAttachment.query.get_or_404(cid)
    data = request.form.to_dict()
    if 'file' in request.files:
        f = request.files['file']
        if f and f.filename:
            if record.file_path:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], record.file_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
            ext = os.path.splitext(f.filename)[1]
            record.file_name = f.filename
            record.file_path = f"cert_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:8]}{ext}"
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], record.file_path))
    fields = ['cert_type', 'cert_number', 'issue_date', 'issuer', 'notes']
    for f in fields:
        if f in data:
            setattr(record, f, data[f])
    db.session.commit()
    return jsonify(record.to_dict())


@app.route('/api/certificates/<int:cid>', methods=['DELETE'])
def delete_certificate(cid):
    record = CertificateAttachment.query.get_or_404(cid)
    if record.file_path:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], record.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/inventory/batches', methods=['GET'])
def get_inventory_batches():
    status = request.args.get('status', '')
    query = InventoryBatch.query
    if status:
        query = query.filter_by(status=status)
    batches = query.order_by(InventoryBatch.created_at.desc()).all()
    return jsonify([b.to_dict() for b in batches])


@app.route('/api/inventory/batches/<int:bid>', methods=['GET'])
def get_inventory_batch(bid):
    batch = InventoryBatch.query.get_or_404(bid)
    return jsonify(batch.to_dict())


@app.route('/api/inventory/batches', methods=['POST'])
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


@app.route('/api/inventory/batches/<int:bid>/complete', methods=['POST'])
def complete_inventory_batch(bid):
    batch = InventoryBatch.query.get_or_404(bid)
    batch.status = 'completed'
    batch.end_date = datetime.now().strftime('%Y-%m-%d')
    db.session.commit()
    return jsonify(batch.to_dict())


@app.route('/api/inventory/batches/<int:bid>', methods=['DELETE'])
def delete_inventory_batch(bid):
    batch = InventoryBatch.query.get_or_404(bid)
    db.session.delete(batch)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/inventory/items/<int:iid>/check', methods=['POST'])
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


@app.route('/api/inventory/exceptions', methods=['GET'])
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


@app.route('/api/inventory/exceptions/<int:eid>', methods=['GET'])
def get_inventory_exception(eid):
    record = InventoryException.query.get_or_404(eid)
    return jsonify(record.to_dict())


@app.route('/api/inventory/exceptions', methods=['POST'])
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


@app.route('/api/inventory/exceptions/<int:eid>/resolve', methods=['POST'])
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


@app.route('/api/inventory/exceptions/<int:eid>', methods=['DELETE'])
def delete_inventory_exception(eid):
    record = InventoryException.query.get_or_404(eid)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/insurance', methods=['GET'])
def get_insurance_items():
    status = request.args.get('status', '')
    query = InsuranceItem.query
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(InsuranceItem.created_at.desc()).all()
    return jsonify([i.to_dict() for i in items])


@app.route('/api/insurance/<int:iid>', methods=['GET'])
def get_insurance_item(iid):
    item = InsuranceItem.query.get_or_404(iid)
    return jsonify(item.to_dict())


@app.route('/api/insurance', methods=['POST'])
def create_insurance_item():
    data = request.get_json() or {}
    acc = Accessory.query.get_or_404(data.get('accessory_id'))
    item = InsuranceItem(
        accessory_id=data.get('accessory_id'),
        insurance_company=data.get('insurance_company', ''),
        policy_number=data.get('policy_number', ''),
        coverage_amount=float(data.get('coverage_amount', 0) or 0),
        premium=float(data.get('premium', 0) or 0),
        start_date=data.get('start_date', ''),
        end_date=data.get('end_date', ''),
        status=data.get('status', 'active'),
        notes=data.get('notes', '')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route('/api/insurance/<int:iid>', methods=['PUT'])
def update_insurance_item(iid):
    item = InsuranceItem.query.get_or_404(iid)
    data = request.get_json() or {}
    fields = ['insurance_company', 'policy_number', 'start_date', 'end_date', 'status', 'notes']
    for f in fields:
        if f in data:
            setattr(item, f, data[f])
    if 'coverage_amount' in data:
        item.coverage_amount = float(data['coverage_amount'] or 0)
    if 'premium' in data:
        item.premium = float(data['premium'] or 0)
    db.session.commit()
    return jsonify(item.to_dict())


@app.route('/api/insurance/<int:iid>', methods=['DELETE'])
def delete_insurance_item(iid):
    item = InsuranceItem.query.get_or_404(iid)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': '已删除'})


@app.route('/api/insurance/export', methods=['GET'])
def export_insurance_list():
    all_acc = Accessory.query.filter_by(is_lost=False).all()
    insured_ids = set()
    active_insurance = InsuranceItem.query.filter_by(status='active').all()
    insurance_map = {}
    for ins in active_insurance:
        insured_ids.add(ins.accessory_id)
        insurance_map[ins.accessory_id] = ins

    export_items = []
    total_coverage = 0.0
    total_suggested = 0.0

    for acc in all_acc:
        val = calculate_valuation(acc)
        insured = insurance_map.get(acc.id)
        export_items.append({
            'accessory': acc.to_dict(),
            'estimated_value': val['estimated_value'],
            'insurance_suggestion': val['insurance_suggestion'],
            'risk_level': val['risk_level'],
            'has_insurance': acc.id in insured_ids,
            'current_coverage': insured.coverage_amount if insured else 0,
            'policy_number': insured.policy_number if insured else '',
            'insurance_company': insured.insurance_company if insured else '',
            'insurance_end_date': insured.end_date if insured else ''
        })
        total_suggested += val['insurance_suggestion']
        if insured:
            total_coverage += insured.coverage_amount

    export_items.sort(key=lambda x: -x['estimated_value'])

    lines = []
    lines.append(f'📋 珠宝饰品保险申报清单')
    lines.append(f'📅 生成日期：{datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append(f'📊 饰品总数：{len(all_acc)} 件')
    lines.append(f'💰 总估值：¥{round(sum(v["estimated_value"] for v in export_items), 2)}')
    lines.append(f'💡 建议总保额：¥{round(total_suggested, 2)}')
    lines.append(f'🛡  当前保额：¥{round(total_coverage, 2)}')
    lines.append('')
    lines.append('=' * 60)
    for idx, item in enumerate(export_items, 1):
        acc = item['accessory']
        lines.append(f'\n{idx}. {acc["name"]}（{acc["category"]}）')
        lines.append(f'   材质：{acc["material"]} · 品牌：{acc.get("brand", "未填写") or "未填写"}')
        lines.append(f'   当前估值：¥{item["estimated_value"]}')
        lines.append(f'   建议保额：¥{item["insurance_suggestion"]}')
        risk_label = {'low': '低', 'medium': '中', 'high': '高', 'critical': '严重'}.get(item['risk_level'], item['risk_level'])
        lines.append(f'   风险等级：{risk_label}')
        if item['has_insurance']:
            lines.append(f'   已投保：{item["insurance_company"]} 保单号 {item["policy_number"]} 保额 ¥{item["current_coverage"]}')
            if item['insurance_end_date']:
                lines.append(f'   保险到期：{item["insurance_end_date"]}')
        else:
            lines.append(f'   ⚠️ 未投保，建议尽快办理')

    return jsonify({
        'items': export_items,
        'total_coverage': round(total_coverage, 2),
        'total_suggested': round(total_suggested, 2),
        'uninsured_count': len(all_acc) - len(insured_ids),
        'content': '\n'.join(lines)
    })


@app.route('/api/meta', methods=['GET'])
def get_meta():
    return jsonify({
        'categories': ['项链', '耳环', '手链', '戒指', '胸针', '发饰', '其他'],
        'materials': ['黄金', '白金', '玫瑰金', '纯银', '合金', '珍珠', '水晶', '宝石', '玉石', '布料', '皮革', '其他'],
        'color_families': ['金色', '银色', '玫瑰金', '白色', '黑色', '红色', '粉色', '蓝色', '绿色', '紫色', '米色', '棕色', '灰色', '黄色'],
        'styles': ['优雅', '休闲', '复古', '简约', '华丽', '波西米亚', '甜美', '民族风', '商务', '运动'],
        'occasions': ['日常', '工作', '约会', '派对', '婚礼', '晚宴', '旅行', '运动', '节日', '正式场合'],
        'accessory_statuses': [
            {'value': 'in_stock', 'label': '在库'},
            {'value': 'lent', 'label': '已借出'},
            {'value': 'overdue', 'label': '逾期未还'},
            {'value': 'maintenance', 'label': '保养中'},
            {'value': 'repair', 'label': '维修中'},
            {'value': 'lost', 'label': '已丢失'},
            {'value': 'inventory_exception', 'label': '盘点异常'}
        ],
        'maintenance_statuses': [
            {'value': 'excellent', 'label': '极佳'},
            {'value': 'good', 'label': '良好'},
            {'value': 'fair', 'label': '一般'},
            {'value': 'poor', 'label': '较差'}
        ],
        'cert_types': ['购买发票', '珠宝鉴定证书', '品牌证书', '保修卡', 'GIA证书', 'NGTC证书', '其他'],
        'inventory_batch_types': [
            {'value': 'annual', 'label': '年度盘点'},
            {'value': 'quarterly', 'label': '季度盘点'},
            {'value': 'monthly', 'label': '月度盘点'},
            {'value': 'temporary', 'label': '临时盘点'}
        ],
        'inventory_exception_types': ['缺失', '损坏', '证书不全', '位置不符', '借出未登记', '其他'],
        'insurance_statuses': [
            {'value': 'active', 'label': '有效'},
            {'value': 'expired', 'label': '已过期'},
            {'value': 'pending', 'label': '待续保'}
        ],
        'risk_levels': [
            {'value': 'low', 'label': '低风险'},
            {'value': 'medium', 'label': '中风险'},
            {'value': 'high', 'label': '高风险'},
            {'value': 'critical', 'label': '严重风险'}
        ],
        'purchase_channels': ['品牌专柜', '官方网店', '珠宝店', '代购', '二手市场', '亲友赠送', '其他'],
        'insurance_companies': ['中国平安', '中国人保', '太平洋保险', '泰康保险', '友邦保险', '其他']
    })


with app.app_context():
    db.create_all()

    from sqlalchemy import inspect, text
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
            d['occasions'] = d['occasions']
            db.session.add(Accessory(**d))
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9202, debug=True)
