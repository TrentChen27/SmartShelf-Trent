<template>
  <div class="inventory-management">
    <el-card>
      <template #header>
        <div class="header-title">
          <h3>Inventory Management</h3>
          <div class="header-actions">
            <el-button
              v-if="role === 'manager'"
              type="success"
              @click="openAddStockDialog"
            >
              <el-icon><Plus /></el-icon>
              Add Stock
            </el-button>
            <el-button
              v-if="role === 'manager'"
              type="primary"
              @click="openProductDialog"
            >
              <el-icon><Plus /></el-icon>
              Add Product
            </el-button>
          </div>
        </div>
      </template>

      <!-- Filters -->
      <div class="filters">
        <el-input
          v-model="searchQuery"
          placeholder="Search products by name"
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-if="role === 'region'"
          v-model="storeFilter"
          placeholder="All Stores"
          clearable
          style="width: 200px"
          @change="loadInventory"
        >
          <el-option label="All Stores" :value="null" />
          <el-option
            v-for="store in stores"
            :key="store.id"
            :label="store.name"
            :value="store.id"
          />
        </el-select>

        <el-select
          v-model="categoryFilter"
          placeholder="All Categories"
          clearable
          style="width: 200px"
          @change="filterInventory"
        >
          <el-option label="All Categories" :value="null" />
          <el-option
            v-for="category in categories"
            :key="category"
            :label="category"
            :value="category"
          />
        </el-select>
      </div>

      <!-- Inventory Table -->
      <el-table
        :data="displayedInventory"
        v-loading="loading"
        stripe
        size="small"
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column label="Image" width="70">
          <template #default="{ row }">
            <el-image
              v-if="row.product?.image_url"
              :src="row.product.image_url"
              fit="contain"
              style="width: 50px; height: 50px; border-radius: 4px"
              :preview-src-list="[row.product.image_url]"
            />
            <div v-else class="no-image-small">No Img</div>
          </template>
        </el-table-column>

        <el-table-column
          label="ID"
          width="60"
        >
          <template #default="{ row }">
            {{ row.product_id }}
          </template>
        </el-table-column>

        <el-table-column
          label="Product Name"
          min-width="150"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ row.product?.product_name || 'Unknown' }}
          </template>
        </el-table-column>

        <el-table-column
          label="Category"
          width="100"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ row.product?.kind || '-' }}
          </template>
        </el-table-column>

        <el-table-column
          label="Price"
          width="90"
          align="right"
        >
          <template #default="{ row }">
            ${{ formatPrice(row.product?.price || 0) }}
          </template>
        </el-table-column>

        <el-table-column
          v-if="role === 'manager'"
          label="Store"
          width="130"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ row.store_name }}
          </template>
        </el-table-column>

        <el-table-column
          :label="role === 'region' ? 'Total Stock' : 'Stock'"
          :width="role === 'region' ? 100 : 80"
          align="right"
        >
          <template #default="{ row }">
            <el-tag :type="getStockTagType(row.stock)" size="small">
              {{ row.stock }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="Actions"
          :width="role === 'manager' ? 200 : 180"
          fixed="right"
        >
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                size="small"
                type="primary"
                @click="openEditStockDialog(row)"
              >
                Stock
              </el-button>
              <el-button
                v-if="role === 'manager'"
                size="small"
                type="warning"
                @click="openEditProductDialog(row)"
              >
                Product
              </el-button>
              <el-button
                v-else-if="role === 'region'"
                size="small"
                @click="viewProductDetails(row)"
              >
                View
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredInventory.length"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- Add Product Dialog -->
    <el-dialog
      v-model="showProductDialog"
      title="Add New Product"
      width="650px"
      @close="resetProductForm"
    >
      <el-form
        ref="productFormRef"
        :model="productForm"
        :rules="productRules"
        label-position="top"
        size="large"
      >
        <!-- Product Image -->
        <div class="form-section">
          <h4 class="section-title">Product Image</h4>
          <el-form-item label="Image" prop="image_url">
            <div class="image-upload-container">
              <el-upload
                class="image-uploader"
                :show-file-list="false"
                :http-request="handleImageUpload"
                :auto-upload="true"
                accept="image/*"
                drag
                :disabled="uploadingImage"
              >
                <div v-if="uploadingImage" class="upload-loading">
                  <el-icon class="is-loading" :size="40"><Loading /></el-icon>
                  <div class="upload-text">Uploading...</div>
                </div>
                <div v-else-if="productForm.image_url" class="image-preview">
                  <el-image
                    :src="productForm.image_url"
                    fit="contain"
                    style="width: 100%; height: 200px;"
                  />
                  <div class="image-overlay">
                    <el-button type="danger" size="small" @click.stop="removeImage">
                      Remove
                    </el-button>
                  </div>
                </div>
                <div v-else class="upload-placeholder">
                  <el-icon class="upload-icon"><Plus /></el-icon>
                  <div class="upload-text">Click or drag image here</div>
                  <div class="upload-hint">Supports: PNG, JPG, JPEG, GIF, WEBP (Max 5MB)</div>
                </div>
              </el-upload>
            </div>
          </el-form-item>
        </div>

        <!-- Product Information -->
        <div class="form-section">
          <h4 class="section-title">Product Information</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Product Name" prop="product_name">
                <el-input
                  v-model="productForm.product_name"
                  placeholder="Enter product name"
                  size="large"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Category" prop="kind">
                <el-select
                  v-model="productForm.kind"
                  placeholder="Select or enter category"
                  size="large"
                  style="width: 100%"
                  allow-create
                  filterable
                >
                  <el-option
                    v-for="category in categories"
                    :key="category"
                    :label="category"
                    :value="category"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Price (USD)" prop="price">
                <el-input
                  v-model="productFormPriceInput"
                  placeholder="0.00"
                  size="large"
                  style="width: 100%"
                  @blur="formatProductPrice"
                  @input="validateProductPriceInput"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Description" prop="description">
            <el-input
              v-model="productForm.description"
              type="textarea"
              :rows="4"
              placeholder="Enter product description"
              size="large"
            />
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showProductDialog = false" size="large">Cancel</el-button>
        <el-button type="primary" @click="saveProduct" :loading="saving" size="large">
          Create Product
        </el-button>
      </template>
    </el-dialog>

    <!-- View Product Dialog (Read-only for Region Manager) -->
    <el-dialog
      v-model="showViewProductDialog"
      title="Product Information (View Only)"
      width="650px"
      @close="resetViewProductForm"
    >
      <div v-if="viewProductData" class="product-view-content">
        <!-- Product Image -->
        <div v-if="viewProductData.image_url" class="product-view-image">
          <el-image
            :src="viewProductData.image_url"
            fit="contain"
            style="width: 100%; height: 300px;"
            :preview-src-list="[viewProductData.image_url]"
          />
        </div>

        <!-- Product Information -->
        <el-descriptions :column="2" border size="large" style="margin-top: 20px">
          <el-descriptions-item label="Product ID">
            {{ viewProductData.id }}
          </el-descriptions-item>
          <el-descriptions-item label="Product Name">
            {{ viewProductData.product_name }}
          </el-descriptions-item>
          <el-descriptions-item label="Category">
            {{ viewProductData.kind || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="Price">
            ${{ formatPrice(viewProductData.price) }}
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">
            {{ viewProductData.description || 'No description available' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="showViewProductDialog = false" size="large">Close</el-button>
      </template>
    </el-dialog>

    <!-- Edit Product Dialog -->
    <el-dialog
      v-model="showEditProductDialog"
      title="Edit Product Information"
      width="650px"
      @close="resetEditProductForm"
    >
      <el-form
        ref="editProductFormRef"
        :model="editProductForm"
        :rules="productRules"
        label-position="top"
        size="large"
      >
        <!-- Product Image -->
        <div class="form-section">
          <h4 class="section-title">Product Image</h4>
          <el-form-item label="Image" prop="image_url">
            <div class="image-upload-container">
              <el-upload
                class="image-uploader"
                :show-file-list="false"
                :http-request="handleEditImageUpload"
                :auto-upload="true"
                accept="image/*"
                drag
                :disabled="uploadingEditImage"
              >
                <div v-if="uploadingEditImage" class="upload-loading">
                  <el-icon class="is-loading" :size="40"><Loading /></el-icon>
                  <div class="upload-text">Uploading...</div>
                </div>
                <div v-else-if="editProductForm.image_url" class="image-preview">
                  <el-image
                    :src="editProductForm.image_url"
                    fit="contain"
                    style="width: 100%; height: 200px;"
                  />
                  <div class="image-overlay">
                    <el-button type="danger" size="small" @click.stop="removeEditImage">
                      Remove
                    </el-button>
                  </div>
                </div>
                <div v-else class="upload-placeholder">
                  <el-icon class="upload-icon"><Plus /></el-icon>
                  <div class="upload-text">Click or drag image here</div>
                  <div class="upload-hint">Supports: PNG, JPG, JPEG, GIF, WEBP (Max 5MB)</div>
                </div>
              </el-upload>
            </div>
          </el-form-item>
        </div>

        <!-- Product Information -->
        <div class="form-section">
          <h4 class="section-title">Product Information</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Product Name" prop="product_name">
                <el-input
                  v-model="editProductForm.product_name"
                  placeholder="Enter product name"
                  size="large"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Category" prop="kind">
                <el-select
                  v-model="editProductForm.kind"
                  placeholder="Select or enter category"
                  size="large"
                  style="width: 100%"
                  allow-create
                  filterable
                >
                  <el-option
                    v-for="category in categories"
                    :key="category"
                    :label="category"
                    :value="category"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Price (USD)" prop="price">
                <el-input
                  v-model="editProductFormPriceInput"
                  placeholder="0.00"
                  size="large"
                  style="width: 100%"
                  @blur="formatEditProductPrice"
                  @input="validateEditProductPriceInput"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Description" prop="description">
            <el-input
              v-model="editProductForm.description"
              type="textarea"
              :rows="4"
              placeholder="Enter product description"
              size="large"
            />
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showEditProductDialog = false" size="large">Cancel</el-button>
        <el-button type="primary" @click="saveEditProduct" :loading="saving" size="large">
          Update Product
        </el-button>
      </template>
    </el-dialog>

    <!-- Add Stock Dialog -->
    <el-dialog
      v-model="showAddStockDialog"
      title="Add Stock to Inventory"
      width="650px"
      @close="resetAddStockForm"
    >
      <el-form
        ref="addStockFormRef"
        :model="addStockForm"
        :rules="addStockRules"
        label-position="top"
        size="large"
      >
        <!-- Select Product -->
        <div class="form-section">
          <h4 class="section-title">Select Product</h4>

          <!-- Product Selection -->
          <el-form-item label="Product" prop="product_id">
            <el-select
              v-model="addStockForm.product_id"
              placeholder="Select or search for a product"
              style="width: 100%"
              filterable
              @change="handleProductSelect"
            >
              <el-option
                v-for="product in allProducts"
                :key="product.id"
                :label="`#${product.id} - ${product.product_name} ($${formatPrice(product.price)})`"
                :value="product.id"
              >
                <div class="product-option">
                  <span class="product-option-name">{{ product.product_name }}</span>
                  <el-tag v-if="product.kind" size="small" type="info" style="margin-left: 8px">
                    {{ product.kind }}
                  </el-tag>
                  <span class="product-option-price">${{ formatPrice(product.price) }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <!-- Selected Product Preview -->
          <div v-if="selectedProductForAdd" class="selected-product-preview">
            <el-image
              v-if="selectedProductForAdd.image_url"
              :src="selectedProductForAdd.image_url"
              fit="contain"
              style="width: 80px; height: 80px; border-radius: 8px"
            />
            <div class="product-preview-details">
              <h4>{{ selectedProductForAdd.product_name }}</h4>
              <p class="product-preview-price">${{ formatPrice(selectedProductForAdd.price) }}</p>
              <el-tag v-if="selectedProductForAdd.kind" size="small" type="info">
                {{ selectedProductForAdd.kind }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- Store Selection (Region Manager only) -->
        <div v-if="role === 'region'" class="form-section">
          <h4 class="section-title">Select Store</h4>
          <el-form-item label="Store" prop="store_id">
            <el-select
              v-model="addStockForm.store_id"
              placeholder="Select store"
              style="width: 100%"
            >
              <el-option
                v-for="store in stores"
                :key="store.id"
                :label="store.name"
                :value="store.id"
              />
            </el-select>
          </el-form-item>
        </div>

        <!-- Stock Quantity -->
        <div class="form-section">
          <h4 class="section-title">Stock Quantity</h4>
          <el-form-item label="Initial Stock" prop="stock">
            <el-input-number
              v-model="addStockForm.stock"
              :min="0"
              :step="1"
              placeholder="0"
              style="width: 100%"
              size="large"
            />
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showAddStockDialog = false" size="large">Cancel</el-button>
        <el-button type="success" @click="saveAddStock" :loading="saving" size="large">
          Add to Inventory
        </el-button>
      </template>
    </el-dialog>

    <!-- Edit Stock Dialog -->
    <el-dialog
      v-model="showEditStockDialog"
      :title="role === 'region' ? 'View Stock Information' : 'Edit Stock'"
      width="700px"
      @close="resetEditStockForm"
    >
      <div v-if="selectedInventory" class="stock-dialog-content">
        <!-- Product Info Header -->
        <div class="product-info-header">
          <el-image
            v-if="selectedInventory.product?.image_url"
            :src="selectedInventory.product.image_url"
            fit="contain"
            style="width: 80px; height: 80px; border-radius: 8px"
          />
          <div class="product-details">
            <h4>{{ selectedInventory.product?.product_name }}</h4>
            <p class="product-price">${{ formatPrice(selectedInventory.product?.price || 0) }}</p>
            <el-tag v-if="selectedInventory.product?.kind" size="small" type="info">
              {{ selectedInventory.product.kind }}
            </el-tag>
          </div>
        </div>

        <!-- Edit Form for My Store (Top) - Only for Store Managers -->
        <template v-if="role === 'manager'">
          <el-divider />

          <div class="edit-my-stock">
            <h4 class="section-subtitle">Edit Your Store's Stock</h4>
            <el-form
              ref="editStockFormRef"
              :model="editStockForm"
              label-position="top"
              size="large"
            >
              <el-form-item label="Store">
                <el-input :value="myStoreName" disabled />
              </el-form-item>

              <el-form-item
                label="Stock Quantity"
                prop="stock"
                :rules="[{ required: true, message: 'Please enter stock quantity' }]"
              >
                <el-input-number
                  v-model="editStockForm.stock"
                  :min="0"
                  :step="1"
                  placeholder="0"
                  style="width: 100%"
                />
              </el-form-item>

              <el-alert
                :title="`Current stock: ${currentMyStock}`"
                type="info"
                :closable="false"
                show-icon
              />
            </el-form>
          </div>

          <el-divider />
        </template>

        <!-- All Stores Stock (Reference) - Below -->
        <div class="all-stores-stock">
          <h4 class="section-subtitle">
            Stock Across {{ role === 'region' ? 'Region' : 'All' }} Stores (Reference)
          </h4>
          <el-table
            :data="allStoresStock"
            size="small"
            stripe
          >
            <el-table-column prop="store_name" label="Store" min-width="150" />
            <el-table-column label="Stock" width="100" align="right">
              <template #default="{ row }">
                <el-tag :type="getStockTagType(row.stock)" size="small">
                  {{ row.stock }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <el-button @click="showEditStockDialog = false" size="large">
          {{ role === 'region' ? 'Close' : 'Cancel' }}
        </el-button>
        <el-button
          v-if="role === 'manager'"
          type="primary"
          @click="saveEditStock"
          :loading="saving"
          size="large"
        >
          Update Stock
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Loading } from '@element-plus/icons-vue'
import axios from '../../api/axios'

const props = defineProps({
  role: {
    type: String,
    required: true
  }
})

// Data
const loading = ref(false)
const saving = ref(false)
const inventory = ref([])
const stores = ref([])
const categories = ref([])
const allProducts = ref([])
const searchQuery = ref('')
const storeFilter = ref(null)
const categoryFilter = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const myStoreId = ref(null)
const myStoreName = ref('')

// Product Dialog
const showProductDialog = ref(false)
const productFormRef = ref(null)
const productForm = ref({
  product_name: '',
  kind: '',
  price: 0,
  description: '',
  image_url: ''
})

// Price input handling for product form
const productFormPriceInput = ref('')

function validateProductPriceInput(value) {
  // Only allow numbers and one decimal point with max 2 decimal places
  const regex = /^\d*\.?\d{0,2}$/
  if (!regex.test(value)) {
    // If invalid, remove the last character
    productFormPriceInput.value = value.slice(0, -1)
  } else {
    // Update the price in cents
    const numValue = parseFloat(value)
    if (!isNaN(numValue)) {
      productForm.value.price = Math.round(numValue * 100)
    } else {
      productForm.value.price = 0
    }
  }
}

function formatProductPrice() {
  let value = productFormPriceInput.value.trim()

  // If empty, keep it empty and set price to 0
  if (!value || value === '' || value === '.') {
    productFormPriceInput.value = ''
    productForm.value.price = 0
    return
  }

  // Parse the number
  let numValue = parseFloat(value)
  if (isNaN(numValue)) {
    productFormPriceInput.value = ''
    productForm.value.price = 0
    return
  }

  // Format to 2 decimal places
  productFormPriceInput.value = numValue.toFixed(2)
  productForm.value.price = Math.round(numValue * 100)
}

const productRules = {
  product_name: [{ required: true, message: 'Please enter product name', trigger: 'blur' }],
  kind: [{ required: true, message: 'Please select category', trigger: 'blur' }],
  price: [{ required: true, message: 'Please enter price', trigger: 'blur' }],
  image_url: [{ required: true, message: 'Please upload product image', trigger: 'change' }]
}

// Add Stock Dialog
const showAddStockDialog = ref(false)
const addStockFormRef = ref(null)
const addStockForm = ref({
  product_id: null,
  store_id: null,
  stock: 0
})
const selectedProductForAdd = ref(null)

const addStockRules = {
  product_id: [{ required: true, message: 'Please select a product', trigger: 'change' }],
  store_id: props.role === 'region' ? [{ required: true, message: 'Please select a store', trigger: 'change' }] : [],
  stock: [{ required: true, message: 'Please enter stock quantity', trigger: 'blur' }]
}

// Edit Stock Dialog
const showEditStockDialog = ref(false)
const selectedInventory = ref(null)
const editStockFormRef = ref(null)
const editStockForm = ref({
  stock: 0
})
const allStoresStock = ref([])
const currentMyStock = ref(0)
const uploadingImage = ref(false)
const uploadingEditImage = ref(false)

// View Product Dialog (for region manager)
const showViewProductDialog = ref(false)
const viewProductData = ref(null)

// Edit Product Dialog (for store manager)
const showEditProductDialog = ref(false)
const editProductFormRef = ref(null)
const editProductForm = ref({
  id: null,
  product_name: '',
  kind: '',
  price: 0,
  description: '',
  image_url: ''
})

// Price input handling for edit product form
const editProductFormPriceInput = ref('')

function validateEditProductPriceInput(value) {
  // Only allow numbers and one decimal point with max 2 decimal places
  const regex = /^\d*\.?\d{0,2}$/
  if (!regex.test(value)) {
    // If invalid, remove the last character
    editProductFormPriceInput.value = value.slice(0, -1)
  } else {
    // Update the price in cents
    const numValue = parseFloat(value)
    if (!isNaN(numValue)) {
      editProductForm.value.price = Math.round(numValue * 100)
    } else {
      editProductForm.value.price = 0
    }
  }
}

function formatEditProductPrice() {
  let value = editProductFormPriceInput.value.trim()

  // If empty, keep it empty and set price to 0
  if (!value || value === '' || value === '.') {
    editProductFormPriceInput.value = ''
    editProductForm.value.price = 0
    return
  }

  // Parse the number
  let numValue = parseFloat(value)
  if (isNaN(numValue)) {
    editProductFormPriceInput.value = ''
    editProductForm.value.price = 0
    return
  }

  // Format to 2 decimal places
  editProductFormPriceInput.value = numValue.toFixed(2)
  editProductForm.value.price = Math.round(numValue * 100)
}

// Computed
const filteredInventory = computed(() => {
  let filtered = [...inventory.value]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(inv =>
      inv.product?.product_name?.toLowerCase().includes(query)
    )
  }

  // Category filter
  if (categoryFilter.value) {
    filtered = filtered.filter(inv => inv.product?.kind === categoryFilter.value)
  }

  // For regional managers, aggregate inventory by product (sum stock across all stores)
  if (props.role === 'region') {
    const productMap = new Map()

    filtered.forEach(inv => {
      const productId = inv.product_id
      if (productMap.has(productId)) {
        // Aggregate stock
        const existing = productMap.get(productId)
        existing.stock += inv.stock
      } else {
        // Create new aggregated entry
        productMap.set(productId, {
          ...inv,
          stock: inv.stock,
          // Keep the first inventory item's store info for reference
          _aggregated: true
        })
      }
    })

    return Array.from(productMap.values())
  }

  return filtered
})

const displayedInventory = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredInventory.value.slice(start, end)
})

// Methods
function formatPrice(cents) {
  return (cents / 100).toFixed(2)
}

function getStockTagType(stock) {
  if (stock === 0) return 'info'
  if (stock < 10) return 'warning'
  return 'success'
}

let searchTimeout = null
function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
  }, 300)
}

function filterInventory() {
  currentPage.value = 1
}

function handlePageChange() {
  // Page changed
}

function handleSizeChange() {
  currentPage.value = 1
}

async function loadInventory() {
  loading.value = true
  try {
    const params = {}

    if (props.role === 'region' && storeFilter.value) {
      params.store_id = storeFilter.value
    }

    const response = await axios.get('/inventory', { params })
    inventory.value = response.data.inventory || []
  } catch (error) {
    console.error('Failed to load inventory:', error)
    ElMessage.error('Failed to load inventory')
  } finally {
    loading.value = false
  }
}

async function loadStores() {
  try {
    const response = await axios.get('/stores')
    stores.value = response.data || []

    if (props.role === 'manager' && stores.value.length > 0) {
      myStoreId.value = stores.value[0].id
      myStoreName.value = stores.value[0].name
      addStockForm.value.store_id = stores.value[0].id
    }
  } catch (error) {
    console.error('Failed to load stores:', error)
  }
}

async function loadCategories() {
  try {
    const response = await axios.get('/products/categories')
    categories.value = response.data || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

async function loadAllProducts() {
  try {
    const response = await axios.get('/products')
    allProducts.value = response.data || []
  } catch (error) {
    console.error('Failed to load products:', error)
  }
}

function openProductDialog() {
  showProductDialog.value = true
}

function resetProductForm() {
  productForm.value = {
    product_name: '',
    kind: '',
    price: 0,
    description: '',
    image_url: ''
  }
  productFormPriceInput.value = ''
  productFormRef.value?.clearValidate()
}

async function handleImageUpload(options) {
  const { file } = options

  // Validate file size
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('Image size cannot exceed 5MB')
    return
  }

  // Validate file type
  const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('Only PNG, JPG, JPEG, GIF, WEBP images are allowed')
    return
  }

  uploadingImage.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)

    console.log('Uploading file:', file.name, 'Type:', file.type, 'Size:', file.size)

    const response = await axios.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    console.log('Upload response:', response.data)

    productForm.value.image_url = response.data.url
    ElMessage.success('Image uploaded successfully')
  } catch (error) {
    console.error('Failed to upload image:', error)
    console.error('Error response:', error.response?.data)
    const errorMsg = error.response?.data?.error || error.message || 'Failed to upload image'
    ElMessage.error(errorMsg)
  } finally {
    uploadingImage.value = false
  }
}

