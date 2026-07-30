import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Provider } from 'react-redux';
import { store } from '../src/app/store';
import App from '../src/App';

describe('Frontend App Smoke Test', () => {
  it('renders navbar brand title', () => {
    render(
      <Provider store={store}>
        <App />
      </Provider>
    );
    expect(screen.getByText('Case')).toBeDefined();
    expect(screen.getByText('Compass')).toBeDefined();
  });
});
