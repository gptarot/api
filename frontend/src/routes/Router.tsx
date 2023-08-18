import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from '../pages/Home';
import Random from '../pages/Random';
import DefaultLayout from '../components/layouts/DefaultLayout';

const Router: React.FC = (): JSX.Element => {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <DefaultLayout>
              <Home />
            </DefaultLayout>
          }
        />
        <Route
          path="random"
          element={
            <DefaultLayout>
              <Random />
            </DefaultLayout>
          }
        />
        <Route
          path="/*"
          element={
            <DefaultLayout>
              <Home />
            </DefaultLayout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;
