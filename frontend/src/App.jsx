import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import List from './pages/List';
import SingleReview from './pages/SingleReview';
import Rank from './pages/Rank';
import UserReviews from './pages/UserReviews';
import JournalReviews from './pages/JournalReviews';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/group/xiangma" replace />} />
      <Route path="/group/:groupName" element={<Layout><Home /></Layout>} />
      <Route path="/group/:groupName/all" element={<Layout><List type="all" /></Layout>} />
      <Route path="/group/:groupName/my_sharing" element={<Layout><List type="my_sharing" /></Layout>} />
      <Route path="/group/:groupName/recent" element={<Layout><List type="recent" /></Layout>} />
      <Route path="/group/:groupName/this_month" element={<Layout><List type="this_month" /></Layout>} />
      <Route path="/group/:groupName/last_month" element={<Layout><List type="last_month" /></Layout>} />
      <Route path="/group/:groupName/trash" element={<Layout><List type="trash" /></Layout>} />
      <Route path="/group/:groupName/review/:reviewId" element={<Layout><SingleReview /></Layout>} />
      <Route path="/group/:groupName/user/:userId" element={<Layout><UserReviews /></Layout>} />
      <Route path="/group/:groupName/journal/:journalName" element={<Layout><JournalReviews /></Layout>} />
      <Route path="/group/:groupName/rank" element={<Layout><Rank type="this_month" /></Layout>} />
      <Route path="/group/:groupName/rank/:rankType" element={<Layout><Rank /></Layout>} />
    </Routes>
  );
}

export default App;
