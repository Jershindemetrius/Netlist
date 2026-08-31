"use client";

import React from "react";
import {
  CheckCircle2,
  Sliders,
  AlertTriangle,
  Unplug,
  Bug,
  Zap,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";

interface AnalysisSidebarProps {
  activeModule?: string;
  onSelectModule?: (module: string) => void;
}

export const AnalysisSidebar: React.FC<AnalysisSidebarProps> = ({
  activeModule = "Confidence",
  onSelectModule,
}) => {
  const pipelineSteps = [
    { label: "Image Preprocessing", status: "completed" },
    { label: "Component Detection", status: "completed" },
    { label: "Wire Tracing", status: "completed" },
    { label: "Terminal Estimation", status: "completed" },
    { label: "Graph Construction", status: "completed" },
    { label: "Graph Analysis", status: "active" },
  ];

  const modules = [
    { id: "Confidence", label: "Confidence", icon: Sliders },
    { id: "Error Detection", label: "Error Detection", icon: AlertTriangle },
    { id: "Disconnected Subcircuits", label: "Disconnected Subcircuits", icon: Unplug },
    { id: "Debugger", label: "Debugger (Visualizer)", icon: Bug },
    { id: "Simplification", label: "Simplification", icon: Zap },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 p-4 flex flex-col justify-between shrink-0 font-sans text-xs">
      <div className="space-y-6">
        {/* Analysis Pipeline */}
        <div>
          <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-3 px-2">
            Analysis Pipeline
          </h4>
          <div className="space-y-1">
            {pipelineSteps.map((step, idx) => (
              <div
                key={idx}
                className={`flex items-center justify-between px-2.5 py-1.5 rounded-lg transition-colors ${
                  step.status === "active"
                    ? "bg-indigo-50 text-indigo-700 font-semibold border border-indigo-100"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-2">
                  {step.status === "completed" ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 fill-emerald-50" />
                  ) : (
                    <span className="w-3.5 h-3.5 rounded-full border-2 border-indigo-600 bg-indigo-600" />
                  )}
                  <span>{step.label}</span>
                </div>
                <ChevronRight className="w-3.5 h-3.5 text-slate-300" />
              </div>
            ))}
          </div>
        </div>

        {/* Analysis Modules */}
        <div>
          <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-3 px-2">
            Analysis Modules
          </h4>
          <div className="space-y-1">
            {modules.map((mod) => {
              const Icon = mod.icon;
              const isActive = activeModule === mod.id;
              return (
                <button
                  key={mod.id}
                  type="button"
                  onClick={() => onSelectModule && onSelectModule(mod.id)}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-left transition-all cursor-pointer ${
                    isActive
                      ? "bg-indigo-600 text-white font-semibold shadow-2xs"
                      : "text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-500"}`} />
                  <span>{mod.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Legend Box */}
      <div className="pt-4 border-t border-slate-200 space-y-2">
        <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2">
          Legend
        </h4>
        <div className="space-y-1.5 px-2 text-[11px] font-medium text-slate-600">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span>High Confidence (0.90-1.00)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            <span>Medium Confidence (0.70-0.89)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
            <span>Low Confidence (&lt;0.70)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 border-b-2 border-dashed border-amber-500 inline-block h-0" />
            <span>Uncertain / Possible Error</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-600 flex items-center justify-center text-white text-[8px] font-bold">
              !
            </span>
            <span>Confirmed Error</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
