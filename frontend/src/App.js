import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AskQuestion from "./Components/AskQuestion";
import Navbar from "./Components/Navbar";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/ask" element={<AskQuestion />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
