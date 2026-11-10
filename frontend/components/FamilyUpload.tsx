import { useState, useRef } from 'react'
import { UploadCloud, CheckCircle2, Loader2 } from 'lucide-react'
import axios from 'axios'
import { motion } from 'framer-motion'

export default function FamilyUpload() {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [success, setSuccess] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  const handleUpload = async () => {
    if (files.length === 0) return
    
    setUploading(true)
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    try {
      // In local testing, API is usually on 8000
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await axios.post(`${apiUrl}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSuccess(true)
      setFiles([])
    } catch (error) {
      console.error("Upload failed", error)
      alert("Failed to upload media. Ensure backend is running.")
    } finally {
      setUploading(false)
    }
  }

  if (success) {
    return (
      <motion.div initial={{scale: 0.9, opacity: 0}} animate={{scale: 1, opacity: 1}} className="flex flex-col items-center p-12 bg-neutral-900/40 rounded-2xl border border-green-900/30">
        <CheckCircle2 size={64} className="text-green-500 mb-6" />
        <h2 className="text-2xl font-light mb-2">Memories Uploaded</h2>
        <p className="text-neutral-400 text-center max-w-md">
          The processing pipeline is now indexing faces in the background. Visitors will soon be able to find their shared moments.
        </p>
        <button onClick={() => setSuccess(false)} className="mt-8 px-6 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-full transition-colors text-sm">
          Upload More
        </button>
      </motion.div>
    )
  }

  return (
    <div className="flex flex-col items-center w-full max-w-2xl mx-auto backdrop-blur-sm bg-neutral-900/40 p-8 md:p-12 rounded-3xl border border-neutral-800 shadow-2xl">
      <h2 className="text-3xl font-light mb-2 tracking-wide">Family Setup</h2>
      <p className="text-neutral-500 mb-8 text-center text-sm">
        Upload photos and videos containing your loved one.
      </p>

      <div 
        onClick={() => fileInputRef.current?.click()}
        className="w-full h-64 border-2 border-dashed border-neutral-700 hover:border-neutral-500 rounded-xl flex flex-col items-center justify-center cursor-pointer bg-neutral-950/50 transition-colors group mb-8"
      >
        <UploadCloud size={48} className="text-neutral-600 group-hover:text-neutral-400 mb-4 transition-colors" />
        <p className="text-neutral-400 font-medium">Click to browse files</p>
        <p className="text-xs text-neutral-600 mt-2">Supports JPG, PNG, MP4</p>
        <input 
          type="file" 
          multiple 
          accept="image/*,video/*" 
          ref={fileInputRef} 
          onChange={handleFileChange}
          onClick={(e) => e.stopPropagation()}
          className="hidden" 
        />
      </div>

      {files.length > 0 && (
        <div className="w-full mb-8">
          <p className="text-sm text-neutral-400 mb-4">{files.length} file(s) selected</p>
          <div className="flex flex-wrap gap-2">
            {files.slice(0, 5).map((f, i) => (
              <div key={i} className="px-3 py-1 bg-neutral-800 rounded text-xs text-neutral-300 truncate max-w-[150px]">
                {f.name}
              </div>
            ))}
            {files.length > 5 && <div className="px-3 py-1 text-xs text-neutral-500">+{files.length - 5} more</div>}
          </div>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={files.length === 0 || uploading}
        className="w-full py-4 bg-white text-black font-medium rounded-xl hover:bg-neutral-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all shadow-[0_0_40px_rgba(255,255,255,0.1)] hover:shadow-[0_0_60px_rgba(255,255,255,0.2)]"
      >
        {uploading ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            Processing...
          </>
        ) : (
          "Upload & Index Memories"
        )}
      </button>
    </div>
  )
}
