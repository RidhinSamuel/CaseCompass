import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useRegisterUserMutation, useLoginUserMutation } from '../api/apiSlice';
import { useAppDispatch } from '../app/hooks';
import { setCredentials } from '../features/authSlice';
import { UserPlus, Mail, Lock, User, AlertCircle } from 'lucide-react';

export const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [registerUser, { isLoading: isRegistering }] = useRegisterUserMutation();
  const [loginUser, { isLoading: isLoggingIn }] = useLoginUserMutation();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      await registerUser({ email, password, full_name: fullName }).unwrap();
      const loginRes = await loginUser({ email, password }).unwrap();
      dispatch(setCredentials({ token: loginRes.access_token }));
      navigate('/dashboard');
    } catch (err: any) {
      setErrorMsg(err.data?.detail || 'Registration failed. Please try again.');
    }
  };

  return (
    <div style={{ maxWidth: '440px', margin: '3rem auto 0', padding: '0 1rem' }}>
      <div className="glass-panel" style={{ padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ display: 'inline-flex', padding: '0.75rem', borderRadius: '12px', background: 'rgba(139, 92, 246, 0.1)', marginBottom: '1rem' }}>
            <UserPlus size={32} color="#c084fc" />
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Create Account</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Join Case Compass for user-isolated AI legal research.</p>
        </div>

        {errorMsg && (
          <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '0.75rem 1rem', color: '#fca5a5', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Full Name</label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                required
                className="input-field"
                placeholder="Adv. Ridhin Samuel"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                style={{ paddingLeft: '2.5rem' }}
              />
              <User size={18} color="#94a3b8" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Email Address</label>
            <div style={{ position: 'relative' }}>
              <input
                type="email"
                required
                className="input-field"
                placeholder="advocate@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ paddingLeft: '2.5rem' }}
              />
              <Mail size={18} color="#94a3b8" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Password</label>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                required
                minLength={8}
                className="input-field"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ paddingLeft: '2.5rem' }}
              />
              <Lock size={18} color="#94a3b8" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
          </div>

          <button type="submit" disabled={isRegistering || isLoggingIn} className="btn-primary" style={{ marginTop: '0.5rem', justifyContent: 'center', padding: '0.8rem' }}>
            {isRegistering || isLoggingIn ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: '#60a5fa', textDecoration: 'none', fontWeight: 500 }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};
