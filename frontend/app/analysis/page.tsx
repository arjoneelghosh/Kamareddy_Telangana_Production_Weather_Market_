'use client';
// Market Analysis page
import React, { useEffect, useState, useCallback } from "react";
import Layout from "@/components/layout/Layout";
import PriceTrendChart from "@/components/charts/PriceTrendChart";
import ArrivalVsPriceChart from "@/components/charts/ArrivalVsPriceChart";
import SeasonalPatternChart from "@/components/charts/SeasonalPatternChart";
import Select from "@/components/ui/Select";
import { getPriceTrends, getSeasonalData, getArrivalData, getCommodities } from "@/services/api";
import {
  PriceTrendData,
  SeasonalData,
  ArrivalData,
  Commodity,
  SelectOption,
} from "@/types";

export default function AnalysisPage() {
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [selectedCommodity, setSelectedCommodity] = useState("Tomato");

  const [priceTrend, setPriceTrend] = useState<PriceTrendData[]>([]);
  const [seasonalData, setSeasonalData] = useState<SeasonalData[]>([]);
  const [arrivalData, setArrivalData] = useState<ArrivalData[]>([]);

  const [loadingTrend, setLoadingTrend] = useState(true);
  const [loadingSeasonal, setLoadingSeasonal] = useState(true);
  const [loadingArrival, setLoadingArrival] = useState(true);

  // Load commodity list on mount
  useEffect(() => {
    getCommodities().then(setCommodities);
  }, []);

  const loadAnalysisData = useCallback(async (commodity: string) => {
    setLoadingTrend(true);
    setLoadingSeasonal(true);
    setLoadingArrival(true);

    try {
      // Load trend data and extract single-commodity price series
      const [trendRaw, seasonal, arrival] = await Promise.all([
        getPriceTrends(commodity),
        getSeasonalData(commodity),
        getArrivalData(commodity),
      ]);

      // Convert multi-commodity trend data to single PriceTrendData[]
      const trend: PriceTrendData[] = trendRaw.map((d) => ({
        date: d.date as string,
        price: d[commodity] as number,
        commodity,
      }));

      setPriceTrend(trend);
      setSeasonalData(seasonal);
      setArrivalData(arrival);
    } catch (err) {
      console.error("Failed to load analysis data:", err);
    } finally {
      setLoadingTrend(false);
      setLoadingSeasonal(false);
      setLoadingArrival(false);
    }
  }, []);

  useEffect(() => {
    loadAnalysisData(selectedCommodity);
  }, [selectedCommodity, loadAnalysisData]);

  const commodityOptions: SelectOption[] = commodities.map((c) => ({
    value: c.name,
    label: `${c.name} (${c.category})`,
  }));

  return (
    <Layout
      title="Market Analysis"
      subtitle="Deep-dive into price trends and patterns"
      onRefresh={() => loadAnalysisData(selectedCommodity)}
    >
      {/* Filter bar */}
      <div className="flex flex-wrap items-end gap-4 mb-6 bg-white rounded-xl shadow-sm p-4">
        <div className="min-w-[200px]">
          <Select
            label="Commodity"
            options={commodityOptions}
            value={selectedCommodity}
            onChange={(e) => setSelectedCommodity(e.target.value)}
          />
        </div>
        <p className="text-xs text-gray-500 pb-1">
          Showing analysis for <strong>{selectedCommodity}</strong>
        </p>
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
        <PriceTrendChart
          data={priceTrend}
          commodity={selectedCommodity}
          loading={loadingTrend}
        />
        <ArrivalVsPriceChart data={arrivalData} loading={loadingArrival} />
      </div>

      <SeasonalPatternChart data={seasonalData} loading={loadingSeasonal} />
    </Layout>
  );
}
