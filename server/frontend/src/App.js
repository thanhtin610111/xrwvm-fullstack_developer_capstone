import LoginPanel from "./components/Login/Login"
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPanel />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;