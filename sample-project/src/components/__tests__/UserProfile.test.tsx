import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserProfile } from '../UserProfile';

// Mock fetch for API calls
global.fetch = vi.fn();

describe('UserProfile Component', () => {
  const mockOnSave = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with correct title', () => {
    render(
      <UserProfile
        title="Test Profile"
        onSave={mockOnSave}
      />
    );

    expect(screen.getByText('Test Profile')).toBeInTheDocument();
  });

  it('renders form fields correctly', () => {
    render(
      <UserProfile
        title="Test Profile"
        onSave={mockOnSave}
      />
    );

    expect(screen.getByLabelText('Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save profile/i })).toBeInTheDocument();
  });

  it('loads user data when userId is provided', async () => {
    const mockUserData = { name: 'John Doe', email: 'john@example.com' };
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockUserData),
    });

    render(
      <UserProfile
        title="Edit Profile"
        onSave={mockOnSave}
        userId="123"
      />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/users/123');
    });
  });

  it('handles form submission correctly', async () => {
    render(
      <UserProfile
        title="Test Profile"
        onSave={mockOnSave}
      />
    );

    const nameInput = screen.getByLabelText('Name');
    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', { name: /save profile/i });

    fireEvent.change(nameInput, { target: { value: 'Test User' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalled();
    });
  });

  it('displays loading state during submission', async () => {
    const slowOnSave = vi.fn(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(
      <UserProfile
        title="Test Profile"
        onSave={slowOnSave}
      />
    );

    const submitButton = screen.getByRole('button', { name: /save profile/i });
    fireEvent.click(submitButton);

    expect(screen.getByText('Saving...')).toBeInTheDocument();
  });

  it('applies correct variant styling', () => {
    const { rerender } = render(
      <UserProfile
        title="Test Profile"
        onSave={mockOnSave}
        variant="primary"
      />
    );

    const mainElement = screen.getByRole('main');
    expect(mainElement).toHaveClass('user-profile--primary');

    rerender(
      <UserProfile
        title="Test Profile"
        onSave={mockOnSave}
        variant="secondary"
      />
    );

    expect(mainElement).toHaveClass('user-profile--secondary');
  });
});
