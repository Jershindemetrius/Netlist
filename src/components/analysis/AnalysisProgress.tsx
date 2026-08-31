"use client";

import React from "react";
import { CheckCircle2, RefreshCw, Clock } from "lucide-react";
import { ProcessingStep } from "../../lib/types";

interface AnalysisProgressProps {
  steps: ProcessingStep[];
  currentStep: number;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ steps, currentStep }) => {
  return (
    <div className="w-full max-w-5xl mx-auto my-8 space-y-6">
      {/* Header section matching Screenshot 1 */}
      <div>
        <h1 className="text-4xl md:text-5xl font-sans font-black tracking-tight text-neutral-950 uppercase mb-2">
          ANALYZING CIRCUIT
        </h1>
        <p className="font-mono text-xs text-neutral-600 tracking-wider">
          JOB_ID: 9X4-ALF-001 &nbsp;|&nbsp; INGEST: 1024x1024 PNG &nbsp;|&nbsp; THREADS: 8
        </p>
      </div>

      {/* 2-Column Split Layout matching Screenshot 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Numbered Step List */}
        <div className="lg:col-span-7 bg-white border border-neutral-300 divide-y divide-neutral-200 shadow-sm">
          {steps.map((step) => {
            const isCompleted = step.status === "completed";
            const isProcessing = step.status === "processing";
            const stepNumberStr = step.id < 10 ? `0${step.id}` : `${step.id}`;

            return (
              <div
                key={step.id}
                className={`flex items-center justify-between px-6 py-4 transition-all duration-150 border-l-4 ${
                  isProcessing
                    ? "bg-lime-50/80 border-l-lime-500 font-bold"
                    : isCompleted
                    ? "bg-white border-l-lime-500 text-neutral-900"
                    : "bg-white border-l-transparent text-neutral-400"
                }`}
              >
                <div className="flex items-center gap-6">
                  <span className="font-mono text-xs font-bold tracking-widest text-neutral-500">
                    {stepNumberStr}
                  </span>
                  <span
                    className={`font-mono text-sm font-bold uppercase tracking-wider ${
                      isProcessing
                        ? "text-black"
                        : isCompleted
                        ? "text-neutral-900"
                        : "text-neutral-400"
                    }`}
                  >
                    {step.label}
                  </span>
                </div>

                <div>
                  {isCompleted && (
                    <div className="w-6 h-6 rounded-full bg-lime-400 text-black flex items-center justify-center shadow-sm">
                      <CheckCircle2 className="w-4 h-4 text-black fill-lime-400" />
                    </div>
                  )}

                  {isProcessing && (
                    <div className="w-6 h-6 rounded-full bg-black text-white flex items-center justify-center animate-spin">
                      <RefreshCw className="w-3.5 h-3.5" />
                    </div>
                  )}

                  {!isCompleted && !isProcessing && (
                    <Clock className="w-5 h-5 text-neutral-300" />
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: LIVE TELEMETRY Card matching Screenshot 1 */}
        <div className="lg:col-span-5 bg-neutral-100 border border-neutral-300 p-6 shadow-sm flex flex-col items-center justify-center min-h-[380px]">
          <div className="w-full text-left font-mono text-xs font-bold uppercase text-neutral-700 tracking-widest mb-6">
            LIVE TELEMETRY
          </div>

          {/* Grid Canvas Telemetry Box */}
          <div className="relative w-64 h-64 bg-white border border-neutral-300 flex items-center justify-center shadow-inner overflow-hidden">
            {/* Grid Pattern Inside Box */}
            <div
              className="absolute inset-0 opacity-20"
              style={{
                backgroundImage:
                  "linear-gradient(to right, #000 1px, transparent 1px), linear-gradient(to bottom, #000 1px, transparent 1px)",
                backgroundSize: "24px 24px",
              }}
            />

            {/* Animated Geometry Nodes Vector */}
            <svg className="w-40 h-40 relative z-10 animate-telemetry" viewBox="0 0 100 100">
              <path
                d="M 20 60 L 40 40 L 60 70 L 80 30"
                fill="none"
                stroke="#84cc16"
                strokeWidth="6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="20" cy="60" r="5" fill="#84cc16" />
              <circle cx="40" cy="40" r="5" fill="#84cc16" />
              <circle cx="60" cy="70" r="5" fill="#84cc16" />
              <circle cx="80" cy="30" r="5" fill="#84cc16" />
            </svg>
          </div>

          <div className="mt-6 text-center space-y-1">
            <p className="font-mono text-xs font-bold text-neutral-900">
              Detecting circuit geometry...
            </p>
            <p className="font-mono text-xs text-neutral-500">
              Nodes identified: <span className="font-bold text-black font-mono">12</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
