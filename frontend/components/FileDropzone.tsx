import { useCallback, useRef, useState } from "react";

type Props = {
  onFiles: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
};

export default function FileDropzone({ onFiles, accept = "", multiple = true }: Props) {
  const [isOver, setIsOver] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleFiles = useCallback((flist: FileList | null) => {
    if (!flist) return;
    const files = Array.from(flist);
    onFiles(files);
  }, [onFiles]);

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsOver(true); }}
      onDragLeave={() => setIsOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsOver(false);
        handleFiles(e.dataTransfer.files);
      }}
      className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer ${isOver ? "bg-gray-100" : "bg-white"}`}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
    >
      <p className="text-sm">Arrastra y suelta archivos aquí, o <span className="underline">haz clic</span></p>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        multiple={multiple}
        accept={accept}
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}
