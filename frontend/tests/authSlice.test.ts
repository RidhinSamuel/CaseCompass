import { describe, it, expect } from 'vitest';
import authReducer, { logout, setCredentials } from '../src/features/authSlice';

describe('authSlice', () => {
  it('stores the token on login and clears it on logout', () => {
    let state = authReducer(undefined, setCredentials({ token: 'abc' }));
    expect(state.isAuthenticated).toBe(true);
    expect(state.token).toBe('abc');
    expect(localStorage.getItem('token')).toBe('abc');

    state = authReducer(state, logout());
    expect(state.isAuthenticated).toBe(false);
    expect(state.token).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });
});
