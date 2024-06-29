import axios from 'axios';

const API_URL = 'http://192.168.1.14:5000/api';

export const addToQueue = (url, channel) => {
  return axios.post(`${API_URL}/add-to-queue`, { url, channel });
};
