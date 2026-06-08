from datetime import datetime
from backend.extensions import db


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
        from backend.models.accessory import Accessory
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
