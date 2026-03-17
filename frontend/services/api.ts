// API service layer for AI Agricultural Market Intelligence System
import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import {
  PredictPriceRequest,
  PredictPriceResponse,
  Commodity,
  Market,
  District,
  MultiCommodityTrendData,
  MarketOverview,
  TopCommodity,
  MarketCluster,
  SeasonalData,
  ArrivalData,
} from "@/types";

// Create axios instance with base configuration
const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error("[API Request Error]", error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    // Provide user-friendly error messages
    let message = "An unexpected error occurred. Please try again.";

    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = "Invalid request. Please check your inputs.";
          break;
        case 401:
          message = "Unauthorized. Please log in again.";
          break;
        case 403:
          message = "Access denied.";
          break;
        case 404:
          message = "Resource not found.";
          break;
        case 422:
          message = "Validation error. Please check your inputs.";
          break;
        case 500:
          message = "Server error. Please try again later.";
          break;
        default:
          message = error.response.data?.detail || message;
      }
    } else if (error.request) {
      message = "Cannot connect to server. Please check if the backend is running.";
    }

    console.error("[API Error]", message, error);
    return Promise.reject(new Error(message));
  }
);

// =====================
// API Methods
// =====================

/**
 * Predict the price for a given commodity
 */
export async function predictPrice(data: PredictPriceRequest): Promise<PredictPriceResponse> {
  const response = await api.post<PredictPriceResponse>("/predict-price", data);
  return response.data;
}

/**
 * Get list of available commodities
 */
export async function getCommodities(): Promise<Commodity[]> {
  const response = await api.get<Commodity[]>("/commodities");
  return response.data;
}

/**
 * Get list of available markets
 */
export async function getMarkets(): Promise<Market[]> {
  const response = await api.get<Market[]>("/markets");
  return response.data;
}

/**
 * Get list of available districts
 */
export async function getDistricts(): Promise<District[]> {
  const response = await api.get<District[]>("/districts");
  return response.data;
}

/**
 * Get price trend data for given commodity (or defaults)
 */
export async function getPriceTrends(commodity?: string): Promise<MultiCommodityTrendData[]> {
  const response = await api.get<MultiCommodityTrendData[]>("/price-trends", {
    params: commodity ? { commodity } : undefined,
  });
  return response.data;
}

/**
 * Get dashboard market overview stats
 */
export async function getMarketOverview(): Promise<MarketOverview> {
  const response = await api.get<MarketOverview>("/market-overview");
  return response.data;
}

/**
 * Get top commodities by price/volume
 */
export async function getTopCommodities(): Promise<TopCommodity[]> {
  const response = await api.get<TopCommodity[]>("/top-commodities");
  return response.data;
}

/**
 * Get market cluster data
 */
export async function getMarketClusters(): Promise<MarketCluster[]> {
  const response = await api.get<MarketCluster[]>("/market-clusters");
  return response.data;
}

/**
 * Get seasonal pattern data for analysis page
 */
export async function getSeasonalData(commodity?: string): Promise<SeasonalData[]> {
  const response = await api.get<SeasonalData[]>("/seasonal-data", {
    params: commodity ? { commodity } : undefined,
  });
  return response.data;
}

/**
 * Get arrival vs price data
 */
export async function getArrivalData(commodity?: string): Promise<ArrivalData[]> {
  const response = await api.get<ArrivalData[]>("/arrival-data", {
    params: commodity ? { commodity } : undefined,
  });
  return response.data;
}

/**
 * Ask the AI agent a question about agricultural markets
 */
export interface AskAgentRequest {
  query: string;
}

export interface AskAgentResponse {
  answer: string;
  sources?: string[];
}

export async function askAgent(data: AskAgentRequest): Promise<AskAgentResponse> {
  const response = await api.post<AskAgentResponse>("/ask-agent", data);
  return response.data;
}

export default api;
