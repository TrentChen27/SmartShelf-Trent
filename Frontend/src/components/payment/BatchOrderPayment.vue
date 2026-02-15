<template>
  <el-dialog
    v-model="visible"
    title="Complete Payment"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
  >
    <div class="batch-payment-content">
      <!-- Orders Summary -->
      <div class="orders-summary">
        <h3>Orders to Pay</h3>
        <div v-for="order in orders" :key="order.id" class="order-summary-item">
          <div class="order-info">
            <span class="order-id">Order #{{ order.id }}</span>
            <span class="store-name">{{ order.store?.name || `Store #${order.store_id}` }}</span>
          </div>
          <span class="order-amount">${{ (order.total_amount / 100).toFixed(2) }}</span>
        </div>
        <el-divider />
        <div class="total-summary">
          <span class="total-label">Total Amount:</span>
          <span class="total-amount">${{ totalAmount }}</span>
        </div>
      </div>

      <!-- Payment Form -->
      <el-form
        ref="formRef"
        :model="paymentForm"
        :rules="rules"
        label-position="top"
        class="payment-form"
      >
        <el-form-item label="Card Number" prop="cardNumber">
          <el-input
            v-model="paymentForm.cardNumber"
            placeholder="1234 5678 9012 3456"
            maxlength="19"
            @input="formatCardNumber"
          >
            <template #prefix>
              <el-icon><CreditCard /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="Cardholder Name" prop="cardholderName">
          <el-input
            v-model="paymentForm.cardholderName"
            placeholder="John Doe"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Expiry Date" prop="expiryDate">
              <el-input
                v-model="paymentForm.expiryDate"
                placeholder="MM/YY"
                maxlength="5"
                @input="formatExpiryDate"
              >
                <template #prefix>
                  <el-icon><Calendar /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="CVV" prop="cvv">
              <el-input
                v-model="paymentForm.cvv"
                placeholder="123"
                maxlength="4"
                type="password"
                show-password
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        class="payment-note"
      >
        This is a demo payment. All valid card formats will be accepted.
      </el-alert>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel" :disabled="processing">Cancel</el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="processing"
        >
          Pay ${{ totalAmount }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { CreditCard, User, Calendar, Lock } from '@element-plus/icons-vue'
import axios from '../../api/axios'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  orders: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'success', 'cancel'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formRef = ref(null)
const processing = ref(false)

const paymentForm = ref({
  cardNumber: '',
  cardholderName: '',
  expiryDate: '',
  cvv: ''
})

// Calculate total amount
const totalAmount = computed(() => {
  if (!props.orders || props.orders.length === 0) return '0.00'
  const total = props.orders.reduce((sum, order) => sum + order.total_amount, 0)
  return (total / 100).toFixed(2)
})

// Validation rules
const rules = {
  cardNumber: [
    { required: true, message: 'Please enter card number', trigger: 'blur' },
    {
      pattern: /^\d{13,19}$/,
      message: 'Card number must be 13-19 digits',
      trigger: 'blur',
      transform: (value) => value.replace(/\s/g, '')
    }
  ],
  cardholderName: [
    { required: true, message: 'Please enter cardholder name', trigger: 'blur' },
    { min: 3, message: 'Name must be at least 3 characters', trigger: 'blur' }
  ],
  expiryDate: [
    { required: true, message: 'Please enter expiry date', trigger: 'blur' },
    { pattern: /^\d{2}\/\d{2}$/, message: 'Format: MM/YY', trigger: 'blur' }
  ],
  cvv: [
    { required: true, message: 'Please enter CVV', trigger: 'blur' },
    { pattern: /^\d{3,4}$/, message: 'CVV must be 3 or 4 digits', trigger: 'blur' }
  ]
}

// Format card number with spaces
function formatCardNumber(value) {
  const cleaned = value.replace(/\s/g, '')
  const formatted = cleaned.replace(/(\d{4})(?=\d)/g, '$1 ')
  paymentForm.value.cardNumber = formatted
}

// Format expiry date
function formatExpiryDate(value) {
  const cleaned = value.replace(/\D/g, '')
  if (cleaned.length >= 2) {
    paymentForm.value.expiryDate = cleaned.substring(0, 2) + '/' + cleaned.substring(2, 4)
  } else {
    paymentForm.value.expiryDate = cleaned
  }
}

// Reset form when dialog closes
watch(visible, (newVal) => {
  if (!newVal) {
    formRef.value?.resetFields()
    paymentForm.value = {
      cardNumber: '',
      cardholderName: '',
      expiryDate: '',
      cvv: ''
    }
  }
})

// Handle form submit
async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  processing.value = true

  try {
    // Process payment for all orders
    const paymentPromises = props.orders.map(order => {
      return axios.post(`/orders/${order.id}/process-payment`, {
        cardNumber: paymentForm.value.cardNumber.replace(/\s/g, ''),
        cardholderName: paymentForm.value.cardholderName,
        expiryDate: paymentForm.value.expiryDate,
        cvv: paymentForm.value.cvv
      })
    })

    await Promise.all(paymentPromises)

    ElMessage.success(`Payment successful for ${props.orders.length} order(s)!`)
    visible.value = false
    emit('success')
  } catch (error) {
    console.error('Payment failed:', error)
    ElMessage.error(error.response?.data?.error || 'Payment failed. Please try again.')
  } finally {
    processing.value = false
  }
}

// Handle cancel
function handleCancel() {
  visible.value = false
  emit('cancel')
}
</script>

<style scoped>
.batch-payment-content {
  padding: 10px 0;
}

.orders-summary {
  margin-bottom: 24px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.orders-summary h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.order-summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-id {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.store-name {
  font-size: 13px;
  color: #909399;
}

.order-amount {
  font-weight: 600;
  font-size: 16px;
  color: #409eff;
}

.total-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
}

.total-label {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.total-amount {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}

.payment-form {
  margin-top: 20px;
}

.payment-note {
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
