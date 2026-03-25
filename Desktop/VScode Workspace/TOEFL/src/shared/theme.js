// TOEFL Practice — Design Tokens
// Unified TOEFL iBT exam palette

export const colors = {
  // Primary (TOEFL teal)
  primary: '#00695c',
  primaryDark: '#004d40',
  primaryLight: '#e0f2f1',
  primaryGradient: 'linear-gradient(135deg, #00695c 0%, #004d40 100%)',
  primaryShadow: 'rgba(0, 105, 92, 0.25)',

  // Layout
  bg: '#f5f5f5',
  white: '#FFFFFF',
  card: '#FFFFFF',
  cardHover: '#f0f0f0',
  inputBg: '#fafafa',

  // Text
  text: '#1a1a1a',
  textMedium: '#555',
  textMuted: '#888',
  textLight: '#aaa',

  // Borders
  border: '#ddd',
  borderLight: '#e5e5e5',

  // Feedback
  success: '#2e7d32',
  successBg: 'rgba(46, 125, 50, 0.08)',
  successBorder: 'rgba(46, 125, 50, 0.3)',
  error: '#c62828',
  errorBg: 'rgba(198, 40, 40, 0.08)',
  errorBorder: 'rgba(198, 40, 40, 0.3)',
  warning: '#e65100',

  // Exam accents
  toeflTeal: '#00695c',
  toeflTealLight: '#00897b',
  toeflRed: '#c62828',
}

export const fonts = {
  heading: "'Georgia', 'Times New Roman', serif",
  body: "'DM Sans', sans-serif",
}

export const radii = {
  sm: 6,
  md: 10,
  lg: 14,
}

export const shadows = {
  card: '0 2px 8px rgba(0, 0, 0, 0.08)',
  cardHover: '0 8px 24px rgba(0, 105, 92, 0.12)',
  button: '0 4px 16px rgba(0, 105, 92, 0.2)',
}
