import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import ForgetPassword from './components/ForgetPassword';

const App = () => {
  return (
    <div className='overflow-hidden w-full h-full relative'>
      <Router>
        <div className="h-full">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            {/* <Route path="/forget_password" element={<ForgetPassword />} /> */}
            <Route path="/" element={<Login />} />
          </Routes>
        </div>
      </Router>
    </div>
  );
};

export default App;
