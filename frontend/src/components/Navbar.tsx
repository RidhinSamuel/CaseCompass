import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { logout } from '../features/authSlice';
import { Compass, FileText, Search, LayoutDashboard, LogOut, User, Settings } from 'lucide-react';

export const Navbar: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="glass-panel" style={{ borderRadius: '0 0 16px 16px', marginBottom: '2rem', padding: '0.75rem 2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1200px', margin: '0 auto' }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none', color: '#fff' }}>
          <div style={{ background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', padding: '0.5rem', borderRadius: '10px', display: 'flex' }}>
            <Compass size={24} color="#fff" />
          </div>
          <span style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
            Case<span style={{ color: '#60a5fa' }}>Compass</span>
          </span>
        </Link>

        {isAuthenticated ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Link to="/dashboard" className={isActive('/dashboard') ? 'btn-primary' : 'btn-secondary'} style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>
                <LayoutDashboard size={16} /> Dashboard
              </Link>
              <Link to="/documents" className={isActive('/documents') ? 'btn-primary' : 'btn-secondary'} style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>
                <FileText size={16} /> Documents
              </Link>
              <Link to="/search" className={isActive('/search') ? 'btn-primary' : 'btn-secondary'} style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>
                <Search size={16} /> AI Search
              </Link>
              <Link to="/settings" className={isActive('/settings') ? 'btn-primary' : 'btn-secondary'} style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>
                <Settings size={16} /> Settings
              </Link>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', borderLeft: '1px solid var(--border-color)', paddingLeft: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                <User size={16} color="#60a5fa" />
                <span>{user?.full_name || user?.email || 'User'}</span>
              </div>
              <button onClick={handleLogout} className="btn-secondary" style={{ padding: '0.5rem 0.75rem', fontSize: '0.85rem' }} title="Logout">
                <LogOut size={16} />
              </button>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link to="/login" className="btn-secondary">Login</Link>
            <Link to="/register" className="btn-primary">Register</Link>
          </div>
        )}
      </div>
    </nav>
  );
};
