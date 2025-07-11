// src/utils/getAuthHeaders.ts
export const getAuthHeaders = (role: 'admin' | 'user' = 'user') => {
  const token =
    role === 'admin'
      ? sessionStorage.getItem('adminAccessToken')
      : localStorage.getItem('accessToken');

  return {
    'ngrok-skip-browser-warning': 'true',
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};