function removeImage() {
  productForm.value.image_url = ''
}

function removeEditImage() {
  editProductForm.value.image_url = ''
}

async function handleEditImageUpload(options) {
  const { file } = options

  // Validate file size
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('Image size cannot exceed 5MB')
    return
  }

  // Validate file type
  const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('Only PNG, JPG, JPEG, GIF, WEBP images are allowed')
    return
  }

  uploadingEditImage.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    editProductForm.value.image_url = response.data.url
    ElMessage.success('Image uploaded successfully')
  } catch (error) {
    console.error('Failed to upload image:', error)
    const errorMsg = error.response?.data?.error || error.message || 'Failed to upload image'
    ElMessage.error(errorMsg)
  } finally {
    uploadingEditImage.value = false
  }
}

async function saveProduct() {
  if (!productFormRef.value) return

  try {
    await productFormRef.value.validate()
  } catch {
    return
  }

  saving.value = true

  try {
    const productData = {
      product_name: productForm.value.product_name,
      kind: productForm.value.kind,
      price: productForm.value.price,
      description: productForm.value.description,
      image_url: productForm.value.image_url
    }

    await axios.post('/products', productData)
    ElMessage.success('Product created successfully')

    showProductDialog.value = false
    await loadAllProducts()
    await loadCategories()
  } catch (error) {
    console.error('Failed to save product:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to save product')
  } finally {
    saving.value = false
  }
}

