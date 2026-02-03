/// <reference types="vite/client" />
import axios from "axios";

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL as string) || "/api",
});

async function fetchData() {
  try {
    const response = await api.post("/hello", { message: "hello" });

    return response.data;
  } catch (error) {
    return error;
  }
}

export { fetchData };
