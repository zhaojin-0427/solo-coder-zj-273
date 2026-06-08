from datetime import datetime
from backend.extensions import db


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
        from backend.models.accessory import Accessory
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
