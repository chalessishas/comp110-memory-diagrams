import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import Layout from './Layout.jsx'
import Reading from './pages/Reading.jsx'
import Home from './pages/Home.jsx'
import Writing from './pages/Writing.jsx'
import BuildSentence from './writing/BuildSentence.jsx'
import WriteEmail from './writing/WriteEmail.jsx'
import AcademicDiscussion from './writing/AcademicDiscussion.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/reading" element={<Reading />} />
          <Route path="/writing" element={<Writing />} />
          <Route path="/writing/build-sentence" element={<BuildSentence />} />
          <Route path="/writing/email" element={<WriteEmail />} />
          <Route path="/writing/discussion" element={<AcademicDiscussion />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  </StrictMode>,
)
