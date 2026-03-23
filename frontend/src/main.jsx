import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import F1Dashboard from './F1Dashboard.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <F1Dashboard />
  </StrictMode>,
)
