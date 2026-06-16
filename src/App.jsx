import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./App.css";
import Login from "./auth/Login";

const appRouter = createBrowserRouter([
  {
    path: "/",
    element: <Login />,
  },
]);

function App() {
  return (
    <>
      <RouterProvider router={appRouter} />
    </>
  );
}

export default App;
