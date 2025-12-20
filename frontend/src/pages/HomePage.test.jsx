// Tests for the HomePage component
// Ensures hero, query form, features, and CTA button render correctly

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from './HomePage';

// Mock the QueryForm component to avoid rendering the actual form
vi.mock('../components/QueryForm', () => ({
  default: () => <div data-testid="query-form">Query Form</div>,
}));

describe('HomePage', () => {
  // Utility function to render HomePage with BrowserRouter
  const renderHomePage = () => {
    return render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
  };

  // Test if hero section renders correctly with title and subtitle
  it('renders hero section with title', () => {
    renderHomePage();

    // Check for main heading
    expect(screen.getByText(/competitive intelligence/i)).toBeInTheDocument();

    // Check for subtitle
    expect(screen.getByText(/made simple/i)).toBeInTheDocument();
  });

  // Test if the QueryForm component is rendered
  it('renders query form', () => {
    renderHomePage();

    // Check if mocked QueryForm is present
    expect(screen.getByTestId('query-form')).toBeInTheDocument();
  });

  // Test if the features section is displayed
  it('renders features section', () => {
    renderHomePage();

    // Section title
    expect(screen.getByText(/why choose us/i)).toBeInTheDocument();

    // Section subtitle
    expect(screen.getByText(/powerful features/i)).toBeInTheDocument();
  });

  // Test if the "Analyze Competitors" button is rendered correctly
  it('renders analyze competitors button', () => {
    renderHomePage();

    const button = screen.getByRole('link', { name: /analyze competitors/i });

    // Button is present
    expect(button).toBeInTheDocument();

    // Button points to the query form section
    expect(button).toHaveAttribute('href', '#form');
  });
});
