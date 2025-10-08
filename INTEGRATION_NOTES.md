## Integration Notes

### SMS Providers
- Africa's Talking (recommended in KE): `https://developers.africastalking.com`
  - Required: Username, API Key, Sender ID (optional/paid)
  - Scopes/permissions: SMS Send
  - Sandbox: Use sandbox credentials and base URLs from official docs
- Twilio alternative: `https://www.twilio.com/docs/sms`
  - Required: Account SID, Auth Token, From Number

Implementation uses an adapter `SMSProvider` with `sendSMS` and `checkStatus`.
Provide env vars in `.env`. Do not hardcode credentials.

### M-Pesa Daraja (B2C)
Docs: `https://developer.safaricom.co.ke/daraja/apis/post/BusinessPayment`
- Use Sandbox first. Obtain: Consumer Key, Consumer Secret, Shortcode, Initiator Name, Security Credential.
- This repo requires `sandbox=true` in requests and `ENABLE_REAL_PAYMENTS=true` env to allow real payouts.
- Provide callback URLs as required by Daraja for async results (to be added in backend services/payments).

### TLS and Secrets
- All external calls must use HTTPS. Secrets are passed via environment variables and should be stored in a secret manager in production.