function openAddStockDialog() {
  loadAllProducts()
  showAddStockDialog.value = true
}

function resetAddStockForm() {
  addStockForm.value = {
    product_id: null,
    store_id: props.role === 'manager' ? myStoreId.value : null,
    stock: 0
  }
  selectedProductForAdd.value = null
  addStockFormRef.value?.clearValidate()
}

function handleProductSelect(productId) {
  selectedProductForAdd.value = allProducts.value.find(p => p.id === productId)
}

async function saveAddStock() {
  if (!addStockFormRef.value) return

  try {
    await addStockFormRef.value.validate()
  } catch {
    return
  }

  saving.value = true

  try {
    const storeId = props.role === 'manager' ? myStoreId.value : addStockForm.value.store_id

    await axios.post('/inventory', {
      store_id: storeId,
      product_id: addStockForm.value.product_id,
      stock: addStockForm.value.stock
    })

    ElMessage.success('Stock added successfully')
    showAddStockDialog.value = false
    await loadInventory()
  } catch (error) {
    console.error('Failed to add stock:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to add stock')
  } finally {
    saving.value = false
  }
}

async function openEditStockDialog(inventoryItem) {
  selectedInventory.value = inventoryItem
  editStockForm.value.stock = inventoryItem.stock
  currentMyStock.value = inventoryItem.stock

  try {
    const response = await axios.get(`/products/${inventoryItem.product_id}`)
    const product = response.data

    allStoresStock.value = stores.value.map(store => {
      const storeInv = product.stores_inventory?.[store.id]
      return {
        store_id: store.id,
        store_name: store.name,
        stock: storeInv ? storeInv.stock : 0
      }
    })

    myStoreId.value = inventoryItem.store_id
    myStoreName.value = inventoryItem.store_name

  } catch (error) {
    console.error('Failed to load product details:', error)
    ElMessage.error('Failed to load stock details')
    return
  }

  showEditStockDialog.value = true
}

