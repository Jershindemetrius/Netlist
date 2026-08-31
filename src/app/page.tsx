"use client";

import React from "react";
import { useCircuitAnalysis } from "../hooks/useCircuitAnalysis";
import { CircuitUploader } from "../components/upload/CircuitUploader";
import { ImagePreview } from "../components/upload/ImagePreview";
import { AnalysisProgress } from "../components/analysis/AnalysisProgress";
import { CircuitWorkspace } from "../components/workspace/CircuitWorkspace";
import {
  Cpu,
  Zap,
  Activity,
  AlertCircle,
  RotateCcw,
  Upload,
  CheckCircle2,
  FileCode,
} from "lucide-react";

export default function HomePage() {
  const {
    imageFile,
    imagePreviewUrl,
    isAnalyzing,
    currentStep,
    processingSteps,
    result,
    error,
    selection,
    uncertainConnections,
    handleImageSelect,
    runAnalysis,
    loadDemo,
    reset,
    selectComponent,
    selectTerminal,
    selectNet,
  } = useCircuitAnalysis();

  return (
    <div className="min-h-screen flex flex-col bg-[#fafafa] text-neutral-900">
      {/* Engineering Workspace Header */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-neutral-200 px-6 py-3.5 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-black text-white flex items-center justify-center font-mono font-bold text-base shadow-sm">
              N
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-base font-black tracking-tight text-neutral-900">
                  NETLIST
                </span>
                <span className="text-[10px] font-mono font-bold bg-black text-white px-2 py-0.5 rounded uppercase tracking-wider">
                  v1.0 CV Core
                </span>
              </div>
              <p className="font-mono text-xs text-neutral-500">
                Hand-drawn Circuit → Structured Graph & SPICE Netlist
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-full font-mono text-xs font-semibold text-emerald-800">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span>System Ready</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
        {/* State 1: Empty Upload State */}
        {!imagePreviewUrl && !isAnalyzing && !result && !error && (
          <div className="py-12">
            <div className="text-center max-w-2xl mx-auto mb-8">
              <h1 className="text-3xl md:text-4xl font-mono font-bold text-neutral-900 tracking-tight mb-3">
                Circuit Vision & Graph Reconstruction Engine
              </h1>
              <p className="font-mono text-sm text-neutral-600">
                Upload a photograph or hand-drawn electronic diagram to extract components, terminal locations, wire skeletons, electrical nets, and SPICE netlists.
              </p>
            </div>

            <CircuitUploader
              onImageSelect={handleImageSelect}
              onLoadDemo={loadDemo}
              isAnalyzing={isAnalyzing}
            />
          </div>
        )}

        {/* State 2: Image Selected - Ready to Analyze */}
        {imagePreviewUrl && !isAnalyzing && !result && !error && (
          <ImagePreview
            imageUrl={imagePreviewUrl}
            file={imageFile}
            onAnalyze={runAnalysis}
            onReset={reset}
            isAnalyzing={isAnalyzing}
          />
        )}

        {/* State 3: Processing Progress State */}
        {isAnalyzing && (
          <AnalysisProgress steps={processingSteps} currentStep={currentStep} />
        )}

        {/* State 4: Results Workspace */}
        {result && imagePreviewUrl && !isAnalyzing && (
          <CircuitWorkspace
            data={result}
            imageUrl={imagePreviewUrl}
            selection={selection}
            uncertainConnections={uncertainConnections}
            onSelectComponent={selectComponent}
            onSelectTerminal={selectTerminal}
            onSelectNet={selectNet}
            onReset={reset}
          />
        )}

        {/* State 5: Error State */}
        {error && (
          <div className="max-w-xl mx-auto my-12 bg-white border border-red-200 rounded-xl p-8 shadow-sm">
            <div className="flex items-center gap-3 text-red-600 mb-4 pb-3 border-b border-red-100">
              <AlertCircle className="w-6 h-6" />
              <h3 className="font-mono text-lg font-bold">Unable to Reconstruct Circuit</h3>
            </div>

            <p className="font-mono text-xs text-neutral-700 mb-6 bg-red-50 p-4 rounded-lg border border-red-200">
              {error}
            </p>

            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={runAnalysis}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-black hover:bg-neutral-800 text-white font-mono text-xs font-bold rounded-lg shadow"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Retry Analysis</span>
              </button>
              <button
                type="button"
                onClick={reset}
                className="inline-flex items-center gap-1.5 px-4 py-2 border border-neutral-300 hover:bg-neutral-100 font-mono text-xs font-semibold rounded-lg"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Another Image</span>
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-200 py-6 px-6 bg-white text-center font-mono text-xs text-neutral-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-bold text-neutral-900">PROJECT NETLIST</span> — Computer Vision to Electrical Circuit Graph Engine
          </div>
          <div className="flex items-center gap-4 text-neutral-400">
            <span>FastAPI Backend Ready</span>
            <span>•</span>
            <span>Light Theme Developer Workspace</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
