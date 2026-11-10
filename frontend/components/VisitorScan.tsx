import { useState, useRef, useCallback } from 'react'
import Webcam from 'react-webcam'
import { Camera, ShieldCheck, Loader2, RefreshCcw } from 'lucide-react'
import axios from 'axios'
import MemoryReel from './MemoryReel'

export default function VisitorScan() {
  const webcamRef = useRef<Webcam>(null)
  const [consentGranted, setConsentGranted] = useState(false)
  const [isScanning, setIsScanning] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [message, setMessage] = useState<string>("")
  const [capturedImage, setCapturedImage] = useState<string | null>(null)

  const handleRestart = () => {
    setCapturedImage(null)
    setResults(null)
    setMessage("")
    setIsScanning(false)
  }

  const captureAndMatch = useCallback(async () => {
    
    if (!webcamRef.current) return
    const imageSrc = webcamRef.current.getScreenshot()
    if (!imageSrc) return

    setCapturedImage(imageSrc)
    setIsScanning(true)
    setMessage("Analyzing features securely...")

    try {
      // Convert base64 to blob
      const res = await fetch(imageSrc)
      const blob = await res.blob()
      
      const formData = new FormData()
      formData.append('file', blob, 'visitor.jpg')

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/api/match`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300000, // Increased to 300s for slow local processing
      })

      setResults(response.data)
    } catch (error: any) {
      console.error(error)
      const detail = error?.response?.data?.detail || error?.message || "Connection error"
      setMessage(`error: ${detail}`)
    } finally {
      setIsScanning(false)
    }
  }, [webcamRef])


  if (results) {
    return <MemoryReel results={results} onReset={() => setResults(null)} />
  }

  if (!consentGranted) {
    return (
      <div className="flex flex-col items-center max-w-xl mx-auto p-10 bg-neutral-900/60 backdrop-blur-md rounded-3xl border border-neutral-800 shadow-2xl text-center">
        <ShieldCheck size={56} className="text-neutral-400 mb-6" />
        <h2 className="text-3xl font-light mb-4">Privacy & Consent</h2>
        <p className="text-neutral-400 leading-relaxed mb-8">
          To find shared moments quietly gathered for today, we need to scan your face.
          <br/><br/>
          <strong className="text-white font-medium">Your scan is processed instantly and never permanently stored.</strong> No synthetic or artificial elements are added to your memories.
        </p>
        <button 
          onClick={() => setConsentGranted(true)}
          className="px-8 py-4 bg-white text-black font-medium rounded-xl hover:bg-neutral-200 transition-all w-full md:w-auto"
        >
          I Understand & Consent
        </button>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center w-full max-w-3xl mx-auto">
      <div className="relative w-full aspect-video md:aspect-[4/3] rounded-3xl overflow-hidden border border-neutral-800 shadow-[0_0_50px_rgba(0,0,0,0.8)] bg-black mb-8">
        {capturedImage ? (
          <img 
            src={capturedImage} 
            className="absolute inset-0 w-full h-full object-cover" 
            alt="Captured frame"
          />
        ) : (
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            className="absolute inset-0 w-full h-full object-cover"
            mirrored={true}
          />
        )}
        
        {/* Overlay scanning UI elements */}
        <div className="absolute inset-0 border-4 border-white/10 m-8 rounded-xl pointer-events-none" />
        
        <div className="absolute bottom-8 left-0 right-0 flex flex-col items-center gap-4 z-10">
          {!results && !capturedImage && (
            <button
              onClick={captureAndMatch}
              disabled={isScanning}
              className="group relative flex items-center justify-center w-20 h-20 bg-white/20 hover:bg-white/30 backdrop-blur-xl rounded-full border border-white/50 transition-all disabled:opacity-50"
            >
              <div className="w-14 h-14 bg-white rounded-full group-hover:scale-95 transition-transform" />
            </button>
          )}

          {capturedImage && (
            <button
              onClick={handleRestart}
              className="flex items-center gap-2 px-6 py-2 bg-neutral-800/80 hover:bg-neutral-700 text-white text-xs tracking-widest uppercase rounded-full border border-neutral-700 backdrop-blur-md transition-all shadow-xl"
            >
              <RefreshCcw size={14} className={isScanning ? "animate-spin" : ""} />
              {isScanning ? "Cancel & Restart" : "Restart App"}
            </button>
          )}
        </div>
      </div>
      
      {message && (
        <p className={`text-neutral-400 tracking-wide font-light text-center max-w-sm ${isScanning ? 'animate-pulse' : ''}`}>
          {message}
        </p>
      )}
    </div>
  )
}
