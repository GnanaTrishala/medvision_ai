"use client";

import { motion } from "framer-motion";
import { CloudUpload, ImageIcon } from "lucide-react";
import { useCallback, useState } from "react";
import { cn } from "~/lib/utils";

export function UploadZone({
  onFile,
  disabled,
}: {
  onFile: (file: File) => void;
  disabled?: boolean;
}) {
  const [dragging, setDragging] = useState(false);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const file = files?.[0];
      if (file?.type.startsWith("image/")) onFile(file);
    },
    [onFile],
  );

  return (
    <motion.label
      layout
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      className={cn(
        "relative flex min-h-[280px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed transition-all",
        dragging
          ? "border-teal-500 bg-teal-500/5"
          : "border-border bg-muted/30 hover:border-teal-500/50 hover:bg-muted/50",
        disabled && "pointer-events-none opacity-50",
      )}
    >
      <input
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/webp"
        className="sr-only"
        disabled={disabled}
        onChange={(e) => handleFiles(e.target.files)}
      />
      <motion.div
        animate={{ y: dragging ? -4 : 0 }}
        className="flex flex-col items-center gap-3 p-8 text-center"
      >
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-600/10 text-teal-600">
          <CloudUpload className="h-7 w-7" />
        </div>
        <div>
          <p className="text-lg font-semibold">Drop chest X-ray here</p>
          <p className="mt-1 text-sm text-muted-foreground">
            or click to browse — PNG, JPEG up to 10MB
          </p>
        </div>
        <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
          <ImageIcon className="h-3.5 w-3.5" />
          DICOM support coming soon
        </div>
      </motion.div>
    </motion.label>
  );
}
