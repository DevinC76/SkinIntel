# SkinIntel 🔬

AI-powered skin analysis platform for acne detection and skin disease classification using machine learning.

![SkinIntel Dashboard](docs/screenshot-dashboard.png)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🎯 Overview

SkinIntel is a full-stack web application that analyzes skin images using AI to detect and classify various skin conditions. It provides detailed metrics on acne lesions, redness levels, and potential skin diseases with confidence scores.

### Key Capabilities

- **Acne Detection**: Identifies and counts acne lesions (papules, pustules, comedones, nodules)
- **Redness Analysis**: Calculates average and global redness metrics
- **Disease Classification**: Detects potential skin conditions with confidence scores
- **User Authentication**: Secure user accounts with Supabase Auth
- **Analysis History**: Track and compare skin analysis over time

## ✨ Features

- 🤖 **AI-Powered Analysis** - Uses Roboflow ML models for accurate detection
- 🔐 **Secure Authentication** - Email/password authentication with Supabase
- 📊 **Detailed Metrics** - Comprehensive analysis including lesion types, dimensions, and redness
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile
- 🗄️ **Cloud Database** - PostgreSQL database via Supabase
- 🚀 **Fast & Modern** - Built with FastAPI and React + Vite
- 📈 **History Tracking** - View and compare past analyses
- ⚡ **Rate Limited** - Protected API endpoints to prevent abuse

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn (ASGI)
- **ML Models**: Roboflow (3 models for acne, disease, classification)
- **Image Processing**: Pillow (PIL)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth (JWT)
- **Rate Limiting**: SlowAPI
- **Data Processing**: Pandas, NumPy

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **Auth**: Supabase Auth Client
- **Styling**: CSS Modules
- **Icons**: Lucide React
- **HTTP Client**: Fetch API

### Infrastructure
- **Database**: Supabase PostgreSQL
- **Authentication**: Supabase Auth
- **Storage**: Supabase (Row Level Security enabled)

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  React Client   │────────▶│  FastAPI Backend │────────▶│   Roboflow ML   │
│   (Port 5173)   │  REST   │   (Port 8000)    │  API    │     Models      │
│                 │◀────────│                  │◀────────│                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
         │                           │
         │                           │
         ▼                           ▼
┌─────────────────────────────────────────────────────┐
│                 Supabase Cloud                      │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ PostgreSQL   │  │     Auth     │               │
│  │   Database   │  │   (JWT)      │               │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
```

### Project Structure

```
SkinIntel/
├── app/                        # Backend Python modules
│   ├── auth/                   # Authentication (routes, dependencies)
│   ├── analysis/               # Analysis endpoints
│   ├── services/               # ML models & image processing
│   ├── config.py               # Configuration & settings
│   ├── database.py             # Supabase client
│   └── models.py               # Pydantic schemas
├── client/                     # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── hooks/              # Custom hooks (auth)
│   │   ├── lib/                # API & Supabase clients
│   │   └── types/              # TypeScript types
│   └── ...
├── main.py                     # FastAPI entry point
├── dev.sh                      # Development script
├── supabase_schema.sql         # Database schema
└── requirements.txt            # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Supabase account
- Roboflow account

### 1. Clone Repository

```bash
git clone https://github.com/DevinC76/SkinIntel.git
cd SkinIntel
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env` with your credentials:
```env
API_KEY=your_roboflow_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Frontend Setup

```bash
cd client

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

Edit `client/.env`:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://localhost:8000
```

### 4. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run `supabase_schema.sql`
3. Get your API keys from Settings → API
4. (Optional) Disable email confirmation in Authentication → Settings

### 5. Run the Application

**Option 1: Use the dev script (recommended)**
```bash
chmod +x dev.sh
./dev.sh
```

**Option 2: Manual start**
```bash
# Terminal 1 - Backend
python main.py

# Terminal 2 - Frontend
cd client && npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 Usage

### 1. Sign Up / Login

Navigate to http://localhost:5173 and create an account or sign in.

### 2. Upload Image

- Click the upload area or drag and drop a skin image
- Supported formats: JPG, PNG, WEBP
- Click "Analyze Skin"

### 3. View Results

The analysis will show:
- **Acne Detection**: Total lesion count and breakdown by type
- **Redness Analysis**: Average and global redness metrics
- **Skin Classification**: Detected conditions with confidence scores
- **Lesion Dimensions**: Average size metrics for detected lesions

### 4. View History

Click "History" to see all your past analyses and compare results over time.

## 📡 API Documentation

### Authentication Endpoints

#### POST `/auth/signup`
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### POST `/auth/login`
Login and receive access token.

**Response:**
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Analysis Endpoints

#### POST `/skinprocessing`
Analyze a skin image (requires authentication).

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request:**
- `file`: Image file (multipart upload)

**Response:**
```json
{
  "id": "uuid",
  "filename": "image.jpg",
  "acne_count": 5,
  "avg_acne_width": 12.5,
  "papules_count": 2,
  "pustules_count": 1,
  "avg_redness": 0.45,
  "skin_disease_label": "acne_vulgaris",
  "skin_disease_confidence": 0.89
}
```

#### GET `/analyses`
Get user's analysis history.

**Query Parameters:**
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset (default: 0)

#### GET `/analyses/{id}`
Get specific analysis by ID.

#### DELETE `/analyses/{id}`
Delete an analysis.

### Rate Limits

- Signup: 5 requests/minute
- Login: 10 requests/minute
- Analysis: 30 requests/minute
- History: 60 requests/minute

## 🚀 Deployment

### Backend (Railway/Render)

1. Add environment variables in platform dashboard
2. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Deploy from GitHub

### Frontend (Vercel)

1. Connect GitHub repository
2. Set root directory to `client`
3. Add environment variables
4. Deploy

### Environment Variables for Production

Update CORS origins in `app/config.py` to include your production frontend URL.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Roboflow for ML model infrastructure
- Supabase for backend services
- FastAPI and React communities

---

**Built with ❤️ for better skin health**
