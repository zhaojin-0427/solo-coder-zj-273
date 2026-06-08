from datetime import datetime
from backend.extensions import db


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
        from backend.models.accessory import Accessory
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
        from backend.models.accessory import Accessory
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
