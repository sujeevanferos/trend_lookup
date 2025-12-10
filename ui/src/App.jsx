import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import NationalActivity from './pages/NationalActivity';
import OperationalEnvironment from './pages/OperationalEnvironment';
import RiskOpportunity from './pages/RiskOpportunity';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/national-activity" element={<NationalActivity />} />
          <Route path="/operational-environment" element={<OperationalEnvironment />} />
          <Route path="/risk-opportunity" element={<RiskOpportunity />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
