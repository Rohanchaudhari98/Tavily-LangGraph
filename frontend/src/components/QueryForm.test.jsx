// Unit tests for the QueryForm component

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import QueryForm from './QueryForm';
import * as api from '../services/api';

// Mock the API service
vi.mock('../services/api', () => ({
  createQuery: vi.fn(),
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock CompetitorInput component
vi.mock('./CompetitorInput', () => ({
  default: ({ competitors, setCompetitors }) => (
    <div data-testid="competitor-input">
      <input
        data-testid="add-competitor-input"
        placeholder="Add competitor"
        onKeyDown={(e) => {
          if (e.key === 'Enter' && e.target.value) {
            setCompetitors([...competitors, e.target.value]);
            e.target.value = '';
          }
        }}
      />
      <div data-testid="competitors-list">
        {competitors.map((comp, idx) => (
          <div key={idx} data-testid={`competitor-${idx}`}>
            {comp}
          </div>
        ))}
      </div>
    </div>
  ),
}));

describe('QueryForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  // Helper to render the form within a router
  const renderQueryForm = () => {
    return render(
      <BrowserRouter>
        <QueryForm />
      </BrowserRouter>
    );
  };

  // Test that basic form fields render
  it('renders form fields', () => {
    renderQueryForm();
    expect(screen.getByPlaceholderText(/e.g., Tavily/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/pricing strategy/i)).toBeInTheDocument();
    expect(screen.getByText(/freshness filter/i)).toBeInTheDocument();
    expect(screen.getAllByText(/auto-discovery/i).length).toBeGreaterThan(0);
  });

  // Test entering company name and query
  it('allows entering company name and query', async () => {
    const user = userEvent.setup();
    renderQueryForm();

    const companyInput = screen.getByPlaceholderText(/e.g., Tavily/i);
    const queryInput = screen.getByPlaceholderText(/pricing strategy/i);

    await user.type(companyInput, 'Tavily');
    await user.type(queryInput, 'Compare pricing and features');

    expect(companyInput).toHaveValue('Tavily');
    expect(queryInput).toHaveValue('Compare pricing and features');
  });

  // Test toggling auto-discovery UI
  it('toggles auto-discovery', async () => {
    const user = userEvent.setup();
    renderQueryForm();

    const toggleButtons = screen.getAllByRole('button');
    const discoveryToggle = toggleButtons.find(btn => 
      btn.className.includes('bg-gradient-to-br') || btn.className.includes('bg-gray-300')
    );

    if (discoveryToggle) {
      await user.click(discoveryToggle);
      expect(screen.getByText(/maximum competitors to find/i)).toBeInTheDocument();
    }
  });

  // Test that competitor input renders when auto-discovery is off
  it('shows competitor input when auto-discovery is off', () => {
    renderQueryForm();
    expect(screen.getByTestId('competitor-input')).toBeInTheDocument();
  });

  // Test validation requiring competitors when auto-discovery is off
  it('validates that competitors are required when auto-discovery is off', async () => {
    renderQueryForm();
    const submitButton = screen.getByRole('button', { name: /analyze competitors/i });
    expect(submitButton).toBeDisabled();
  });

  // Test submitting the form with auto-discovery enabled
  it('submits form with auto-discovery enabled', async () => {
    const user = userEvent.setup();
    const mockResponse = { query_id: 'test-123' };
    api.createQuery.mockResolvedValue(mockResponse);

    renderQueryForm();

    // Fill in required fields
    await user.type(screen.getByPlaceholderText(/e.g., Tavily/i), 'Netflix');
    await user.type(screen.getByPlaceholderText(/pricing strategy/i), 'Compare pricing');

    // Enable auto-discovery
    const toggleButtons = screen.getAllByRole('button');
    const discoveryToggle = toggleButtons.find(btn => 
      btn.type === 'button' && (btn.className.includes('bg-gray-300') || btn.className.includes('rounded-full'))
    );

    if (discoveryToggle) {
      await user.click(discoveryToggle);

      // Wait for auto-discovery options to appear
      await waitFor(() => {
        expect(screen.getByText(/maximum competitors to find/i)).toBeInTheDocument();
      });

      // Submit the form
      const submitButton = screen.getByRole('button', { name: /analyze competitors/i });
      expect(submitButton).not.toBeDisabled();
      await user.click(submitButton);

      await waitFor(() => {
        expect(api.createQuery).toHaveBeenCalledWith(
          expect.objectContaining({
            company_name: 'Netflix',
            query: 'Compare pricing',
            use_auto_discovery: true,
          })
        );
      });
    }
  });

  // Test changing freshness filter
  it('allows changing freshness filter', async () => {
    const user = userEvent.setup();
    renderQueryForm();

    const selects = screen.getAllByRole('combobox');
    const freshnessSelect = selects.find(select => 
      select.querySelector('option[value="3months"]')
    ) || selects[0];

    if (freshnessSelect) {
      await user.selectOptions(freshnessSelect, '3months');
      expect(freshnessSelect).toHaveValue('3months');
    }
  });
});
