"use client";

import React from "react";
import { CheckCircle2, Loader2, Circle } from "lucide-react";
import { ProcessingStep } from "../../lib/types";

interface AnalysisProgressProps {
  steps: ProcessingStep[];
  currentStep: number;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ steps }) => {
  return (
    <div className="w-full max-w-xl mx-auto my-12 bg-white border border-neutral-200 rounded-xl p-8 shadow-sm">
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-neutral-200">
        <div className="w-3 h-3 rounded-full bg-black animate-ping" />
        <h3 className="text-lg font-mono font-bold tracking-tight text-neutral-900 uppercase">
          Analyzing Circuit Diagram
        </h3>
      </div>

      <div className="space-y-4">
        {steps.map((step) => {
          const isCompleted = step.status === "completed";
          const isProcessing = step.status === "processing";
          const isPending = step.status === "pending";

          return (
            <div
              key={step.id}
              className={`flex items-start gap-4 p-3.5 rounded-lg border transition-all duration-200 ${
                isProcessing
                  ? "bg-neutral-100 border-black shadow-sm"
                  : isCompleted
                  ? "bg-neutral-50 border-neutral-200 text-neutral-700"
                  : "bg-white border-neutral-100 text-neutral-400"
              }`}
            >
              <div className="mt-0.5">
                {isCompleted && <CheckCircle2 className="w-5 h-5 text-black" />}
                {isProcessing && <Loader2 className="w-5 h-5 text-black animate-spin" />}
                {isPending && <Circle className="w-5 h-5 text-neutral-300" />}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className={`font-mono text-sm font-bold ${isProcessing ? "text-black" : ""}`}>
                    Step {step.id}: {step.label}
                  </span>
                  <span className="font-mono text-xs text-neutral-400 uppercase">
                    {isCompleted ? "Completed" : isProcessing ? "In Progress..." : "Queued"}
                  </span>
                </div>
                <p className="font-mono text-xs text-neutral-500 mt-0.5">{step.detail}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
