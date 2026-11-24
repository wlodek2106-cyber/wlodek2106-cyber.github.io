# ZER0LIFE Academy owner activation

1. Create your own account at https://zer0life-academy.onrender.com/dashboard using a unique password of at least 12 characters. Never send the password, session token, database URL, or wallet private key to anyone.
2. Sign in and record the numeric Account ID shown in your account. Verify the ID from your own authenticated session.
3. In the existing Academy Render service, merge ACADEMY_ADMIN_ENABLED=true and ACADEMY_PARTNER_ADMIN_IDS=<your verified numeric ID>. Do not replace the other environment variables. Do not grant access based only on an email.
4. After successful deployment, sign in and confirm Admin Dashboard, Registration Network, Founder Control Center and Partner administration appear. Check that a separate ordinary account cannot access these sections.
5. Account security allows password changes; changing a password invalidates all existing sessions. Administrative access is still password/session based; MFA is not implemented.
6. Before commercial launch: verify a real USDC payment and a real manual payout with explicit authorization and funds, establish sales/refund/privacy terms, and migrate protected curriculum and answer keys to nonpublic storage. Existing public Git history cannot be made confidential merely by deleting files.

No paid services are required for owner activation. No funds are transferred during setup.
