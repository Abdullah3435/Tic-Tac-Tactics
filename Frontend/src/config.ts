// Get local IP address or use a fixed one for the server
// You'll need to update this value with your actual server IP address
// This could be stored in an environment variable in production

// For development, use either:
// 1. IP address of the computer running the Flask server (e.g., "192.168.1.5:5000")
// 2. hostname if you have DNS set up (e.g., "my-server:5000")
// 3. localhost if running on same machine (e.g., "localhost:5000")

const API_BASE_URL = "http://10.20.5.165:5000"; // Replace with your actual local IP

export const config = {
  apiBaseUrl: API_BASE_URL,
};
