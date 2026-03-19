import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import Reading from './pages/Reading.jsx'
import Home from './pages/Home.jsx'
import Writing from './pages/Writing.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/reading" element={<Reading />} />
        <Route path="/writing" element={<Writing />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
