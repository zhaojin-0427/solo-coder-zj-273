<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><Tools /></el-icon>
      借出与保养追踪
    </div>

    <div class="stat-cards">
      <div class="stat-card" @click="activeTab = 'loans'">
        <div class="stat-ic" style="background: linear-gradient(135deg, #5a8cc8, #7aa8e0);">
          <el-icon :size="22" color="#fff"><User /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ summary.active_loan_count || 0 }}</div>
          <div class="stat-l">当前借出</div>
        </div>
      </div>
      <div class="stat-card" @click="activeTab = 'overdue'" style="cursor: pointer;">
        <div class="stat-ic" style="background: linear-gradient(135deg, #c83c3c, #e87878);">
          <el-icon :size="22" color="#fff"><Warning /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ summary.overdue_loan_count || 0 }}</div>
          <div class="stat-l">逾期未还</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #6ba878, #8ac492);">
          <el-icon :size="22" color="#fff"><MagicStick /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ summary.active_maintenance_count || 0 }}</div>
          <div class="stat-l">保养中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #e8a45b, #f0c088);">
          <el-icon :size="22" color="#fff"><Setting /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ summary.active_repair_count || 0 }}</div>
          <div class="stat-l">维修中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #9b7ab8, #b598d0);">
          <el-icon :size="22" color="#fff"><Money /></el-icon>
        </div>
        <div>
          <div class="stat-v">¥{{ summary.total_maintenance_cost || 0 }}</div>
          <div class="stat-l">累计维修保养费</div>
        </div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="main-tabs">
      <el-tab-pane label="借出管理" name="loans">
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div class="section-title" style="margin: 0;">借出记录</div>
            <el-button class="btn-primary" @click="openLoanDialog()">
              <el-icon><Plus /></el-icon> 新增借出
            </el-button>
          </div>
          <div class="filter-bar" style="margin-bottom: 16px;">
            <el-radio-group v-model="loanFilter" @change="loadLoans">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="active">借出中</el-radio-button>
              <el-radio-button value="overdue">已逾期</el-radio-button>
              <el-radio-button value="returned">已归还</el-radio-button>
            </el-radio-group>
          </div>
          <el-table :data="loans" stripe>
            <el-table-column label="饰品" min-width="200">
              <template #default="{ row }">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <div style="width: 40px; height: 40px; border-radius: 6px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                    <img v-if="row.accessory?.photo" :src="'/uploads/' + row.accessory.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                    <el-icon v-else color="#ccc"><Picture /></el-icon>
                  </div>
                  <div>
                    <div style="font-weight: 500;">{{ row.accessory?.name }}</div>
                    <div style="font-size: 12px; color: #999;">{{ row.accessory?.category }} · {{ row.accessory?.color_family }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="借用人" width="140" prop="borrower_name" />
            <el-table-column label="联系方式" width="160">
              <template #default="{ row }">
                <div v-if="row.borrower_phone" style="font-size: 13px;">
                  {{ row.borrower_phone }}
                </div>
                <div v-if="row.borrower_contact" style="font-size: 12px; color: #999;">
                  {{ row.borrower_contact }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="借出日期" width="120" prop="loan_date" />
            <el-table-column label="应还日期" width="120">
              <template #default="{ row }">
                <span :style="{ color: row.is_overdue ? '#c83c3c' : '' }">{{ row.due_date }}</span>
                <el-tag v-if="row.is_overdue" type="danger" size="small" effect="light" style="margin-left: 6px;">
                  逾期{{ row.days_overdue }}天
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="押金" width="100">
              <template #default="{ row }">
                <span v-if="row.deposit > 0">¥{{ row.deposit }}</span>
                <span v-else style="color: #999;">无</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.returned" type="success" effect="light">已归还</el-tag>
                <el-tag v-else-if="row.is_overdue" type="danger" effect="light">逾期</el-tag>
                <el-tag v-else type="primary" effect="light">借出中</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button v-if="!row.returned" size="small" type="success" @click="handleReturn(row)">
                  归还
                </el-button>
                <el-button size="small" @click="openLoanDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" type="danger" @click="handleDeleteLoan(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="逾期提醒" name="overdue">
        <div class="card">
          <div class="section-title">
            逾期未还饰品
            <el-tag type="danger" effect="light" style="margin-left: 10px;">
              {{ overdueLoans.length }} 件需跟进
            </el-tag>
          </div>
          <div v-if="overdueLoans.length === 0" class="empty-tip" style="padding: 30px;">
            <el-icon><SuccessFilled /></el-icon>
            <p>太好了，没有逾期未还的饰品</p>
          </div>
          <div v-else class="overdue-list">
            <div v-for="loan in overdueLoans" :key="loan.id" class="overdue-card">
              <div class="od-header">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <div style="width: 50px; height: 50px; border-radius: 8px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                    <img v-if="loan.accessory?.photo" :src="'/uploads/' + loan.accessory.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                    <el-icon v-else color="#ccc" :size="24"><Picture /></el-icon>
                  </div>
                  <div>
                    <div style="font-weight: 600; font-size: 15px; color: #4a2c2a;">{{ loan.accessory?.name }}</div>
                    <div style="font-size: 12px; color: #999;">{{ loan.accessory?.category }} · {{ loan.accessory?.material }}</div>
                  </div>
                </div>
                <el-tag type="danger" effect="dark">
                  逾期 {{ loan.days_overdue }} 天
                </el-tag>
              </div>
              <div class="od-info">
                <div class="od-info-row">
                  <span class="od-label">借用人：</span>
                  <span class="od-value">{{ loan.borrower_name }}</span>
                </div>
                <div class="od-info-row" v-if="loan.borrower_phone">
                  <span class="od-label">电话：</span>
                  <span class="od-value">{{ loan.borrower_phone }}</span>
                </div>
                <div class="od-info-row" v-if="loan.borrower_contact">
                  <span class="od-label">其他联系方式：</span>
                  <span class="od-value">{{ loan.borrower_contact }}</span>
                </div>
                <div class="od-info-row">
                  <span class="od-label">借出日期：</span>
                  <span class="od-value">{{ loan.loan_date }}</span>
                </div>
                <div class="od-info-row">
                  <span class="od-label">应还日期：</span>
                  <span class="od-value" style="color: #c83c3c;">{{ loan.due_date }}</span>
                </div>
                <div class="od-info-row" v-if="loan.deposit > 0">
                  <span class="od-label">押金：</span>
                  <span class="od-value">¥{{ loan.deposit }} {{ loan.deposit_returned ? '(已退)' : '(未退)' }}</span>
                </div>
              </div>
              <div v-if="loan.notes" class="od-notes">
                <el-icon color="#c9a96e"><ChatDotRound /></el-icon>
                {{ loan.notes }}
              </div>
              <div class="od-actions">
                <el-button class="btn-primary" size="small" @click="handleReturn(loan)">
                  <el-icon><Check /></el-icon> 标记已归还
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="维修/保养" name="maintenance">
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div class="section-title" style="margin: 0;">维修保养记录</div>
            <el-button class="btn-primary" @click="openMaintDialog()">
              <el-icon><Plus /></el-icon> 新增工单
            </el-button>
          </div>
          <div class="filter-bar" style="margin-bottom: 16px;">
            <el-radio-group v-model="maintFilter" @change="loadMaintenance">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="active">进行中</el-radio-button>
              <el-radio-button value="completed">已完成</el-radio-button>
              <el-radio-button value="maintenance">仅保养</el-radio-button>
              <el-radio-button value="repair">仅维修</el-radio-button>
            </el-radio-group>
          </div>
          <el-table :data="maintenanceList" stripe>
            <el-table-column label="类型" width="90">
              <template #default="{ row }">
                <el-tag :type="row.record_type === 'repair' ? 'warning' : 'success'" effect="light">
                  {{ row.record_type === 'repair' ? '维修' : '保养' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="饰品" min-width="180">
              <template #default="{ row }">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <div style="width: 36px; height: 36px; border-radius: 6px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                    <img v-if="row.accessory?.photo" :src="'/uploads/' + row.accessory.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                    <el-icon v-else color="#ccc"><Picture /></el-icon>
                  </div>
                  <div>
                    <div style="font-weight: 500; font-size: 13px;">{{ row.accessory?.name }}</div>
                    <div style="font-size: 11px; color: #999;">{{ row.accessory?.category }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="标题" min-width="160" prop="title" />
            <el-table-column label="店铺" width="120" prop="shop" />
            <el-table-column label="送修日期" width="110" prop="sent_date" />
            <el-table-column label="完成日期" width="110" prop="completed_date" />
            <el-table-column label="费用" width="100">
              <template #default="{ row }">
                <span v-if="row.cost > 0">¥{{ row.cost }}</span>
                <span v-else style="color: #999;">-</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag v-if="row.completed" type="success" effect="light">已完成</el-tag>
                <el-tag v-else type="warning" effect="light">进行中</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button v-if="!row.completed" size="small" type="success" @click="handleCompleteMaint(row)">
                  完成
                </el-button>
                <el-button size="small" @click="openMaintDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" type="danger" @click="handleDeleteMaint(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="card" style="margin-top: 16px;">
          <div class="section-title">费用统计</div>
          <div v-if="!summary.cost_trend?.length" class="empty-tip" style="padding: 30px;">
            <el-icon><Money /></el-icon>
            <p>暂无费用数据</p>
          </div>
          <div v-else ref="costChartRef" style="height: 300px;"></div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="保养日历" name="calendar">
        <div class="card">
          <div class="section-title">
            未来 30 天保养提醒
            <el-tag type="warning" effect="light" style="margin-left: 10px;">
              {{ summary.maintenance_reminders_30d?.length || 0 }} 件需保养
            </el-tag>
          </div>
          <div v-if="!summary.maintenance_reminders_30d?.length" class="empty-tip" style="padding: 30px;">
            <el-icon><Calendar /></el-icon>
            <p>未来 30 天内没有待保养的饰品</p>
          </div>
          <div v-else>
            <el-table :data="summary.maintenance_reminders_30d" stripe>
              <el-table-column label="饰品" min-width="200">
                <template #default="{ row }">
                  <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 40px; height: 40px; border-radius: 6px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                      <img v-if="row.photo" :src="'/uploads/' + row.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                      <el-icon v-else color="#ccc"><Picture /></el-icon>
                    </div>
                    <div>
                      <div style="font-weight: 500;">{{ row.name }}</div>
                      <div style="font-size: 12px; color: #999;">{{ row.category }} · {{ row.material }}</div>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="下次保养日期" width="150">
                <template #default="{ row }">
                  <el-tag :type="row.days_until <= 7 ? 'danger' : row.days_until <= 14 ? 'warning' : 'success'" effect="light">
                    {{ row.next_maintenance_date }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="倒计时" width="100">
                <template #default="{ row }">
                  <span :style="{ color: row.days_until <= 7 ? '#c83c3c' : row.days_until <= 14 ? '#e8a45b' : '#6ba878', fontWeight: 600 }">
                    还剩 {{ row.days_until }} 天
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="保养周期" width="120">
                <template #default="{ row }">
                  <span v-if="row.maintenance_cycle_days > 0">每 {{ row.maintenance_cycle_days }} 天</span>
                  <span v-else style="color: #999;">未设置</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="160">
                <template #default="{ row }">
                  <el-button size="small" @click="openSetMaintenance(row)">
                    <el-icon><Edit /></el-icon> 设置日期
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <div class="card" style="margin-top: 16px;">
          <div class="section-title">
            高风险频繁维修饰品
          </div>
          <div v-if="!summary.high_risk_accessories?.length" class="empty-tip" style="padding: 30px;">
            <el-icon><SuccessFilled /></el-icon>
            <p>没有频繁维修的高风险饰品</p>
          </div>
          <div v-else class="high-risk-list">
            <div v-for="acc in summary.high_risk_accessories" :key="acc.id" class="high-risk-card">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 50px; height: 50px; border-radius: 8px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                  <img v-if="acc.photo" :src="'/uploads/' + acc.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                  <el-icon v-else color="#ccc" :size="24"><Picture /></el-icon>
                </div>
                <div style="flex: 1;">
                  <div style="font-weight: 600; color: #4a2c2a;">{{ acc.name }}</div>
                  <div style="font-size: 12px; color: #999;">{{ acc.category }} · {{ acc.material }}</div>
                </div>
              </div>
              <div style="margin-top: 12px; display: flex; gap: 24px; font-size: 13px;">
                <div>
                  <span style="color: #999;">维修次数：</span>
                  <el-tag type="danger" effect="light">{{ acc.repair_count }} 次</el-tag>
                </div>
                <div>
                  <span style="color: #999;">累计费用：</span>
                  <span style="color: #c83c3c; font-weight: 600;">¥{{ acc.total_repair_cost }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="loanDialogVisible" :title="editingLoan ? '编辑借出记录' : '新增借出记录'" width="560px">
      <el-form :model="loanForm" ref="loanFormRef" :rules="loanRules" label-width="100px">
        <el-form-item label="饰品" prop="accessory_id">
          <el-select v-model="loanForm.accessory_id" placeholder="选择饰品" style="width: 100%;" filterable>
            <el-option
              v-for="acc in availableAccessories"
              :key="acc.id"
              :label="acc.name"
              :value="acc.id"
            >
              <span style="display: flex; align-items: center; gap: 8px;">
                <span class="color-dot" :style="{ background: colorMap[acc.color_family] }"></span>
                {{ acc.name }}
                <span style="color: #999; font-size: 12px;">({{ acc.category }})</span>
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="借用人" prop="borrower_name">
          <el-input v-model="loanForm.borrower_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="loanForm.borrower_phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="其他联系">
          <el-input v-model="loanForm.borrower_contact" placeholder="微信/地址等" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="借出日期" prop="loan_date">
              <el-date-picker v-model="loanForm.loan_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="应还日期" prop="due_date">
              <el-date-picker v-model="loanForm.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="押金(元)">
          <el-input-number v-model="loanForm.deposit" :min="0" :precision="2" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="loanForm.notes" type="textarea" :rows="2" placeholder="备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="loanDialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleSubmitLoan">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="maintDialogVisible" :title="editingMaint ? '编辑工单' : '新增工单'" width="560px">
      <el-form :model="maintForm" ref="maintFormRef" :rules="maintRules" label-width="100px">
        <el-form-item label="类型" prop="record_type">
          <el-radio-group v-model="maintForm.record_type">
            <el-radio value="maintenance">保养</el-radio>
            <el-radio value="repair">维修</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="饰品" prop="accessory_id">
          <el-select v-model="maintForm.accessory_id" placeholder="选择饰品" style="width: 100%;" filterable>
            <el-option
              v-for="acc in inStockAccessories"
              :key="acc.id"
              :label="acc.name"
              :value="acc.id"
            >
              <span style="display: flex; align-items: center; gap: 8px;">
                <span class="color-dot" :style="{ background: colorMap[acc.color_family] }"></span>
                {{ acc.name }}
                <span style="color: #999; font-size: 12px;">({{ acc.category }})</span>
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="maintForm.title" placeholder="如：清洁抛光、链条修复" />
        </el-form-item>
        <el-form-item label="店铺">
          <el-input v-model="maintForm.shop" placeholder="送修店铺或服务商" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="送修日期" prop="sent_date">
              <el-date-picker v-model="maintForm.sent_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="费用(元)">
              <el-input-number v-model="maintForm.cost" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="maintForm.description" type="textarea" :rows="2" placeholder="问题描述或保养项目" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="maintForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="maintDialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleSubmitMaint">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="setMaintVisible" title="设置保养日期" width="440px">
      <el-form :model="setMaintForm" label-width="120px">
        <el-form-item label="饰品">
          <span style="font-weight: 500;">{{ setMaintForm.name }}</span>
        </el-form-item>
        <el-form-item label="下次保养日期">
          <el-date-picker v-model="setMaintForm.next_maintenance_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="保养周期(天)">
          <el-input-number v-model="setMaintForm.maintenance_cycle_days" :min="0" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="setMaintVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleSetMaintenance">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Tools, User, Warning, MagicStick, Setting, Money, Plus, Picture,
  Edit, Delete, Check, ChatDotRound, Calendar, SuccessFilled
} from '@element-plus/icons-vue'
import {
  getAccessories, getLoans, createLoan, returnLoan, updateLoan, deleteLoan,
  getMaintenance, createMaintenance, completeMaintenance, updateMaintenance,
  deleteMaintenance, setMaintenanceDate, getTrackingSummary
} from '@/api'

const summary = ref({})
const activeTab = ref('loans')
const loanFilter = ref('')
const maintFilter = ref('')
const loans = ref([])
const maintenanceList = ref([])
const accessories = ref([])
const costChartRef = ref(null)

const overdueLoans = computed(() => loans.value.filter(l => l.is_overdue && !l.returned))

const availableAccessories = computed(() => accessories.value.filter(a => a.status === 'in_stock'))
const inStockAccessories = computed(() => accessories.value.filter(a => a.status === 'in_stock'))

const colorMap = {
  '金色': '#d4a855', '银色': '#c0c0c0', '玫瑰金': '#e8b4a0', '白色': '#f8f5f0',
  '黑色': '#333333', '红色': '#c83c3c', '粉色': '#f0a0b0', '蓝色': '#5a8cc8',
  '绿色': '#6ba878', '紫色': '#9b7ab8', '米色': '#e8dcc8', '棕色': '#8b6f47',
  '灰色': '#999999', '黄色': '#e8c85a'
}

const loanDialogVisible = ref(false)
const editingLoan = ref(false)
const loanFormRef = ref(null)
const loanForm = reactive({
  id: null, accessory_id: null, borrower_name: '', borrower_phone: '',
  borrower_contact: '', loan_date: '', due_date: '', deposit: 0, notes: ''
})
const loanRules = {
  accessory_id: [{ required: true, message: '请选择饰品', trigger: 'change' }],
  borrower_name: [{ required: true, message: '请输入借用人姓名', trigger: 'blur' }],
  loan_date: [{ required: true, message: '请选择借出日期', trigger: 'change' }],
  due_date: [{ required: true, message: '请选择应还日期', trigger: 'change' }]
}

const maintDialogVisible = ref(false)
const editingMaint = ref(false)
const maintFormRef = ref(null)
const maintForm = reactive({
  id: null, accessory_id: null, record_type: 'maintenance', title: '',
  description: '', cost: 0, shop: '', sent_date: '', notes: ''
})
const maintRules = {
  accessory_id: [{ required: true, message: '请选择饰品', trigger: 'change' }],
  record_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  sent_date: [{ required: true, message: '请选择送修日期', trigger: 'change' }]
}

const setMaintVisible = ref(false)
const setMaintForm = reactive({
  id: null, name: '', next_maintenance_date: '', maintenance_cycle_days: 0
})

const loadData = async () => {
  await Promise.all([
    loadSummary(),
    loadAccessories(),
    loadLoans(),
    loadMaintenance()
  ])
}

const loadSummary = async () => {
  summary.value = await getTrackingSummary()
}

const loadAccessories = async () => {
  accessories.value = await getAccessories()
}

const loadLoans = async () => {
  const params = {}
  if (loanFilter.value) params.status = loanFilter.value
  loans.value = await getLoans(params)
}

const loadMaintenance = async () => {
  const params = {}
  if (maintFilter.value && ['active', 'completed'].includes(maintFilter.value)) {
    params.status = maintFilter.value
  } else if (maintFilter.value && ['maintenance', 'repair'].includes(maintFilter.value)) {
    params.type = maintFilter.value
  }
  maintenanceList.value = await getMaintenance(params)
}

const openLoanDialog = (loan) => {
  if (loan) {
    editingLoan.value = true
    Object.assign(loanForm, {
      id: loan.id, accessory_id: loan.accessory_id, borrower_name: loan.borrower_name,
      borrower_phone: loan.borrower_phone, borrower_contact: loan.borrower_contact,
      loan_date: loan.loan_date, due_date: loan.due_date, deposit: loan.deposit, notes: loan.notes
    })
  } else {
    editingLoan.value = false
    Object.assign(loanForm, {
      id: null, accessory_id: null, borrower_name: '', borrower_phone: '',
      borrower_contact: '', loan_date: new Date().toISOString().slice(0, 10),
      due_date: '', deposit: 0, notes: ''
    })
  }
  loanDialogVisible.value = true
}

const handleSubmitLoan = async () => {
  await loanFormRef.value.validate()
  if (editingLoan.value) {
    await updateLoan(loanForm.id, loanForm)
    ElMessage.success('已更新')
  } else {
    await createLoan(loanForm)
    ElMessage.success('已创建借出记录')
  }
  loanDialogVisible.value = false
  loadData()
}

const handleReturn = async (loan) => {
  await ElMessageBox.confirm(`确定「${loan.accessory?.name}」已归还吗？`, '提示', { type: 'success' })
  await returnLoan(loan.id)
  ElMessage.success('已标记归还')
  loadData()
}

const handleDeleteLoan = async (loan) => {
  await ElMessageBox.confirm(`确定删除这条借出记录吗？`, '提示', { type: 'warning' })
  await deleteLoan(loan.id)
  ElMessage.success('已删除')
  loadData()
}

const openMaintDialog = (record) => {
  if (record) {
    editingMaint.value = true
    Object.assign(maintForm, {
      id: record.id, accessory_id: record.accessory_id, record_type: record.record_type,
      title: record.title, description: record.description, cost: record.cost,
      shop: record.shop, sent_date: record.sent_date, notes: record.notes
    })
  } else {
    editingMaint.value = false
    Object.assign(maintForm, {
      id: null, accessory_id: null, record_type: 'maintenance', title: '',
      description: '', cost: 0, shop: '', sent_date: new Date().toISOString().slice(0, 10), notes: ''
    })
  }
  maintDialogVisible.value = true
}

const handleSubmitMaint = async () => {
  await maintFormRef.value.validate()
  if (editingMaint.value) {
    await updateMaintenance(maintForm.id, maintForm)
    ElMessage.success('已更新')
  } else {
    await createMaintenance(maintForm)
    ElMessage.success('已创建工单')
  }
  maintDialogVisible.value = false
  loadData()
}

const handleCompleteMaint = async (record) => {
  await ElMessageBox.confirm(`确定「${record.title}」已完成吗？`, '提示', { type: 'success' })
  await completeMaintenance(record.id)
  ElMessage.success('已标记完成')
  loadData()
}

const handleDeleteMaint = async (record) => {
  await ElMessageBox.confirm(`确定删除这条记录吗？`, '提示', { type: 'warning' })
  await deleteMaintenance(record.id)
  ElMessage.success('已删除')
  loadData()
}

const openSetMaintenance = (acc) => {
  Object.assign(setMaintForm, {
    id: acc.id, name: acc.name,
    next_maintenance_date: acc.next_maintenance_date || '',
    maintenance_cycle_days: acc.maintenance_cycle_days || 0
  })
  setMaintVisible.value = true
}

const handleSetMaintenance = async () => {
  await setMaintenanceDate(setMaintForm.id, {
    next_maintenance_date: setMaintForm.next_maintenance_date,
    maintenance_cycle_days: setMaintForm.maintenance_cycle_days
  })
  ElMessage.success('已保存')
  setMaintVisible.value = false
  loadData()
}

const renderCostChart = () => {
  if (!costChartRef.value || !summary.value.cost_trend?.length) return
  const chart = echarts.init(costChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}: ¥{c}' },
    grid: { left: 50, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: 'category',
      data: summary.value.cost_trend.map(d => d.month),
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f5f0e8' } },
      axisLabel: { color: '#999', formatter: '¥{value}' }
    },
    series: [{
      type: 'bar',
      data: summary.value.cost_trend.map(d => d.cost),
      barWidth: '40%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#b598d0' },
          { offset: 1, color: '#9b7ab8' }
        ]),
        borderRadius: [6, 6, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '¥{c}', color: '#4a2c2a', fontWeight: 600 }
    }]
  })
}

watch(activeTab, (val) => {
  if (val === 'maintenance') {
    nextTick(renderCostChart)
  }
})

onMounted(async () => {
  await loadData()
  nextTick(renderCostChart)
})
</script>

<style scoped>
.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 12px rgba(74, 44, 42, 0.06);
  transition: all 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(74, 44, 42, 0.1);
}

.stat-ic {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-v {
  font-size: 22px;
  font-weight: 700;
  color: #4a2c2a;
  line-height: 1.2;
}

.stat-l {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.main-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.overdue-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 14px;
}

.overdue-card {
  background: linear-gradient(135deg, #fdf2f0 0%, #faf7f5 100%);
  border: 1px solid #f0d8d4;
  border-radius: 12px;
  padding: 16px;
}

.od-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.od-info {
  background: #fff;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 10px;
}

.od-info-row {
  display: flex;
  font-size: 13px;
  padding: 3px 0;
}

.od-label {
  color: #999;
  width: 90px;
  flex-shrink: 0;
}

.od-value {
  color: #4a2c2a;
  font-weight: 500;
}

.od-notes {
  display: flex;
  gap: 6px;
  font-size: 12px;
  color: #8b6f47;
  background: #fff9ef;
  padding: 8px 10px;
  border-radius: 6px;
  margin-bottom: 12px;
  align-items: flex-start;
}

.od-actions {
  text-align: right;
}

.high-risk-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.high-risk-card {
  background: #faf7f5;
  border: 1px solid #f0e8dd;
  border-radius: 10px;
  padding: 14px;
}
</style>
