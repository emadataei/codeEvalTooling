# User Profile Component

A React component for displaying and editing user information with enhanced features.

## Features

- **Data Loading**: Automatically loads user data when `userId` is provided
- **Form Handling**: Robust form submission with error handling
- **Accessibility**: Semantic HTML with proper ARIA labels
- **Styling Variants**: Primary and secondary visual themes
- **Loading States**: Visual feedback during async operations

## Usage

### Basic Usage

```tsx
import { UserProfile } from './components/UserProfile';

function App() {
  const handleSave = async (formData: FormData) => {
    // Handle form submission
    const userData = {
      name: formData.get('name') as string,
      email: formData.get('email') as string,
    };
    
    await saveUser(userData);
  };

  return (
    <UserProfile
      title="Create User"
      onSave={handleSave}
      variant="primary"
    />
  );
}
```

### Edit Existing User

```tsx
<UserProfile
  title="Edit User Profile"
  onSave={handleSave}
  variant="primary"
  userId="123"
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | Required | The title displayed at the top of the form |
| `onSave` | `(data: FormData) => void` | Required | Callback function when form is submitted |
| `variant` | `'primary' \| 'secondary'` | `'primary'` | Visual styling variant |
| `userId` | `string` | `undefined` | Optional user ID for loading existing data |

## API Integration

The component expects a REST API with the following endpoints:

- `GET /api/users/{id}` - Load user data
- `PUT /api/users/{id}` - Update user data

### Response Format

```json
{
  "success": true,
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

## Styling

The component uses CSS classes that can be customized:

- `.user-profile` - Main container
- `.user-profile--primary` - Primary variant styling
- `.user-profile--secondary` - Secondary variant styling
- `.form-group` - Form field containers

## Accessibility

- Uses semantic HTML elements (`<main>`, `<form>`)
- Proper ARIA labels and descriptions
- Keyboard navigation support
- Screen reader friendly

## Testing

Run tests with:

```bash
npm test UserProfile
```

See `__tests__/UserProfile.test.tsx` for test examples.
