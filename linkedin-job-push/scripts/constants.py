"""Static URLs and API endpoints used across the project."""

# LinkedIn guest API — no login required
LINKEDIN_JOBS_SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
LINKEDIN_JOB_POSTING_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

# Used as Referer header for LinkedIn requests
LINKEDIN_JOBS_REFERER = "https://www.linkedin.com/jobs/search/"

# Telegram Bot API
TELEGRAM_SEND_MESSAGE_URL = "https://api.telegram.org/bot{token}/sendMessage"
