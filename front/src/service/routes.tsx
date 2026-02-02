import axios from 'axios';
async function fetchData() {
  try {
    const response = await axios.post(`/test-endpoint`,"hello");

    return response.data;
  } catch (error) {
    return error;
  }
}
