// TypeScript type definitions for AI Agricultural Market Intelligence System

// API Request/Response types
export interface PredictPriceRequest {
  commodity: string;
  market?: string;
  district?: string;
  month?: number;
  year?: number;
}

export interface PredictPriceResponse {
  commodity: string;
  predicted_price: number;
  market?: string;
  district?: string;
  confidence?: number;
}

// Commodity types
export interface Commodity {
  id: string;
  name: string;
  category: string;
}

// Market types
export interface Market {
  id: string;
  name: string;
  district: string;
}

// District types
export interface District {
  id: string;
  name: string;
  state: string;
}

// Price trend data for charts
export interface PriceTrendData {
  date: string;
  price: number;
  commodity?: string;
}

export interface MultiCommodityTrendData {
  date: string;
  [commodity: string]: number | string;
}

// Dashboard stats
export interface MarketOverview {
  totalMarkets: number;
  activeCommodities: number;
  avgPrice: number;
  totalVolume: number;
  priceChange: number;
}

// Top commodity data
export interface TopCommodity {
  name: string;
  price: number;
  change: number;
  volume: number;
}

// Market cluster data
export interface MarketCluster {
  name: string;
  markets: number;
  avgPrice: number;
  region: string;
}

// Seasonal pattern data
export interface SeasonalData {
  month: string;
  avgPrice: number;
  volume: number;
}

// Arrival vs price data
export interface ArrivalData {
  month: string;
  arrival: number;
  price: number;
}

// API error type
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

// Chart tooltip props
export interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  label?: string;
}

// Component prop types
export interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  color?: "primary" | "secondary" | "accent" | "gray";
  loading?: boolean;
}

export interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
  loading?: boolean;
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: React.ReactNode;
}

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
  helperText?: string;
}

// Form state
export interface PredictionFormState {
  commodity: string;
  market: string;
  district: string;
  month: string;
  year: string;
}

// Loading states
export interface LoadingState {
  overview: boolean;
  trends: boolean;
  commodities: boolean;
  clusters: boolean;
}
