# Component Documentation

## Core Components

### ChatContainer

The main chat interface component that handles message display and input.

```tsx
import { ChatContainer } from '@/components/Chat/ChatContainer';

<ChatContainer
  className="custom-class"  // Optional custom styling
  initialMessages={[]}      // Optional initial messages
/>
```

#### Props
- `className?: string` - Additional CSS classes
- `initialMessages?: Message[]` - Initial chat messages

#### Features
- Handles message sending and receiving
- Manages conversation history
- Integrates with streaming responses
- Handles loading states and errors
- Responsive layout with sidebar

### StreamingProvider

Provides streaming functionality for real-time message updates.

```tsx
import { StreamingProvider } from '@/providers/StreamingProvider';

<StreamingProvider>
  <App />
</StreamingProvider>
```

#### Context Values
- `isStreaming: boolean` - Current streaming status
- `streamMessage: (messages: Message[]) => Promise<Message | null>` - Start streaming
- `abortStream: () => void` - Cancel current stream

#### Usage Example
```tsx
const { streamMessage, isStreaming } = useStreaming();

const handleSend = async (content: string) => {
  const result = await streamMessage([{ role: 'user', content }]);
  if (result) {
    // Handle streamed message
  }
};
```

### ConversationSearch

Search component for filtering conversations.

```tsx
import { ConversationSearch } from '@/components/Chat/ConversationSearch';

<ConversationSearch
  onSearch={(query) => {}}
  className="custom-class"
/>
```

#### Props
- `onSearch: (query: string) => void` - Search callback
- `className?: string` - Additional CSS classes

#### Features
- Debounced search input
- Clear button
- Search history

## UI Components

### ChatInput

Text input component for sending messages.

```tsx
import { ChatInput } from '@/components/Chat/ChatInput';

<ChatInput
  onSend={(message) => {}}
  isLoading={false}
  isDisabled={false}
  placeholder="Type a message..."
  className="custom-class"
/>
```

#### Props
- `onSend: (message: string) => void` - Send message callback
- `isLoading?: boolean` - Loading state
- `isDisabled?: boolean` - Disabled state
- `placeholder?: string` - Input placeholder
- `className?: string` - Additional CSS classes

#### Features
- Auto-expanding textarea
- Loading state handling
- Message drafts
- Keyboard shortcuts

### ChatMessage

Individual message component.

```tsx
import { ChatMessage } from '@/components/Chat/ChatMessage';

<ChatMessage
  message={messageObject}
  artifacts={artifacts}
  isLast={false}
  className="custom-class"
/>
```

#### Props
- `message: Message` - Message data
- `artifacts?: Artifact[]` - Message artifacts
- `isLast?: boolean` - Is last message
- `className?: string` - Additional CSS classes

#### Features
- Role-based styling (user/assistant)
- Markdown rendering
- Code syntax highlighting
- Artifact display

## Providers

### ThemeProvider

Manages application theme state.

```tsx
import { ThemeProvider } from '@/contexts/ThemeProvider';

<ThemeProvider>
  <App />
</ThemeProvider>
```

#### Context Values
- `theme: Theme` - Current theme
- `setTheme: (theme: Theme) => void` - Update theme
- `toggleTheme: () => void` - Toggle dark/light mode

### ChatProvider

Manages chat state and operations.

```tsx
import { ChatProvider } from '@/providers/ChatProvider';

<ChatProvider>
  <App />
</ChatProvider>
```

#### Context Values
- `messages: Message[]` - Chat messages
- `sendMessage: (content: string) => Promise<void>` - Send message
- `clearChat: () => void` - Clear chat history
- `isLoading: boolean` - Loading state
- `error: string | null` - Error state

## Hooks

### useChat

```tsx
const {
  messages,
  sendMessage,
  clearChat,
  isLoading,
  error
} = useChat(initialMessages);
```

#### Parameters
- `initialMessages?: Message[]` - Initial messages

#### Returns
- `messages: Message[]` - Current messages
- `sendMessage: (content: string) => Promise<void>` - Send message
- `clearChat: () => void` - Clear chat
- `isLoading: boolean` - Loading state
- `error: string | null` - Error state

### useStreaming

```tsx
const {
  streamMessage,
  isStreaming,
  abortStream
} = useStreaming();
```

#### Returns
- `streamMessage: (messages: Message[]) => Promise<Message | null>` - Start streaming
- `isStreaming: boolean` - Current streaming status
- `abortStream: () => void` - Cancel current stream

## Types

### Message
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}
```

### Artifact
```typescript
interface Artifact {
  id: string;
  type: 'code' | 'markdown' | 'html' | 'svg' | 'mermaid' | 'react';
  content: string;
  title?: string;
  metadata?: Record<string, any>;
}
```

### Theme
```typescript
type Theme = 'light' | 'dark' | 'system';
```

## CSS Classes

### Layout
```css
.chat-container /* Main chat layout */
.message-container /* Message wrapper */
.input-container /* Input area */
.sidebar /* Chat sidebar */
```

### Theme
```css
.glass /* Glass morphism effect */
.glass-light /* Lighter glass effect */
.animate-in /* Fade in animation */
.animate-out /* Fade out animation */
```

### States
```css
.loading /* Loading state */
.disabled /* Disabled state */
.error /* Error state */
```