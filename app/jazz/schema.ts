/**
 * Jazz CoValue schemas for feedback data structures.
 * Uses CRDTs for conflict-free replicated data.
 * Can be used as primary data store (no backend needed!)
 */
import { co, CoMap, CoList, Group, Account } from "jazz-tools";

/**
 * Feedback item schema
 * Represents a single feedback entry with CRDT properties
 */
export class FeedbackItem extends CoMap {
  orderId = co.string;
  courierId = co.number;
  rating = co.number;
  comment = co.string;
  reasons = co.json<string[]>();
  publishConsent = co.boolean;
  needsFollowUp = co.boolean;
  timestamp = co.string;
  requestId = co.string;
  synced = co.boolean;  // Track if synced to server
  syncAttempts = co.number;  // Number of sync attempts

  // Metadata
  createdAt = co.string;
  updatedAt = co.string;
  deviceId = co.string;
}

/**
 * Pending feedback queue
 * CRDT list that automatically syncs across devices
 */
export class PendingFeedbackQueue extends CoList.Of(co.ref(FeedbackItem)) {}

/**
 * All feedback collection (for dashboard)
 * Replaces SQL database in jazz-only mode
 */
export class FeedbackCollection extends CoMap {
  items = co.ref(CoList.Of(co.ref(FeedbackItem)));
  totalCount = co.number;
  lastUpdated = co.string;
}

/**
 * Courier information
 */
export class Courier extends CoMap {
  id = co.number;
  name = co.string;
  phone = co.string;
  contactLink = co.string;
  createdAt = co.string;
}

/**
 * Couriers collection
 */
export class CourierCollection extends CoMap {
  items = co.ref(CoList.Of(co.ref(Courier)));
}

/**
 * Admin user for Jazz-only authentication
 */
export class AdminUser extends CoMap {
  username = co.string;
  passwordHash = co.string;  // bcrypt hash
  createdAt = co.string;
  lastLogin = co.string;
}

/**
 * Admin users collection
 */
export class AdminCollection extends CoMap {
  users = co.ref(CoList.Of(co.ref(AdminUser)));
}

/**
 * Feedback session metadata
 * Tracks session info for analytics
 */
export class FeedbackSession extends CoMap {
  sessionId = co.string;
  userId = co.string;  // Anonymous or authenticated
  deviceId = co.string;
  startedAt = co.string;
  lastActivity = co.string;
  pendingCount = co.number;
  syncedCount = co.number;
  mode = co.string;  // jazz_only, hybrid, etc.
}

/**
 * Application state root
 * Top-level CoMap containing all app data
 * In jazz-only mode, this IS the database
 */
export class AppState extends CoMap {
  pendingQueue = co.ref(PendingFeedbackQueue);
  allFeedback = co.ref(FeedbackCollection);
  couriers = co.ref(CourierCollection);
  admins = co.ref(AdminCollection);
  session = co.ref(FeedbackSession);
  lastSync = co.string;
  mode = co.string;
}

/**
 * Helper functions for working with Jazz data
 */
