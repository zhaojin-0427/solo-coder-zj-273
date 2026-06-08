from datetime import datetime
from backend.extensions import db


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
        from backend.models.loan import LoanRecord
        from backend.models.maintenance import MaintenanceRecord
        from backend.models.inventory import InventoryException
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
