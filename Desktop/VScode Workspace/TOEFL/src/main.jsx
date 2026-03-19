import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'
import Reading from './pages/Reading.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/reading" replace />} />
        <Route path="/reading" element={<Reading />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