function resetEditStockForm() {
  selectedInventory.value = null
  editStockForm.value = {
    stock: 0
  }
  allStoresStock.value = []
  currentMyStock.value = 0
  editStockFormRef.value?.clearValidate()
}

async function saveEditStock() {
  if (!editStockFormRef.value) return

  try {
    await editStockFormRef.value.validate()
  } catch {
    return
  }

  saving.value = true

  try {
    await axios.post('/inventory', {
      store_id: myStoreId.value,
      product_id: selectedInventory.value.product_id,
      stock: editStockForm.value.stock
    })

    ElMessage.success('Stock updated successfully')
    showEditStockDialog.value = false
    await loadInventory()
  } catch (error) {
    console.error('Failed to update stock:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to update stock')
  } finally {
    saving.value = false
  }
}

function viewProductDetails(inventoryItem) {
  if (!inventoryItem.product) {
    ElMessage.error('Product information not available')
    return
  }

  viewProductData.value = {
    id: inventoryItem.product_id,
    product_name: inventoryItem.product.product_name,
    kind: inventoryItem.product.kind,
    price: inventoryItem.product.price,
    description: inventoryItem.product.description,
    image_url: inventoryItem.product.image_url
  }

  showViewProductDialog.value = true
}

function resetViewProductForm() {
  viewProductData.value = null
}

