from datetime import datetime
from backend.extensions import db


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
        from backend.models.accessory import Accessory
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
