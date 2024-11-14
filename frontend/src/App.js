import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AskQuestion from "./Components/AskQuestion";
import Navbar from "./Components/Navbar";
import "./App.css";

function App() {

  return (
      <div className="App">
        <Navbar />
        <AskQuestion />  
      </div>
  );
}


export default App;
