import React from "react";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar">
      <h2>PDF Q&A Application</h2>
      <ul>
        <li>
          <Link to="/">Upload PDF</Link>
        </li>
        <li>
          <Link to="/ask">Ask a Question</Link>
        </li>
      </ul>
    </nav>
  );
}

export default Navbar;