export const JazzHelpers = {
  /**
   * Create a new feedback item
   */
  createFeedbackItem(data: {
    orderId: string;
    courierId: number;
    rating: number;
    comment: string;
    reasons: string[];
    publishConsent: boolean;
    requestId: string;
  }): Partial<FeedbackItem> {
    const now = new Date().toISOString();
    return {
      orderId: data.orderId,
      courierId: data.courierId,
      rating: data.rating,
      comment: data.comment,
      reasons: data.reasons,
      publishConsent: data.publishConsent,
      needsFollowUp: data.rating <= 4,
      timestamp: now,
      requestId: data.requestId,
      synced: false,
      syncAttempts: 0,
      createdAt: now,
      updatedAt: now,
      deviceId: getDeviceId(),
    };
  },

  /**
   * Create courier
   */
  createCourier(data: {
    id: number;
    name: string;
    phone: string;
    contactLink?: string;
  }): Partial<Courier> {
    return {
      id: data.id,
      name: data.name,
      phone: data.phone,
      contactLink: data.contactLink || "",
      createdAt: new Date().toISOString(),
    };
  },

  /**
   * Create admin user
   */
  createAdminUser(username: string, passwordHash: string): Partial<AdminUser> {
    return {
      username,
      passwordHash,
      createdAt: new Date().toISOString(),
      lastLogin: new Date().toISOString(),
    };
  },

  /**
   * Convert Jazz feedback to plain object
   */
  feedbackToJSON(feedback: FeedbackItem): any {
    return {
      order_id: feedback.orderId,
      courier_id: feedback.courierId,
      rating: feedback.rating,
      comment: feedback.comment,
      reasons: feedback.reasons,
      publish_consent: feedback.publishConsent,
      needs_follow_up: feedback.needsFollowUp,
      timestamp: feedback.timestamp,
      request_id: feedback.requestId,
      synced: feedback.synced,
      sync_attempts: feedback.syncAttempts,
      created_at: feedback.createdAt,
      updated_at: feedback.updatedAt,
      device_id: feedback.deviceId,
    };
  },

  /**
   * Convert courier to plain object
   */
  courierToJSON(courier: Courier): any {
    return {
      id: courier.id,
      name: courier.name,
      phone: courier.phone,
      contact_link: courier.contactLink,
      created_at: courier.createdAt,
    };
  },

  /**
   * Mark feedback as synced
   */
  markAsSynced(feedback: FeedbackItem): void {
    feedback.synced = true;
    feedback.syncAttempts = (feedback.syncAttempts || 0) + 1;
    feedback.updatedAt = new Date().toISOString();
  },

  /**
   * Add feedback to main collection (for dashboard)
   */
  addToCollection(
    collection: FeedbackCollection,
    feedback: FeedbackItem
  ): void {
    if (collection.items) {
      collection.items.push(feedback);
      collection.totalCount = (collection.totalCount || 0) + 1;
      collection.lastUpdated = new Date().toISOString();
    }
  },

  /**
   * Filter feedback by date range
   */
  filterByDateRange(
    items: FeedbackItem[],
    fromDate?: string,
    toDate?: string
  ): FeedbackItem[] {
    let filtered = items;

    if (fromDate) {
      const from = new Date(fromDate);
      filtered = filtered.filter(
        (item) => new Date(item.createdAt) >= from
      );
    }

    if (toDate) {
      const to = new Date(toDate);
      filtered = filtered.filter(
        (item) => new Date(item.createdAt) <= to
      );
    }

    return filtered;
  },

  /**
   * Filter feedback by rating
   */
  filterByRatings(
    items: FeedbackItem[],
    ratings: number[]
  ): FeedbackItem[] {
    if (ratings.length === 0) return items;
    return items.filter((item) => ratings.includes(item.rating));
  },
};

/**
 * Get or create device ID
 */
function getDeviceId(): string {
  let deviceId = localStorage.getItem("jazz_device_id");
  if (!deviceId) {
    deviceId = `device_${Math.random().toString(36).substring(2, 15)}`;
    localStorage.setItem("jazz_device_id", deviceId);
  }
  return deviceId;
}

/**
 * Initialize app state for jazz-only mode
 */
export async function initializeJazzOnlyApp(account: Account): Promise<AppState> {
  // Create or load app state
  const stateId = localStorage.getItem("jazz_app_state_id");
  let appState: AppState;

  if (stateId) {
    appState = await AppState.load(stateId, account, {});
    if (appState) return appState;
  }

  // Create new app state
  const group = await Group.create(account);

  appState = AppState.create(
    {
      pendingQueue: PendingFeedbackQueue.create([], { owner: group }),
      allFeedback: FeedbackCollection.create(
        {
          items: CoList.Of(co.ref(FeedbackItem)).create([], { owner: group }),
          totalCount: 0,
          lastUpdated: new Date().toISOString(),
        },
        { owner: group }
      ),
      couriers: CourierCollection.create(
        {
          items: CoList.Of(co.ref(Courier)).create([], { owner: group }),
        },
        { owner: group }
      ),
      admins: AdminCollection.create(
        {
          users: CoList.Of(co.ref(AdminUser)).create([], { owner: group }),
        },
        { owner: group }
      ),
      session: FeedbackSession.create(
        {
          sessionId: `session_${Date.now()}`,
          userId: account.id,
          deviceId: getDeviceId(),
          startedAt: new Date().toISOString(),
          lastActivity: new Date().toISOString(),
          pendingCount: 0,
          syncedCount: 0,
          mode: "jazz_only",
        },
        { owner: group }
      ),
      lastSync: new Date().toISOString(),
      mode: "jazz_only",
    },
    { owner: group }
  );

  localStorage.setItem("jazz_app_state_id", appState.id);
  return appState;
}
