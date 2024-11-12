import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import UploadPDF from "./Components/UploadPDF";
import AskQuestion from "./Components/AskQuestion";
import Navbar from "./Components/Navbar";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<UploadPDF />} />
          <Route path="/ask" element={<AskQuestion />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
