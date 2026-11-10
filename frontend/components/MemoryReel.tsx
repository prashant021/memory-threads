import { motion } from 'framer-motion'
import { RefreshCcw, Heart } from 'lucide-react'

interface MemoryReelProps {
  results: {
    message: string;
    collage?: string | null;
    reel?: string | null;
    count?: number;
  };
  onReset: () => void;
}

export default function MemoryReel({ results, onReset }: MemoryReelProps) {
  
  // If no match found
  if (!results.collage && !results.reel) {
    return (
      <motion.div 
        initial={{opacity: 0, scale: 0.95}} 
        animate={{opacity: 1, scale: 1}}
        className="flex flex-col items-center bg-neutral-900/50 p-12 rounded-3xl border border-neutral-800 text-center max-w-xl mx-auto"
      >
        <Heart size={48} className="text-neutral-500 mb-6" />
        <h2 className="text-2xl font-light mb-4">{results.message || "No matches found"}</h2>
        <p className="text-neutral-400 mb-8">
          The facial similarity search requires strict thresholds to prevent false positives. We couldn&apos;t reliably match your presence in the shared repository.
        </p>
        <button onClick={onReset} className="px-6 py-2 bg-neutral-800 rounded-full hover:bg-neutral-700 transition flex items-center gap-2 text-sm">
          <RefreshCcw size={16} /> Try Again
        </button>
      </motion.div>
    )
  }

  // Assuming local dev: files are stored in backend data/outputs, we might need a route to serve them.
  // For MVP UI visualization, we just display the mock data structure handling since the backend 
  // currently returns local system paths which won't load natively in the browser without a static route.
  
  return (
    <motion.div 
      initial={{opacity: 0, y: 20}} 
      animate={{opacity: 1, y: 0}}
      className="flex flex-col items-center w-full max-w-5xl mx-auto"
    >
      <div className="text-center mb-12">
        <h2 className="text-4xl font-light mb-4 text-white">Your Shared Moments</h2>
        <p className="text-neutral-400 text-lg">Found {results.count || 0} genuine memories together.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
        {/* Collage Section */}
        <div className="bg-neutral-900/30 p-6 rounded-3xl border border-neutral-800/50 flex flex-col">
          <h3 className="text-xl font-medium mb-6 text-neutral-300">Memory Grid</h3>
          <div className="flex-1 bg-black rounded-2xl overflow-hidden relative min-h-[300px] border border-neutral-800/80 group">
            {results.collage ? (
              <img 
                src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${results.collage}`} 
                alt="Shared Memories Collage" 
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center text-neutral-500">
                 <p className="text-sm">Processing...</p>
                 <p className="text-xs text-neutral-600 mt-4 italic">Collage not available</p>
              </div>
            )}
          </div>
        </div>

        {/* Video Reel Section */}
        <div className="bg-neutral-900/30 p-6 rounded-3xl border border-neutral-800/50 flex flex-col">
          <h3 className="text-xl font-medium mb-6 text-neutral-300">Video Reel</h3>
          <div className="flex-1 bg-black rounded-2xl overflow-hidden relative min-h-[300px] border border-neutral-800/80 flex items-center justify-center">
            {results.reel ? (
              <video 
                src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${results.reel}`} 
                controls 
                autoPlay
                className="max-w-full max-h-full object-contain"
              />
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center text-neutral-500">
                 <p className="text-sm">Not available</p>
                 <p className="text-xs text-neutral-600 mt-4 italic">No matching media could be stitched into a reel.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <button onClick={onReset} className="mt-16 text-neutral-500 hover:text-white transition flex items-center gap-2">
        <RefreshCcw size={16} /> Return to Portal
      </button>
    </motion.div>
  )
}
