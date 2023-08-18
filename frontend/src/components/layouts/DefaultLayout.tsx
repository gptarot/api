import React from 'react';
import Navbar from '../Navbar';

interface DefaultLayoutProps {
  children: string | JSX.Element | JSX.Element[];
}

const DefaultLayout: React.FC<DefaultLayoutProps> = ({ children }) => {
  return (
    <div className="bg-[#21212c] h-screen flex flex-col items-center justify-center relative">
      <div className="absolute inset-0 bg-background bg-center opacity-20" />
      <Navbar />
      {children}
    </div>
  );
};

export default DefaultLayout;
