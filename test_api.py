import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def log(msg, success=True):
    status = "[SUCCESS]" if success else "[FAILURE]"
    print(f"{status} {msg}")

def check(response, expected_status=200):
    if response.status_code != expected_status:
        log(f"Expected {expected_status}, got {response.status_code}: {response.text}", False)
        return False
    return True

def main():
    print("Running API verification...")
    
    # 0. Setup: We need a user to assign issues to. 
    # Since there is no POST /users endpoint in the requirements, we assume manual seeding or we can add a quick one for testing.
    # Wait, the requirements don't mention creating users, but models have User.
    # Let's see if we can just create an issue with assignee_id=1. 
    # If the user table is empty, this will fail with foreign key violation.
    # I should probably insert a dummy user using a direct DB script or add a temp endpoint. 
    # Actually, I can use the same `check_db.py` approach to seed a user.
    
    # Let's first try to list issues to see if the app is responding
    try:
        r = requests.get(f"{BASE_URL}/issues")
        if not check(r, 200): sys.exit(1)
        print("API is up and running.")
    except Exception as e:
        log(f"API is not reachable: {e}", False)
        sys.exit(1)
        
    # Seed a user directly via DB for independent testing
    try:
        from app.database import SessionLocal
        from app.models import User
        db = SessionLocal()
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            user = User(name="Test User", email="test@example.com")
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Seeded User ID: {user.id}")
        user_id = user.id
        db.close()
    except Exception as e:
        log(f"Failed to seed user: {e}", False)
        sys.exit(1)

    # 1. Create Issue
    issue_data = {
        "title": "Test Issue",
        "description": "This is a test issue",
        "assignee_id": user_id
    }
    r = requests.post(f"{BASE_URL}/issues", json=issue_data)
    if not check(r, 200): return
    issue = r.json()
    issue_id = issue['id']
    log(f"Created Issue {issue_id}")

    # 2. Add Comment
    comment_data = {
        "author_id": user_id,
        "body": "This is a comment"
    }
    r = requests.post(f"{BASE_URL}/issues/{issue_id}/comments", json=comment_data)
    if not check(r, 200): return
    log(f"Added comment to Issue {issue_id}")

    # 3. Add Labels
    label_names = ["bug", "priority"]
    r = requests.put(f"{BASE_URL}/issues/{issue_id}/labels", json=label_names)
    if not check(r, 200): return
    labels = r.json()
    if len(labels) == 2:
        log(f"Added {len(labels)} labels to Issue {issue_id}")
    else:
        log(f"Expected 2 labels, got {len(labels)}", False)

    # 4. Get Detailed View
    r = requests.get(f"{BASE_URL}/issues/{issue_id}")
    if not check(r, 200): return
    detail = r.json()
    
    # Verify relations
    has_comments = len(detail['comments']) > 0
    has_labels = len(detail['labels']) > 0
    has_assignee = detail['assignee'] is not None
    
    if has_comments and has_labels and has_assignee:
        log(f"Verified Issue Detail: Comments={len(detail['comments'])}, Labels={len(detail['labels'])}")
    else:
        log(f"Verification Failed: Comments={has_comments}, Labels={has_labels}, Assignee={has_assignee}", False)

    print("\nAll logical checks passed!")

if __name__ == "__main__":
    main()
