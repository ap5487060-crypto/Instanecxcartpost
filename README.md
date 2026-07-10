# 🤖 Affiliate Auto-Post System
**Daily automated trending product posts on Instagram + Facebook**

Roz subah 9 AM: System khud hi trending bestseller products scrape karta hai,
professional images banata hai, EarnKaro affiliate links add karta hai, aur
Instagram Feed, Instagram Story aur Facebook Page par post kar deta hai.
Google Sheet bhi update hoti hai, aur bio link page bhi.

---

## 📁 File Structure
```
insta-affiliate-bot/
├── .github/
│   └── workflows/
│       └── daily_post.yml     ← GitHub Actions (daily 9 AM auto-run)
├── scripts/
│   ├── main.py                ← Main pipeline (runs all steps)
│   ├── scrape_products.py     ← Amazon bestseller scraper
│   ├── earnkaro.py            ← EarnKaro affiliate link converter
│   ├── generate_image.py      ← PIL image generator (1080x1080)
│   ├── upload_image.py        ← imgbb public image hosting
│   ├── post_instagram.py      ← Instagram Graph API (Feed + Story)
│   ├── post_facebook.py       ← Facebook Graph API (Page post)
│   ├── update_sheet.py        ← Google Sheets updater
│   ├── update_bio_page.py     ← GitHub Pages bio-link page builder
│   └── caption.py             ← Hindi/English caption generator
├── docs/
│   └── index.html             ← Bio link page (served via GitHub Pages)
├── data/
│   ├── posted_products.json   ← Duplicate prevention log
│   └── results.json           ← Daily run history
└── requirements.txt
```

---

## ⚙️ ONE-TIME SETUP (sirf ek baar karna hai)

### Step 1 — GitHub Repo banao
1. GitHub par new repo banao: `insta-affiliate-bot` (Private rakho)
2. Ye saare files upload karo (zip karke ya individually)
3. Repo Settings → Pages → Source: **Deploy from branch** → Branch: `main` → Folder: `/docs` → Save
4. Tumhara bio link hoga: `https://YOUR_USERNAME.github.io/insta-affiliate-bot/`

---

### Step 2 — imgbb API Key lo (FREE)
1. https://imgbb.com par jao, sign up karo (free)
2. Login ke baad: https://api.imgbb.com/ → "Get API Key"
3. Key copy karo (baad mein GitHub Secret mein dalni hai)

---

### Step 3 — Facebook Developer App + Instagram Token

#### 3a. App banao:
1. https://developers.facebook.com → My Apps → Create App
2. "Business" type → naam do → Create
3. Dashboard mein "Instagram Graph API" → Set Up click karo

#### 3b. Token generate karo:
1. https://developers.facebook.com/tools/explorer → apna App select karo
2. "Add a Permission" mein ye add karo:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
   - `pages_show_list`
   - `pages_manage_posts`
3. "Generate Access Token" → Login karo → Allow
4. Token copy karo (ye short-lived hai, neeche convert karenge)

#### 3c. Long-lived token banao (60 din ke liye):
Browser mein ye URL open karo (apni values bharo):
```
https://graph.facebook.com/v19.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id=YOUR_APP_ID
  &client_secret=YOUR_APP_SECRET
  &fb_exchange_token=SHORT_LIVED_TOKEN_FROM_ABOVE
```
Response mein `access_token` milega — ye 60-day token hai → copy karo.

> ⚠️ Ye token 60 din mein expire hota hai.
> Har 50 din baad GitHub Secret `IG_ACCESS_TOKEN` update karo.

#### 3d. Instagram Business Account ID nikalo:
Graph API Explorer mein query chalao: `me/accounts`
Response mein apna Facebook Page ID milega.

Phir: `{PAGE_ID}?fields=instagram_business_account`
Response mein `instagram_business_account.id` milega → ye hai tumhara **IG_BUSINESS_ACCOUNT_ID**.

#### 3e. Facebook Page Access Token:
`me/accounts` response mein hi Page ka `access_token` bhi hoga → ye hai **FB_PAGE_ACCESS_TOKEN**.
**FB_PAGE_ID** bhi wahi se milega.

---

### Step 4 — Google Sheet + Service Account

#### 4a. Sheet banao:
1. Google Sheets par ek nayi sheet banao
2. URL mein se ID copy karo:
   `https://docs.google.com/spreadsheets/d/**SHEET_ID_YAHAN_HAI**/edit`
3. Share → "Anyone with the link" → **Viewer** → Done

#### 4b. Service Account (Google Cloud):
1. https://console.cloud.google.com → Project: `youtube-comment-bot-499516` (tumhara existing project)
2. IAM & Admin → Service Accounts → Create Service Account
3. Naam: `affiliate-sheet-bot` → Create
4. Keys tab → Add Key → JSON → Download karo
5. Sheet ko us service account ki email se share karo as **Editor**:
   (email format: `affiliate-sheet-bot@youtube-comment-bot-499516.iam.gserviceaccount.com`)

---

### Step 5 — GitHub Secrets add karo
Repo → Settings → Secrets and Variables → Actions → New Repository Secret

| Secret Name | Value |
|---|---|
| `EARNKARO_API_KEY` | Tumhari EarnKaro API key |
| `IMGBB_API_KEY` | imgbb se mili key |
| `IG_ACCESS_TOKEN` | 60-day long-lived FB/IG token |
| `IG_BUSINESS_ACCOUNT_ID` | Instagram Business Account ID |
| `FB_PAGE_ACCESS_TOKEN` | Facebook Page access token |
| `FB_PAGE_ID` | Facebook Page ID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Service account JSON file ka **poora content** paste karo |
| `GOOGLE_SHEET_ID` | Google Sheet ID |

---

### Step 6 — Test Run karo
1. Repo → Actions tab → "Daily Affiliate Auto-Post" → Run workflow → Run
2. Logs dekho — saara pipeline ek baar test ho jayega
3. Instagram, Facebook, Sheet, bio page — sab check karo

---

## 🔄 Daily Automatic Schedule
**Roz subah 9:00 AM IST** pe khud chalega. Tum kuch nahi karte.

Manually chalana ho to: Actions → Daily Affiliate Auto-Post → Run workflow

---

## 📊 Sheet Format
| Date | Category | Image | Product Name | Price | Buy Link |
|---|---|---|---|---|---|
| 14 Jul 2026 | Electronics | 🖼️ | Boat Earbuds | Rs 999 | earnkaro link |

Sheet ka link: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/`
Ye link bio mein daal sakte ho directly — view-only for public.

---

## ⚠️ Important Notes
- **EarnKaro API key**: Tumne ise public chat mein share kiya — EarnKaro dashboard se isko regenerate kar lo aur naya key GitHub Secret mein daalo.
- **Token refresh**: IG_ACCESS_TOKEN 60 din mein expire hota hai — calendar mein reminder lagao.
- **Amazon scraping**: Kabhi-kabhi Amazon scraper block ho sakta hai. Agar product count 0 dikhe to `scrape_products.py` mein CSS selectors check karo.
- **Instagram limit**: Instagram Graph API se din mein max 25 posts allowed hain — 8 products daily safe hai.
