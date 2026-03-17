# AI Agricultural Market Intelligence Dashboard

A production-ready frontend dashboard for an AI Agricultural Market Intelligence System built with **Next.js 14**, **TypeScript**, and **Tailwind CSS**. Connect to a FastAPI backend to get real-time agricultural market insights and crop price predictions.

---

## ✨ Features

- 📊 **Dashboard** – Real-time statistics, multi-commodity price trend charts, top commodities, and market clusters
- 🔮 **Price Prediction** – AI-powered crop price forecasting via FastAPI backend
- 📈 **Market Analysis** – Deep-dive charts: price trends, arrival vs price, and seasonal patterns
- 📱 **Responsive Design** – Mobile-first layout with collapsible sidebar
- ⚡ **Real-time Charts** – Interactive Recharts-powered visualisations
- 🧪 **Mock Data** – Fully functional without a backend for development/testing

---

## 🛠️ Tech Stack

| Layer            | Technology              |
|------------------|-------------------------|
| Framework        | Next.js 14 (App Router) |
| Language         | TypeScript (strict)     |
| Styling          | Tailwind CSS            |
| Charts           | Recharts                |
| HTTP Client      | Axios                   |
| Icons            | Lucide React            |
| Date Handling    | date-fns                |

---

## 📋 Prerequisites

- **Node.js** 18+
- **npm** 9+ or **yarn** 1.22+

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/Krish23101996/ai-agricultural-market-frontend.git
cd ai-agricultural-market-frontend

# 2. Install dependencies
npm install

# 3. Set up environment variables
cp .env.local.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL to your backend URL

# 4. Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📁 Project Structure

```
ai-agricultural-market-frontend/
├── app/
│   ├── layout.tsx              # Root layout with metadata
│   ├── page.tsx                # Dashboard page (/)
│   ├── globals.css             # Global styles with Tailwind
│   ├── prediction/page.tsx     # Price Prediction (/prediction)
│   └── analysis/page.tsx      # Market Analysis (/analysis)
├── components/
│   ├── layout/                 # Layout, Sidebar, Header
│   ├── ui/                     # Card, Button, Input, Select, LoadingSpinner
│   ├── dashboard/              # StatCard, TopCommodities, MarketClusters
│   ├── charts/                 # TrendChart, PriceTrendChart, ArrivalVsPriceChart, SeasonalPatternChart
│   └── prediction/             # PredictionForm, PredictionResult
├── services/api.ts             # Axios API client & mock data
├── types/index.ts              # TypeScript interfaces
└── utils/formatters.ts         # Currency, number, date formatters
```

---

## 📜 Available Scripts

| Script          | Description                         |
|-----------------|-------------------------------------|
| `npm run dev`   | Start development server            |
| `npm run build` | Build for production                |
| `npm run start` | Start production server             |
| `npm run lint`  | Run ESLint                          |

---

## 🔌 API Integration

### Backend URL

Set `NEXT_PUBLIC_API_URL` in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Prediction Endpoint

```http
POST /predict-price
Content-Type: application/json

{
  "commodity": "Tomato",
  "market": "Mumbai Market",
  "district": "Mumbai",
  "month": 6,
  "year": 2025
}
```

**Response:**

```json
{
  "commodity": "Tomato",
  "predicted_price": 4250
}
```

---

## 🌍 Environment Variables

| Variable                | Description                     | Default                    |
|-------------------------|---------------------------------|----------------------------|
| `NEXT_PUBLIC_API_URL`   | FastAPI backend base URL        | `http://localhost:8000`    |

---

## 🏗️ Building for Production

```bash
npm run build
npm run start
```

---

## 🚢 Deployment

The app can be deployed to **Vercel** (recommended for Next.js):

```bash
npm install -g vercel
vercel
```

Or any Node.js-capable hosting platform.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT © 2024 AI Agricultural Market Intelligence
