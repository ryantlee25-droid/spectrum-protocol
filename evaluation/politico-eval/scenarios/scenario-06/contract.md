# Contract: billing-system-0331

**Frozen at**: 2026-03-31T12:30:00Z
**Status**: FROZEN — do not modify. File AMENDMENT.md if changes are needed.

---

## Shared Types

All Howlers importing shared types MUST use the paths defined here. Do not re-declare these types.

### Plan (source: howler-subscriptions)
```typescript
// src/billing/subscriptions/plan.schema.ts
export interface Plan {
  id: string;
  name: string;
  priceMonthly: number;       // in cents
  priceAnnual: number;        // in cents
  features: string[];
  isActive: boolean;
  createdAt: Date;
}
```

### Invoice (source: howler-invoices)
```typescript
// src/billing/invoices/invoice.schema.ts
export type InvoiceStatus = "draft" | "open" | "paid" | "void" | "uncollectible";

export interface Invoice {
  id: string;
  customerId: string;
  subscriptionId: string;
  status: InvoiceStatus;
  lineItems: LineItem[];
  totalCents: number;
  dueDate: Date;
  paidAt?: Date;
}

export interface LineItem {
  description: string;
  quantity: number;
  unitAmount: number;        // in cents
  totalAmount: number;       // in cents
}
```

### PaymentIntent (source: howler-payments)
```typescript
// src/billing/payments/payment.service.ts (re-exported)
export interface PaymentIntent {
  id: string;                // Stripe PaymentIntent ID (pi_...)
  customerId: string;
  amount: number;            // Payment amount
  currency: string;          // ISO 4217 currency code (lowercase: "usd", "eur")
  status: "requires_payment_method" | "requires_confirmation" | "processing" | "succeeded" | "canceled";
  invoiceId?: string;        // Linked invoice if applicable
  metadata: Record<string, string>;
  createdAt: Date;
}
```

### BillingEvent (source: howler-webhooks)
```typescript
// src/billing/webhooks/webhook.handler.ts (re-exported)
export type BillingEventType =
  | "payment.succeeded"
  | "payment.failed"
  | "subscription.created"
  | "subscription.updated"
  | "subscription.canceled"
  | "invoice.created"
  | "invoice.paid";

export interface BillingEvent {
  id: string;
  type: BillingEventType;
  payload: Record<string, unknown>;
  processedAt?: Date;
}
```

---

## Naming Conventions

- **Module structure**: `src/billing/{domain}/{file}.ts`
- **Service files**: `{entity}.service.ts` — class with injectable methods
- **Route files**: `{entity}.routes.ts` — Express Router export
- **Schema files**: `{entity}.schema.ts` — TypeScript interface definitions
- **Stripe IDs**: always prefixed strings (`pi_`, `sub_`, `in_`, `cus_`) — never plain UUIDs
- **Monetary values**: stored in cents (integer) throughout the system; `amount` fields are cents
- **Currency**: lowercase ISO 4217 (`"usd"`, `"eur"`) in all types and Stripe API calls
- **Events**: emitted via Node.js EventEmitter pattern; listeners registered in `src/billing/router.ts`

---

## Integration Points

| From | To | Interface | Where |
|------|----|-----------|-------|
| howler-subscriptions | howler-invoices | `Plan` type + subscription events | howler-invoices creates invoices from subscription lifecycle events |
| howler-payments | howler-webhooks | `PaymentIntent` type | howler-webhooks processes `payment.succeeded` / `payment.failed` Stripe events |
| howler-payments | howler-notifications | `PaymentIntent` type | howler-notifications sends payment receipt emails |
| howler-invoices | howler-notifications | `Invoice` type | howler-notifications sends invoice ready emails |
| howler-webhooks | howler-notifications | `BillingEvent` type | howler-notifications listens for billing events to trigger dunning |
| howler-subscriptions | howler-integration | Plan routes registration | howler-integration mounts `plan.routes.ts` at `/billing/plans` |
| howler-invoices | howler-integration | Invoice routes registration | howler-integration mounts `invoice.routes.ts` at `/billing/invoices` |
| howler-payments | howler-integration | Payment routes registration | howler-integration mounts `payment.routes.ts` at `/billing/payments` |
| howler-webhooks | howler-integration | Webhook routes registration | howler-integration mounts `webhook.routes.ts` at `/billing/webhooks` |

---

## Design-by-Contract: howler-subscriptions

### Preconditions
- PostgreSQL available at `DATABASE_URL`
- Stripe SDK configured with `STRIPE_SECRET_KEY`

### Postconditions
- `plan.service.ts` exports `PlanService` class with `createPlan()`, `updatePlan()`, `assignPlan()`, `changePlan()` methods
- `proration.ts` exports `calculateProration(oldPlan: Plan, newPlan: Plan, daysRemaining: number): number` — returns proration amount in cents
- `plan.routes.ts` exports Express Router mounted at the routes defined in the integration points
- `plan.schema.ts` exports `Plan` interface matching the contract definition above

