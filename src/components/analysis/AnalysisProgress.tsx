"use client";

import React from "react";
import { CheckCircle2, Loader2, Clock, Cpu, Sparkles } from "lucide-react";
import { ProcessingStep } from "../../lib/types";

interface AnalysisProgressProps {
  steps: ProcessingStep[];
  currentStep: number;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ steps, currentStep }) => {
  const activeStepNum = currentStep || 1;
  const progressPercent = Math.min(100, Math.round((activeStepNum / steps.length) * 100));

  return (
    <div className="w-full max-w-5xl mx-auto my-8 space-y-6">
      {/* Header section */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-600 text-xs font-semibold uppercase tracking-wider mb-1">
            <Cpu className="w-4 h-4 animate-spin text-indigo-600" />
            <span>Real-Time CV Pipeline Executing</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Analyzing Circuit Diagram
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Running YOLO11 symbol localization, terminal estimation, skeleton wire tracing, and net graph reconstruction.
          </p>
        </div>

        {/* Overall Progress Bar Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-2xs min-w-[220px]">
          <div className="flex items-center justify-between text-xs font-bold text-slate-900 mb-2">
            <span>Processing</span>
            <span className="text-indigo-600">{progressPercent}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* 2-Column Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Numbered Step List */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl divide-y divide-slate-100 shadow-xs overflow-hidden">
          {steps.map((step) => {
            const isCompleted = step.status === "completed" || step.id < activeStepNum;
            const isProcessing = step.status === "processing" || step.id === activeStepNum;
            const stepNumberStr = step.id < 10 ? `0${step.id}` : `${step.id}`;

            return (
              <div
                key={step.id}
                className={`flex items-center justify-between px-6 py-4 transition-all duration-200 border-l-4 ${
                  isProcessing
                    ? "bg-indigo-50/70 border-l-indigo-600 font-semibold shadow-2xs"
                    : isCompleted
                    ? "bg-white border-l-emerald-500 text-slate-900"
                    : "bg-white border-l-transparent text-slate-400 opacity-60"
                }`}
              >
                <div className="flex items-center gap-4">
                  <span className="font-mono text-xs font-semibold text-slate-400">
                    {stepNumberStr}
                  </span>
                  <div>
                    <span
                      className={`text-sm font-semibold block ${
                        isProcessing
                          ? "text-indigo-900"
                          : isCompleted
                          ? "text-slate-800"
                          : "text-slate-400"
                      }`}
                    >
                      {step.label}
                    </span>
                    <span className="text-xs text-slate-500 font-normal">
                      {step.detail}
                    </span>
                  </div>
                </div>

                <div>
                  {isCompleted && (
                    <div className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shadow-2xs">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                  )}

                  {isProcessing && (
                    <div className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center animate-spin shadow-2xs">
                      <Loader2 className="w-4 h-4" />
                    </div>
                  )}

                  {!isCompleted && !isProcessing && (
                    <Clock className="w-5 h-5 text-slate-300" />
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Live Status Box */}
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col items-center justify-center min-h-[380px]">
          <div className="w-full flex items-center justify-between text-xs font-semibold text-slate-400 tracking-wider mb-6">
            <span>LIVE ANALYSIS STATUS</span>
            <span className="inline-flex items-center gap-1.5 text-indigo-600 font-bold bg-indigo-50 px-2.5 py-1 rounded-full text-[11px]">
              <Sparkles className="w-3.5 h-3.5 animate-spin" /> Step {activeStepNum} of {steps.length}
            </span>
          </div>

          <div className="relative w-64 h-64 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-center overflow-hidden shadow-inner">
            {/* Pulsing Vector Graph Animation */}
            <svg className="w-44 h-44 relative z-10" viewBox="0 0 100 100">
              <path
                d="M 15 65 L 35 35 L 55 75 L 85 25"
                fill="none"
                stroke="#6366f1"
                strokeWidth="4.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="animate-pulse"
              />
              <circle cx="15" cy="65" r="5" fill="#6366f1" />
              <circle cx="35" cy="35" r="5" fill="#6366f1" />
              <circle cx="55" cy="75" r="5" fill="#6366f1" />
              <circle cx="85" cy="25" r="5" fill="#6366f1" />
            </svg>
          </div>

          <div className="mt-6 text-center space-y-1">
            <p className="text-xs font-bold text-slate-900">
              {steps[activeStepNum - 1]?.label || "Processing circuit layout..."}
            </p>
            <p className="text-xs text-slate-500">
              {steps[activeStepNum - 1]?.detail || "Running model inference"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
