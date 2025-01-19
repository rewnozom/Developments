# Testing Guide

## Overview

The application uses a comprehensive testing strategy including:
- Unit Tests
- Integration Tests
- Component Tests
- End-to-End Tests

## Test Stack

- **Vitest** - Test runner and framework
- **Testing Library** - Component testing
- **MSW** - API mocking
- **Playwright** - End-to-end testing

## Running Tests

### All Tests
```bash
npm test
# or
yarn test
```

### Watch Mode
```bash
npm test:watch
# or
yarn test:watch
```

### Coverage Report
```bash
npm test:coverage
# or
yarn test:coverage
```

## Test Structure

```
src/
├── __tests__/          # Global test utilities
├── components/
│   └── __tests__/      # Component tests
├── hooks/
│   └── __tests__/      # Hook tests
└── test/
    ├── mocks/          # Mock data and handlers
    └── utils/          # Test utilities
```

## Component Testing

### Basic Component Test

```typescript
import { render, screen } from '@testing-library/react';
import { ChatMessage } from '../ChatMessage';

describe('ChatMessage', () => {
  it('renders correctly', () => {
    const message = {
      id: '123',
      role: 'user',
      content: 'Test message',
    };

    render(<ChatMessage message={message} />);
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });
});
```

### Testing User Interactions

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('ChatInput', () => {
  it('handles user input', async () => {
    const onSend = vi.fn();
    const { user } = render(<ChatInput onSend={onSend} />);

    const input = screen.getByRole('textbox');
    await user.type(input, 'Hello{Enter}');

    expect(onSend).toHaveBeenCalledWith('Hello');
  });
});
```

## Hook Testing

### Testing Custom Hooks

```typescript
import { renderHook, act } from '@testing-library/react';
import { useChat } from '../useChat';

describe('useChat', () => {
  it('manages chat state', () => {
    const { result } = renderHook(() => useChat());

    act(() => {
      result.current.sendMessage('Test message');
    });

    expect(result.current.messages).toHaveLength(1);
  });
});
```

## API Mocking

### MSW Setup

```typescript
// src/test/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.post('/api/chat', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 'response-id',
        messages: [{
          role: 'assistant',
          content: 'Mocked response'
        }]
      })
    );
  }),
];
```

### Testing API Interactions

```typescript
import { server } from '../../test/mocks/server';
import { rest } from 'msw';

describe('API Integration', () => {
  it('handles API errors', async () => {
    server.use(
      rest.post('/api/chat', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    // Test error handling
  });
});
```

## Streaming Tests

### Testing Streaming Responses

```typescript
describe('Streaming', () => {
  it('handles streamed messages', async () => {
    server.use(
      rest.post('/api/chat', (req, res, ctx) => {
        const encoder = new TextEncoder();
        const stream = new ReadableStream({
          start(controller) {
            const chunks = ['Hello', ' world'];
            chunks.forEach(chunk => {
              controller.enqueue(
                encoder.encode(`data: ${JSON.stringify({ content: chunk })}\n\n`)
              );
            });
            controller.close();
          },
        });

        return new Response(stream, {
          headers: { 'Content-Type': 'text/event-stream' },
        });
      })
    );

    // Test streaming functionality
  });
});
```

## Integration Testing

### Testing Provider Integration

```typescript
import { render } from '../../test/utils/test-utils';

const AllTheProviders = ({ children }) => {
  return (
    <ThemeProvider>
      <SettingsProvider>
        <ChatProvider>
          {children}
        </ChatProvider>
      </SettingsProvider>
    </ThemeProvider>
  );
};

const customRender = (ui, options) =>
  render(ui, { wrapper: AllTheProviders, ...options });
```

## End-to-End Testing

### Playwright Setup

```typescript
// e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test('complete chat flow', async ({ page }) => {
  await page.goto('/');
  
  // Send a message
  await page.fill('textarea', 'Hello Claude');
  await page.click('button[type="submit"]');
  
  // Wait for response
  await expect(page.locator('.message-content')).toContainText('Hello');
});
```

## Test Utilities

### Custom Matchers

```typescript
expect.extend({
  toBeValidMessage(received) {
    return {
      pass: received.id && received.role && received.content,
      message: () => 'Expected valid message structure',
    };
  },
});
```

### Mock Data Generators

```typescript
export const createMockMessage = (overrides = {}) => ({
  id: 'test-id',
  role: 'user',
  content: 'Test message',
  timestamp: new Date().toISOString(),
  ...overrides,
});
```

## Performance Testing

### Load Testing

```typescript
import { performance } from 'perf_hooks';

describe('Performance', () => {
  it('renders messages efficiently', async () => {
    const start = performance.now();
    
    // Render 1000 messages
    render(<ChatContainer messages={Array(1000).fill(createMockMessage())} />);
    
    const end = performance.now();
    expect(end - start).toBeLessThan(1000); // Should render in under 1s
  });
});
```

## Accessibility Testing

### Testing A11y

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('should have no accessibility violations', async () => {
  const { container } = render(<ChatContainer />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Code Coverage

### Coverage Thresholds

```javascript
// vitest.config.ts
export default {
  coverage: {
    reporter: ['text', 'json', 'html'],
    branches: 80,
    functions: 80,
    lines: 80,
    statements: 80,
  },
};
```

## Test Best Practices

1. **Arrange-Act-Assert**: Structure tests clearly
2. **Test Behavior**: Focus on component behavior, not implementation
3. **Meaningful Assertions**: Make assertions that validate important outcomes
4. **Isolation**: Keep tests independent and isolated
5. **Mock Wisely**: Only mock what's necessary
6. **Test Edge Cases**: Consider error states and edge cases
7. **Maintainable Tests**: Write clear, maintainable test code
8. **CI Integration**: Run tests in CI/CD pipeline

## Debug Testing

### Debug Tools

```typescript
// Debug rendered component
screen.debug();

// Debug specific element
screen.debug(screen.getByRole('button'));

// Log all available elements
console.log(screen.logTestingPlaygroundURL());
```