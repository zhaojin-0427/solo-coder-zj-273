from datetime import datetime
from backend.extensions import db


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
        from backend.models.accessory import Accessory
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
