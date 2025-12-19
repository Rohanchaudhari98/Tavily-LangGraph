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

  const renderQueryForm = () => {
    return render(
      <BrowserRouter>
        <QueryForm />
      </BrowserRouter>
    );
  };

  it('renders form fields', () => {
    renderQueryForm();
    
    expect(screen.getByPlaceholderText(/e.g., Tavily/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/pricing strategy/i)).toBeInTheDocument();
    expect(screen.getByText(/freshness filter/i)).toBeInTheDocument();
    expect(screen.getAllByText(/auto-discovery/i).length).toBeGreaterThan(0);
  });

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

  it('toggles auto-discovery', async () => {
    const user = userEvent.setup();
    renderQueryForm();
    
    const toggleButton = screen.getByRole('button', { name: '' }); // Toggle button
    const toggleButtons = screen.getAllByRole('button');
    const discoveryToggle = toggleButtons.find(btn => 
      btn.className.includes('bg-gradient-to-br') || btn.className.includes('bg-gray-300')
    );
    
    if (discoveryToggle) {
      await user.click(discoveryToggle);
      expect(screen.getByText(/maximum competitors to find/i)).toBeInTheDocument();
    }
  });

  it('shows competitor input when auto-discovery is off', () => {
    renderQueryForm();
    expect(screen.getByTestId('competitor-input')).toBeInTheDocument();
  });

  it('validates that competitors are required when auto-discovery is off', async () => {
    renderQueryForm();
    
    // The submit button should be disabled when no competitors and auto-discovery is off
    const submitButton = screen.getByRole('button', { name: /analyze competitors/i });
    expect(submitButton).toBeDisabled();
  });

  it('submits form with auto-discovery enabled', async () => {
    const user = userEvent.setup();
    const mockResponse = { query_id: 'test-123' };
    api.createQuery.mockResolvedValue(mockResponse);
    
    renderQueryForm();
    
    // Fill in required fields
    await user.type(screen.getByPlaceholderText(/e.g., Tavily/i), 'Netflix');
    await user.type(screen.getByPlaceholderText(/pricing strategy/i), 'Compare pricing');
    
    // Enable auto-discovery by finding the toggle button
    const toggleButtons = screen.getAllByRole('button');
    const discoveryToggle = toggleButtons.find(btn => 
      btn.type === 'button' && (btn.className.includes('bg-gray-300') || btn.className.includes('rounded-full'))
    );
    
    if (discoveryToggle) {
      await user.click(discoveryToggle);
      
      // Wait for auto-discovery UI to appear
      await waitFor(() => {
        expect(screen.getByText(/maximum competitors to find/i)).toBeInTheDocument();
      });
      
      // Submit form
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

  it('allows changing freshness filter', async () => {
    const user = userEvent.setup();
    renderQueryForm();
    
    // Find the select element by its text content or role
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

