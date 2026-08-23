import React from "react";
import { Tag, Sparkles, HelpCircle } from "lucide-react";

const FIELD_LABELS = {
  product_name: "Product / Commodity Name",
  brand_name: "Brand Name",
  net_quantity: "Net Quantity",
  unit: "Standard Unit",
  mrp: "Maximum Retail Price (MRP)",
  date_of_manufacture: "Date of Manufacture (MFD)",
  expiry_date: "Expiry / Use-by Date",
  date_of_import: "Date of Import",
  batch_number: "Batch / Lot Number",
  country_of_origin: "Country of Origin",
  manufacturer_name: "Manufacturer / Packer",
  importer_name: "Importer Details",
  customer_care_details: "Customer Care / Grievance",
  food_license_number: "FSSAI License No.",
  ingredients: "Ingredients List",
  allergen_information: "Allergen Information",
  storage_instructions: "Storage Instructions",
};

export default function ExtractedFields({ extractedFields }) {
  if (!extractedFields || extractedFields.length === 0) {
    return (
      <div className="section-card">
        <div className="section-header">
          <div className="flex items-center gap-2">
            <Tag className="w-4 h-4 text-cyan-400" />
            <h3 className="section-title">Extracted Packaging Declarations</h3>
          </div>
        </div>
        <div className="p-4 text-sm text-slate-400">No packaging declarations detected.</div>
      </div>
    );
  }

  return (
    <div className="section-card">
      <div className="section-header">
        <div className="flex items-center gap-2">
          <Tag className="w-4 h-4 text-cyan-400" />
          <h3 className="section-title">Extracted Packaging Declarations</h3>
          <span className="badge-meta">{extractedFields.length} Fields Detected</span>
        </div>
      </div>

      <div className="extracted-fields-grid">
        {extractedFields.map((field, idx) => {
          const friendlyLabel = FIELD_LABELS[field.field_name] || field.field_name.replace(/_/g, " ");
          const confPercent = Math.round((field.confidence || 0.9) * 100);

          return (
            <div key={idx} className="field-card">
              <div className="field-card-header">
                <span className="field-name-label">{friendlyLabel}</span>
                <span className="field-conf-badge">{confPercent}% conf</span>
              </div>

              <div className="field-value-display">
                {field.field_value || <span className="text-slate-500 italic">Not detected</span>}
                {field.unit && <span className="field-unit-pill">{field.unit}</span>}
              </div>

              {field.source_text && (
                <div className="field-source-text" title={`Source OCR Line: ${field.source_text}`}>
                  <span className="text-slate-500 font-normal">Source: </span>
                  {field.source_text}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
