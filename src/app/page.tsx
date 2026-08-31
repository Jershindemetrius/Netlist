"use client";

import React from "react";
import { useCircuitAnalysis } from "../hooks/useCircuitAnalysis";
import { CircuitUploader } from "../components/upload/CircuitUploader";
import { ImagePreview } from "../components/upload/ImagePreview";
import { AnalysisProgress } from "../components/analysis/AnalysisProgress";
import { CircuitWorkspace } from "../components/workspace/CircuitWorkspace";
import { AlertCircle, RotateCcw, Upload } from "lucide-react";

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
    <div className="min-h-screen flex flex-col font-sans">
      {/* Header matching Screenshots 1 & 2 */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-neutral-300 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Logo on Left */}
          <div className="flex items-center gap-3">
            <span className="font-sans font-black text-2xl tracking-tighter text-black">
              NETLIST
            </span>
          </div>

          {/* Status & Tagline on Right */}
          <div className="flex items-center gap-6 font-mono text-xs font-bold uppercase tracking-wider text-neutral-700">
            <span>Hand-drawn Circuit → Structured Graph</span>
            <div className="flex items-center gap-2 text-black">
              <span className="w-2.5 h-2.5 rounded-full bg-lime-500 animate-pulse shadow-sm" />
              <span>SYSTEM READY</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8">
        {/* State 1: Empty Upload State */}
        {!imagePreviewUrl && !isAnalyzing && !result && !error && (
          <CircuitUploader
            onImageSelect={handleImageSelect}
            onLoadDemo={loadDemo}
            isAnalyzing={isAnalyzing}
          />
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
          <div className="max-w-xl mx-auto my-12 bg-white border border-red-300 rounded-none p-8 shadow-sm">
            <div className="flex items-center gap-3 text-red-600 mb-4 pb-3 border-b border-red-100">
              <AlertCircle className="w-6 h-6" />
              <h3 className="font-mono text-lg font-bold">Unable to Reconstruct Circuit</h3>
            </div>

            <p className="font-mono text-xs text-neutral-800 mb-6 bg-red-50 p-4 rounded border border-red-200">
              {error}
            </p>

            <div className="flex items-center justify-end gap-3 font-mono text-xs">
              <button
                type="button"
                onClick={runAnalysis}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-black text-white font-bold rounded-none shadow"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Retry Analysis</span>
              </button>
              <button
                type="button"
                onClick={reset}
                className="inline-flex items-center gap-1.5 px-4 py-2 border border-neutral-300 hover:bg-neutral-100 font-semibold rounded-none"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Another Image</span>
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-300 py-4 px-6 bg-white text-center font-mono text-xs text-neutral-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-bold text-black">NETLIST CORE</span> — Computer Vision to Electrical Netlist Engine
          </div>
          <div className="flex items-center gap-4 text-neutral-400">
            <span>FastAPI Backend Ready</span>
            <span>•</span>
            <span>Technical Schematic Workspace</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
