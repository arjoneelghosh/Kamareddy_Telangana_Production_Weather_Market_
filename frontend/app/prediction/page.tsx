'use client';
// Price Prediction page
import React, { useState } from "react";
import Layout from "@/components/layout/Layout";
import Card from "@/components/ui/Card";
import PredictionForm from "@/components/prediction/PredictionForm";
import PredictionResult from "@/components/prediction/PredictionResult";
import { predictPrice } from "@/services/api";
import { PredictPriceResponse, PredictionFormState } from "@/types";
import { AlertCircle } from "lucide-react";

export default function PredictionPage() {
  const [result, setResult] = useState<PredictPriceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: PredictionFormState) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await predictPrice({
        commodity: data.commodity,
        market: data.market || undefined,
        district: data.district || undefined,
        month: data.month ? Number(data.month) : undefined,
        year: data.year ? Number(data.year) : undefined,
      });
      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to get prediction. Please check your connection and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout
      title="Price Prediction"
      subtitle="AI-powered agricultural price forecasting"
    >
      <div className="max-w-4xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Form */}
          <Card title="Prediction Parameters" subtitle="Fill in the details to get a price prediction">
            <PredictionForm onSubmit={handleSubmit} loading={loading} />
          </Card>

          {/* Result / placeholder */}
          <div>
            {error && (
              <Card>
                <div className="flex items-start gap-3 text-red-700">
                  <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-sm">Prediction Failed</p>
                    <p className="text-sm mt-1">{error}</p>
                  </div>
                </div>
              </Card>
            )}

            {result && (
              <Card title="Prediction Result">
                <PredictionResult result={result} />
              </Card>
            )}

            {!result && !error && (
              <Card>
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="w-16 h-16 bg-primary-50 rounded-full flex items-center justify-center mb-4">
                    <span className="text-3xl">🌾</span>
                  </div>
                  <p className="font-medium text-gray-700 mb-1">Ready to Predict</p>
                  <p className="text-sm text-gray-500">
                    Fill in the form and click &quot;Predict Price&quot; to get an AI-powered price forecast.
                  </p>
                </div>
              </Card>
            )}

            {/* Info card */}
            <div className="mt-4 bg-secondary-50 border border-secondary-100 rounded-xl p-4">
              <h4 className="text-sm font-semibold text-secondary-800 mb-2">How it works</h4>
              <ul className="text-xs text-secondary-700 space-y-1">
                <li>• Select a commodity and optional market/district</li>
                <li>• Choose the target month and year</li>
                <li>• Our AI model analyzes historical patterns</li>
                <li>• Get a price prediction with confidence score</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
