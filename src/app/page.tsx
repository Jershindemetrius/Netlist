"use client";

import React, { useState } from "react";
import { useCircuitAnalysis } from "../hooks/useCircuitAnalysis";
import { CircuitUploader } from "../components/upload/CircuitUploader";
import { ImagePreview } from "../components/upload/ImagePreview";
import { AnalysisProgress } from "../components/analysis/AnalysisProgress";
import { CircuitWorkspace } from "../components/workspace/CircuitWorkspace";
import { SimplificationPanel } from "../components/workspace/SimplificationPanel";
import { ComponentList } from "../components/analysis/ComponentList";
import { NetlistPanel } from "../components/netlist/NetlistPanel";
import { DetailsPanel } from "../components/workspace/DetailsPanel";
import { CircuitGraphSearch } from "../components/graph/CircuitGraphSearch";
import { AlertCircle, RotateCcw, Upload, Cpu, Download, FileCode, FileText, Image as ImageIcon, Sliders, Zap } from "lucide-react";
import { exportCircuitJson, exportSpiceNetlist, exportReportAsPdf, exportGraphAsJpeg } from "../lib/export";

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

  const [activeTab, setActiveTab] = useState<"Workspace" | "Simplification" | "Reports" | "Debugger" | "Settings">("Workspace");

  return (
    <div className="min-h-screen flex flex-col font-sans bg-slate-50 text-slate-900" id="full-workspace-capture">
      {/* Cozy Header Matching Image 2 */}
      <header className="sticky top-0 z-50 bg-white border-b border-slate-200 px-6 py-3 shadow-2xs">
        <div className="max-w-[1700px] mx-auto flex flex-wrap items-center justify-between gap-4">
          {/* Logo on Left */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-xs">
              N
            </div>
            <div>
              <span className="font-extrabold text-lg tracking-tight text-slate-900 leading-none block">
                NETLIST
              </span>
              <span className="text-[11px] text-slate-400 font-medium">
                Intelligent Circuit Graph Analyzer
              </span>
            </div>
          </div>

          {/* Dedicated Section Tabs */}
          <div className="hidden md:flex items-center gap-1 text-xs font-semibold bg-slate-100 p-1 rounded-2xl border border-slate-200">
            {(["Workspace", "Simplification", "Reports", "Debugger", "Settings"] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-xl transition-all cursor-pointer ${
                  activeTab === tab
                    ? "bg-white text-slate-900 shadow-2xs font-bold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Top Right Action & Export Menu */}
          <div className="flex items-center gap-2.5 text-xs font-semibold">
            <div className="flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-[11px]">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>System Ready</span>
            </div>

            {result && (
              <>
                <button
                  type="button"
                  onClick={() => exportReportAsPdf("full-workspace-capture")}
                  className="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-xl transition-colors flex items-center gap-1.5 cursor-pointer shadow-2xs"
                  title="Export Analysis Report as PDF"
                >
                  <FileText className="w-3.5 h-3.5 text-indigo-600" />
                  <span>PDF</span>
                </button>

                <button
                  type="button"
                  onClick={() => exportGraphAsJpeg("full-workspace-capture")}
                  className="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-xl transition-colors flex items-center gap-1.5 cursor-pointer shadow-2xs"
                  title="Export Circuit Graph as JPEG"
                >
                  <ImageIcon className="w-3.5 h-3.5 text-emerald-600" />
                  <span>JPEG</span>
                </button>

                <button
                  type="button"
                  onClick={() => exportSpiceNetlist(result)}
                  className="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-xl transition-colors flex items-center gap-1.5 cursor-pointer shadow-2xs"
                  title="Export SPICE Netlist (.cir)"
                >
                  <Download className="w-3.5 h-3.5 text-slate-500" />
                  <span>SPICE</span>
                </button>
              </>
            )}

            <button
              type="button"
              onClick={reset}
              className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl transition-colors flex items-center gap-1.5 cursor-pointer shadow-2xs"
            >
              <span>New Analysis</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Workspace Container */}
      <main className="flex-1 max-w-[1700px] w-full mx-auto p-4 md:p-6">
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

        {/* State 4: Results Workspace Tab Router */}
        {result && imagePreviewUrl && !isAnalyzing && (
          <>
            {/* Section 1: Main Workspace */}
            {activeTab === "Workspace" && (
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

            {/* Section 2: Dedicated Circuit Simplification View */}
            {activeTab === "Simplification" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                  <div>
                    <h2 className="text-xl font-bold text-slate-900">Circuit Simplification Engine (Beta)</h2>
                    <p className="text-xs text-slate-500">Automated topological equivalence reduction for series/parallel component subgraphs.</p>
                  </div>
                  <span className="bg-indigo-50 text-indigo-700 font-bold px-3 py-1 rounded-full text-xs">
                    {result.components.length} Original Components
                  </span>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <SimplificationPanel />
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col justify-between">
                    <h3 className="font-bold text-slate-900 text-sm mb-3">Reducible Component Subgraphs</h3>
                    <div className="space-y-3 font-mono text-xs">
                      {result.components.filter(c => c.type.includes("resistor")).map(r => (
                        <div key={r.id} className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex justify-between items-center">
                          <span className="font-bold text-slate-900">{r.id} ({r.type})</span>
                          <span className="text-indigo-600 font-bold">{r.value || "10kΩ"}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Section 3: Dedicated Component & SPICE Netlist Reports View */}
            {activeTab === "Reports" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                  <div>
                    <h2 className="text-xl font-bold text-slate-900">Component & Netlist Inspection Reports</h2>
                    <p className="text-xs text-slate-500">Full tabular component list and simulation-ready SPICE netlist text.</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <ComponentList
                    components={result.components}
                    selection={selection}
                    onSelectComponent={selectComponent}
                    onSelectNet={selectNet}
                  />
                  <NetlistPanel
                    data={result}
                    selection={selection}
                    onSelectNet={selectNet}
                    onSelectTerminal={selectTerminal}
                    onSelectComponent={selectComponent}
                  />
                </div>
              </div>
            )}

            {/* Section 4: Interactive Graph Debugger View */}
            {activeTab === "Debugger" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                  <div>
                    <h2 className="text-xl font-bold text-slate-900">Interactive Circuit Graph Debugger & AI Search</h2>
                    <p className="text-xs text-slate-500">Run real-time graph traversal (BFS / Shortest Path) between components and inspect terminal assignments.</p>
                  </div>
                </div>

                <CircuitGraphSearch
                  data={result}
                  onSelectComponent={selectComponent}
                  onSelectNet={selectNet}
                />

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2">
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
                  </div>
                  <div className="lg:col-span-1">
                    <DetailsPanel
                      selection={selection}
                      components={result.components}
                      onFocusImage={selectComponent}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Section 5: Settings View */}
            {activeTab === "Settings" && (
              <div className="max-w-2xl mx-auto bg-white border border-slate-200 rounded-2xl p-8 shadow-xs space-y-6">
                <h2 className="text-xl font-bold text-slate-900 pb-3 border-b border-slate-200">System Configuration & Model Settings</h2>
                <div className="space-y-4 text-xs font-sans">
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="font-semibold text-slate-700">Active YOLO Checkpoint</span>
                    <span className="font-mono bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-md font-bold">models/checkpoints/best.pt (5 Epochs)</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="font-semibold text-slate-700">Detection Threshold</span>
                    <span className="font-mono text-slate-900 font-bold">conf = 0.10, iou = 0.45</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="font-semibold text-slate-700">High Confidence Threshold</span>
                    <span className="font-mono text-emerald-600 font-bold">≥ 0.90</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="font-semibold text-slate-700">Medium Confidence Threshold</span>
                    <span className="font-mono text-amber-600 font-bold">0.70 - 0.89</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="font-semibold text-slate-700">Low Confidence Threshold</span>
                    <span className="font-mono text-rose-600 font-bold">&lt; 0.70 (Tagged as Warning)</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* State 5: Error State */}
        {error && (
          <div className="max-w-xl mx-auto my-12 bg-white border border-rose-200 rounded-2xl p-8 shadow-sm">
            <div className="flex items-center gap-3 text-rose-600 mb-4 pb-3 border-b border-rose-100">
              <AlertCircle className="w-6 h-6" />
              <h3 className="text-base font-bold text-slate-900">Unable to Reconstruct Circuit</h3>
            </div>

            <p className="text-xs text-slate-700 mb-6 bg-rose-50 p-4 rounded-xl border border-rose-100 font-mono">
              {error}
            </p>

            <div className="flex items-center justify-end gap-3 text-xs">
              <button
                type="button"
                onClick={runAnalysis}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 transition-colors shadow-xs"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Retry Analysis</span>
              </button>
              <button
                type="button"
                onClick={reset}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 transition-colors"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Another Image</span>
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
