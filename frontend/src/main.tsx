import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Reset from "./pages/Reset";
import Shell from "./pages/Shell";
import Verify from "./pages/Verify";

const router = createBrowserRouter([
  { path: "/", element: <Shell /> },
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
  { path: "/verify", element: <Verify /> },
  { path: "/reset", element: <Reset /> },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
