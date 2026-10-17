export type Deck = {
  id: number;
  name: string;
  type: string;
  description: string | null;
  use_review_dates?: boolean;
  daily_limit?: number;
  review_interval_days?: number;
  reviews_today?: number;
};

export type DeckFormValues = {
  name: string;
  description: string;
};

export type DeckPayload = DeckFormValues & {
  type: string;
};

export type ApiMessage = {
  message?: string;
  error?: string;
};
