# Nyonga WhatsApp Admissions Bot (Vercel)

This version removes legacy/invalid runtime settings that caused the error:
> Function Runtimes must have a valid version, for example `now-php@1.0.0`

## Deploy
1) Push to GitHub → Import into Vercel.
2) Add env vars from `.env.example` (Project Settings → Environment Variables).
3) Your webhook URL will be:
   `https://<your-vercel-domain>/api/webhook`
4) In Meta Developers → WhatsApp → Configuration:
   - Callback URL: that URL
   - Verify Token: same as `WABA_VERIFY_TOKEN`
   - Subscribe to `messages` and `message_template_status_update`.

No `runtime` versions are specified; Vercel auto-detects Node for files in `/api`.
