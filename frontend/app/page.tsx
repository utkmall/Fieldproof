"use client";

import { useState } from "react";
import { AlertCircle, ShieldAlert, ChevronRight, Activity, MapPin, Calendar, Database } from "lucide-react";

export default function RiskEngineDashboard() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // START EMPTY
  const [formData, setFormData] = useState({
    district: "",
    crop: "",
    season: "",
    lat: "",
    lon: "",
    observation_start_date: "",
    assessment_date: "",
  });

  const runAssessment = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); 
    setError(null); 
    setResult(null);

    // STRICT FRONTEND VALIDATION
    if (!formData.district || !formData.crop || !formData.season || !formData.lat || !formData.lon || !formData.observation_start_date || !formData.assessment_date) {
        setError("All fields are required. Please enter the complete assessment context.");
        setLoading(false);
        return;
    }

    const parsedLat = parseFloat(formData.lat);
    const parsedLon = parseFloat(formData.lon);

    if (isNaN(parsedLat) || !isFinite(parsedLat) || isNaN(parsedLon) || !isFinite(parsedLon)) {
        setError("Latitude and Longitude must be valid finite numbers.");
        setLoading(false);
        return;
    }

    try {
      // LIVE CLOUD BACKEND URL
      const response = await fetch("https://pmfby-api-backend-production.up.railway.app/v1/plugin/assess_claim", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          lat: parsedLat,
          lon: parsedLon,
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Assessment failed.");
      }
      setResult(await response.json());
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50 text-slate-900 font-sans selection:bg-amber-100">
      <nav className="border-b border-stone-200 bg-white px-8 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-amber-600" />
          <span className="font-semibold text-sm tracking-wide uppercase">PMFBY Risk Intelligence</span>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-8 py-10 grid grid-cols-12 gap-8">
        <div className="col-span-4 space-y-6">
          <div className="bg-white border border-stone-200 shadow-sm p-6">
            <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-800 mb-6 flex items-center">
              <MapPin className="h-4 w-4 mr-2 text-amber-500" /> Assessment Parameters
            </h2>
            <form onSubmit={runAssessment} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">District</label>
                  <input type="text" placeholder="Enter district" className="w-full text-sm border-b border-stone-200 py-1 focus:outline-none bg-transparent placeholder:text-stone-300" value={formData.district} onChange={(e) => setFormData({...formData, district: e.target.value})} />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Crop Type</label>
                  <select className="w-full text-sm border-b border-stone-200 py-1 focus:outline-none bg-transparent text-slate-800" value={formData.crop} onChange={(e) => setFormData({...formData, crop: e.target.value})}>
                    <option value="" disabled>Select crop</option>
                    <option value="Wheat">Wheat</option>
                    <option value="Rice">Rice</option>
                    <option value="Soyabean">Soyabean</option>
                    <option value="Cotton">Cotton</option>
                    <option value="Maize">Maize</option>
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Season</label>
                  <select className="w-full text-sm border-b border-stone-200 py-1 focus:outline-none bg-transparent text-slate-800" value={formData.season} onChange={(e) => setFormData({...formData, season: e.target.value})}>
                    <option value="" disabled>Select season</option>
                    <option value="Kharif">Kharif</option>
                    <option value="Rabi">Rabi</option>
                    <option value="Zaid">Zaid</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Latitude</label>
                  <input type="number" step="any" placeholder="e.g. 18.5204" className="w-full text-sm border-b border-stone-200 py-1 focus:outline-none bg-transparent placeholder:text-stone-300" value={formData.lat} onChange={(e) => setFormData({...formData, lat: e.target.value})} />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Longitude</label>
                  <input type="number" step="any" placeholder="e.g. 73.8567" className="w-full text-sm border-b border-stone-200 py-1 focus:outline-none bg-transparent placeholder:text-stone-300" value={formData.lon} onChange={(e) => setFormData({...formData, lon: e.target.value})} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1 flex items-center"><Calendar className="w-3 h-3 mr-1"/> Observation Start Date</label>
                  <input type="date" className="w-full text-sm border-b border-stone-200 py-1 focus:outline-none bg-transparent text-slate-800" value={formData.observation_start_date} onChange={(e) => setFormData({...formData, observation_start_date: e.target.value})} />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1 flex items-center"><Calendar className="w-3 h-3 mr-1"/> Assessment Date</label>
                  <input type="date" className="w-full text-sm border-b border-stone-200 py-1 focus:outline-none bg-transparent text-slate-800" value={formData.assessment_date} onChange={(e) => setFormData({...formData, assessment_date: e.target.value})} />
                </div>
              </div>

              <button type="submit" disabled={loading} className="w-full mt-6 bg-slate-900 text-white text-sm font-medium py-3 px-4 hover:bg-slate-800 transition-colors flex items-center justify-center disabled:bg-slate-300">
                {loading ? "Executing Pipeline..." : "Initialize Assessment"} {!loading && <ChevronRight className="h-4 w-4 ml-2" />}
              </button>
            </form>
          </div>
        </div>

        <div className="col-span-8">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 text-sm flex items-start mb-6">
              <AlertCircle className="h-5 w-5 mr-2 mt-0.5 shrink-0" /> <span>{error}</span>
            </div>
          )}

          {result && (
            <div className="space-y-6 animate-in fade-in duration-500">
              <div className="bg-white border border-stone-200 shadow-sm p-8">
                <div className="flex justify-between items-start border-b border-stone-100 pb-6 mb-6">
                  <div>
                    <p className="text-xs font-semibold tracking-widest text-slate-400 uppercase mb-1">Operational Assessment</p>
                    <h1 className="text-2xl font-light tracking-tight text-slate-900">
                      {result.operational_assessment.action?.replace(/_/g, ' ')}
                    </h1>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-12 mb-2">
                  <div>
                    <p className="text-xs font-medium text-slate-500 mb-1">Predicted Relative Yield</p>
                    <p className="text-2xl font-light">{(result.model_assessment.predicted_relative_yield * 100).toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-slate-500 mb-1">Estimated Weather-Linked Loss</p>
                    <p className="text-2xl font-light">{result.model_assessment.estimated_weather_linked_loss_percentage}%</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-12 mt-8 pt-6 border-t border-stone-100">
                  <div>
                    <p className="text-xs font-medium text-slate-500 mb-1">Weather-Linked Loss Assessment</p>
                    <p className="text-sm font-medium mt-2">{result.model_assessment.weather_linked_loss_assessment?.replace(/_/g, ' ')}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-slate-500 mb-1">Catastrophic Failure Model</p>
                    <p className="text-sm font-medium mt-2 flex items-center text-slate-700">
                      {result.model_assessment.catastrophic_failure_detected ? (
                        <><ShieldAlert className="h-4 w-4 text-red-500 mr-1" /> Detected</>
                      ) : "Not Detected"}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-stone-100 border border-stone-200 px-6 py-4 flex flex-col space-y-2 text-xs text-slate-500">
                 <div className="flex justify-between font-medium">
                    <span className="flex items-center"><Calendar className="w-3 h-3 mr-2"/> NASA POWER Data Window: <span className="text-slate-900 ml-1">{result.processing_metadata.weather_start_date} to {result.processing_metadata.weather_end_date}</span></span>
                    <span className="flex items-center"><Database className="w-3 h-3 mr-2"/> Processing Metadata: <span className="text-slate-900 ml-1">{result.processing_metadata.processed_features} features</span></span>
                 </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}