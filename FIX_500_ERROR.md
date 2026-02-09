# Fix for 500 Server Error - Railway Deployment

## Problem
After pushing the updated code, you're getting a 500 Server Error on go2sportandmusic.com

## Root Cause
The new `EventCategory` model requires:
1. Database migrations to create the table
2. Categories to be populated
3. Stripe package to be installed

## Solution

### Step 1: Verify Environment Variables
Go to Railway Dashboard → Your Project → Settings → Environment Variables

Make sure these are set:
```
STRIPE_SECRET_KEY=Publishable_key
STRIPE_PUBLISHABLE_KEY=Publishable_key
```

### Step 2: Trigger New Deployment
The updated **Procfile** will automatically run:
- Migrations
- Category population

**Option A: Push a new commit**
```bash
git add .
git commit -m "Fix: Updated Procfile for migrations"
git push origin main
```

**Option B: Redeploy in Railway**
1. Go to Railway Dashboard
2. Click on your project
3. Go to "Deployments"
4. Click the three dots on the latest deployment
5. Click "Redeploy"

### Step 3: Monitor the Deployment
1. Go to Railway Dashboard
2. Click on your project
3. Go to "Logs"
4. Watch for messages like:
   - "Running migrations..."
   - "Populating categories..."
   - "Migrations completed successfully"

### Step 4: Verify the Fix
Once deployment completes:
1. Visit go2sportandmusic.com
2. You should see the new landing page design
3. Categories should display in the "Browse by Category" section

## If Still Getting 500 Error

### Check Railway Logs
1. Go to Railway Dashboard → Your Project → Logs
2. Look for error messages
3. Common errors:
   - "ModuleNotFoundError: No module named 'stripe'" → Run `pip install stripe`
   - "relation 'events_eventcategory' does not exist" → Migrations didn't run
   - "ImportError" → Check imports in views.py

### Manual Fix via Railway Console
If automatic fix doesn't work:

1. Go to Railway Dashboard → Your Project → Shell
2. Run these commands:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py populate_categories
   ```
3. Restart the app

### Fallback: Revert to Old Design
If you need to quickly revert:
```bash
# Restore old home page
cp templates/events/home_backup.html templates/events/home.html
git add .
git commit -m "Revert: Restore old home page"
git push origin main
```

## Files Changed
- ✅ Procfile - Updated with migration commands
- ✅ run_migrations.py - Backup migration script
- ✅ All code changes from previous update

## Support
If the error persists:
1. Check Railway logs for specific error message
2. Verify all environment variables are set
3. Try manual migration via Railway console
4. Contact support with the error message from logs

---

**Status**: Ready to deploy
**Estimated Fix Time**: 2-5 minutes