### Invariants
- Plan prices are always stored in cents (integer arithmetic only)
- `assignPlan()` emits a `subscription.created` event on the EventEmitter
- `changePlan()` emits a `subscription.updated` event and calls `calculateProration()`

---

## Design-by-Contract: howler-invoices

### Preconditions
- `howler-subscriptions#types` checkpoint is STABLE (`Plan` type finalized)

### Postconditions
- `invoice.service.ts` exports `InvoiceService` with `createInvoice()`, `finalizeInvoice()`, `voidInvoice()` methods
- `line-items.ts` exports `calculateLineItems(plan: Plan, period: { start: Date; end: Date }): LineItem[]`
- `pdf.ts` exports `generateInvoicePdf(invoice: Invoice): Promise<Buffer>`
- `invoice.schema.ts` exports `Invoice`, `LineItem`, `InvoiceStatus` matching the contract above
- `invoice.routes.ts` exports Express Router for invoice CRUD

### Invariants
- Invoice state machine: `draft` → `open` → `paid | void | uncollectible` (no other transitions)
- `totalCents` always equals sum of `lineItems[*].totalAmount`
- PDF generation is lazy (only when explicitly requested)

---

## Design-by-Contract: howler-payments

### Preconditions
- Stripe SDK (`stripe` npm package) configured with `STRIPE_SECRET_KEY`

### Postconditions
- `payment.service.ts` exports `PaymentService` with `createPaymentIntent()`, `capturePayment()`, `refundPayment()` methods
- `stripe.client.ts` exports singleton Stripe client instance
- `retry.ts` exports `withRetry<T>(fn: () => Promise<T>, maxAttempts: number): Promise<T>`
- `PaymentIntent` interface is re-exported from `payment.service.ts`

### Invariants
- All Stripe API calls are wrapped in `withRetry()` with `maxAttempts: 3`
- `createPaymentIntent()` always sets `metadata.invoiceId` when an invoiceId is provided
- Currency passed to Stripe is always lowercase (enforced by `PaymentIntent.currency` type using lowercase convention)

---

## Design-by-Contract: howler-webhooks

### Preconditions
- `howler-payments#types` checkpoint is STABLE (`PaymentIntent` type finalized)
- `STRIPE_WEBHOOK_SECRET` environment variable defined

### Postconditions
- `webhook.handler.ts` exports `WebhookHandler` class with `handleEvent(rawBody: Buffer, signature: string): Promise<BillingEvent>`
- `idempotency.ts` exports `isAlreadyProcessed(eventId: string): Promise<boolean>` and `markProcessed(eventId: string): Promise<void>`
- `webhook.routes.ts` exports Express Router with `POST /` that validates signature and calls `handleEvent`
- `BillingEvent` and `BillingEventType` are exported from `webhook.handler.ts`

### Invariants
- Signature validation uses `stripe.webhooks.constructEvent()` — any other approach is rejected
- `handleEvent` is idempotent: processing the same event ID twice has no additional effect
- Webhook route must use `express.raw({ type: "application/json" })` body parser (not `express.json()`)

---

## Design-by-Contract: howler-notifications

### Preconditions
- None (no type dependencies on other Howlers at build time; receives events at runtime)
- `SENDGRID_API_KEY` or `SMTP_HOST` environment variable defined

### Postconditions
- `email.service.ts` exports `EmailService` with `sendPaymentReceipt()`, `sendInvoiceReady()`, `sendDunningEmail()` methods
- `templates.ts` exports typed email template functions for each email type
- `dunning.ts` exports `DunningSchedule` type and `scheduleDunning(customerId: string, invoiceId: string): Promise<void>`
- `EmailService` is initialized with the EventEmitter from `src/billing/router.ts` and registers its own listeners

### Invariants
- Email sending never throws — failures are logged and retried asynchronously
- Dunning emails: 3, 7, 14 days after invoice due date (hardcoded schedule)

---

## Design-by-Contract: howler-integration

### Preconditions
- All five billing Howlers are fully complete (not just #types)
- Express app context is available for router mounting

### Postconditions
- `src/billing/router.ts` exports `billingRouter` (Express Router) with all billing routes mounted
- `src/billing/router.ts` creates and exports the `billingEvents` EventEmitter instance
- `src/billing/middleware.ts` exports billing-specific middleware (Stripe signature check, billing auth guard)
- `tests/billing.integration.test.ts` covers: plan creation → subscription → invoice generation → payment → webhook processing
- `tests/billing.fixtures.ts` exports test fixtures for all billing entities

### Invariants
- All billing routes are mounted under `/billing` prefix
- `billingEvents` EventEmitter is the single event bus for the entire billing module
- howler-notifications' `EmailService` is initialized with `billingEvents` in the router setup
