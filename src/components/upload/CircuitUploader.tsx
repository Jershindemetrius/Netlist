"use client";

import React, { useRef, useState } from "react";
import { Upload, FileImage, Play, Sparkles, AlertCircle } from "lucide-react";

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
        setDragError("Please drop a valid image file (PNG, JPG, JPEG, WebP).");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onImageSelect(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto my-8">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative group cursor-pointer border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 ${
          isDragOver
            ? "border-black bg-neutral-100/80 scale-[1.01]"
            : "border-neutral-300 bg-neutral-50 hover:border-black hover:bg-neutral-100/50"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png, image/jpeg, image/jpg, image/webp"
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-black text-white flex items-center justify-center shadow-md group-hover:scale-105 transition-transform duration-200">
            <Upload className="w-8 h-8" />
          </div>

          <div className="space-y-1">
            <h3 className="text-xl font-bold tracking-tight text-neutral-900">
              Drop a circuit image here
            </h3>
            <p className="text-sm text-neutral-500 font-medium">
              or <span className="text-black underline underline-offset-4 font-semibold">browse from your computer</span>
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs text-neutral-400 font-mono pt-2">
            <FileImage className="w-4 h-4" />
            <span>Supports PNG, JPG, JPEG, WebP (up to 20MB)</span>
          </div>
        </div>

        {dragError && (
          <div className="mt-4 inline-flex items-center gap-2 text-xs font-semibold text-red-600 bg-red-50 border border-red-200 px-3 py-1.5 rounded-md">
            <AlertCircle className="w-4 h-4" />
            <span>{dragError}</span>
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center justify-center gap-4">
        <span className="text-xs font-mono text-neutral-400 uppercase tracking-widest">— OR —</span>
      </div>

      <div className="mt-4 flex justify-center">
        <button
          type="button"
          onClick={onLoadDemo}
          disabled={isAnalyzing}
          className="inline-flex items-center gap-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-900 border border-neutral-300 font-mono text-sm px-5 py-2.5 rounded-lg font-semibold transition-all duration-150 shadow-sm"
        >
          <Sparkles className="w-4 h-4 text-black" />
          <span>Try Demo Circuit Diagram</span>
        </button>
      </div>
    </div>
  );
};
