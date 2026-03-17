'use client';
// Main Dashboard page
import React, { useEffect, useState, useCallback } from "react";
import Layout from "@/components/layout/Layout";
import StatCard from "@/components/dashboard/StatCard";
import TopCommodities from "@/components/dashboard/TopCommodities";
import MarketClusters from "@/components/dashboard/MarketClusters";
import TrendChart from "@/components/charts/TrendChart";
import {
  getMarketOverview,
  getTopCommodities,
  getMarketClusters,
  getPriceTrends,
} from "@/services/api";
import {
  MarketOverview,
  TopCommodity,
  MarketCluster,
  MultiCommodityTrendData,
  LoadingState,
} from "@/types";
import { formatCurrency, formatNumber, formatPercentage } from "@/utils/formatters";
import { Store, Package, TrendingUp, BarChart2 } from "lucide-react";

export default function DashboardPage() {
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [topCommodities, setTopCommodities] = useState<TopCommodity[]>([]);
  const [clusters, setClusters] = useState<MarketCluster[]>([]);
  const [trendData, setTrendData] = useState<MultiCommodityTrendData[]>([]);
  const [loading, setLoading] = useState<LoadingState>({
    overview: true,
    trends: true,
    commodities: true,
    clusters: true,
  });
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading({ overview: true, trends: true, commodities: true, clusters: true });
    setError(null);

    try {
      const [overviewData, commoditiesData, clustersData, trendsData] = await Promise.all([
        getMarketOverview(),
        getTopCommodities(),
        getMarketClusters(),
        getPriceTrends(),
      ]);
      setOverview(overviewData);
      setTopCommodities(commoditiesData);
      setClusters(clustersData);
      setTrendData(trendsData);
    } catch (err) {
      setError("Failed to load dashboard data. Please try again.");
      console.error(err);
    } finally {
      setLoading({ overview: false, trends: false, commodities: false, clusters: false });
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <Layout
      title="Dashboard"
      subtitle="Agricultural Market Overview"
      onRefresh={loadData}
    >
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="Total Markets"
          value={overview ? formatNumber(overview.totalMarkets) : "—"}
          icon={<Store className="w-6 h-6" />}
          color="primary"
          loading={loading.overview}
        />
        <StatCard
          title="Active Commodities"
          value={overview ? formatNumber(overview.activeCommodities) : "—"}
          icon={<Package className="w-6 h-6" />}
          color="secondary"
          loading={loading.overview}
        />
        <StatCard
          title="Avg Market Price"
          value={overview ? formatCurrency(overview.avgPrice) : "—"}
          change={overview?.priceChange}
          icon={<TrendingUp className="w-6 h-6" />}
          color="accent"
          loading={loading.overview}
        />
        <StatCard
          title="Total Volume (MT)"
          value={overview ? formatNumber(overview.totalVolume) : "—"}
          icon={<BarChart2 className="w-6 h-6" />}
          color="gray"
          loading={loading.overview}
        />
      </div>

      {/* Trend chart */}
      <div className="mb-6">
        <TrendChart
          data={trendData}
          commodities={["Tomato", "Paddy", "Cotton"]}
          loading={loading.trends}
        />
      </div>

      {/* Bottom row: top commodities + market clusters */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopCommodities commodities={topCommodities} loading={loading.commodities} />
        <MarketClusters clusters={clusters} loading={loading.clusters} />
      </div>
    </Layout>
  );
}
