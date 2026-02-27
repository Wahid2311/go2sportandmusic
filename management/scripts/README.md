# Go2SportAndMusic Management Scripts

This directory contains automated management scripts for the go2sportandmusic.com platform.

## Scripts Overview

### 1. automatic_event_delete.py
**Purpose:** Automatically deletes expired events from the database

**Features:**
- Deletes events older than 30 days (configurable)
- Automatically removes associated tickets
- Logs all deletions
- Prevents accidental data loss with safety checks

**Usage:**
```bash
python management/scripts/automatic_event_delete.py
```

**Configuration:**
- `days_after_expiry`: Number of days after event date to delete (default: 30)

---

### 2. automatic_listing_delete.py
**Purpose:** Automatically deletes expired or sold-out ticket listings

**Features:**
- Deletes sold-out tickets
- Deletes listings for past events
- Deletes listings with 0 available tickets
- Provides detailed deletion logs

**Usage:**
```bash
python management/scripts/automatic_listing_delete.py
```

**Configuration:**
- `delete_sold_out`: Delete sold-out tickets (default: True)
- `days_after_expiry`: Days after event to delete (default: 7)

---

### 3. scraper.py
**Purpose:** Scrapes events from external sources and imports them into the database

**Features:**
- Multi-process scraping for performance
- Supports XS2Events API
- Supports Ticketmaster API
- Automatic duplicate detection
- Error handling and logging

**Supported Sources:**
- XS2Events (requires `XS2EVENT_API_KEY`)
- Ticketmaster (requires `TICKETMASTER_API_KEY`)

**Usage:**
```bash
python management/scripts/scraper.py
```

**Environment Variables Required:**
```
XS2EVENT_API_KEY=your_api_key
TICKETMASTER_API_KEY=your_api_key
```

---

### 4. checking.py
**Purpose:** Verifies data integrity and generates comprehensive reports

**Features:**
- Event data validation
- Listing integrity checks
- Sales and order verification
- Category analysis
- Comprehensive reporting
- Identifies data issues and warnings

**Checks Performed:**
- Events without categories/dates/names
- Listings without events or sections
- Listings with 0 tickets
- Orders without buyers
- Sales without orders
- Unpaid sales tracking

**Usage:**
```bash
python management/scripts/checking.py
```

**Output:**
- Detailed log file in `logs/checking.log`
- Console output with statistics and issues

---

### 5. pricing.py
**Purpose:** Manages dynamic pricing and pricing optimization

**Features:**
- Dynamic pricing based on demand
- Early bird discounts
- Bulk discounts
- Category-based pricing
- Automatic price optimization
- Revenue impact analysis

**Pricing Strategies:**
- **Demand-based:** Prices increase as availability decreases and event approaches
- **Early bird:** Discounts for events far in the future
- **Bulk:** Discounts for large quantities
- **Category:** Category-specific pricing multipliers

**Usage:**
```bash
python management/scripts/pricing.py
```

**Demand Levels:**
- `very_high`: 50% price increase
- `high`: 25% price increase
- `medium`: No change
- `low`: 15% price decrease

---

## Installation & Setup

### 1. Create logs directory
```bash
mkdir -p logs
```

### 2. Set environment variables
Create a `.env` file in the project root:
```
XS2EVENT_API_KEY=your_key
TICKETMASTER_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token (optional)
TELEGRAM_CHAT_ID=your_chat_id (optional)
```

### 3. Make scripts executable
```bash
chmod +x management/scripts/*.py
```

---

## Scheduling with Cron

### Daily automatic cleanup (2 AM)
```bash
0 2 * * * cd /path/to/project && python management/scripts/automatic_event_delete.py
0 3 * * * cd /path/to/project && python management/scripts/automatic_listing_delete.py
```

### Daily pricing optimization (1 AM)
```bash
0 1 * * * cd /path/to/project && python management/scripts/pricing.py
```

### Daily data integrity check (4 AM)
```bash
0 4 * * * cd /path/to/project && python management/scripts/checking.py
```

### Hourly event scraping
```bash
0 * * * * cd /path/to/project && python management/scripts/scraper.py
```

---

## Logging

All scripts generate detailed logs in the `logs/` directory:
- `logs/event_deletion.log` - Event deletion logs
- `logs/listing_deletion.log` - Listing deletion logs
- `logs/scraper.log` - Scraper logs
- `logs/checking.log` - Data integrity check logs
- `logs/pricing.log` - Pricing optimization logs

---

## Error Handling

All scripts include:
- Comprehensive error logging
- Exception handling
- Traceback logging
- Graceful failure modes
- Optional Telegram notifications (if configured)

---

## Database Backups

**Important:** Before running deletion scripts, ensure you have recent database backups:

```bash
# Create backup
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Restore backup if needed
python manage.py loaddata backup_20260227_120000.json
```

---

## Performance Considerations

- Scripts use Django ORM for safety
- Batch operations where possible
- Multiprocessing for parallel scraping
- Configurable batch sizes
- Logging for performance monitoring

---

## Troubleshooting

### Script not running
- Check Django settings are configured correctly
- Verify database connection
- Check file permissions (`chmod +x`)

### API errors
- Verify API keys in `.env` file
- Check API rate limits
- Review API documentation

### Database errors
- Check database backups exist
- Verify database permissions
- Check disk space

### Memory issues
- Reduce batch sizes
- Increase server resources
- Run during off-peak hours

---

## Support & Maintenance

For issues or questions:
1. Check the relevant log file
2. Review error messages
3. Verify configuration
4. Check database integrity with `checking.py`

---

## Version History

- v1.0 (2026-02-27): Initial release
  - Event deletion
  - Listing deletion
  - Web scraping
  - Data checking
  - Dynamic pricing

---

## License

Internal use only for go2sportandmusic.com
