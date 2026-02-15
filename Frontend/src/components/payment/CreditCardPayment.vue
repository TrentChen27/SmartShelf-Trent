<template>
  <el-dialog
    v-model="visible"
    title="Credit Card Payment"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="140px"
      label-position="left"
    >
      <!-- Order Summary -->
      <el-alert type="info" :closable="false" style="margin-bottom: 20px">
        <template #title>
          <strong>Order #{{ order?.id }}</strong>
        </template>
        Total Amount: <strong>${{ formatAmount(order?.total_amount) }}</strong>
      </el-alert>

      <!-- Card Number -->
      <el-form-item label="Card Number" prop="cardNumber">
        <el-input
          v-model="form.cardNumber"
          placeholder="1234 5678 9012 3456"
          maxlength="19"
          @input="formatCardNumber"
        >
          <template #prefix>
            <el-icon><CreditCard /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <!-- Card Holder Name -->
      <el-form-item label="Cardholder Name" prop="cardholderName">
        <el-input
          v-model="form.cardholderName"
          placeholder="JOHN DOE"
          style="text-transform: uppercase"
        >
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <!-- Expiry Date and CVV -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Expiry Date" prop="expiryDate">
            <el-input
              v-model="form.expiryDate"
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
              v-model="form.cvv"
              type="password"
              placeholder="123"
              maxlength="4"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- Security Notice -->
      <el-alert type="success" :closable="false" show-icon style="margin-top: 20px">
        <template #title>Demo Payment System</template>
        This is a demo - enter any 13-19 digit card number, valid expiry date (MM/YY), and 3-4 digit CVV to complete payment.
      </el-alert>
    </el-form>

    <template #footer>
      <el-button @click="handleClose" :disabled="processing">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleSubmit"
        :loading="processing"
        size="large"
      >
        <el-icon v-if="!processing"><Check /></el-icon>
        Pay ${{ formatAmount(order?.total_amount) }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { CreditCard, User, Calendar, Lock, Check } from '@element-plus/icons-vue'
import { processPayment } from '../../api/orders'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  order: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = ref(false)
const formRef = ref(null)
const processing = ref(false)

const form = ref({
  cardNumber: '',
  cardholderName: '',
  expiryDate: '',
  cvv: ''
})

// Validation rules
const validateCardNumber = (rule, value, callback) => {
  const cleaned = value.replace(/\s/g, '')
  if (!cleaned) {
    callback(new Error('Please enter card number'))
  } else if (!/^\d{13,19}$/.test(cleaned)) {
    callback(new Error('Card number must be 13-19 digits'))
  } else {
    // For demo purposes, accept any card number with valid format
    // In production, you would validate using Luhn algorithm
    callback()
  }
}

const validateExpiryDate = (rule, value, callback) => {
  if (!value) {
    callback(new Error('Please enter expiry date'))
  } else if (!/^\d{2}\/\d{2}$/.test(value)) {
    callback(new Error('Format: MM/YY'))
  } else {
    const [month, year] = value.split('/')
    const monthNum = parseInt(month)
    const yearNum = parseInt('20' + year)
    const now = new Date()
    const currentYear = now.getFullYear()
    const currentMonth = now.getMonth() + 1

    if (monthNum < 1 || monthNum > 12) {
      callback(new Error('Invalid month'))
    } else if (yearNum < currentYear || (yearNum === currentYear && monthNum < currentMonth)) {
      callback(new Error('Card has expired'))
    } else {
      callback()
    }
  }
}

const validateCVV = (rule, value, callback) => {
  if (!value) {
    callback(new Error('Please enter CVV'))
  } else if (!/^\d{3,4}$/.test(value)) {
    callback(new Error('CVV must be 3 or 4 digits'))
  } else {
    callback()
  }
}

const rules = {
  cardNumber: [
    { required: true, validator: validateCardNumber, trigger: 'blur' }
  ],
  cardholderName: [
    { required: true, message: 'Please enter cardholder name', trigger: 'blur' },
    { min: 3, message: 'Name must be at least 3 characters', trigger: 'blur' }
  ],
  expiryDate: [
    { required: true, validator: validateExpiryDate, trigger: 'blur' }
  ],
  cvv: [
    { required: true, validator: validateCVV, trigger: 'blur' }
  ]
}

// Luhn algorithm for card number validation
function luhnCheck(cardNumber) {
  let sum = 0
  let isEven = false

  for (let i = cardNumber.length - 1; i >= 0; i--) {
    let digit = parseInt(cardNumber[i])

    if (isEven) {
      digit *= 2
      if (digit > 9) {
        digit -= 9
      }
    }

    sum += digit
    isEven = !isEven
  }

  return sum % 10 === 0
}

// Format card number with spaces
function formatCardNumber() {
  let value = form.value.cardNumber.replace(/\s/g, '')
  let formatted = value.match(/.{1,4}/g)?.join(' ') || value
  form.value.cardNumber = formatted
}

// Format expiry date
function formatExpiryDate() {
  let value = form.value.expiryDate.replace(/\D/g, '')
  if (value.length >= 2) {
    value = value.substring(0, 2) + '/' + value.substring(2, 4)
  }
  form.value.expiryDate = value
}

function formatAmount(amount) {
  if (!amount) return '0.00'
  return (amount / 100).toFixed(2)
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    processing.value = true
    try {
      // Process payment
      await processPayment(props.order.id, {
        cardNumber: form.value.cardNumber.replace(/\s/g, ''),
        cardholderName: form.value.cardholderName,
        expiryDate: form.value.expiryDate,
        cvv: form.value.cvv
      })

      ElMessage.success('Payment successful!')
      emit('success')
      handleClose()
    } catch (error) {
      console.error('Payment failed:', error)
      ElMessage.error(error.response?.data?.error || 'Payment failed')
    } finally {
      processing.value = false
    }
  })
}

function handleClose() {
  // Reset form
  form.value = {
    cardNumber: '',
    cardholderName: '',
    expiryDate: '',
    cvv: ''
  }
  formRef.value?.clearValidate()
  emit('update:modelValue', false)
}

watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  if (!val) {
    emit('update:modelValue', false)
  }
})
</script>

<style scoped>
:deep(.el-input__inner) {
  font-family: 'Courier New', monospace;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
