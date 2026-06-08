export const colorMap = {
  '金色': '#D4AF37',
  '银色': '#C0C0C0',
  '玫瑰金': '#B76E79',
  '白色': '#FFFAF0',
  '黑色': '#1C1C1C',
  '红色': '#C83C3C',
  '粉色': '#FFB6C1',
  '蓝色': '#4682B4',
  '绿色': '#50C878',
  '紫色': '#9370DB',
  '米色': '#F5F5DC',
  '棕色': '#8B4513',
  '灰色': '#808080',
  '黄色': '#FFD700'
}

export const statusMap = {
  in_stock: { label: '在库', type: 'success' },
  lent: { label: '已借出', type: 'primary' },
  overdue: { label: '逾期未还', type: 'danger' },
  maintenance: { label: '保养中', type: 'warning' },
  repair: { label: '维修中', type: 'warning' },
  lost: { label: '已丢失', type: 'danger' },
  inventory_exception: { label: '盘点异常', type: 'danger' }
}