function openEditProductDialog(inventoryItem) {
  if (!inventoryItem.product) {
    ElMessage.error('Product information not available')
    return
  }

  editProductForm.value = {
    id: inventoryItem.product_id,
    product_name: inventoryItem.product.product_name,
    kind: inventoryItem.product.kind || '',
    price: inventoryItem.product.price,
    description: inventoryItem.product.description || '',
    image_url: inventoryItem.product.image_url || ''
  }

  // Initialize price input with formatted value
  editProductFormPriceInput.value = (inventoryItem.product.price / 100).toFixed(2)

  showEditProductDialog.value = true
}

function resetEditProductForm() {
  editProductForm.value = {
    id: null,
    product_name: '',
    kind: '',
    price: 0,
    description: '',
    image_url: ''
  }
  editProductFormPriceInput.value = ''
  editProductFormRef.value?.clearValidate()
}

async function saveEditProduct() {
  if (!editProductFormRef.value) return

  try {
    await editProductFormRef.value.validate()
  } catch {
    return
  }

  saving.value = true

  try {
    const productData = {
      product_name: editProductForm.value.product_name,
      kind: editProductForm.value.kind,
      price: editProductForm.value.price,
      description: editProductForm.value.description,
      image_url: editProductForm.value.image_url
    }

    await axios.put(`/products/${editProductForm.value.id}`, productData)
    ElMessage.success('Product updated successfully')

    showEditProductDialog.value = false
    await loadInventory()
    await loadAllProducts()
    await loadCategories()
  } catch (error) {
    console.error('Failed to update product:', error)
    ElMessage.error(error.response?.data?.error || 'Failed to update product')
  } finally {
    saving.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadStores().then(() => {
    loadInventory()
  })
  loadCategories()
})
</script>

