"use client";

import React, { useRef, useState } from "react";
import { Upload, FileImage, Sparkles, AlertCircle, ArrowRight } from "lucide-react";

interface CircuitUploaderProps {
  onImageSelect: (file: File) => void;
  onLoadDemo: () => void;
  isAnalyzing: boolean;
}

export const CircuitUploader: React.FC<CircuitUploaderProps> = ({
  onImageSelect,
  onLoadDemo,
  isAnalyzing,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [dragError, setDragError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    setDragError(null);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type.startsWith("image/")) {
        onImageSelect(file);
      } else {
        setDragError("Please upload a valid image file (PNG, JPG, JPEG, WebP).");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onImageSelect(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto my-8">
      {/* Outer Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-8 md:p-12 shadow-xs text-center">
        {/* Model Spec Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-indigo-50 border border-indigo-100 text-indigo-700 rounded-full text-xs font-semibold mb-6">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Active Model: Custom Trained YOLO11s (5 Epochs • Batch 30)</span>
        </div>

        <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-slate-900 mb-4">
          Convert Circuit Diagrams into Graph & SPICE
        </h1>

        <p className="max-w-2xl mx-auto text-sm text-slate-600 mb-8 leading-relaxed">
          Upload a photograph of a hand-drawn electronic schematic. NETLIST detects components, terminals, and net topologies, generating a canonical graph and simulation netlist in real-time.
        </p>

        {/* Drag & Drop Container */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative cursor-pointer border-2 border-dashed rounded-2xl p-10 transition-all duration-200 group ${
            isDragOver
              ? "bg-indigo-50/50 border-indigo-500 shadow-md"
              : "bg-slate-50/80 border-slate-300 hover:bg-slate-100/70 hover:border-slate-400"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png, image/jpeg, image/jpg, image/webp"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="flex flex-col items-center justify-center py-6">
            <div className="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mb-5 text-indigo-600 group-hover:scale-110 transition-transform shadow-xs">
              <Upload className="w-8 h-8" />
            </div>

            <span className="text-base font-semibold text-slate-900 mb-1">
              Drag & Drop Circuit Photograph Here
            </span>
            <span className="text-xs text-slate-500">
              Supports PNG, JPG, JPEG, or WebP schematic images
            </span>
          </div>
        </div>

        {dragError && (
          <div className="mt-4 inline-flex items-center gap-2 text-xs font-semibold text-rose-600 bg-rose-50 border border-rose-200 px-3.5 py-2 rounded-xl">
            <AlertCircle className="w-4 h-4" />
            <span>{dragError}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isAnalyzing}
            className="bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm px-7 py-3 rounded-xl shadow-xs transition-all flex items-center gap-2 cursor-pointer"
          >
            <span>Upload Circuit Image</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={onLoadDemo}
            disabled={isAnalyzing}
            className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 font-semibold text-sm px-7 py-3 rounded-xl shadow-2xs transition-all cursor-pointer"
          >
            Load Sample Schematic
          </button>
        </div>
      </div>
    </div>
  );
};
