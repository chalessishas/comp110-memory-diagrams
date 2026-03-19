import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import Reading from './pages/Reading.jsx'
import Home from './pages/Home.jsx'
import Writing from './pages/Writing.jsx'
import BuildSentence from './writing/BuildSentence.jsx'
import WriteEmail from './writing/WriteEmail.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/reading" element={<Reading />} />
        <Route path="/writing" element={<Writing />} />
        <Route path="/writing/build-sentence" element={<BuildSentence />} />
        <Route path="/writing/email" element={<WriteEmail />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
