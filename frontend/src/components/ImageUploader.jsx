import React, { useState, useRef } from "react";
import { UploadCloud, Image as ImageIcon, X, Sliders, CheckCircle2 } from "lucide-react";

const SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"];
const STRATEGY_OPTIONS = [
  { id: "standard", label: "Standard", desc: "Adaptive enhancement & noise reduction" },
  { id: "grayscale_clahe", label: "Grayscale + CLAHE", desc: "Local contrast equalization" },
  { id: "binarized", label: "Binarized", desc: "Otsu thresholding for high contrast" },
  { id: "raw", label: "Raw", desc: "Original direct image input" },
];

export default function ImageUploader({
  selectedFile,
  onFileSelect,
  onFileRemove,
  onFileError,
  strategy,
  onStrategyChange,
  disabled,
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file) => {
    if (!file) return;

    if (file.size === 0) {
      if (onFileError) onFileError("Selected file is empty (0 bytes).");
      return;
    }

    const MAX_SIZE = 20 * 1024 * 1024; // 20 MB
    if (file.size > MAX_SIZE) {
      if (onFileError) {
        onFileError(`File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds maximum allowed limit of 20 MB.`);
      }
      return;
    }

    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!SUPPORTED_EXTENSIONS.includes(ext)) {
      if (onFileError) {
        onFileError(`Unsupported file format. Please upload: ${SUPPORTED_EXTENSIONS.join(", ")}`);
      }
      return;
    }

    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    onFileSelect(file);
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    onFileRemove();
  };

  return (
    <div className="upload-section">
      <div
        className={`dropzone ${isDragging ? "dropzone-dragging" : ""} ${selectedFile ? "dropzone-has-file" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !selectedFile && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={SUPPORTED_EXTENSIONS.join(",")}
          onChange={handleFileChange}
          className="hidden"
          disabled={disabled}
        />

        {!selectedFile ? (
          <div className="dropzone-empty">
            <div className="dropzone-icon-circle">
              <UploadCloud className="w-8 h-8 text-cyan-400" />
            </div>
            <h3 className="dropzone-title">Upload Packaged Product Image</h3>
            <p className="dropzone-subtitle">
              Drag & drop package label image or <span className="text-cyan-400 font-semibold underline">browse files</span>
            </p>
            <div className="dropzone-badges">
              <span className="filetype-badge">JPG</span>
              <span className="filetype-badge">PNG</span>
              <span className="filetype-badge">WEBP</span>
              <span className="filetype-badge">BMP</span>
              <span className="filetype-badge">TIFF</span>
            </div>
          </div>
        ) : (
          <div className="dropzone-preview-container">
            <div className="preview-image-wrapper">
              <img src={previewUrl} alt="Product package preview" className="preview-image" />
              {!disabled && (
                <button
                  type="button"
                  onClick={handleRemove}
                  className="preview-remove-btn"
                  title="Remove image"
                >
                  <X className="w-4 h-4 text-white" />
                </button>
              )}
            </div>

            <div className="preview-meta">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold text-slate-100 truncate max-w-[280px]">
                  {selectedFile.name}
                </span>
              </div>
              <span className="text-xs text-slate-400">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • {selectedFile.type || "Image"}
              </span>

              {!disabled && (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-xs text-cyan-400 hover:text-cyan-300 underline mt-2 block"
                >
                  Change image
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Preprocessing Strategy Selector */}
      <div className="strategy-selector-card">
        <div className="flex items-center gap-2 mb-3">
          <Sliders className="w-4 h-4 text-cyan-400" />
          <h4 className="text-sm font-semibold text-slate-200">
            Image Preprocessing Strategy
          </h4>
        </div>
        <div className="strategy-grid">
          {STRATEGY_OPTIONS.map((opt) => (
            <label
              key={opt.id}
              className={`strategy-option ${strategy === opt.id ? "strategy-option-selected" : ""}`}
            >
              <input
                type="radio"
                name="preprocessing_strategy"
                value={opt.id}
                checked={strategy === opt.id}
                onChange={(e) => onStrategyChange(e.target.value)}
                disabled={disabled}
                className="hidden"
              />
              <div className="font-medium text-xs text-slate-100">{opt.label}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">{opt.desc}</div>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
