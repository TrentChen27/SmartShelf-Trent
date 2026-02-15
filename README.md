# SmartShelf

SmartShelf is a comprehensive retail management system designed to streamline store operations, inventory management, and customer interactions. Built with modern web technologies, it provides a full-featured solution for managing multi-store retail businesses with support for both home and business customers.

## 🌟 Features

### Customer Features
- **Product Browsing**: Browse products across multiple stores with real-time inventory information
- **Store Selection**: View products available at specific store locations
- **Shopping Cart**: Add products to cart and manage orders
- **Order Management**: Track order status, payment, and pickup information
- **User Authentication**: Secure login and registration system with JWT authentication

### Manager/Admin Features
- **Dashboard**: Comprehensive management interface with analytics and statistics
- **Store Management**: Manage multiple store locations and their details
- **Inventory Management**: Track and manage product stock across stores
- **Customer Management**: Manage both home and business customer accounts
- **Order Management**: Process and track customer orders
- **Sales Team Management**: Manage salespersons and their assignments
- **Profile Management**: Update user profile and account settings

### System Features
- **Multi-Region Support**: Organize stores by regions with regional managers
- **Employee Management**: Track employees, roles, and salaries
- **Product Categories**: Organize products by type and category
- **Payment Processing**: Handle payment status and order fulfillment
- **Image Upload**: Support for product images via cloud storage (R2)
- **Statistics & Analytics**: View sales and performance metrics

## 🏗️ Architecture

SmartShelf follows a modern full-stack architecture with clear separation between frontend and backend:

```
SmartShelf/
├── Frontend/          # Vue.js 3 web application
│   ├── src/
│   │   ├── components/   # Reusable Vue components
│   │   ├── views/        # Page components
│   │   ├── stores/       # Pinia state management
│   │   └── router/       # Vue Router configuration
│   └── package.json
│
├── Backend/           # Flask REST API
│   ├── app/
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── routes/       # API endpoints
│   │   └── utils/        # Helper utilities
│   ├── dev/              # Development scripts
│   └── requirements.txt
│
└── Table.sql          # Database schema
```

## 🛠️ Tech Stack

### Frontend
- **Vue.js 3**: Progressive JavaScript framework with Composition API
- **Vite**: Next-generation frontend build tool
- **Element Plus**: Vue 3 UI component library
- **Vue Router**: Official routing library
- **Pinia**: State management for Vue 3
- **Axios**: HTTP client for API requests
- **ECharts**: Data visualization library

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Relational database
- **Flask-JWT-Extended**: JWT authentication
- **Flask-CORS**: Cross-origin resource sharing
- **Boto3**: AWS SDK for Python (R2 storage)
- **Gunicorn**: WSGI HTTP server

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- npm or yarn

### Backend Setup

1. Navigate to the Backend directory:
```bash
cd Backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create a `.env` file):
```env
DATABASE_URL=postgresql://username:password@localhost:5432/smartshelf
JWT_SECRET_KEY=your-secret-key
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=your-bucket-name
R2_ENDPOINT_URL=your-r2-endpoint
```

5. Initialize the database:
```bash
# Create tables using the schema
psql -U username -d smartshelf -f ../Table.sql

# Or use the init script
python dev/init_db.py
```

6. (Optional) Seed the database with sample data:
```bash
python dev/seed.py
```

7. Run the development server:
```bash
python run.py
```

The API will be available at `http://localhost:5002`

### Frontend Setup

1. Navigate to the Frontend directory:
```bash
cd Frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure API endpoint (if needed) in your environment or code

4. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Building for Production

**Backend:**
```bash
# The backend is production-ready with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 run:app
```

**Frontend:**
```bash
cd Frontend
npm run build
```

## 📊 Database Schema

The application uses a comprehensive relational database schema with the following main entities:

- **Region**: Store regions with managers
- **Product**: Product catalog with pricing and descriptions
- **OnlineAccount**: User authentication accounts
- **Employee**: Staff members with roles and salaries
- **Customer**: Customer accounts (Home and Business types)
- **Store**: Store locations with managers and inventory
- **SalesPerson**: Sales staff assigned to stores
- **Orders**: Customer orders with payment and pickup status
- **StoreInventory**: Product stock levels per store

See `Table.sql` for the complete schema.

## 🔐 Authentication

SmartShelf uses JWT (JSON Web Tokens) for authentication:
- Tokens are issued upon successful login
- Protected routes require a valid JWT token in the Authorization header
- Tokens contain user role information for role-based access control

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is part of a database systems course project.

## 👤 Author

**Trent Chen**
- GitHub: [@TrentChen27](https://github.com/TrentChen27)

## 🙏 Acknowledgments

- Built as part of a database systems course
- Uses Element Plus UI components
- Cloud storage powered by Cloudflare R2
