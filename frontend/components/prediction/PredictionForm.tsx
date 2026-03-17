'use client';
// Form component for crop price prediction
import React, { useState, useEffect } from "react";
import { Commodity, Market, District, PredictionFormState, SelectOption } from "@/types";
import { getCommodities, getMarkets, getDistricts } from "@/services/api";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import { Search } from "lucide-react";

interface PredictionFormProps {
  onSubmit: (data: PredictionFormState) => Promise<void>;
  loading?: boolean;
}

const currentYear = new Date().getFullYear();
const months: SelectOption[] = [
  { value: "1", label: "January" },
  { value: "2", label: "February" },
  { value: "3", label: "March" },
  { value: "4", label: "April" },
  { value: "5", label: "May" },
  { value: "6", label: "June" },
  { value: "7", label: "July" },
  { value: "8", label: "August" },
  { value: "9", label: "September" },
  { value: "10", label: "October" },
  { value: "11", label: "November" },
  { value: "12", label: "December" },
];

const years: SelectOption[] = Array.from({ length: 5 }, (_, i) => ({
  value: String(currentYear + i),
  label: String(currentYear + i),
}));

export default function PredictionForm({ onSubmit, loading = false }: PredictionFormProps) {
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);

  const [form, setForm] = useState<PredictionFormState>({
    commodity: "",
    market: "",
    district: "",
    month: String(new Date().getMonth() + 1),
    year: String(currentYear),
  });

  const [errors, setErrors] = useState<Partial<PredictionFormState>>({});

  // Load options on mount
  useEffect(() => {
    Promise.all([getCommodities(), getMarkets(), getDistricts()]).then(([c, m, d]) => {
      setCommodities(c);
      setMarkets(m);
      setDistricts(d);
    });
  }, []);

  const handleChange = (field: keyof PredictionFormState) => (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const newErrors: Partial<PredictionFormState> = {};
    if (!form.commodity) newErrors.commodity = "Please select a commodity.";
    if (!form.month) newErrors.month = "Please select a month.";
    if (!form.year) newErrors.year = "Please select a year.";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    await onSubmit(form);
  };

  const commodityOptions: SelectOption[] = commodities.map((c) => ({
    value: c.name,
    label: `${c.name} (${c.category})`,
  }));

  const marketOptions: SelectOption[] = markets.map((m) => ({
    value: m.name,
    label: m.name,
  }));

  const districtOptions: SelectOption[] = districts.map((d) => ({
    value: d.name,
    label: `${d.name}, ${d.state}`,
  }));

  return (
    <form onSubmit={handleSubmit} noValidate aria-label="Price prediction form">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="sm:col-span-2">
          <Select
            label="Commodity *"
            options={commodityOptions}
            value={form.commodity}
            onChange={handleChange("commodity")}
            error={errors.commodity}
            disabled={loading}
          />
        </div>

        <Select
          label="Market (optional)"
          options={marketOptions}
          value={form.market}
          onChange={handleChange("market")}
          disabled={loading}
        />

        <Select
          label="District (optional)"
          options={districtOptions}
          value={form.district}
          onChange={handleChange("district")}
          disabled={loading}
        />

        <Select
          label="Month *"
          options={months}
          value={form.month}
          onChange={handleChange("month")}
          error={errors.month}
          disabled={loading}
        />

        <Select
          label="Year *"
          options={years}
          value={form.year}
          onChange={handleChange("year")}
          error={errors.year}
          disabled={loading}
        />
      </div>

      <div className="mt-6">
        <Button
          type="submit"
          size="lg"
          loading={loading}
          disabled={loading}
          icon={<Search className="w-4 h-4" />}
          className="w-full sm:w-auto"
        >
          {loading ? "Predicting..." : "Predict Price"}
        </Button>
      </div>
    </form>
  );
}
