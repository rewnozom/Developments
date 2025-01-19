const DRAFT_KEY_PREFIX = 'claude_draft_';
const DRAFT_METADATA_KEY = 'claude_drafts_metadata';

interface DraftMetadata {
  conversationId: string;
  timestamp: string;
  preview: string;
}

class DraftManager {
  private getDraftKey(conversationId: string): string {
    return `${DRAFT_KEY_PREFIX}${conversationId}`;
  }

  private getMetadata(): Record<string, DraftMetadata> {
    try {
      const metadata = localStorage.getItem(DRAFT_METADATA_KEY);
      return metadata ? JSON.parse(metadata) : {};
    } catch {
      return {};
    }
  }

  private setMetadata(metadata: Record<string, DraftMetadata>): void {
    localStorage.setItem(DRAFT_METADATA_KEY, JSON.stringify(metadata));
  }

  saveDraft(conversationId: string, content: string): void {
    if (!content.trim()) {
      this.deleteDraft(conversationId);
      return;
    }

    const draftKey = this.getDraftKey(conversationId);
    const metadata = this.getMetadata();

    try {
      localStorage.setItem(draftKey, content);
      metadata[conversationId] = {
        conversationId,
        timestamp: new Date().toISOString(),
        preview: content.slice(0, 100),
      };
      this.setMetadata(metadata);
    } catch (error) {
      console.error('Error saving draft:', error);
      this.cleanup();
    }
  }

  loadDraft(conversationId: string): string | null {
    try {
      const draftKey = this.getDraftKey(conversationId);
      return localStorage.getItem(draftKey);
    } catch {
      return null;
    }
  }

  deleteDraft(conversationId: string): void {
    const draftKey = this.getDraftKey(conversationId);
    const metadata = this.getMetadata();

    localStorage.removeItem(draftKey);
    delete metadata[conversationId];
    this.setMetadata(metadata);
  }

  getAllDrafts(): DraftMetadata[] {
    const metadata = this.getMetadata();
    return Object.values(metadata).sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }

  cleanup(): void {
    const metadata = this.getMetadata();
    const now = Date.now();
    const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days

    Object.entries(metadata).forEach(([id, data]) => {
      if (now - new Date(data.timestamp).getTime() > maxAge) {
        this.deleteDraft(id);
      }
    });

    // Also clean up any orphaned drafts
    Object.keys(localStorage)
      .filter(key => key.startsWith(DRAFT_KEY_PREFIX))
      .forEach(key => {
        const id = key.slice(DRAFT_KEY_PREFIX.length);
        if (!metadata[id]) {
          localStorage.removeItem(key);
        }
      });
  }
}

export const draftManager = new DraftManager();