import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from './HomePage';

// Mock QueryForm component
vi.mock('../components/QueryForm', () => ({
  default: () => <div data-testid="query-form">Query Form</div>,
}));

describe('HomePage', () => {
  const renderHomePage = () => {
    return render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
  };

  it('renders hero section with title', () => {
    renderHomePage();
    expect(screen.getByText(/competitive intelligence/i)).toBeInTheDocument();
    expect(screen.getByText(/made simple/i)).toBeInTheDocument();
  });

  it('renders query form', () => {
    renderHomePage();
    expect(screen.getByTestId('query-form')).toBeInTheDocument();
  });

  it('renders features section', () => {
    renderHomePage();
    expect(screen.getByText(/why choose us/i)).toBeInTheDocument();
    expect(screen.getByText(/powerful features/i)).toBeInTheDocument();
  });

  it('renders analyze competitors button', () => {
    renderHomePage();
    const button = screen.getByRole('link', { name: /analyze competitors/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute('href', '#form');
  });
});

