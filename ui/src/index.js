import React from 'react';
import ReactDOM from 'react-dom/client';
import * as Sentry from '@sentry/react';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  environment: process.env.REACT_APP_SENTRY_ENVIRONMENT || 'development',
  release: process.env.REACT_APP_SENTRY_RELEASE,
  tracesSampleRate: Number(process.env.REACT_APP_SENTRY_TRACES_SAMPLE_RATE || '1.0'),
  integrations: [Sentry.browserTracingIntegration()],
  // Outgoing requests matching these get `sentry-trace` + `baggage` headers.
  // That header propagation is the ONLY thing linking a frontend trace to the
  // Flask backend trace. Remove it -> two unrelated traces (common support ticket).
  // Dev hits the CRA proxy, prod hits nginx; both are same-origin /api/*.
  tracePropagationTargets: ['localhost', /^\/api\//],
  dataCollection: {
    // Keep user data and HTTP bodies out of frontend events by default.
    userInfo: false,
    httpBodies: [],
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Sentry.ErrorBoundary fallback={<p>Something went wrong.</p>}>
      <App />
    </Sentry.ErrorBoundary>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