<style scoped>
.inventory-management {
  padding: 0;
}

.header-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.no-image {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 4px;
  color: #909399;
  font-size: 12px;
  text-align: center;
}

.no-image-small {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 4px;
  color: #909399;
  font-size: 10px;
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-buttons .el-button {
  margin: 0;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* Dialog Sections */
.form-section {
  margin-bottom: 24px;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.section-subtitle {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #606266;
}

/* Image Upload */
.image-upload-container {
  width: 100%;
}

.image-uploader {
  width: 100%;
}

.image-uploader :deep(.el-upload) {
  width: 100%;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.image-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}

.image-preview {
  width: 100%;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 20px;
}

.image-overlay {
  position: absolute;
  bottom: 10px;
  right: 10px;
}

.upload-placeholder {
  padding: 60px 20px;
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: #8c939d;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
}

.upload-hint {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

.upload-loading {
  padding: 60px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-loading .is-loading {
  color: #409eff;
}

/* Add Stock Dialog */
.product-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.product-option-name {
  flex: 1;
  font-weight: 500;
}

.product-option-price {
  margin-left: auto;
  color: #409eff;
  font-weight: 600;
}

.selected-product-preview {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ebf0 100%);
  border-radius: 8px;
  margin-top: 16px;
}

.product-preview-details h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.product-preview-price {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

/* View Product Dialog */
.product-view-content {
  padding: 10px 0;
}

.product-view-image {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

/* Edit Stock Dialog */
.stock-dialog-content {
  padding: 10px 0;
}

.product-info-header {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ebf0 100%);
  border-radius: 8px;
}

.product-details h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.product-price {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
}

.edit-my-stock {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  border: 2px solid #409eff;
}

.all-stores-stock {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filters .el-input,
  .filters .el-select {
    width: 100% !important;
  }

  .header-actions {
    flex-direction: column;
  }
}
</style>
