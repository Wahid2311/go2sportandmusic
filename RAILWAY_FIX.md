# Railway 500 Error Fix - Complete Solution

## Problem Identified
**Error**: `relation "events_eventcategory" does not exist`

**Root Cause**: The migration files for the new EventCategory model were not created, so the database table was never created.

## Solution Applied

### 1. Created Missing Migration Files
✅ `events/migrations/0005_eventcategory.py` - Creates EventCategory table and adds category fields to Event model
✅ `tickets/migrations/0004_stripe_fields.py` - Adds Stripe payment fields to Order model

### 2. Updated Procfile
✅ Procfile now includes:
```
release: python manage.py migrate && python manage.py populate_categories
web: python manage.py collectstatic --noinput && gunicorn go2events.wsgi
```

## How to Deploy the Fix

### Step 1: Push the Updated Code
```bash
git add .
git commit -m "Fix: Add missing migrations for EventCategory and Stripe fields"
git push origin main
```

### Step 2: Verify Environment Variables
Go to Railway Dashboard → Your Project → Settings → Environment Variables

Make sure these exist:
```
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
```

### Step 3: Trigger Deployment
Railway will automatically deploy when you push. Monitor the logs:

1. Go to Railway Dashboard → Your Project → Logs
2. Look for these messages:
   - "Running migrations..."
   - "Operations to perform:"
   - "Applying events.0005_eventcategory..."
   - "Applying tickets.0004_stripe_fields..."
   - "Populating categories..."
   - "Successfully created 5 categories"

### Step 4: Verify the Fix
Once deployment completes:
1. Visit go2sportandmusic.com
2. You should see the new landing page (no 500 error)
3. Categories should display in the "Browse by Category" section

## Files Modified/Created

### New Migration Files:
- ✅ `events/migrations/0005_eventcategory.py`
- ✅ `tickets/migrations/0004_stripe_fields.py`

### Updated Files:
- ✅ `Procfile` - Added migration and category population commands
- ✅ `requirements.txt` - Already includes stripe==11.0.0

## What These Migrations Do

### EventCategory Migration (0005_eventcategory.py)
1. Creates `events_eventcategory` table with fields:
   - id (primary key)
   - name (unique)
   - slug (unique)
   - description
   - icon
   - is_active
   - order
   - created_at
   - updated_at

2. Adds to Event model:
   - `category` (ForeignKey to EventCategory)
   - `category_legacy` (for backward compatibility)

### Stripe Fields Migration (0004_stripe_fields.py)
1. Adds to Order model:
   - `stripe_payment_intent_id`
   - `stripe_session_id`

2. Makes Revolut fields nullable:
   - `revolut_order_id`
   - `revolut_checkout_url`

## Troubleshooting

### Still Getting 500 Error?

1. **Check Railway Logs**
   - Look for migration errors
   - Check for import errors
   - Look for database connection issues

2. **Verify Migrations Ran**
   - Look for "Applying events.0005_eventcategory..." in logs
   - Look for "Applying tickets.0004_stripe_fields..." in logs

3. **Manual Fix via Railway Console**
   - Go to Railway Dashboard → Your Project → Shell
   - Run: `python manage.py migrate --verbose`
   - Run: `python manage.py populate_categories`

4. **Check Database Connection**
   - Verify DATABASE_URL is set in environment variables
   - Verify PostgreSQL is running and accessible

### If Categories Don't Appear

1. Check that `populate_categories` command ran in logs
2. Manually run: `python manage.py populate_categories`
3. Verify categories in Django admin: `/admin/events/eventcategory/`

## Testing Checklist

- [ ] Push code to GitHub
- [ ] Railway auto-deploys
- [ ] Check logs for migration success
- [ ] Visit site - no 500 error
- [ ] See new landing page design
- [ ] Categories display in "Browse by Category" section
- [ ] Search functionality works
- [ ] Payment flow works (redirects to Stripe)

## Support

If issues persist:
1. Check the exact error in Railway logs
2. Verify all environment variables are set
3. Try manual migration via Railway console
4. Check that all files were pushed to GitHub

---

**Status**: Ready to Deploy
**Estimated Fix Time**: 5-10 minutes
**Deployment Time**: 2-3 minutes
