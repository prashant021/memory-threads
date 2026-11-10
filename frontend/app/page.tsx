"use client"
import { useState } from 'react'
import FamilyUpload from '@/components/FamilyUpload'
import VisitorScan from '@/components/VisitorScan'
import { motion, AnimatePresence } from 'framer-motion'
import { Camera, ImagePlus } from 'lucide-react'

export default function Home() {
  const [mode, setMode] = useState<'selection' | 'family' | 'visitor'>('selection')

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 md:p-24 relative overflow-hidden">
      
      {/* Subtle dynamic background gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-neutral-800/20 via-neutral-900 to-black z-0" />
      
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm leading-6 relative">
        <AnimatePresence mode="wait">
          {mode === 'selection' && (
            <motion.div 
              key="selection"
              initial={{opacity: 0, y: 20}}
              animate={{opacity: 1, y: 0}}
              exit={{opacity: 0, y: -20}}
              className="text-center"
            >
              <h1 className="text-4xl md:text-6xl font-light mb-8 tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-gray-200 to-gray-500">
                Memory Threads
              </h1>
              <p className="text-neutral-400 mb-4 text-lg">Shared memories, brought together.</p>
              <p className="text-neutral-500 mb-16 text-sm">Choose a portal to proceed.</p>
              
              <div className="flex flex-col md:flex-row gap-6 justify-center">
                <button 
                  onClick={() => setMode('family')}
                  className="group relative flex flex-col items-center justify-center gap-4 border border-neutral-800 bg-neutral-900/50 p-12 rounded-2xl hover:border-neutral-500 transition-all duration-500 overflow-hidden"
                >
                  <div className="absolute inset-0 bg-white/5 translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-out" />
                  <ImagePlus size={48} className="text-neutral-400 group-hover:text-white transition-colors" />
                  <span className="text-xl font-medium tracking-wide">Family Upload</span>
                  <span className="text-xs text-neutral-500">Add cherished memories</span>
                </button>
                
                <button 
                  onClick={() => setMode('visitor')}
                  className="group relative flex flex-col items-center justify-center gap-4 border border-neutral-800 bg-neutral-900/50 p-12 rounded-2xl hover:border-neutral-500 transition-all duration-500 overflow-hidden"
                >
                  <div className="absolute inset-0 bg-white/5 translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-out" />
                  <Camera size={48} className="text-neutral-400 group-hover:text-white transition-colors" />
                  <span className="text-xl font-medium tracking-wide">Visitor Scan</span>
                  <span className="text-xs text-neutral-500">Find shared moments</span>
                </button>
              </div>
            </motion.div>
          )}

          {mode === 'family' && (
             <motion.div key="family" initial={{opacity: 0, x: 20}} animate={{opacity: 1, x: 0}}>
                <button onClick={() => setMode('selection')} className="mb-8 text-neutral-400 hover:text-white transition-colors uppercase text-xs tracking-widest flex items-center gap-2">
                  &larr; Back
                </button>
                <FamilyUpload />
             </motion.div>
          )}

          {mode === 'visitor' && (
             <motion.div key="visitor" initial={{opacity: 0, x: -20}} animate={{opacity: 1, x: 0}}>
                <button onClick={() => setMode('selection')} className="mb-8 text-neutral-400 hover:text-white transition-colors uppercase text-xs tracking-widest flex items-center gap-2">
                  &larr; Back
                </button>
                <VisitorScan />
             </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  )
}
