
import urllib.request
import json
import ssl

def make_request(query, variables):
    url = "https://leetcode.com/graphql"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    data = json.dumps({'query': query, 'variables': variables}).encode('utf-8')
    
    # Bypass SSL verification if needed (though usually not recommended, good for quick scripts)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, data, headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def test_leetcode_api(username):
    # 1. Test Profile Stats
    query_profile = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        username
        submitStats: submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
            submissions
          }
        }
      }
    }
    """
    
    # 2. Test Recent Submissions
    query_recent = """
    query getRecentSubmissions($username: String!) {
      recentAcSubmissionList(username: $username, limit: 5) {
        id
        title
        titleSlug
        timestamp
      }
    }
    """
    
    print(f"Testing for user: {username}")
    
    # Profile Request
    print("Fetching Profile...")
    profile_data = make_request(query_profile, {'username': username})
    if profile_data:
        print("Profile Data:")
        print(json.dumps(profile_data, indent=2))
        
    # Recent Submissions Request
    print("Fetching Recent Submissions...")
    recent_data = make_request(query_recent, {'username': username})
    if recent_data:
        print("Recent Submissions Data:")
        print(json.dumps(recent_data, indent=2))

if __name__ == "__main__":
    test_leetcode_api("awice")
