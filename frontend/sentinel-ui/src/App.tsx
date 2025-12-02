import { useEffect, useState } from "react";
import './App.css'

function App() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/logs")
      .then(res => res.json())
      .then(json => setData(json));
  }, []);

  return (
    <>
      <h1>Sentinel UI</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </>
  );
}

export default App
