import axios from "axios";
const API_ROOT = process.env.REACT_APP_API_ROOT || "http://localhost:5001/api";

export const fetchNews = (limit=50) => axios.post(`${API_ROOT}/fetch_news`, {limit});
export const listNews = (page=1, per=30) => axios.get(`${API_ROOT}/news`, {params:{page, per}});
export const summarize = (id) => axios.post(`${API_ROOT}/summarize/${id}`);
export const topics = (clusters=5) => axios.get(`${API_ROOT}/analytics/topics`, {params:{clusters}});
