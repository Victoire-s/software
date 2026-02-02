
import './App.css'
import { fetchData } from './service/routes';
import { useState } from 'react';
function App() {
  const [data, setData] = useState(null);

  const handleClick = async () => {
    const result = await fetchData();
    setData(result);
  };
  return (
    <>
      <div>
      <h1>hello world</h1>
       <button onClick={handleClick}>click me</button>
        {data && <p>Response: {JSON.stringify(data)}</p>}
      </div>
    </>
  )
}

export default App
