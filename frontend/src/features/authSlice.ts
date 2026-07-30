import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  created_at: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
}

const initialToken = localStorage.getItem('token');

const initialState: AuthState = {
  token: initialToken,
  user: null,
  isAuthenticated: !!initialToken,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ token: string; user?: User }>
    ) => {
      state.token = action.payload.token;
      state.isAuthenticated = true;
      if (action.payload.user) {
        state.user = action.payload.user;
      }
      localStorage.setItem('token', action.payload.token);
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    logout: (state) => {
      state.token = null;
      state.user = null;
      state.isAuthenticated = false;
      localStorage.removeItem('token');
    },
  },
});

export const { setCredentials, setUser, logout } = authSlice.actions;
export default authSlice.reducer;
