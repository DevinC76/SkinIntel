import React from "react";
import { NavLink } from "react-router-dom";
import "./Header.css";

const Header = () => {
  return (
    <header className="header">
      <div className="logo">
        <NavLink to="/" className="logo-link">Skintel</NavLink>
      </div>
      <nav className="nav-links">
        <NavLink to="/scan" className={({ isActive }) => isActive ? "active-link" : ""}>Scan</NavLink>
        <NavLink to="/data" className={({ isActive }) => isActive ? "active-link" : ""}>Data</NavLink>
        <NavLink to="/routine" className={({ isActive }) => isActive ? "active-link" : ""}>Routine</NavLink>
        <NavLink to="/info" className={({ isActive }) => isActive ? "active-link" : ""}>Info</NavLink>
        <NavLink to="/settings" className={({ isActive }) => isActive ? "active-link" : ""}>Personal Settings</NavLink>
      </nav>
    </header>
  );
};

export default Header;
