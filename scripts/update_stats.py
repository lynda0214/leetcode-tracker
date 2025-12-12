import json
import os
import urllib.request
import ssl
import datetime
from datetime import timezone

# Config
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
STATS_FILE = os.path.join(DATA_DIR, 'stats.json')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def make_request(query, variables):
    url = "https://leetcode.com/graphql"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    data = json.dumps({'query': query, 'variables': variables}).encode('utf-8')
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, data, headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Request failed for {variables}: {e}")
        return None

def get_user_data(username):
    query = """
    query getUserData($username: String!) {
      matchedUser(username: $username) {
        username
        submitStats: submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
      recentAcSubmissionList(username: $username, limit: 50) {
        id
        title
        titleSlug
        timestamp
      }
    }
    """
    return make_request(query, {'username': username})

def send_discord_notification(username, new_problems):
    if not DISCORD_WEBHOOK_URL:
        return
    
    # Group by count if too many
    if len(new_problems) > 5:
         content = f"🔥 **{username}** just crushed **{len(new_problems)}** problems! Keep it up!"
    else:
        probs_str = "\n".join([f"- [{p['title']}](https://leetcode.com/problems/{p['titleSlug']}/)" for p in new_problems])
        content = f"🚀 **{username}** solved:\n{probs_str}"

    payload = {
        "content": content
    }
    
    req = urllib.request.Request(DISCORD_WEBHOOK_URL, 
                                 data=json.dumps(payload).encode('utf-8'), 
                                 headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
        print(f"Sent notification for {username}")
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

def get_current_week_start():
    # ISO Calendar: Monday is 1, Sunday is 7
    # We want Monday 00:00 UTC of the current week
    now = datetime.datetime.now(timezone.utc)
    # Subtract days to get to the most recent Monday
    monday = now - datetime.timedelta(days=now.weekday())
    # Reset time to midnight
    return monday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

def main():
    # 1. Load Data
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print("users.json not found.")
        return

    stats = {}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
        except json.JSONDecodeError:
            pass
    
    week_start = get_current_week_start()
    week_start_dt = datetime.datetime.fromisoformat(week_start)
    
    # Check if new week reset is needed
    current_week_start_in_file = stats.get('week_start')
    
    if current_week_start_in_file != week_start:
        print(f"New week detected! Resetting baselines. Old: {current_week_start_in_file}, New: {week_start}")
        stats['week_start'] = week_start
        if 'users' not in stats:
             stats['users'] = {}
        
        # Reset baselines for existing users
        for u in stats.get('users', {}):
             stats['users'][u]['weekly_baseline'] = stats['users'][u].get('total_solved', 0)
             stats['users'][u]['history'] = [] # Clear weekly history
    
    if 'users' not in stats:
        stats['users'] = {}

    # Cleanup: Remove users from stats that are no longer in users.json
    existing_users_in_stats = list(stats['users'].keys())
    for u in existing_users_in_stats:
        if u not in users:
            print(f"Removing {u} from stats (not in users.json)")
            del stats['users'][u]

    # 2. Update Stats
    for username in users:
        print(f"Processing {username}...")
        data = get_user_data(username)
        
        if not data or 'errors' in data:
            print(f"Error fetching data for {username}")
            continue
            
        user_info = data.get('data', {}).get('matchedUser', {})
        submissions = data.get('data', {}).get('recentAcSubmissionList', [])
        
        # Parse total solved
        total_solved = 0
        submit_stats = user_info.get('submitStats', {}).get('acSubmissionNum', [])
        for s in submit_stats:
            if s['difficulty'] == 'All':
                total_solved = s['count']
                break
        
        # Calculate unique problems solved this week from API
        # This allows us to "smart correct" the baseline if it's new or incorrect
        solved_this_week_from_api = set()
        for sub in submissions:
             ts = int(sub['timestamp'])
             sub_dt = datetime.datetime.fromtimestamp(ts, timezone.utc)
             if sub_dt >= week_start_dt:
                 solved_this_week_from_api.add(sub['titleSlug'])
        
        count_this_week_api = len(solved_this_week_from_api)

        # Init user in stats if missing
        if username not in stats['users']:
            # Smart Baseline: Total - This Week's Activity
            baseline = max(0, total_solved - count_this_week_api)
            stats['users'][username] = {
                'total_solved': total_solved,
                'weekly_baseline': baseline,
                'last_check_solved': total_solved,
                'history': []
            }
        
        user_record = stats['users'][username]
        
        # Smart Correction: If baseline implies negative progress or misses this week's API data
        # Theoretical max baseline = Total - Count_This_Week
        # If current baseline > Theoretical max, it means baseline includes problems solved this week. Fix it.
        theoretical_baseline = max(0, total_solved - count_this_week_api)
        if user_record.get('weekly_baseline', 0) > theoretical_baseline:
             print(f"Correcting baseline for {username}. Old: {user_record.get('weekly_baseline')}, New: {theoretical_baseline}")
             user_record['weekly_baseline'] = theoretical_baseline

        # Update History & Detect New Problems
        newly_solved_this_run = []
        
        # We also need to populate 'history' if it's empty but we found problems in API
        # (CASE: First run for a user who already solved problems this week)
        existing_ids = {h['id'] for h in user_record.get('history', [])}
        
        for sub in submissions:
             ts = int(sub['timestamp'])
             sub_dt = datetime.datetime.fromtimestamp(ts, timezone.utc)
             
             if sub_dt >= week_start_dt:
                 if sub['id'] not in existing_ids:
                     # It's new to our record!
                     problem_data = {
                         'id': sub['id'],
                         'title': sub['title'],
                         'titleSlug': sub['titleSlug'],
                         'timestamp': sub['timestamp']
                     }
                     # Add to history
                     user_record.setdefault('history', []).insert(0, problem_data)
                     
                     # Only notify if this is NOT a "backfill" during initialization
                     # We can guess it's a backfill if we just corrected the baseline or initialized the user.
                     # But simple heuristic: Notify if we already had a record and we are updating.
                     # However, for simplicity, we notify freshly discovered problems unless we want to suppress initial flood.
                     # Let's count it as "newly solved" to return meaningful stats, but maybe limit notification/log.
                     newly_solved_this_run.append(problem_data)
                     existing_ids.add(sub['id'])
        
        # Update counts
        user_record['total_solved'] = total_solved
        
        # Send Notifications for newly found problems
        # To avoid spamming on first run/fix, maybe check if newly_solved_this_run count is small or matches exactly the API count?
        # If we just fixed the baseline, these are 'old' new problems. 
        # But the user wants to see "Updates".
        if newly_solved_this_run:
            print(f"Found {len(newly_solved_this_run)} new problems for {username}")
            send_discord_notification(username, newly_solved_this_run)
        
    # 3. Save Stats
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Also save to site/public/stats.json for the frontend
    site_stats_path = os.path.join(os.path.dirname(__file__), '../site/public/stats.json')
    try:
        os.makedirs(os.path.dirname(site_stats_path), exist_ok=True)
        with open(site_stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Stats duplicated to {site_stats_path}")
    except Exception as e:
        print(f"Warning: Could not copy stats to site/public: {e}")

    print("Stats updated.")

if __name__ == "__main__":
    main()
