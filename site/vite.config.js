import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Assuming this will be deployed to a repo named 'leetcode-tracker' or similar. 
  // For standard User/Org pages it might be root, but usually it's /repo-name/
  // We'll assume relative base for broader compatibility.
  base: './', 
})
